#!/usr/bin/env python3
"""Merge selected upstream paths using Git's three-way merge; never execute upstream code."""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)


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
        p = subprocess.run(['git', 'merge-file', '-p', *map(str, paths)], capture_output=True)
    if not 0 <= p.returncode <= 127:
        raise RuntimeError('git merge-file failed')
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
        ours = path.read_bytes() if path.is_file() else None
        base, base_mode = old.get(relative, (None, None))
        theirs, their_mode = new.get(relative, (None, None))
        merged, conflict = merge_file(ours, base, theirs)
        if conflict:
            conflicts.append(str(path.relative_to(root)))
            continue
        our_mode = ('100755' if path.stat().st_mode & 0o111 else '100644') if path.is_file() else None
        mode = merge_mode(our_mode, base_mode, their_mode)
        plan[path] = (merged, mode)
    return plan, conflicts


def sync(root, report_path, cache=None):
    manifest_path = root / '.sync/upstreams.json'
    manifest = json.loads(manifest_path.read_text())
    cache = cache or root / '.git/upstream-cache'
    cache.mkdir(parents=True, exist_ok=True)
    plan, updates, conflicts = {}, [], []
    for source in manifest['sources']:
        repo, ref, base = source['repo'], source['ref'], source['revision']
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
            raise ValueError('Unsupported upstream repository')
        if not re.fullmatch(r'[a-f0-9]{40}', base):
            raise ValueError('Upstream baseline must be a full commit SHA')
        mirror = cache / repo.replace('/', '--')
        if not mirror.exists():
            subprocess.run(['git', 'init', '--bare', '-q', str(mirror)], check=True)
        url = 'https://github.com/' + repo + '.git'
        git(mirror, 'fetch', '--quiet', '--depth=1', url, 'refs/heads/' + ref)
        head = git(mirror, 'rev-parse', 'FETCH_HEAD').decode().strip()
        if head == base:
            continue
        try:
            git(mirror, 'cat-file', '-e', base + '^{commit}')
        except subprocess.CalledProcessError:
            git(mirror, 'fetch', '--quiet', '--depth=1', url, base)
        for mapping in source['paths']:
            old = snapshot(mirror, base, mapping['source'])
            new = snapshot(mirror, head, mapping['source'])
            # License changes need a human licensing review, not text auto-merge.
            if mapping['destination'].startswith('licenses/') and new != old:
                conflicts.append(mapping['destination'] + ' (license changed)')
                continue
            changes, blocked = plan_mapping(root, old, new, mapping['destination'])
            if plan.keys() & changes.keys():
                raise ValueError('Overlapping upstream destinations')
            plan.update(changes)
            conflicts.extend(blocked)
        updates.append({'repo': repo, 'from': base, 'to': head})
        source['revision'] = head
    report = {'updates': updates, 'conflicts': conflicts, 'applied': False}
    # All-or-nothing: conflicts never leave a partially updated working tree.
    if not conflicts:
        for path, (content, mode) in plan.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
                path.chmod(0o755 if mode == '100755' else 0o644)
        if updates:
            manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
        report['applied'] = True
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 2 if conflicts else 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--cache', type=Path)
    args = parser.parse_args()
    raise SystemExit(sync(ROOT, args.report, args.cache))
