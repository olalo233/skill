"""Base-suite checks: invocation config, passive descriptions, index freshness."""
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ['ask-me', 'wait-what', 'eli5']
AUTO = ['html', 'show-me']
STRONG = re.compile(r'\b(must|always|proactive|proactively|automatically)\b', re.I)


def frontmatter(name):
    text = (ROOT / 'skills' / name / 'SKILL.md').read_text()
    assert text.startswith('---\n'), name
    return text.split('---', 2)[1]


class ManualInvocationTests(unittest.TestCase):
    def test_claude_cursor_flag(self):
        for name in MANUAL:
            with self.subTest(skill=name):
                self.assertIn('disable-model-invocation: true', frontmatter(name))

    def test_devin_trigger_user_only(self):
        for name in MANUAL:
            with self.subTest(skill=name):
                fm = frontmatter(name)
                m = re.search(r'^triggers:\s*\n((?:\s+-\s+\w+\s*\n)+)', fm, re.M)
                self.assertIsNotNone(m, f'{name}: no triggers list')
                values = re.findall(r'-\s*(\w+)', m.group(1))
                self.assertEqual(values, ['user'])

    def test_codex_policy(self):
        for name in MANUAL:
            with self.subTest(skill=name):
                path = ROOT / 'skills' / name / 'agents/openai.yaml'
                self.assertTrue(path.is_file(), f'{name}: missing agents/openai.yaml')
                self.assertIn('allow_implicit_invocation: false', path.read_text())


class AutoInvocationTests(unittest.TestCase):
    def test_passive_descriptions(self):
        for name in AUTO:
            with self.subTest(skill=name):
                m = re.search(r'^description:\s*(.+)$', frontmatter(name), re.M)
                self.assertIsNotNone(m)
                self.assertIsNone(STRONG.search(m.group(1)), m.group(1))
                self.assertTrue(m.group(1).startswith('Use when'), m.group(1))

    def test_model_invocation_not_disabled(self):
        for name in AUTO:
            with self.subTest(skill=name):
                fm = frontmatter(name)
                self.assertNotIn('disable-model-invocation: true', fm)
                if re.search(r'^triggers:', fm, re.M):
                    self.fail(f'{name}: explicit triggers should keep the default [user, model]')
                policy = ROOT / 'skills' / name / 'agents/openai.yaml'
                if policy.is_file():
                    self.assertNotIn('allow_implicit_invocation: false', policy.read_text())


class IndexTests(unittest.TestCase):
    def test_index_files_current(self):
        result = subprocess.run(['python3', str(ROOT / 'scripts/build_index.py'), '--check'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_index_covers_all_skill_files(self):
        index = {e['path'] for e in json.loads((ROOT / 'index.json').read_text())['skills']}
        on_disk = {p.relative_to(ROOT).as_posix()
                   for d in ('skills', 'vendor')
                   for p in (ROOT / d).glob('**/SKILL.md')} - {''}
        self.assertEqual(index, on_disk)

    def test_base_suite_membership(self):
        src = json.loads((ROOT / '.sync/index-source.json').read_text())
        self.assertEqual(set(src['suites']['base']['skills']), set(MANUAL + AUTO))


if __name__ == '__main__':
    unittest.main()
