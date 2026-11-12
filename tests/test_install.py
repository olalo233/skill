"""install-base checks: pinned source, dry-run purity, manifest rollback, project safety."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / 'scripts/install-base'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


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


def make_clone(base, extra_retired=None):
    """A minimal 'skill' clone: two skills plus the index the installer reads."""
    src = base / 'clone'
    (src / 'skills/ask-me').mkdir(parents=True)
    (src / 'skills/ask-me/SKILL.md').write_text(
        '---\nname: ask-me\ndescription: router\n---\nbody\n')
    (src / 'skills/demo').mkdir(parents=True)
    (src / 'skills/demo/SKILL.md').write_text(
        '---\nname: demo\ndescription: demo\n---\nbody\n')
    (src / '.sync').mkdir()
    retired = {'*': ['adr', 'work-archive']}
    retired.update(extra_retired or {})
    (src / '.sync/index-source.json').write_text(json.dumps({
        'suites': {'base': {'title': 'Base', 'skills': ['ask-me', 'demo']}},
        'depends': {}, 'retired': retired}))
    (src / 'index.json').write_text(json.dumps({'version': 1, 'skills': [
        {'name': 'ask-me', 'suite': 'base', 'summary': 'r',
         'path': 'skills/ask-me/SKILL.md', 'depends': []},
        {'name': 'demo', 'suite': 'base', 'summary': 'd',
         'path': 'skills/demo/SKILL.md', 'depends': []}]}))
    (src / 'INDEX.md').write_text('# index\n')
    subprocess.run(['git', 'init', '-q', str(src)], check=True)
    subprocess.run(['git', '-C', str(src), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(src), '-c', 'user.name=Test',
                    '-c', 'user.email=test@example.com', 'commit', '-qm', 'init'], check=True)
    return src, git(src, 'rev-parse', 'HEAD')


class InstallTests(unittest.TestCase):
    def run_install(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(INSTALL), *args],
                              capture_output=True, text=True, cwd=cwd)

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
            self.assertIn('retire', result.stdout)   # dry-run lists retire
            self.assertIn('index', result.stdout)    # ... and root index changes
            self.assertEqual(before, tree_state(base))  # nothing written anywhere

    def test_apply_then_rollback_restores_user_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            gemini = base / 'home/.gemini/skills'
            src, head = make_clone(base, {str(gemini): ['grilling']})
            other = base / 'home/.claude/skills'
            (gemini / 'grilling').mkdir(parents=True)
            (gemini / 'grilling/old.md').write_text('matt copy')
            (other / 'adr').mkdir(parents=True)
            (other / 'index.json').write_text('stale index')
            self.assertEqual(self.run_install(
                '--apply', '--source', str(src), '--ref', head,
                '--target', str(gemini), '--target', str(other)).returncode, 0)
            self.assertTrue((gemini / 'demo').is_symlink())
            self.assertFalse((gemini / 'grilling').exists())      # retired
            self.assertFalse((other / 'adr').exists())            # '*' retired
            backups = list(base.glob('home/.install-base-backup-*'))
            self.assertEqual(len(backups), 1)
            result = self.run_install('--rollback', str(backups[0]))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((gemini / 'grilling/old.md').is_file())
            self.assertTrue((other / 'adr').is_dir())
            self.assertEqual((other / 'index.json').read_text(), 'stale index')
            self.assertFalse((gemini / 'demo').exists())
            # second rollback is a no-op
            self.assertEqual(self.run_install('--rollback', str(backups[0])).returncode, 0)

    def test_failed_apply_rolls_back_earlier_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = make_clone(base)
            ok = base / 'ok/skills'
            (ok / 'adr').mkdir(parents=True)
            blocker = base / 'blocker'
            blocker.write_text('a file, not a directory')
            bad = blocker / 'skills'   # mkdir must fail: parent is a file
            result = self.run_install('--apply', '--source', str(src), '--ref', head,
                                      '--target', str(ok), '--target', str(bad))
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue((ok / 'adr').is_dir())          # retirement undone
            self.assertFalse((ok / 'demo').exists())        # install undone
            self.assertFalse((ok / 'index.json').exists())  # index write undone

    def test_project_install_never_retires_and_writes_source_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = make_clone(base)
            proj = base / 'proj'
            stale = proj / '.agents/skills/adr'
            stale.mkdir(parents=True)
            (stale / 'keep.md').write_text('project skill, not retired')
            result = self.run_install('--apply', '--project', '--source', str(src),
                                      '--ref', head, cwd=proj)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((stale / 'keep.md').is_file())        # untouched
            copied = proj / '.agents/skills/ask-me'
            self.assertTrue(copied.is_dir() and not copied.is_symlink())
            meta = json.loads((copied / 'source.json').read_text())
            self.assertEqual(meta, {'repo': str(src.resolve()), 'ref': head})
            self.assertTrue((copied / 'index.json').is_file())
            self.assertTrue((proj / '.agents/skills/index.json').is_file())
            self.assertTrue((proj / '.claude/skills/demo').is_dir())

    def test_ref_mismatch_and_dirty_clone_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            src, head = make_clone(base)
            target = base / 'skills'
            result = self.run_install('--apply', '--source', str(src), '--ref', '0' * 40,
                                      '--target', str(target))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('ref', result.stderr + result.stdout)
            self.assertFalse(target.exists())
            (src / 'dirty.txt').write_text('uncommitted')
            result = self.run_install('--apply', '--source', str(src), '--ref', head,
                                      '--target', str(target))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('uncommitted', result.stderr + result.stdout)
            self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
