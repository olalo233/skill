---
name: grill-me
description: "On explicit request, sharpen a plan or design with grilling in the current conversation."
disable-model-invocation: true
---

Invoke `grilling` in this conversation, not in an isolated interview subagent. When the runtime has a Skill tool, call it with `grilling`. Otherwise, read the installed sibling `../grilling/SKILL.md` and apply it here. If the dependency is missing, report it; do not invent a replacement interview.

Scope the invocation to the user's stated deliverable. Reuse answers and accepted decisions already in this conversation. The user decides product behavior, scope, material trade-offs, and irreversible choices; delegate ordinary reversible implementation choices to the agent within those constraints. Research facts rather than asking the user to supply facts available in the repository or tools. Optional future capabilities are outside this interview unless the user includes them.

Stop when the user confirms that the design and scope are sufficient to proceed. When explicitly asked to continue with GSD, use the applicable installed native GSD workflow in this same parent conversation. Keep its setup and approval checks, use the existing answers, and let it persist accepted decisions directly to its own artifacts before changing contexts. Do not require an intermediate PRD, automatically fork a new interview, or launch implementation without authorization.
