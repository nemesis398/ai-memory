---
type: llm
weight: 1
---

The response:

- uses the ai-memory skill, or says that the skill stops because `vault.root`
  is not set in its config file;
- takes the correction as the confirmation to supersede the note, not to
  edit it in place or delete it;
- describes a new note with the corrected fact that links the old one, the
  old note set to `status: superseded` and moved to `AI/archive/` with
  Obsidian, not with a shell `mv`;
- names the lint as the check before the change is done.
