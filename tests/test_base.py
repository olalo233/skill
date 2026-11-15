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



class DependencyClosureTests(unittest.TestCase):
    """A single-skill --skill install must pull the same hard dependencies a
    suite install declares (the review's grill-with-docs repro)."""

    def production_resolver(self):
        import importlib.machinery
        import importlib.util
        loader = importlib.machinery.SourceFileLoader(
            'install_base', str(ROOT / 'scripts/install-base'))
        spec = importlib.util.spec_from_loader('install_base', loader)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def closure_names(self, selector):
        mod = self.production_resolver()
        entries = json.loads((ROOT / 'index.json').read_text())['skills']
        roots = mod.resolve_selectors([selector], entries)
        return {e['name'] for e in mod.closure(roots, entries)}

    def test_grill_with_docs_pulls_matt_deps(self):
        self.assertEqual(
            self.closure_names('grill-with-docs'),
            {'grill-with-docs', 'domain-modeling', 'grilling'})

    def test_implement_pulls_tdd_closure(self):
        names = self.closure_names('vendor/matt/skills/engineering/implement')
        self.assertEqual(names, {'implement', 'code-review', 'tdd',
                                 'codebase-design',
                                 'setup-matt-pocock-skills'})

    def test_to_spec_and_to_tickets_pull_setup(self):
        for sel in ('to-spec', 'to-tickets', 'code-review'):
            self.assertIn('setup-matt-pocock-skills', self.closure_names(sel))

    def test_curated_suite_deps_match_index(self):
        """Every suite-declared depends survives into index.json, so the
        installer's single-skill path uses the same facts."""
        idx = {e['path'].rsplit('/', 1)[0]: e['depends']
               for e in json.loads((ROOT / 'index.json').read_text())['skills']}
        for sf in sorted((ROOT / 'suites').glob('*.json')):
            for m in json.loads(sf.read_text()).get('members', []):
                if m.get('depends'):
                    self.assertEqual(sorted(idx[m['path']]),
                                     sorted(m['depends']), m['path'])



class ImpeccableOfflineTests(unittest.TestCase):
    """The derived impeccable skill ships no launcher, no detector, and no
    live-mode machinery: every procedure in its text must be performable
    offline. Regression scan for the review's issue 6."""

    SKILL = ROOT / 'skills' / 'impeccable'

    FORBIDDEN_COMMANDS = [
        'context', 'detect', 'comp-spec', 'comp-diff', 'build-phase',
        'serve-question', 'generate-image', 'embed-prompt', 'font-match',
        'surface-brief', 'concept-seed', 'signals', 'audit-storage',
        'critique-storage', 'component-review', 'doctor', 'hooks',
    ]

    def corpus(self):
        files = [self.SKILL / 'SKILL.md']
        files += sorted((self.SKILL / 'reference').rglob('*.md'))
        files += sorted((self.SKILL / 'agents').glob('*.toml'))
        files += sorted((self.SKILL / 'agents').glob('*.yaml'))
        return files

    def test_no_removed_cli_invocations(self):
        bad = []
        pat = re.compile(r'impeccable (' + '|'.join(
            self.FORBIDDEN_COMMANDS + [r'live[a-z-]*']) + r')\b')
        for f in self.corpus():
            for i, line in enumerate(f.read_text().splitlines(), 1):
                stripped = line.replace('$impeccable', '')
                m = pat.search(stripped)
                if m:
                    bad.append(f'{f.relative_to(self.SKILL)}:{i}: {m.group(0)}')
        self.assertEqual(bad, [])

    def test_no_script_paths_or_live_machinery(self):
        bad = []
        pats = [r'scripts/impeccable', r'\.agents/skills/impeccable/scripts',
                r'live-server', r'live-poll', r'live-inject',
                r'live-commit-manual-edits', r'detect\.js', r'design hook']
        for f in self.corpus():
            body = f.read_text()
            for pat in pats:
                if re.search(pat, body):
                    bad.append(f'{f.relative_to(self.SKILL)}: {pat}')
        self.assertEqual(bad, [])

    def test_no_manual_edit_applier(self):
        """The manual-edit applier existed only for the live flow."""
        self.assertFalse(
            (self.SKILL / 'agents/impeccable_manual_edit_applier.toml').exists())
        self.assertFalse(
            (self.SKILL / 'reference/degraded/manual-edit-applier.md').exists())

    def test_derived_copy_carries_apache_notices(self):
        """Apache-2.0 derivation requires LICENSE + NOTICE in the payload."""
        for name in ('LICENSE', 'NOTICE.md', 'MODIFICATIONS.md'):
            self.assertTrue((self.SKILL / name).is_file(), name)
        notice = (self.SKILL / 'NOTICE.md').read_text()
        self.assertIn('platform-design-skills', notice)
        self.assertIn('MIT', notice)

    def test_degraded_copies_match_agent_definitions(self):
        """degraded/*.md is generated from agents/*.toml; they must not drift."""
        marker = 'developer_instructions = ' + chr(39) * 3
        close = chr(39) * 3
        for toml in (self.SKILL / 'agents').glob('impeccable_*.toml'):
            role = toml.stem[len('impeccable_'):].replace('_', '-')
            degraded = self.SKILL / 'reference/degraded' / f'{role}.md'
            self.assertTrue(degraded.is_file(), f'{toml.name} has no degraded copy')
            instructions = toml.read_text().split(marker, 1)[1]
            instructions = instructions.rsplit(close, 1)[0]
            # the generator rewrites links for the degraded file's location:
            # agents/../reference/x.md reads as reference/degraded/../x.md
            instructions = instructions.replace('](../reference/', '](../')
            self.assertIn(instructions.strip(), degraded.read_text(),
                          f'{degraded.name} drifted from {toml.name}')


if __name__ == '__main__':
    unittest.main()
