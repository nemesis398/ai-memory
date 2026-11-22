---
type: llm
weight: 1
---

The response:

- uses the ai-memory skill, or says that the skill stops because `vault.root`
  is not set in its config file;
- when it drafts a note: one fact, flat frontmatter with `type`, `status`,
  `domain` as a list, `updated` and a double-quoted `description`;
- puts the exact symptom string "Unknown USB bridge" and the fix `-d sat`
  into the `description`;
- does not save the IP address or any secret.
