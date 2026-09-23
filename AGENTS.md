# Maintaining this skill collection

This repository distributes reusable skills and assets. Keep each skill under `skills/<name>/`; preserve upstream attribution and licenses. `docs/gsd-project-policy.md` is an optional policy for projects adopting the GSD development suite, not a requirement for using unrelated skills or maintaining this repository.

- Maintain the reviewed upstream commit and exact path mappings in `.sync/upstreams.json`.
- Keep personal machine paths, credentials, environment inventories and execution logs outside this public repository.
- Preserve local adaptations with three-way merging; never replace a customized skill wholesale with upstream HEAD.
- Run `python3 scripts/validate.py` and `python3 -m unittest discover -s tests` before publishing. Review the actual diff and run Gitleaks over staged content/history.
- Keep ordinary skill files portable between runtimes. Use paths relative to the installed skill; install documented sibling dependencies together.
- Do not copy this AGENTS.md or the GSD project policy into other repositories automatically.
