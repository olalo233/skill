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

    def test_manifest_rejects_overlap_even_when_sources_are_unchanged(self):
        source = {'repo': 'fixture/first', 'ref': 'main', 'revision': 'a' * 40,
                  'paths': [{'source': 'skill', 'destination': 'skills/demo'}]}
        other = {'repo': 'fixture/other', 'ref': 'main', 'revision': 'b' * 40,
                 'paths': [{'source': 'skill', 'destination': 'skills/demo/nested'}]}
        with self.assertRaisesRegex(ValueError, 'Overlapping'):
            sync.validate_manifest({'sources': [source, other]})

    def test_fetch_failure_does_not_block_independent_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / '.sync').mkdir()
            sources = [{'repo': 'fixture/' + name, 'ref': 'main', 'revision': 'a' * 40,
                        'paths': [{'source': 'skill', 'destination': 'skills/' + name}]}
                       for name in ['broken', 'clean']]
            config = root / '.sync/upstreams.json'
            config.write_text(json.dumps({'sources': sources}))
            def fake_git(repo, *args):
                if args[0] == 'fetch' and 'broken' in str(repo):
                    raise subprocess.TimeoutExpired('git', 90)
                return ('b' * 40).encode() if args[0] == 'rev-parse' else b''
            def fake_snapshot(repo, revision, source):
                return {} if revision == 'a' * 40 else {'SKILL.md': (b'new skill', '100644')}
            with patch.object(sync, 'git', side_effect=fake_git), patch.object(sync, 'snapshot', side_effect=fake_snapshot):
                self.assertEqual(sync.sync(root, root / 'report.json', root / 'cache'), 2)
            report = json.loads((root / 'report.json').read_text())
            self.assertEqual([x['status'] for x in report['sources']], ['error', 'updated'])
            self.assertEqual((root / 'skills/clean/SKILL.md').read_bytes(), b'new skill')
            revisions = [s['revision'] for s in json.loads(config.read_text())['sources']]
            self.assertEqual(revisions, ['a' * 40, 'b' * 40])

    def test_license_change_blocks_entire_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / '.sync').mkdir(); (root / 'skills/demo').mkdir(parents=True)
            path = root / 'skills/demo/SKILL.md'; path.write_text('old')
            (root / 'licenses').mkdir(); (root / 'licenses/demo.txt').write_text('old')
            manifest = {'sources': [{'repo': 'fixture/demo', 'ref': 'main', 'revision': 'a' * 40,
                        'paths': [{'source': 'skill', 'destination': 'skills/demo'},
                                  {'source': 'LICENSE', 'destination': 'licenses/demo.txt'}]}]}
            config = root / '.sync/upstreams.json'; config.write_text(json.dumps(manifest))
            def fake_snapshot(repo, revision, source):
                return {'' if source == 'LICENSE' else 'SKILL.md':
                        (b'old' if revision == 'a' * 40 else b'new', '100644')}
            with patch.object(sync, 'git', return_value=('b' * 40).encode()), patch.object(sync, 'snapshot', side_effect=fake_snapshot):
                self.assertEqual(sync.sync(root, root / 'report.json', root / 'cache'), 2)
            self.assertEqual(path.read_text(), 'old')
            self.assertEqual(json.loads(config.read_text()), manifest)
            report = json.loads((root / 'report.json').read_text())
            self.assertEqual(report['sources'][0]['status'], 'blocked')
            self.assertIn('-old', report['sources'][0]['reviews'][0]['upstream_diff'])

    def test_merge_failure_does_not_block_independent_source(self):
        run = subprocess.run
        for failure in ('returncode', 'timeout'):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp); (root / '.sync').mkdir()
                path = root / 'skills/broken/SKILL.md'
                path.parent.mkdir(parents=True); path.write_bytes(b'local')
                clean = root / 'skills/clean/SKILL.md'
                clean.parent.mkdir(parents=True); clean.write_bytes(b'old')
                sources = [{'repo': 'fixture/' + name, 'ref': 'main', 'revision': 'a' * 40,
                            'paths': [{'source': 'skill', 'destination': 'skills/' + name}]}
                           for name in ['broken', 'clean']]
                config = root / '.sync/upstreams.json'
                config.write_text(json.dumps({'sources': sources}))
                def fake_run(args, **kwargs):
                    if args[:2] == ['git', 'merge-file']:
                        self.assertEqual(kwargs['timeout'], 90)
                        if failure == 'timeout':
                            raise subprocess.TimeoutExpired('git', 90)
                        return subprocess.CompletedProcess(args, 255, b'', b'')
                    return run(args, **kwargs)
                def fake_snapshot(repo, revision, source):
                    return {'SKILL.md': (b'old' if revision == 'a' * 40 else b'new', '100644')}
                with patch.object(sync, 'git', return_value=('b' * 40).encode()), \
                     patch.object(sync, 'snapshot', side_effect=fake_snapshot), \
                     patch.object(sync.subprocess, 'run', side_effect=fake_run):
                    self.assertEqual(sync.sync(root, root / 'report.json', root / 'cache'), 2)
                report = json.loads((root / 'report.json').read_text())
                self.assertEqual([s['status'] for s in report['sources']], ['error', 'updated'])
                self.assertEqual(report['sources'][0]['error'],
                                 'TimeoutExpired' if failure == 'timeout' else 'git merge-file failed')
                self.assertEqual(path.read_bytes(), b'local')
                self.assertEqual((root / 'skills/clean/SKILL.md').read_bytes(), b'new')
                self.assertEqual([s['revision'] for s in json.loads(config.read_text())['sources']],
                                 ['a' * 40, 'b' * 40])

    def test_summary_omits_diffs_and_escapes_cells(self):
        report = {'sources': [{'repo': 'fixture/demo', 'status': 'blocked', 'from': 'a' * 40,
                              'to': 'b' * 40, 'conflicts': ['skills/a|b.md', 'skills/c.md'],
                              'error': 'bad|file\r\ntry\ragain\nsoon',
                              'reviews': [{'upstream_diff': '```\nfull diff', 'local_diff': '```'}]},
                             {'repo': 'fixture/error', 'status': 'error', 'from': 'c' * 40}]}
        summary = sync.summary_markdown(report)
        self.assertIn('| fixture/demo | blocked | aaaaaaa | bbbbbbb | skills/a&#124;b.md<br>skills/c.md | bad&#124;file<br>try<br>again<br>soon |', summary)
        self.assertIn('| fixture/error | error | ccccccc |  |  |  |', summary)
        self.assertNotIn('```', summary)
        self.assertNotIn('full diff', summary)
        self.assertIn('upstream-sync-report artifact', summary)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'report.json'; path.write_text(json.dumps(report))
            result = subprocess.run(['python3', str(Path(sync.__file__)), '--summarize', str(path)],
                                    capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout, summary)

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
            a.write_bytes(b'local a\xff'); b.write_text('old b')
            (checkout/'skills/demo/local.md').write_text('keep local asset')
            (checkout/'skills/independent').mkdir()
            (checkout/'skills/independent/a.md').write_text('old a')
            (checkout/'skills/independent/b.md').write_text('old b')
            manifest={'sources':[{'repo':'fixture/upstream','ref':'main','revision':base,'paths':[{'source':'skill','destination':'skills/demo'}]},
                                 {'repo':'fixture/other','ref':'main','revision':base,'paths':[{'source':'skill','destination':'skills/independent'}]}]}
            config=checkout/'.sync/upstreams.json'; config.write_text(json.dumps(manifest))
            env={'GIT_CONFIG_COUNT':'2','GIT_CONFIG_KEY_0':'url.'+remote.as_uri()+'.insteadOf','GIT_CONFIG_VALUE_0':'https://github.com/fixture/upstream.git',
                 'GIT_CONFIG_KEY_1':'url.'+remote.as_uri()+'.insteadOf','GIT_CONFIG_VALUE_1':'https://github.com/fixture/other.git'}
            with patch.dict(os.environ,env):
                self.assertEqual(sync.sync(checkout,root/'conflict.json',root/'cache'),2)
                self.assertEqual(b.read_text(),'old b')
                self.assertEqual(json.loads(config.read_text())['sources'][0]['revision'],base)
                self.assertEqual(json.loads(config.read_text())['sources'][1]['revision'],head)
                self.assertEqual((checkout/'skills/independent/b.md').read_text(),'new b')
                report = json.loads((root/'conflict.json').read_text())
                self.assertEqual([s['status'] for s in report['sources']], ['blocked', 'updated'])
                self.assertIn('-old a', report['sources'][0]['reviews'][0]['upstream_diff'])
                self.assertIn('+local a\ufffd', report['sources'][0]['reviews'][0]['local_diff'])
                a.write_text('old a')
                self.assertEqual(sync.sync(checkout,root/'clean.json',root/'cache'),0)
                self.assertEqual(sync.sync(checkout,root/'noop.json',root/'cache'),0)
                self.assertEqual(json.loads((root/'noop.json').read_text())['updates'], [])
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
