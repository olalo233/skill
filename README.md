# Development workflow

One coding suite, two paths. This repository composes mature upstream tools instead of reimplementing their workflows.

## What owns what

- **Open GSD** is the workflow engine. It owns requirements, project state, planning, worker/subagent execution, verification, and shipping.
- **grilling** stress-tests an idea or design when ordinary discussion is not enough.
- **prototype** answers one logic, state-model, or UI question with throwaway code before production implementation.
- **show-me** explains the current plan, architecture, code shape, diff, or decision with the smallest useful visual.
- **ponytail-review** is a separate final pass that looks only for code that can be deleted or replaced by existing, standard-library, native-platform, or already-installed capabilities.

There is no second task system, memory system, planner, verifier, or worker scheduler in this repository.

## Install

Install Open GSD with its own installer. Its upstream project requires runtime-specific installation, so its internal agents and commands are not copied into this repository.

```bash
npx @opengsd/gsd-core@latest
```

Choose Codex and the desired scope in the installer.

In HarnessKit, create one kit containing:

- this repository's `AGENTS.md`;
- the four folders under `skills/`.

## Quick prototype / MVP path

Use this for a small change or a result needed quickly.

```text
/gsd-quick <task>
```

The default quick path skips discussion, research, plan checking, and the full verifier. Add only the capability the task actually needs:

```text
/gsd-quick --discuss <task>   # a few important ambiguities
/gsd-quick --research <task>  # implementation approach is genuinely unknown
/gsd-quick --validate <task>  # stronger plan and post-execution verification
```

Do not turn every quick task into `--full`.

When the unknown is the design itself rather than the implementation, run `$prototype` first. Keep the prototype throwaway, record the answer it produced, then implement the accepted answer with `/gsd-quick`.

After the result works:

1. Use `$show-me` when a human needs to understand the flow, diff, state change, or architecture.
2. Run `$ponytail-review` as a complexity-only review.
3. Apply only reductions that preserve the requested behavior, then rerun the same acceptance checks.

`/gsd-fast` remains available for truly trivial one-sentence edits; it is not a third workflow.

## Full path

Use this for work that needs requirements discussion, research, several tasks, worker scheduling, persistent state, or formal acceptance.

For a new project:

```text
/gsd-new-project
```

For an existing repository:

```text
/gsd-onboard
```

Then run the existing GSD lifecycle:

```text
/gsd-discuss-phase <N>
/gsd-plan-phase <N>
/gsd-execute-phase <N>
/gsd-code-review <N>
/gsd-verify-work <N>
/gsd-ship <N>
```

Use `$grilling` during requirements or solution exploration only when the idea needs deliberate stress-testing. Use `$show-me` at any checkpoint where text is not enough to align on what the system, plan, or code actually does.

GSD's files are the canonical artifacts:

- `.planning/PROJECT.md` and `.planning/REQUIREMENTS.md` form the project/PRD layer;
- phase `CONTEXT.md` records settled implementation decisions;
- phase research and `PLAN.md` form the implementation-spec and task-planning layer;
- `STATE.md`, summaries, reviews, and UAT files preserve execution and acceptance state.

Do not create a parallel PRD, spec, roadmap, memory, or task hierarchy by default. A single organization-specific PRD or spec document can later be exported from these sources if real use requires it.

## Quality order

Correctness and requested behavior come first. Simplification comes after the change passes its acceptance checks.

```text
implement -> correctness review -> user-facing verification
          -> ponytail-review -> accepted reductions -> re-verify
```

`ponytail-review` does not replace a correctness, security, or performance review.

## Improving the suite

Do not add another skill because it sounds useful. After several real Codex sessions, use `skill-doctor` or Matt Pocock's `retro` against the actual transcripts. Change this suite only when failed sessions provide concrete evidence for the change.

See `SOURCES.md` for pinned upstream revisions and the capabilities intentionally left out of this first version.
