#!/usr/bin/env python3
"""Merge selected upstream paths using Git's three-way merge; never execute upstream code."""
import argparse
import difflib
import json
import re
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE, timeout=90)


def safe_path(value):
    p = PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts or not p.parts or '.git' in p.parts:
        raise ValueError(f'Unsafe relative path: {value}')
    return p


def snapshot(repo, revision, source):
    safe_path(source)
    entries = git(repo, 'ls-tree', '-r', '-z', revision, '--', source).split(b'\0')
    files = {}
    for entry in filter(None, entries):
        meta, raw_path = entry.split(b'\t', 1)
        mode, kind, blob = meta.decode().split()
        path = raw_path.decode()
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise ValueError(f'Unsupported upstream file type: {path}')
        relative = '' if path == source else path.removeprefix(source.rstrip('/') + '/')
        if relative:
            safe_path(relative)
        content = git(repo, 'cat-file', 'blob', blob)
        if b'\0' in content:
            raise ValueError(f'Binary upstream file requires review: {path}')
        content.decode('utf-8')
        files[relative] = (content, mode)
    if not files:
        raise ValueError(f'Upstream path missing at {revision}: {source}')
    return files


def merge_file(ours, base, theirs):
    """Return (merged content, conflict); None represents a deleted file."""
    if theirs == base or ours == theirs:
        return ours, False
    if ours == base:
        return theirs, False
    if ours is None or base is None or theirs is None:
        return None, True
    if b'\0' in ours + base + theirs:
        return None, True
    with tempfile.TemporaryDirectory() as tmp:
        paths = [Path(tmp) / name for name in ('ours', 'base', 'theirs')]
        for path, content in zip(paths, (ours, base, theirs)):
            path.write_bytes(content)
        p = subprocess.run(['git', 'merge-file', '-p', *map(str, paths)], capture_output=True, timeout=90)
    if not 0 <= p.returncode <= 127:
        raise ValueError('git merge-file failed')
    return p.stdout if p.returncode == 0 else None, p.returncode != 0


def merge_mode(ours, base, theirs):
    if theirs == base or ours == theirs:
        return ours
    if ours == base:
        return theirs
    raise ValueError('Conflicting file permissions')


def plan_mapping(root, old, new, destination):
    root = root.resolve()
    safe_path(destination)
    if PurePosixPath(destination).parts[0] not in ('skills', 'licenses'):
        raise ValueError('Sync destinations must be inside skills/ or licenses/')
    plan, conflicts = {}, []
    for relative in sorted(old.keys() | new.keys()):
        path = root / destination / relative if relative else root / destination
        if any(p.is_symlink() for p in [path, *path.parents] if p == root or root in p.parents):
            raise ValueError(f'Symlink destination requires review: {path}')
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('Destination escapes repository')
        if path.exists() and not path.is_file():
            raise ValueError('Destination file replaced by a directory: ' + str(path.relative_to(root)))
        ours = path.read_bytes() if path.is_file() else None
        base, base_mode = old.get(relative, (None, None))
        theirs, their_mode = new.get(relative, (None, None))
        merged, conflict = merge_file(ours, base, theirs)
        if conflict:
            conflicts.append(str(path.relative_to(root)))
            continue
        our_mode = ('100755' if path.stat().st_mode & 0o111 else '100644') if path.is_file() else None
        try:
            mode = merge_mode(our_mode, base_mode, their_mode)
        except ValueError:
            conflicts.append(str(path.relative_to(root)))
            continue
        plan[path] = (merged, mode)
    return plan, conflicts


def validate_manifest(manifest):
    """Reject ambiguous ownership before fetching or changing any files."""
    destinations, repos = [], set()
    for source in manifest['sources']:
        repo = source['repo']
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo) or repo in repos:
            raise ValueError('Unsupported or duplicate upstream repository')
        repos.add(repo)
        if not re.fullmatch(r'[a-f0-9]{40}', source['revision']):
            raise ValueError('Upstream baseline must be a full commit SHA')
        subprocess.run(['git', 'check-ref-format', 'refs/heads/' + source['ref']], check=True, capture_output=True)
        if not source['paths']:
            raise ValueError('Upstream must have reviewed path mappings')
        for mapping in source['paths']:
            safe_path(mapping['source'])
            path = safe_path(mapping['destination'])
            if len(path.parts) < 2 or path.parts[0] not in ('skills', 'licenses'):
                raise ValueError('Sync destinations must be inside skills/ or licenses/')
            if any(path == other or path in other.parents or other in path.parents for other in destinations):
                raise ValueError('Overlapping upstream destinations')
            destinations.append(path)


def review_diff(root, old, new, destination, paths):
    """Keep exact upstream/local deltas in the report, never in installed skills."""
    reviews = []
    for relative in sorted(old.keys() | new.keys()):
        path = str(PurePosixPath(destination) / relative) if relative else destination
        if path not in paths:
            continue
        base = old.get(relative, (b'', None))[0].decode('utf-8')
        theirs = new.get(relative, (b'', None))[0].decode('utf-8')
        local = root / path
        ours = local.read_text(encoding='utf-8', errors='replace') if local.is_file() else ''
        def diff(text, label):
            return ''.join(difflib.unified_diff(base.splitlines(True), text.splitlines(True),
                                               fromfile='base/' + path, tofile=label + '/' + path))
        reviews.append({'path': path, 'upstream_diff': diff(theirs, 'upstream'),
                        'local_diff': diff(ours, 'local'),
                        'modes': {'base': old.get(relative, (None, None))[1],
                                  'upstream': new.get(relative, (None, None))[1]}})
    return reviews


def sync(root, report_path, cache=None):
    root = root.resolve()
    manifest_path = root / '.sync/upstreams.json'
    manifest = json.loads(manifest_path.read_text())
    validate_manifest(manifest)
    cache = cache or Path(git(root, 'rev-parse', '--absolute-git-dir').decode().strip()) / 'upstream-cache'
    cache.mkdir(parents=True, exist_ok=True)
    plan, updates, conflicts, results, errors = {}, [], [], [], []
    for source in manifest['sources']:
        repo, ref, base = source['repo'], source['ref'], source['revision']
        result = {'repo': repo, 'from': base, 'status': 'unchanged', 'conflicts': [], 'reviews': []}
        results.append(result)
        source_plan = {}
        try:
            mirror = cache / repo.replace('/', '--')
            if not mirror.exists():
                subprocess.run(['git', 'init', '--bare', '-q', str(mirror)], check=True)
            url = 'https://github.com/' + repo + '.git'
            git(mirror, 'fetch', '--quiet', '--depth=1', url, 'refs/heads/' + ref)
            head = git(mirror, 'rev-parse', 'FETCH_HEAD').decode().strip()
            result['to'] = head
            if head == base:
                continue
            try:
                git(mirror, 'cat-file', '-e', base + '^{commit}')
            except subprocess.CalledProcessError:
                git(mirror, 'fetch', '--quiet', '--depth=1', url, base)
            for mapping in source['paths']:
                old = snapshot(mirror, base, mapping['source'])
                new = snapshot(mirror, head, mapping['source'])
                destination = mapping['destination']
                changes, blocked = plan_mapping(root, old, new, destination)
                # License changes block the whole source, including its skills.
                if destination.startswith('licenses/') and new != old:
                    blocked = [destination]
                    changes = {}
                result['conflicts'].extend(blocked)
                result['reviews'].extend(review_diff(root, old, new, destination, blocked))
                source_plan.update(changes)
        except (subprocess.SubprocessError, ValueError, OSError) as exc:
            # Keep raw command stderr out of public reports (it may contain auth data).
            result['status'] = 'error'
            result['error'] = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
            errors.append({'repo': repo, 'error': result['error']})
            continue
        if result['conflicts']:
            result['status'] = 'blocked'
            conflicts.extend(result['conflicts'])
            continue
        result['status'] = 'updated'
        plan.update(source_plan)
        updates.append({'repo': repo, 'from': base, 'to': head})
        source['revision'] = head
    # Commit each source's files and baseline together; blocked sources stay untouched.
    for path, (content, mode) in plan.items():
        if content is None:
            path.unlink(missing_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            path.chmod(0o755 if mode == '100755' else 0o644)
    if updates:
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    report = {'updates': updates, 'conflicts': conflicts, 'errors': errors,
              'applied': bool(updates) or not (conflicts or errors), 'sources': results}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 2 if conflicts or errors else 0


def summary_markdown(report):
    def cell(value):
        return str(value).replace('|', '&#124;').replace('\r\n', '\n').replace('\r', '\n').replace('\n', '<br>')
    lines = ['| Repo | Status | From | To | Conflict paths | Error |',
             '| --- | --- | --- | --- | --- | --- |']
    for source in report['sources']:
        values = [source['repo'], source['status'], source['from'][:7], source.get('to', '')[:7],
                  '\n'.join(source.get('conflicts', [])), source.get('error', '')]
        lines.append('| ' + ' | '.join(map(cell, values)) + ' |')
    return '\n'.join(lines) + '\n\nSee the upstream-sync-report artifact for full review diffs.\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--summarize', type=Path)
    parser.add_argument('--cache', type=Path)
    args = parser.parse_args()
    if args.summarize:
        print(summary_markdown(json.loads(args.summarize.read_text())), end='')
        raise SystemExit(0)
    if not args.report:
        parser.error('--report is required unless --summarize is given')
    raise SystemExit(sync(ROOT, args.report, args.cache))
