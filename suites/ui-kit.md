# ui-kit suite — placeholder, no members yet

Deliberately not implemented. Candidate members (`html`, `show-me`,
`drawio`, `dataviz`) are undecided: the review rejected deciding project
dependencies from what happens to be installed globally on one machine,
and `dataviz`'s source is unverified. `html` and `show-me` already ship
in the `base` suite; whether they are also pinned here depends on the
final ui-kit boundary.

When membership is decided, `suites/ui-kit.json` will list them with
explicit paths and a parsed dependency closure. Until then
`--suite ui-kit` fails with "no suite 'ui-kit' in source".
