"""Suite declaration checks: includes expansion, dependency closure parsed
from SKILL.md references, required membership, package layout, and the
trigger/description contract of the new first-party skills."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_suite(name, _stack=()):
    """Expand a suite file's `includes` like install-base's expand_suite."""
    assert name not in _stack, f'include cycle: {_stack + (name,)}'
    suite = json.loads((ROOT / 'suites' / f'{name}.json').read_text())
    members = {}
    order = []
    for inc in suite.get('includes', []):
        for m in load_suite(inc, _stack + (name,))[1]:
            assert members.get(m['name'], m)['path'] == m['path'], \
                f"{m['name']} at two paths"
            if m['name'] not in members:
                members[m['name']] = m
                order.append(m)
    for m in suite.get('members', []):
        assert members.get(m['name'], m)['path'] == m['path']
        if m['name'] not in members:
            members[m['name']] = m
            order.append(m)
    return suite, order


MATT_PLAN_SUITE, MATT_PLAN = load_suite('matt-plan')
MATT_DEV_SUITE, MATT_DEV = load_suite('matt-dev')
DESIGN_SUITE, DESIGN = load_suite('design')
UIKIT_SUITE, UIKIT = load_suite('ui-kit')
PSTACK = json.loads((ROOT / 'suites/pstack.json').read_text())

MATT_PLAN_MEMBERS = {'grill-with-docs', 'grilling', 'domain-modeling', 'to-spec',
                     'to-tickets', 'codebase-design', 'setup-matt-pocock-skills'}
MATT_DEV_MEMBERS = {'implement', 'tdd', 'code-review', 'diagnosing-bugs',
                    'matt-flow'} | MATT_PLAN_MEMBERS

# every skill directory that exists anywhere in the repository
SKILL_DIRS = {p.parent for p in ROOT.glob('skills/*/SKILL.md')} | \
    {p.parent for p in ROOT.glob('vendor/**/SKILL.md')}
SKILL_NAMES = {p.name for p in SKILL_DIRS}

INVOKE_QUOTED = re.compile(r'\bSkill tool\b[^\n]*')      # Skill tool lines
RUN_SLASH = re.compile(r'\brun `(/[a-z0-9-]+)`')         # 'run `/name`'
QUOTED = re.compile(r'"([a-z0-9-]+)"')


def referenced_skills(text):
    """Sibling skills a SKILL.md actually invokes or requires.

    Covers the two real forms used in this repo:
      Call the Skill tool (twice,) (with|for) "name"[, "name2"]
      tell the user to run `/name`
    Routing prose (matt-flow's `/x` mentions) does not count: those are
    recommendations, not invocations.
    """
    refs = set()
    for line in text.splitlines():
        if 'Skill tool' in line:
            refs.update(QUOTED.findall(line))
    refs.update(m.strip('/') for m in RUN_SLASH.findall(text))
    return refs & SKILL_NAMES


def frontmatter(path):
    text = (ROOT / path / 'SKILL.md').read_text()
    assert text.startswith('---\n'), path
    return text.split('---', 2)[1]


class SuiteMemberTests(unittest.TestCase):
    """Shared assertions for member lists: paths exist, names match, depends
    match references parsed out of each SKILL.md, closure is explicit."""

    def check_members(self, suite_name, members):
        by_name = {m['name']: m for m in members}
        for m in members:
            with self.subTest(suite=suite_name, member=m['name']):
                d = ROOT / m['path']
                self.assertTrue(d.is_dir(), m['path'])
                self.assertEqual(m['name'], Path(m['path']).name)
                self.assertTrue((d / 'SKILL.md').is_file(), m['path'])
                parsed = referenced_skills((d / 'SKILL.md').read_text())
                self.assertEqual(set(m.get('depends', [])), parsed,
                                 f"{m['name']}: declared depends differ from "
                                 'references parsed out of SKILL.md')
                for dep in m.get('depends', []):
                    self.assertIn(dep, by_name,
                                  f"{m['name']} depends on {dep}, not a member "
                                  f'of {suite_name} or its includes')
        return by_name


class MattPlanTests(SuiteMemberTests):
    def test_plan_members(self):
        self.assertEqual({m['name'] for m in MATT_PLAN}, MATT_PLAN_MEMBERS)
        self.assertEqual(MATT_PLAN_SUITE.get('kind'), 'skills')

    def test_plan_paths_and_depends(self):
        members = self.check_members('matt-plan', MATT_PLAN)
        for m in MATT_PLAN:
            self.assertTrue(m['path'].startswith('vendor/matt/'), m['path'])
        self.assertEqual(set(members['grill-with-docs']['depends']),
                         {'grilling', 'domain-modeling'})
        for name in ('to-spec', 'to-tickets'):
            self.assertIn('setup-matt-pocock-skills', members[name]['depends'])


class MattDevTests(SuiteMemberTests):
    def test_includes_matt_plan(self):
        self.assertIn('matt-plan', MATT_DEV_SUITE.get('includes', []))

    def test_required_members_present(self):
        self.assertEqual({m['name'] for m in MATT_DEV}, MATT_DEV_MEMBERS)

    def test_paths_and_depends(self):
        members = self.check_members('matt-dev', MATT_DEV)
        for name in ('to-spec', 'to-tickets', 'code-review'):
            self.assertIn('setup-matt-pocock-skills', members[name]['depends'])
        self.assertEqual(set(members['implement']['depends']),
                         {'tdd', 'code-review'})
        self.assertEqual(members['tdd']['depends'], ['codebase-design'])


class DesignSuiteTests(SuiteMemberTests):
    def test_includes_matt_plan_and_adds_three(self):
        self.assertIn('matt-plan', DESIGN_SUITE.get('includes', []))
        own = {m['name'] for m in DESIGN_SUITE['members']}
        self.assertEqual(own, {'ux-spec', 'system-design',
                               'api-and-interface-design'})
        self.assertEqual({m['name'] for m in DESIGN},
                         MATT_PLAN_MEMBERS | own)

    def test_paths_and_depends(self):
        self.check_members('design', DESIGN)
        own = {m['path'] for m in DESIGN_SUITE['members']}
        self.assertTrue(all(p.startswith('skills/') for p in own))

    def test_shared_with_matt_dev_is_one_entity(self):
        dev = {m['name']: m['path'] for m in MATT_DEV}
        for m in DESIGN:
            self.assertEqual(m['path'], dev.get(m['name'], m['path']),
                             f'{m["name"]}: design and matt-dev must pin the '
                             'same source path so installs dedup')


class UiKitSuiteTests(SuiteMemberTests):
    def test_members(self):
        self.assertEqual({m['name'] for m in UIKIT},
                         {'impeccable', 'prototype'})
        self.check_members('ui-kit', UIKIT)

    def test_no_impeccable_binary_or_live_browser(self):
        """The derived impeccable ships no detector CLI, no scripts/, and no
        reference docs for the removed live/hook commands."""
        base = ROOT / 'skills/impeccable'
        self.assertFalse((base / 'scripts').exists())
        for f in base.rglob('*'):
            self.assertFalse(f.is_file() and not f.is_symlink()
                             and f.stat().st_mode & 0o111, f)
        for gone in ('live.md', 'live-setup.md', 'generate.md', 'hooks.md',
                     'doctor.md'):
            self.assertFalse((base / 'reference' / gone).exists())
        skill = (base / 'SKILL.md').read_text()
        self.assertNotIn('reference/live.md', skill)
        self.assertNotIn('reference/hooks.md', skill)
        self.assertNotIn('reference/doctor.md', skill)

    def test_kimi_export_rule_in_critique(self):
        critique = (ROOT / 'skills/impeccable/reference/critique.md').read_text()
        self.assertIn('Kimi', critique)
        self.assertIn('item by item', critique)

    def test_dataviz_noted_pending(self):
        self.assertIn('dataviz', UIKIT_SUITE.get('note', ''))
        self.assertNotIn('dataviz', {m['name'] for m in UIKIT})


class NewSkillTriggerTests(unittest.TestCase):
    """Trigger contract: ux-spec, system-design and impeccable are manual;
    api-and-interface-design stays model-invokable."""

    MANUAL = ['ux-spec', 'system-design', 'impeccable']

    def test_manual_frontmatter(self):
        for name in self.MANUAL:
            with self.subTest(skill=name):
                fm = frontmatter(f'skills/{name}')
                self.assertIn('disable-model-invocation: true', fm)
                m = re.search(r'^triggers:\s*\n((?:\s+-\s+\w+\s*\n)+)', fm, re.M)
                self.assertIsNotNone(m, f'{name}: no triggers list')
                self.assertEqual(re.findall(r'-\s*(\w+)', m.group(1)), ['user'])

    def test_manual_codex_policy(self):
        for name in self.MANUAL:
            with self.subTest(skill=name):
                path = ROOT / 'skills' / name / 'agents/openai.yaml'
                self.assertTrue(path.is_file(), f'{name}: missing agents/openai.yaml')
                self.assertIn('allow_implicit_invocation: false',
                              path.read_text())

    def test_auto_invocation(self):
        fm = frontmatter('skills/api-and-interface-design')
        self.assertNotIn('disable-model-invocation: true', fm)


class DescriptionLengthTests(unittest.TestCase):
    """Codex's skill listing budget: every new/derived SKILL.md description
    stays within 300 characters."""

    def test_new_skill_descriptions_within_budget(self):
        for name in ('ux-spec', 'system-design', 'api-and-interface-design',
                     'impeccable'):
            with self.subTest(skill=name):
                fm = frontmatter(f'skills/{name}')
                m = re.search(r'^description: ["\']?(.+?)["\']?\s*$', fm, re.M)
                self.assertIsNotNone(m)
                self.assertLessEqual(len(m.group(1)), 300, m.group(1))


class BoundaryContractTests(unittest.TestCase):
    def test_ux_spec_boundaries(self):
        text = (ROOT / 'skills/ux-spec/SKILL.md').read_text()
        self.assertIn('docs/ux/', text)
        for word in ('grilling', 'domain-modeling', 'Kimi'):
            self.assertIn(word, text)
        self.assertIn('BMAD', text)          # MIT template credit
        self.assertIn('MIT', text)

    def test_system_design_boundaries(self):
        text = (ROOT / 'skills/system-design/SKILL.md').read_text()
        for word in ('grilling', 'domain-modeling', 'codebase-design',
                     'api-and-interface-design', 'C4', 'Mermaid',
                     'proyecto26', 'MIT'):
            self.assertIn(word, text)
        self.assertFalse(list((ROOT / 'skills/system-design').glob('*/*/*')),
                         'references must stay a single layer')

    def test_api_design_boundaries(self):
        text = (ROOT / 'skills/api-and-interface-design/SKILL.md').read_text()
        self.assertIn('codebase-design', text)
        self.assertNotIn('deprecation-and-migration', text)
        self.assertFalse((ROOT / 'skills/api-and-interface-design/references').exists())


class PstackSuiteTests(unittest.TestCase):
    def test_package_member_is_the_whole_vendored_tree(self):
        self.assertEqual(PSTACK['kind'], 'package')
        (member,) = PSTACK['members']
        self.assertEqual(member['path'], 'vendor/pstack')
        self.assertTrue((ROOT / 'vendor/pstack/plugin.json').is_file())
        self.assertIn('Cursor', PSTACK['note'])  # native-plugin guidance


if __name__ == '__main__':
    unittest.main()
