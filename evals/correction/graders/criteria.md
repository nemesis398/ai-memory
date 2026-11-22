---
type: llm
weight: 1
---

The response:

- uses the ai-memory skill, or says that the skill stops because `vault.root`
  is not set in its config file;
- treats the correction as a reason to write a memory now, of kind
  `feedback`;
- or proposes a better home first (the repository's agent instructions or a
  skill that runs the tests) and says why that beats a memory;
- writes the rule with the behavior it changes, not as a log of what happened.
