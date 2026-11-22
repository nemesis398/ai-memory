---
type: llm
weight: 1
---

The response either says that the ai-memory skill stops because
`vault.root` is not set in its config file, or it:

- treats the correction as a reason to write a memory now, of kind
  `feedback`, and may name a better home as well (the repository's agent
  instructions or a skill that runs the tests);
- puts the note in the vault's `AI/memory/`, not in Claude Code's built-in
  memory folder or its `MEMORY.md` index;
- shows frontmatter with `type: memory`, `status: active`, the kind as a tag
  (`tags: [feedback]`) and a double-quoted `description`;
- writes the rule with the behavior it changes, not as a log of what
  happened.

It fails when the only note it proposes lives anywhere but the vault's
`AI/memory/`.
