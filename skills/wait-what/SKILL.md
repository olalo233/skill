---
name: wait-what
description: "On explicit request, explain an unclear message again in clear Chinese or English without changing the task."
disable-model-invocation: true
---

The last explanation did not land. Explain it again; do not restart the project or advance implementation.

## Language

Use the language explicitly requested with this invocation. Otherwise use the user's latest conversational language, not the language of pasted code or quoted documents. Use clear Chinese in a Chinese conversation and plain technical English in an English conversation. Use bilingual output only when requested; do not duplicate every paragraph by default. Keep code, API names, commands, paths, and identifiers unchanged.

For Chinese, use natural, concrete wording and introduce an unfamiliar term briefly when it matters. Avoid literal translations of English jargon. For English, use short, direct sentences and common technical vocabulary. Do not claim formal ASD-STE100 compliance.

## Explanation

Give the missing background, the actual point, and its consequence for the current task. Start with the question the user is trying to answer. Make the responsible component, action, data/state change, and causal link explicit when relevant. A small example or before/after comparison is often better than another abstraction. Be brief enough to reduce effort, but do not remove material constraints or uncertainty.

Reuse terminology already agreed in this conversation and relevant existing project or GSD context files. Consult a glossary or context map only when it exists and is relevant. Do not require or create CONTEXT.md, CONTEXT-MAP.md, or a new glossary system.

Separate facts, assumptions, and recommendations. When the previous explanation was mistaken, correct it explicitly rather than making the mistake easier to read. When a decision really is needed, state the decision, recommendation, and reason; do not turn routine engineering details into new questions for the user. A request for explanation is not approval of the previous proposal.

Use a tiny diagram only when it materially helps; `show-me` is available when a visual is the better explanation. Do not automatically run another skill, generate a presentation, research the entire project, edit files, or resume execution. Finish the clarification and leave the existing workflow and scope unchanged unless the user explicitly requests more.
