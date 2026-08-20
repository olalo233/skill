---
name: ship-change
description: Prepare a completed feature branch or change for push, pull request, review, or merge. Verify scope and evidence, preserve useful commits, and perform publication actions only with explicit authorization.
---

# Ship Change

Make the outgoing change reviewable and safe to publish. Shipping does not imply permission to push, open a pull request, or merge.

## Prepare

1. Resolve the intended base, head, remote, and integration policy.
2. Inspect branch state, commit list, working tree, and the complete outgoing diff.
3. Confirm every commit belongs to the accepted task and no secrets, generated residue, debug code, or unrelated edits are included.
4. Use `$verify-change`.
5. Use `$review-change`, or consume an independent review already performed against the same base and head.
6. Ensure required documentation, migration notes, screenshots, release notes, or operator instructions are present.

## History

- Preserve useful verified slice commits on the feature branch.
- Do not squash, rebase, amend, force-push, or rewrite another person's commits without explicit authorization.
- At the integration boundary, follow repository policy. Squash merge is a valid way to keep the protected branch concise while retaining checkpoints during development.

## Prepare the publication summary

Include:

- problem and delivered behavior;
- key design decisions and non-goals;
- commit or slice summary;
- exact verification evidence;
- migration, compatibility, rollout, and rollback notes;
- screenshots or demos when relevant;
- known limitations and follow-up work.

## Authorization boundary

Verified slice commits follow the kit's default checkpoint policy. Treat publication and history-changing actions as separate operations requiring explicit user intent:

- push or force-push;
- create or update a pull request;
- mark a pull request ready;
- merge;
- squash, rebase, amend, or otherwise rewrite published history;
- delete a branch or tag.

If an authorized action fails or its result is uncertain, verify read-only before retrying. Never blindly create duplicate pull requests or repeat a publication action.

## Report

State what is ready, what action was actually performed, the resulting remote identifiers, pending CI or review, and any blocker to integration.
