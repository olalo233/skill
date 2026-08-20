# Engineering Core

Engineering Core is the default development kit. It supplies one compact `AGENTS.md` contract and ten workflow skills.

It is deliberately not a project-management framework, language style guide, or model router. Small work remains lightweight; large multi-phase work may be escalated to a dedicated system such as Open GSD.

## Contents

| Skill | Use it for |
| --- | --- |
| `repo-scout` | Evidence-backed orientation before non-trivial work |
| `plan-work` | Converting approved intent into vertical slices |
| `implement-slice` | Implementing, verifying, and committing one slice |
| `diagnose-bug` | Root-cause-first debugging and incident analysis |
| `tdd` | Red-green-refactor at a stable behavioral seam |
| `verify-change` | Selecting the smallest credible evidence for a diff |
| `review-change` | Separate engineering and intent/spec review |
| `simplify-change` | Evidence-backed deletion and simplification |
| `handoff` | Transporting reliable state across agents or sessions |
| `ship-change` | Preparing a verified branch for push, PR, or merge |

## Recommended routing

For a small, clear, reversible change:

```text
implement directly -> verify-change -> commit
```

For an unknown bug:

```text
diagnose-bug -> implement the root-cause fix -> verify-change -> commit
```

For a non-trivial feature:

```text
repo-scout -> design decision -> plan-work
-> implement-slice (repeat) -> review-change -> ship-change
```

For a long-running, multi-phase project with durable state, dependency waves, and UAT, use a dedicated project workflow rather than stretching this kit into one.

## ChatGPT and Codex collaboration

Use `repo-scout` to bring repository facts into design discussions. When a design decision belongs outside the local coding context, stop at the decision gate and use `handoff` to produce a compact evidence package for ChatGPT or another reviewer.

After the decision is settled, `plan-work` turns it into slices. Codex executes one slice at a time with `implement-slice`, commits verified checkpoints, and uses `handoff` again when context or agent changes.

## HarnessKit composition

Create one HarnessKit kit containing:

- `kits/core/AGENTS.md` as the project or global rules file;
- all ten folders under `kits/core/.agents/skills/`.

Keep this Git repository as the editable source. Treat copies installed into Codex, Antigravity, OpenCode, or other agent directories as generated deployment artifacts.

## Direct Codex smoke test

For a project-local test, copy or symlink the skill folders into the target repository's `.agents/skills/`, then place this kit's `AGENTS.md` at the repository root. For user-wide testing, install the skill folders under `~/.agents/skills/` and merge only the guidance you want into `~/.codex/AGENTS.md`.
