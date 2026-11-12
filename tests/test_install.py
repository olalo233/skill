"""install-base checks: immutable snapshots, journaled rollback, verified
restore, qualified identity, project bounds, suites, lock, update/uninstall."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / 'scripts/install-base'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def commit_all(repo, message='commit'):
    subprocess.run(['git', '-C', str(repo), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Test',
                    '-c', 'user.email=test@example.com', 'commit', '-qm', message],
                   check=True)
    return git(repo, 'rev-parse', 'HEAD')


def tree_state(root):
    """Snapshot every path under root (for zero-write assertions)."""
    state = {}
    for p in sorted(root.rglob('*')):
        rel = str(p.relative_to(root))
        if p.is_symlink():
            state[rel] = ('link', str(p.readlink()))
        elif p.is_dir():
            state[rel] = ('dir',)
        elif p.is_file():
            state[rel] = ('file', p.read_bytes())
    return state


def make_clone(base, skills=None, retired=None, suites=None, upstreams=None):
    """A minimal 'skill' clone: skills + index + optional suite files."""
    src = base / 'clone'
    skills = skills or [('ask-me', 'skills/ask-me'), ('demo', 'skills/demo')]
    entries = []
    for name, rel in skills:
        (src / rel).mkdir(parents=True)
        body = f'---\nname: {name}\ndescription: {name} skill\n---\nbody\n'
        (src / rel / 'SKILL.md').write_text(body)
        entries.append({'name': name, 'suite': rel.split('/')[1]
                        if rel.startswith('vendor/') else 'base',
                        'summary': name, 'path': f'{rel}/SKILL.md', 'depends': []})
    for name, spec in (suites or {}).items():
        (src / 'suites').mkdir(exist_ok=True)
        (src / 'suites' / f'{name}.json').write_text(json.dumps(spec))
    (src / '.sync').mkdir(exist_ok=True)
    retired = {'*': ['adr', 'work-archive'], **(retired or {})}
    (src / '.sync/index-source.json').write_text(json.dumps({
        'suites': {'base': {'title': 'Base',
                            'skills': [e['name'] for e in entries
                                       if e['suite'] == 'base']}},
        'depends': {}, 'retired': retired}))
    if upstreams:
        (src / '.sync/upstreams.json').write_text(json.dumps(upstreams))
    (src / 'index.json').write_text(json.dumps({'version': 1, 'skills': entries}))
    (src / 'INDEX.md').write_text('# index\n')
    subprocess.run(['git', 'init', '-q', str(src)], check=True)
    return src, commit_all(src, 'init')


def suite(members):
    return {'name': 'x', 'kind': 'skills',
            'members': [{'name': n, 'path': p, 'depends': d}
                        for n, p, d in members]}


class InstallTests(unittest.TestCase):
    def run_install(self, *args, cwd=None, fail=None):
        env = dict(os.environ)
        if fail:
            env['INSTALL_BASE_FAIL'] = fail
        return subprocess.run([sys.executable, str(INSTALL), *args],
                              capture_output=True, text=True, cwd=cwd, env=env)

    def backups(self, base):
        return sorted(base.rglob('.install-base-backup-*'))

    def test_dry_run_writes_nothing_and_prints_source_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = make_clone(base)
            target = base / 'home/agents/skills'
            (target / 'adr').mkdir(parents=True)
            (target / 'adr/old.md').write_text('old')
            before = tree_state(base)
            result = self.run_install('--dry-run', '--source', str(src),
                                      '--ref', head, '--target', str(target))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(str(src), result.stdout)
            self.assertIn(head, result.stdout)
            self.assertIn('retire', result.stdout)
            self.assertIn('index', result.stdout)
            self.assertEqual(before, tree_state(base))  # nothing written anywhere

    def test_apply_installs_from_immutable_snapshot_not_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = make_clone(base)
            # untracked + ignored files in the worktree must NOT be installed
            (src / 'skills/demo/untracked.txt').write_text('not committed')
            (src / '.gitignore').write_text('secret.env\n')
            (src / 'skills/demo/secret.env').write_text('SECRET=1')
            target = base / 'home/skills'
            result = self.run_install('--apply', '--source', str(src), '--ref', head,
                                      '--target', str(target))
            self.assertEqual(result.returncode, 0, result.stderr)
            demo = target / 'demo'
            self.assertTrue(demo.is_symlink())
            snap = demo.resolve()
            self.assertIn('.install-base-snapshots', str(snap))
            self.assertIn(head, str(snap))
            self.assertFalse((snap / 'untracked.txt').exists())
            self.assertFalse((snap / 'secret.env').exists())
            self.assertTrue((snap.parents[1] / '.snapshot-complete').is_file())

    def test_apply_then_rollback_restores_user_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            gemini = base / 'home/.gemini/skills'
            src, head = make_clone(base, retired={str(gemini): ['grilling']})
            other = base / 'home/.claude/skills'
            (gemini / 'grilling').mkdir(parents=True)
            (gemini / 'grilling/old.md').write_text('matt copy')
            (other / 'adr').mkdir(parents=True)
            (other / 'index.json').write_text('stale index')
            self.assertEqual(self.run_install(
                '--apply', '--source', str(src), '--ref', head,
                '--target', str(gemini), '--target', str(other)).returncode, 0)
            self.assertTrue((gemini / 'demo').is_symlink())
            self.assertFalse((gemini / 'grilling').exists())
            self.assertFalse((other / 'adr').exists())
            backups = list(base.glob('home/.install-base-backup-*'))
            self.assertEqual(len(backups), 1)
            result = self.run_install('--rollback', str(backups[0]))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((gemini / 'grilling/old.md').is_file())
            self.assertTrue((other / 'adr').is_dir())
            self.assertEqual((other / 'index.json').read_text(), 'stale index')
            self.assertFalse((gemini / 'demo').exists())
            self.assertEqual(self.run_install('--rollback', str(backups[0])).returncode, 0)

    def test_failed_apply_rolls_back_earlier_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = make_clone(base)
            ok = base / 'ok/skills'
            (ok / 'adr').mkdir(parents=True)
            blocker = base / 'blocker'
            blocker.write_text('a file, not a directory')
            bad = blocker / 'skills'
            result = self.run_install('--apply', '--source', str(src), '--ref', head,
                                      '--target', str(ok), '--target', str(bad))
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue((ok / 'adr').is_dir())
            self.assertFalse((ok / 'demo').exists())
            self.assertFalse((ok / 'index.json').exists())

    def test_intra_op_failure_restores_evicted_file(self):
        """A copy-file that evicts the old index then fails mid-op must still
        restore the evicted original -- 'done' is not the rollback criterion."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = make_clone(base)
            target = base / 'home/skills'
            target.mkdir(parents=True)
            (target / 'index.json').write_text('OLD INDEX')
            result = self.run_install('--apply', '--source', str(src), '--ref', head,
                                      '--target', str(target), fail='copy-file:index.json')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('previous state restored', result.stderr)
            self.assertEqual((target / 'index.json').read_text(), 'OLD INDEX')
            self.assertFalse((target / 'INDEX.md').exists())

    def test_rollback_refuses_to_drop_post_install_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = make_clone(base)
            target = base / 'home/skills'
            (target / 'adr').mkdir(parents=True)
            result = self.run_install('--apply', '--source', str(src), '--ref', head,
                                      '--target', str(target))
            self.assertEqual(result.returncode, 0, result.stderr)
            backup = self.backups(base)[0]
            (target / 'adr').write_text('user re-created this AFTER install')
            result = self.run_install('--rollback', str(backup))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('refusing', result.stderr)
            self.assertEqual((target / 'adr').read_text(),
                             'user re-created this AFTER install')
            manifest = json.loads((backup / 'manifest.json').read_text())
            self.assertFalse(manifest.get('rolled_back'))

    def test_rollback_restores_broken_symlink_from_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = make_clone(base)
            target = base / 'home/skills'
            target.mkdir(parents=True)
            (target / 'adr').symlink_to(base / 'no-such-place')
            self.assertEqual(self.run_install(
                '--apply', '--source', str(src), '--ref', head,
                '--target', str(target)).returncode, 0)
            backup = self.backups(base)[0]
            self.assertFalse((target / 'adr').exists())
            result = self.run_install('--rollback', str(backup))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / 'adr').is_symlink())  # dangling but restored
            self.assertEqual(os.readlink(target / 'adr'), str(base / 'no-such-place'))

    def test_rollback_failure_is_honest_and_retryable(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = make_clone(base)
            target = base / 'home/skills'
            (target / 'adr').mkdir(parents=True)
            self.assertEqual(self.run_install(
                '--apply', '--source', str(src), '--ref', head,
                '--target', str(target)).returncode, 0)
            backup = self.backups(base)[0]
            target.chmod(0o555)  # restore moves cannot write into it
            try:
                result = self.run_install('--rollback', str(backup))
            finally:
                target.chmod(0o755)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('rollback incomplete', result.stderr)
            manifest = json.loads((backup / 'manifest.json').read_text())
            self.assertNotEqual(manifest.get('rolled_back'), True)
            result = self.run_install('--rollback', str(backup))  # retry works
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / 'adr').is_dir())

    def test_retire_and_explicit_install_share_one_path(self):
        """A skill that is both retired and explicitly installed must be
        evicted once, not planned as two moves on the same path."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            target = base / 'home/skills'
            (target / 'grilling').mkdir(parents=True)
            (target / 'grilling/old.md').write_text('previous install')
            src, head = make_clone(
                base, skills=[('grilling', 'skills/grilling')],
                retired={'*': ['grilling']})
            result = self.run_install('--apply', '--source', str(src), '--ref', head,
                                      '--target', str(target), '--skill', 'grilling')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / 'grilling').is_symlink())
            backup = self.backups(base)[0]
            moved = [p.name for p in (backup / 'files').rglob('grilling')]
            self.assertEqual(len(moved), 1)
            self.assertEqual((backup / 'files' / '0' / 'grilling/old.md').read_text(),
                             'previous install')

    def test_ambiguous_bare_name_errors_and_path_resolves(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            # tdd exists in two vendor trees (the real matt/pstack case):
            # a bare name cannot choose between them
            src, head = make_clone(base, skills=[('tdd', 'vendor/matt/tdd'),
                                                 ('tdd', 'vendor/pstack/tdd')])
            target = base / 'home/skills'
            result = self.run_install('--apply', '--source', str(src), '--ref', head,
                                      '--target', str(target), '--skill', 'tdd')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Ambiguous', result.stderr)
            self.assertIn('vendor/matt/tdd', result.stderr)
            result = self.run_install('--apply', '--source', str(src), '--ref', head,
                                      '--target', str(target),
                                      '--skill', 'vendor/pstack/tdd')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / 'tdd').is_symlink())

    def test_curated_copy_wins_over_vendored_same_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            # wait-what exists both curated (skills/) and vendored: the bare
            # name resolves to the curated one, as the base suite intends
            src, head = make_clone(base, skills=[('wait-what', 'skills/wait-what'),
                                                 ('wait-what', 'vendor/matt/wait-what')])
            target = base / 'home/skills'
            result = self.run_install('--apply', '--source', str(src), '--ref', head,
                                      '--target', str(target), '--skill', 'wait-what')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('skills/wait-what',
                          os.readlink(target / 'wait-what'))

    def test_ref_must_resolve_to_a_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = make_clone(base)
            target = base / 'skills'
            result = self.run_install('--apply', '--source', str(src), '--ref', '0' * 40,
                                      '--target', str(target))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('ref', result.stderr + result.stdout)
            self.assertFalse(target.exists())


class ProjectInstallTests(unittest.TestCase):
    def run_install(self, *args, cwd=None, fail=None):
        env = dict(os.environ)
        if fail:
            env['INSTALL_BASE_FAIL'] = fail
        return subprocess.run([sys.executable, str(INSTALL), *args],
                              capture_output=True, text=True, cwd=cwd, env=env)

    def make_project(self, base):
        proj = base / 'proj'
        proj.mkdir()
        return proj

    def test_project_single_entity_relative_links_and_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = make_clone(base)
            proj = self.make_project(base)
            stale = proj / '.agents/skills/adr'
            stale.mkdir(parents=True)
            (stale / 'keep.md').write_text('project skill, not retired')
            result = self.run_install('--apply', '--project', '--source', str(src),
                                      '--ref', head, cwd=proj)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((stale / 'keep.md').is_file())
            agents = proj / '.agents/skills'
            claude = proj / '.claude/skills'
            copied = agents / 'ask-me'
            self.assertTrue(copied.is_dir() and not copied.is_symlink())
            self.assertTrue((claude / 'demo').is_symlink())
            self.assertEqual(os.readlink(claude / 'demo'), '../../.agents/skills/demo')
            self.assertEqual(os.readlink(claude / 'index.json'),
                             '../../.agents/skills/index.json')
            meta = json.loads((copied / 'source.json').read_text())
            self.assertEqual(meta['commit'], head)
            self.assertEqual(meta['source_path'], 'skills/ask-me')
            self.assertEqual(meta['snapshot_root'], f'.install-base-snapshots/{head}')
            snap = proj / meta['snapshot_root']
            self.assertEqual((snap / '.snapshot-complete').read_text().strip(), head)
            lock = json.loads((proj / '.skills-lock.json').read_text())
            self.assertEqual(lock['skills']['demo']['source_path'], 'skills/demo')
            self.assertEqual(lock['skills']['demo']['source_commit'], head)
            self.assertEqual(lock['skills']['demo']['required_by'], ['explicit'])

    def test_project_target_escape_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = make_clone(base)
            proj = self.make_project(base)
            outside = base / 'outside'
            result = self.run_install('--apply', '--project', '--source', str(src),
                                      '--ref', head, '--target', str(outside), cwd=proj)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('escapes', result.stderr)
            self.assertFalse(outside.exists())

    def test_project_symlinked_scan_root_escape_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = make_clone(base)
            proj = self.make_project(base)
            outside = base / 'outside'
            outside.mkdir()
            (proj / '.claude').symlink_to(outside)  # scan root escapes via symlink
            result = self.run_install('--apply', '--project', '--source', str(src),
                                      '--ref', head, cwd=proj)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('escapes', result.stderr)
            self.assertEqual(tree_state(outside), {})

    def test_same_name_different_entity_conflicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = make_clone(base, skills=[('tdd', 'skills/tdd'),
                                                 ('tdd', 'vendor/x/tdd')])
            proj = self.make_project(base)
            result = self.run_install('--apply', '--project', '--source', str(src),
                                      '--ref', head, '--skill', 'skills/tdd', cwd=proj)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = self.run_install('--apply', '--project', '--source', str(src),
                                      '--ref', head, '--skill', 'vendor/x/tdd', cwd=proj)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Same name, different entity', result.stderr)


class SuiteTests(unittest.TestCase):
    def run_install(self, *args, cwd=None, fail=None):
        env = dict(os.environ)
        if fail:
            env['INSTALL_BASE_FAIL'] = fail
        return subprocess.run([sys.executable, str(INSTALL), *args],
                              capture_output=True, text=True, cwd=cwd, env=env)

    def fixture(self, base):
        skills = [('x', 'skills/x'), ('y', 'skills/y'), ('z', 'skills/z')]
        suites = {
            'one': suite([('x', 'skills/x', []), ('y', 'skills/y', [])]),
            'two': suite([('y', 'skills/y', []), ('z', 'skills/z', [])]),
        }
        upstreams = {'sources': [{'repo': 'example/upstream', 'paths': [
            {'source': 'x', 'destination': 'skills/x'}]}]}
        return make_clone(base, skills=skills, suites=suites, upstreams=upstreams)

    def test_suite_install_merges_required_by(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = self.fixture(base)
            proj = base / 'proj'
            proj.mkdir()
            for s in ('one', 'two'):
                result = self.run_install('--apply', '--project', '--source', str(src),
                                          '--ref', head, '--suite', s, cwd=proj)
                self.assertEqual(result.returncode, 0, result.stderr)
            lock = json.loads((proj / '.skills-lock.json').read_text())
            self.assertEqual(lock['skills']['y']['required_by'], ['one', 'two'])
            self.assertEqual(lock['skills']['x']['source_repo'], 'example/upstream')
            self.assertTrue((proj / '.agents/skills/y').is_dir())
            self.assertTrue((proj / '.claude/skills/z').is_symlink())

    def test_shared_skill_survives_suite_uninstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = self.fixture(base)
            proj = base / 'proj'
            proj.mkdir()
            for s in ('one', 'two'):
                self.assertEqual(self.run_install(
                    '--apply', '--project', '--source', str(src),
                    '--ref', head, '--suite', s, cwd=proj).returncode, 0)
            result = self.run_install('--apply', '--project', '--uninstall', 'one',
                                      cwd=proj)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((proj / '.agents/skills/x').exists())
            self.assertFalse((proj / '.claude/skills/x').exists())
            self.assertTrue((proj / '.agents/skills/y').is_dir())   # shared, kept
            self.assertTrue((proj / '.claude/skills/y').is_symlink())
            self.assertTrue((proj / '.agents/skills/z').is_dir())
            lock = json.loads((proj / '.skills-lock.json').read_text())
            self.assertNotIn('x', lock['skills'])
            self.assertEqual(lock['skills']['y']['required_by'], ['two'])
            result = self.run_install('--apply', '--project', '--uninstall', 'one',
                                      cwd=proj)
            self.assertNotEqual(result.returncode, 0)  # nothing owned -> error

    def test_suite_includes_expand_into_final_suite(self):
        """A suite may `includes` a sub-suite; members merge in deduplicated
        and the lock's required_by records the final suite name only."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            skills = [('x', 'skills/x'), ('y', 'skills/y'), ('z', 'skills/z')]
            suites = {
                'sub': suite([('x', 'skills/x', []), ('y', 'skills/y', [])]),
                'one': {**suite([('z', 'skills/z', [])]), 'includes': ['sub']},
            }
            src, head = make_clone(base, skills=skills, suites=suites)
            proj = base / 'proj'
            proj.mkdir()
            result = self.run_install('--apply', '--project', '--source', str(src),
                                      '--ref', head, '--suite', 'one', cwd=proj)
            self.assertEqual(result.returncode, 0, result.stderr)
            lock = json.loads((proj / '.skills-lock.json').read_text())
            self.assertEqual(set(lock['skills']), {'x', 'y', 'z'})
            for name in ('x', 'y', 'z'):
                self.assertEqual(lock['skills'][name]['required_by'], ['one'])

    def test_includes_shared_member_lands_once_and_survives_uninstall(self):
        """design+matt-dev pattern: two suites including the same sub-suite
        install each shared member once; uninstalling either keeps them."""
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            skills = [('x', 'skills/x'), ('y', 'skills/y'), ('z', 'skills/z')]
            suites = {
                'sub': suite([('x', 'skills/x', [])]),
                'one': {**suite([('y', 'skills/y', [])]), 'includes': ['sub']},
                'two': {**suite([('z', 'skills/z', [])]), 'includes': ['sub']},
            }
            src, head = make_clone(base, skills=skills, suites=suites)
            proj = base / 'proj'
            proj.mkdir()
            for s in ('one', 'two'):
                self.assertEqual(self.run_install(
                    '--apply', '--project', '--source', str(src),
                    '--ref', head, '--suite', s, cwd=proj).returncode, 0)
            lock = json.loads((proj / '.skills-lock.json').read_text())
            self.assertEqual(lock['skills']['x']['required_by'], ['one', 'two'])
            # exactly one payload copy on disk
            self.assertEqual(len(list(proj.glob('.agents/skills/x/SKILL.md'))), 1)
            result = self.run_install('--apply', '--project', '--uninstall',
                                      'one', cwd=proj)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((proj / '.agents/skills/y').exists())
            self.assertTrue((proj / '.agents/skills/x').is_dir())  # shared, kept
            lock = json.loads((proj / '.skills-lock.json').read_text())
            self.assertEqual(lock['skills']['x']['required_by'], ['two'])

    def test_include_cycle_and_missing_include_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            suites = {
                'a': {**suite([]), 'includes': ['b']},
                'b': {**suite([]), 'includes': ['a']},
                'c': {**suite([]), 'includes': ['nope']},
            }
            src, head = make_clone(base, suites=suites)
            proj = base / 'proj'
            proj.mkdir()
            result = self.run_install('--apply', '--project', '--source', str(src),
                                      '--ref', head, '--suite', 'a', cwd=proj)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('cycle', result.stderr)
            result = self.run_install('--apply', '--project', '--source', str(src),
                                      '--ref', head, '--suite', 'c', cwd=proj)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('no suite', result.stderr)

    def test_same_member_name_at_two_paths_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            skills = [('x', 'skills/x'), ('x', 'vendor/v/x')]
            suites = {
                'sub': suite([('x', 'vendor/v/x', [])]),
                'one': {**suite([('x', 'skills/x', [])]), 'includes': ['sub']},
            }
            src, head = make_clone(base, skills=skills, suites=suites)
            proj = base / 'proj'
            proj.mkdir()
            result = self.run_install('--apply', '--project', '--source', str(src),
                                      '--ref', head, '--suite', 'one', cwd=proj)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('both', result.stderr)

    def test_update_replaces_clean_and_protects_local_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head1 = self.fixture(base)
            proj = base / 'proj'
            proj.mkdir()
            self.assertEqual(self.run_install(
                '--apply', '--project', '--source', str(src),
                '--ref', head1, '--suite', 'one', cwd=proj).returncode, 0)
            # new upstream commit changes x and drops z-less y content
            (src / 'skills/x/SKILL.md').write_text('---\nname: x\n---\nNEW body\n')
            head2 = commit_all(src, 'update x')
            # local edit to y must be protected
            (proj / '.agents/skills/y/SKILL.md').write_text('local edit')
            result = self.run_install('--apply', '--project', '--update',
                                      '--source', str(src), '--ref', head2,
                                      '--suite', 'one', cwd=proj)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('locally modified', result.stderr)
            self.assertEqual((proj / '.agents/skills/y/SKILL.md').read_text(),
                             'local edit')
            self.assertIn('body', (proj / '.agents/skills/x/SKILL.md').read_text())
            self.assertNotIn('NEW', (proj / '.agents/skills/x/SKILL.md').read_text())
            result = self.run_install('--apply', '--project', '--update', '--force',
                                      '--source', str(src), '--ref', head2,
                                      '--suite', 'one', cwd=proj)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((proj / '.agents/skills/x/SKILL.md').read_text(),
                             '---\nname: x\n---\nNEW body\n')
            backup = sorted(proj.glob('.install-base-backup-*'))[-1]
            rescued = list(backup.rglob('y/SKILL.md'))
            self.assertEqual(rescued[0].read_text(), 'local edit')  # backed up
            lock = json.loads((proj / '.skills-lock.json').read_text())
            self.assertEqual(lock['skills']['x']['source_commit'], head2)

    def test_update_removes_members_dropped_from_suite(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head1 = self.fixture(base)
            proj = base / 'proj'
            proj.mkdir()
            self.assertEqual(self.run_install(
                '--apply', '--project', '--source', str(src),
                '--ref', head1, '--suite', 'one', cwd=proj).returncode, 0)
            # suite v2 drops y
            (src / 'suites/one.json').write_text(json.dumps(
                suite([('x', 'skills/x', [])])))
            head2 = commit_all(src, 'drop y')
            result = self.run_install('--apply', '--project', '--update',
                                      '--source', str(src), '--ref', head2,
                                      '--suite', 'one', cwd=proj)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((proj / '.agents/skills/y').exists())
            lock = json.loads((proj / '.skills-lock.json').read_text())
            self.assertNotIn('y', lock['skills'])


if __name__ == '__main__':
    unittest.main()
