"""Suite declaration checks: dependency closure parsed from SKILL.md
references, required membership, placeholders, package layout."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATT_DEV = json.loads((ROOT / 'suites/matt-dev.json').read_text())
PSTACK = json.loads((ROOT / 'suites/pstack.json').read_text())

REQUIRED_MEMBERS = {'grill-with-docs', 'to-spec', 'to-tickets', 'implement',
                    'tdd', 'code-review', 'diagnosing-bugs', 'codebase-design',
                    'matt-flow'}

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


class MattDevClosureTests(unittest.TestCase):
    def setUp(self):
        self.members = {m['name']: m for m in MATT_DEV['members']}

    def test_required_members_present(self):
        self.assertTrue(REQUIRED_MEMBERS <= set(self.members),
                        REQUIRED_MEMBERS - set(self.members))

    def test_member_paths_exist_and_match_names(self):
        for m in MATT_DEV['members']:
            with self.subTest(member=m['name']):
                self.assertTrue((ROOT / m['path']).is_dir(), m['path'])
                self.assertEqual(m['name'], Path(m['path']).name)
                self.assertTrue((ROOT / m['path'] / 'SKILL.md').is_file(), m['path'])

    def test_depends_match_parsed_skill_references(self):
        for m in MATT_DEV['members']:
            with self.subTest(member=m['name']):
                text = (ROOT / m['path'] / 'SKILL.md').read_text()
                parsed = referenced_skills(text)
                self.assertEqual(set(m.get('depends', [])), parsed,
                                 f"{m['name']}: declared depends differ from "
                                 'references parsed out of SKILL.md')

    def test_closure_is_explicit_and_complete(self):
        for m in MATT_DEV['members']:
            for dep in m.get('depends', []):
                self.assertIn(dep, self.members,
                              f"{m['name']} depends on {dep}, not a member")

    def test_expected_dependencies(self):
        self.assertEqual(set(self.members['grill-with-docs']['depends']),
                         {'grilling', 'domain-modeling'})
        for name in ('to-spec', 'to-tickets', 'code-review'):
            self.assertIn('setup-matt-pocock-skills', self.members[name]['depends'])
        self.assertEqual(set(self.members['implement']['depends']),
                         {'tdd', 'code-review'})
        self.assertEqual(self.members['tdd']['depends'], ['codebase-design'])


class PstackSuiteTests(unittest.TestCase):
    def test_package_member_is_the_whole_vendored_tree(self):
        self.assertEqual(PSTACK['kind'], 'package')
        (member,) = PSTACK['members']
        self.assertEqual(member['path'], 'vendor/pstack')
        self.assertTrue((ROOT / 'vendor/pstack/plugin.json').is_file())
        self.assertIn('Cursor', PSTACK['note'])  # native-plugin guidance


class PlaceholderTests(unittest.TestCase):
    def test_design_and_uikit_are_documented_but_not_implemented(self):
        for name in ('design', 'ui-kit'):
            with self.subTest(suite=name):
                note = ROOT / 'suites' / f'{name}.md'
                self.assertTrue(note.is_file(), note)
                self.assertIn('not implemented', note.read_text().lower())
                self.assertFalse((ROOT / 'suites' / f'{name}.json').exists())


if __name__ == '__main__':
    unittest.main()
