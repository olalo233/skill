# Sources and design influences

Engineering Core is an original, model-agnostic synthesis. It does not vendor an upstream runtime or copy an upstream skill suite wholesale.

## OpenAI Codex documentation

The directory layout, `SKILL.md` metadata, progressive-disclosure approach, repository skill location, and `AGENTS.md` layering follow current OpenAI Codex documentation:

- https://developers.openai.com/codex/skills
- https://developers.openai.com/codex/guides/agents-md

## Matt Pocock skills

Repository: https://github.com/mattpocock/skills  
Pinned revision reviewed: `885e2ca4d842d139e9aef4e48d366c63cb1b8013`  
License: MIT

Ideas adapted rather than copied wholesale:

- tracer-bullet vertical slicing and explicit blocking edges;
- implementation as orchestration over TDD, verification, review, and commit;
- separate Standards and Spec review axes;
- behavior-focused TDD and repository-aware planning.

## DeepSeek Harness skills

Repository: https://github.com/deepseek-ai/deepseek-harness  
Pinned revision reviewed: `141eb6fef83422698aef7a981029e843e8161534`  
License: MIT

Ideas adapted rather than copied wholesale:

- correctness-first, evidence-backed review;
- selecting checks from the outgoing diff instead of reflexively running everything;
- proving simplification candidates from production consumers and net deletion;
- explicit lifecycle, concurrency, ownership, and public-contract review.

## Open GSD

Repository: https://github.com/open-gsd/gsd-core  
Pinned revision reviewed: `adb46cdd85add7928977a5664793267efdfca83f`  
License: MIT

Open GSD influenced the boundary between this lightweight core and a dedicated long-running project workflow. No Open GSD runtime, commands, or state machinery are included in this kit.
