import importlib.util
import json
import os
from unittest.mock import patch
import subprocess
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('sync', Path(__file__).resolve().parents[1] / 'scripts/sync_upstreams.py')
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class MergeTests(unittest.TestCase):
    def test_disjoint_edits_preserve_customization(self):
        base = b'title\nkeep\nblank\nbody\n'
        ours = b'local title\nkeep\nblank\nbody\n'
        theirs = b'title\nkeep\nblank\nnew body\n'
        merged, conflict = sync.merge_file(ours, base, theirs)
        self.assertFalse(conflict)
        self.assertEqual(merged, b'local title\nkeep\nblank\nnew body\n')

    def test_overlap_requires_review(self):
        self.assertEqual(sync.merge_file(b'local\n', b'old\n', b'upstream\n'), (None, True))

    def test_new_deleted_and_locally_deleted_files(self):
        self.assertEqual(sync.merge_file(None, None, b'new'), (b'new', False))
        self.assertEqual(sync.merge_file(b'old', b'old', None), (None, False))
        self.assertEqual(sync.merge_file(None, b'old', b'old'), (None, False))
        self.assertEqual(sync.merge_file(b'custom', b'old', None), (None, True))
        self.assertEqual(sync.merge_file(None, b'old', b'changed'), (None, True))

    def test_conflict_planning_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); path = root / 'skills/demo/SKILL.md'
            path.parent.mkdir(parents=True); path.write_bytes(b'custom')
            _, conflicts = sync.plan_mapping(root, {'SKILL.md': (b'old', '100644')}, {'SKILL.md': (b'new', '100644')}, 'skills/demo')
            self.assertEqual(conflicts, ['skills/demo/SKILL.md'])
            self.assertEqual(path.read_bytes(), b'custom')

    def test_escape_and_symlink_refused(self):
        for path in ('../escape', '/absolute', '.git/config'):
            with self.assertRaises(ValueError): sync.safe_path(path)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'skills').mkdir(); (root / 'skills/demo').symlink_to(root / 'other')
            with self.assertRaises(ValueError):
                sync.plan_mapping(root, {}, {'SKILL.md': (b'new', '100644')}, 'skills/demo')

    def test_full_transaction_conflict_then_clean_sync(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); remote = root / 'remote'; checkout = root / 'checkout'
            subprocess.run(['git', 'init', '-q', '-b', 'main', str(remote)], check=True)
            (remote / 'skill').mkdir()
            def commit(message):
                subprocess.run(['git','-C',str(remote),'add','.'],check=True)
                subprocess.run(['git','-C',str(remote),'-c','user.name=Test','-c','user.email=test@example.com','commit','-qm',message],check=True)
                return sync.git(remote,'rev-parse','HEAD').decode().strip()
            (remote / 'skill/a.md').write_text('old a')
            (remote / 'skill/b.md').write_text('old b')
            base = commit('base')
            (remote / 'skill/a.md').write_text('new a')
            (remote / 'skill/b.md').write_text('new b')
            head = commit('update')
            (checkout / 'skills/demo').mkdir(parents=True)
            (checkout / '.sync').mkdir()
            a=checkout/'skills/demo/a.md'; b=checkout/'skills/demo/b.md'
            a.write_text('local a'); b.write_text('old b')
            (checkout/'skills/demo/local.md').write_text('keep local asset')
            manifest={'sources':[{'repo':'fixture/upstream','ref':'main','revision':base,'paths':[{'source':'skill','destination':'skills/demo'}]}]}
            config=checkout/'.sync/upstreams.json'; config.write_text(json.dumps(manifest))
            env={'GIT_CONFIG_COUNT':'1','GIT_CONFIG_KEY_0':'url.'+remote.as_uri()+'.insteadOf','GIT_CONFIG_VALUE_0':'https://github.com/fixture/upstream.git'}
            with patch.dict(os.environ,env):
                self.assertEqual(sync.sync(checkout,root/'conflict.json',root/'cache'),2)
                self.assertEqual(b.read_text(),'old b')
                self.assertEqual(json.loads(config.read_text())['sources'][0]['revision'],base)
                a.write_text('old a')
                self.assertEqual(sync.sync(checkout,root/'clean.json',root/'cache'),0)
            self.assertEqual(a.read_text(),'new a'); self.assertEqual(b.read_text(),'new b')
            self.assertEqual((checkout/'skills/demo/local.md').read_text(),'keep local asset')
            self.assertEqual(json.loads(config.read_text())['sources'][0]['revision'],head)

    def test_upstream_symlink_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / 'skill').mkdir(); (root / 'skill/escape').symlink_to('/etc/passwd')
            subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=Test', '-c', 'user.email=test@example.com', 'commit', '-qm', 'fixture'], check=True)
            with self.assertRaises(ValueError): sync.snapshot(root, 'HEAD', 'skill')


if __name__ == '__main__': unittest.main()
