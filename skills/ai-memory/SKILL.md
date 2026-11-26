---
name: ai-memory
description: >-
  Write, supersede and review the memory notes in the vault's memory folder (`AI/memory/` by default):
  one fact per note, flat frontmatter, and a description that retrieval
  injects as one line. Use this when the user says remember this or save a
  memory, when the user corrects or confirms a way of working that is worth
  keeping, when a verified surprise turns up, and whenever a memory
  note is written, reviewed, superseded or archived. It holds the four
  tests a memory has to pass, the better homes to try first, and the format
  that the hooks and the lint read.
allowed-tools:
  - Bash(python3 -B "${CLAUDE_SKILL_DIR}/scripts/skill_values.py" render)
  - Bash(python3 -B "${CLAUDE_SKILL_DIR}/scripts/lint.py":*)
---

# ai-memory

!`python3 -B "${CLAUDE_SKILL_DIR}/scripts/skill_values.py" render`

When Values lists `user.name`, call the user by that name. A line that says
**Stop.** names a value that is not set, and a line such as
`vault.area: invalid: ...` names one that is wrong: on either, stop and tell the
user which value to fix in which file.

A memory is one fact that a future session needs and cannot find anywhere
else. It lives as one small note in the vault's memory folder, and a session
mostly sees only its `description`, injected as a single line. So the work
sits in two places: deciding whether the fact deserves a note at all, and
writing a description in the words a future prompt or error message will
contain.

The vault is the directory `vault.root` in Values names. Every path below
written as `AREA/...` sits under `vault.area` in Values instead, `AI` by
default and `.` for the vault root: its memory, sessions and archive folders
are `AREA/memory/`, `AREA/sessions/` and `AREA/archive/`. Read its `Vault.md`,
if it has one, before the first write of a session, because its rules bind these notes too.

## Save a memory only if all four hold

1. **Not derivable.** The repo, CLAUDE.md, a skill, a vault note or an
   existing memory doesn't already say it. If one does, update that instead.
2. **It changes behavior.** A future session in this domain would act
   differently, or make a mistake, without it.
3. **It lasts.** It is still true in a week, or it carries an expiry date.
4. **It is verified.** For a gotcha, the mechanism is stated, not guessed.

An explicit "remember this" waives the third test only. Ask what was
non-obvious about it and save that.

**Never save:**

- task progress, completed-work logs, or what happened this session (that's
  the session note)
- anything restated from CLAUDE.md, a skill, or a memory that was injected
- negative claims such as "tool X is broken": they harden into refusals that
  outlive the bug
- failures that depend on a fixable environment, transient errors, unresolved
  dead ends
- architecture dumps and fix recipes that the code or its history already
  records
- secrets, tokens, internal IPs, and sensitive personal details unless asked

The vault may sync to the user's phone, so the last item holds for every
note in the area. The lint warns on private IPv4 addresses and on long token-like runs.

## Put it somewhere better first

| It is | It goes in |
| --- | --- |
| A pitfall of one task or tool | the skill for that task, or a comment or test where the code is |
| A correction of a repeatable step | the skill that runs the step |
| A rule for every session | CLAUDE.md |
| A fact about one machine | that machine's note or runbook |
| What happened, what is next | the session note, or the task tracker |
| Something that fits none of those | a memory |

**A gotcha lives where it bites.** The gotcha test, defined with the kinds
below, decides what counts as one, but its home is the thing it bites (the
skill, the runbook, the code), because that is where the next session meets
it. It becomes a memory only when no such home exists.

## When to write

**When to write:** during a turn only for an explicit request, a correction or
confirmation from the user, or a verified surprise. Everything else goes into the
session note's *Memory candidates*, which is searchable but never injected.

**Write when a cost repeats, not when something happens once.** The same error
signature in two sessions, or more than 20 turns spent on one problem, makes a
candidate. A trap nobody writes down costs a session every time it bites
again. Write the exact symptom string into `description`, in backticks,
because the failure hook matches on it.

**Nothing writes a memory unattended.** A hook, a subagent, a workflow or a
headless run never writes one. It reports the candidate to whoever dispatched
it instead.

## A memory note

```markdown
---
type: memory
status: active
domain:
  - claude-code
updated: 2026-09-12
description: "`pkill -f` in the Bash tool matches the tool's own wrapper shell and kills it, shown as `Exit code 144` with no output. Kill by PID."
tags:
  - gotcha
generated: claude
---

# pkill -f kills the Bash tool's own shell

`pkill -f` run from the Bash tool kills the shell running it. The harness wraps
each command in `bash -c` with the whole script as its argument, so the pattern
matches the wrapper's command line before anything else.

**Why:** hit twice on 2026-09-12. Each call died with `Exit code 144`, no
output, and the work half done, which reads like a crash.

**How to apply:** kill by PID. Run `pgrep -f` first, read what it matched, and
only then kill that PID.

Related: a bare wikilink to each related note.

*Verified 2026-09-12 · session SESSION-ID.*
```

After the frontmatter comes an H1 title, then the body: the fact as a
declarative sentence, `**Why:**` (what happened, with the date),
`**How to apply:**`, links to related notes, and a closing provenance line with
the session id. `echo "$CLAUDE_CODE_SESSION_ID"` prints the id in the Bash
tool, and it replaces `SESSION-ID`. Never write a placeholder in angle
brackets: markdownlint reads it as inline HTML (MD033). Keep the period inside
the italics: an emphasized line without closing punctuation reads to
markdownlint as a heading (MD036). The lint counts both as an ERROR.

The H1 repeats the filename, and the filename is a short claim. Retrieval
labels every injected line with that filename, and a bare wikilink resolves by
it, so it has to be unique in the whole vault.

- **Flat frontmatter.** Bases can't reliably filter nested keys such as
  `metadata.type`, and the vault's view properties are a closed set: `type`,
  `status`, `domain`, `updated`, `description`. `generated: claude` is a
  provenance key, and `domain` is a list.
- **`domain` comes from `memory.domains` in the config file.** Its keys are the
  domain vocabulary: the lint warns on any other value, and the prompt hook
  reads each key's keywords to pick a digest.
- **`description` is the line retrieval injects.** Write it as the fact plus
  the behavior it changes, in the user's words for the symptom. Over 250
  characters is a lint WARN. Always put it in double quotes: an unquoted value
  that opens with a backtick or holds a colon followed by a space does not
  parse, and the note then drops out of every hook.
- **The kind is a tag:** `gotcha`, `feedback`, `preference`, `reference`,
  `pinned`. A note carries exactly one of the first four, and `pinned` may
  join it.
  - `gotcha`: a verified behavior that contradicts what you would reasonably
    expect. The test is that someone competent would have guessed wrong.
    Write down what it looks like when it bites, because the symptom is what
    a future session recognizes first, long before it recognizes the cause.
  - `feedback`: a correction or confirmation from the user about how to work.
  - `preference`: how the user wants a thing done, chosen or named.
  - `reference`: where something is found, such as an endpoint, a board or a
    path.
  - `pinned`: operating knowledge that nearly every session needs.
- **Size:** soft cap 2 KB (2048 bytes), hard cap 6 KB (6144 bytes), flagged by
  a lint script. Over the soft cap is a WARN, over the hard cap an ERROR.
- **`updated` moves only when the claim was re-checked.** It drives the review
  queue.

Write the note in English. Every note in the area passes
`markdownlint-cli2` under the vault's `.markdownlint-cli2.jsonc`, and the H1
right after the frontmatter is what satisfies MD041. Links are bare wikilinks,
the way `Vault.md` describes them.

### The symptom goes in backticks

For a gotcha, the exact error text goes in backticks in `description`. The
failure hook compares the error output of a failed tool call with the
backticked spans of every description, and with nothing else, so a symptom
written as plain prose is never matched. The lint warns on a gotcha whose
description has no backticked span of 6 characters or more.

### Both languages in the description

Matching by keyword misses paraphrases, so `description` should carry both
languages' terms where the user mixes languages: **Teilnetzmaske** next to
"subnet mask", **Vermittlungsschicht** next to "network layer".

## How the notes are read

- **SessionStart** injects the descriptions of the notes tagged `pinned`,
  within 4000 characters (about 1k tokens). Pinned means operating knowledge
  that nearly every session needs: how the task tracker answers, where the
  daily note lives, how secrets are fetched. *Rules* about how to work stay in
  CLAUDE.md, because subagents read CLAUDE.md and never see pinned notes. The
  list is generated from frontmatter at hook time, so there is no index file
  to rot.
- **UserPromptSubmit** matches the prompt against titles, descriptions, tags
  and domain keywords, and injects at most 4 hits as path plus description,
  within 1000 characters. The first time a domain's keyword appears in a
  session, it also injects that domain's digest once: the descriptions of its
  active notes, most recently verified first, cut at 4000 characters. That cut
  is the per-domain cap.
- **PostToolUseFailure** matches the error text against the symptom strings in
  the descriptions and injects at most 2 hits. It costs nothing while commands
  succeed.
- **Subagents get nothing.** The parent passes what a subagent needs in its
  prompt.
- **The agent opens a full note only when the line isn't enough.** Notes are
  small, so that read is cheap.

The plugin registers the three hooks (`hooks/hooks.json`). Without
`vault.root` in the config file they inject nothing and say on one stderr line
which key to set in which file, and a note is read only when someone opens
it in the vault.

## Record freshness

A memory states the date it was verified and, where it matters, the version it
was verified on. A claim about a tool goes stale when the tool changes, and
the date and the version are what a review re-checks it against.

## Lifecycle

- **Promote** a candidate on its second occurrence or on request, in a weekly
  review with the user. It starts from the sweep report,
  `python3 -B "${CLAUDE_SKILL_DIR}/scripts/sweep.py" report --since YYYY-MM-DD`
  with the day of the last review, which lists the candidates, the archive
  proposals and the recurring misses and decides nothing. Put each proposal to
  the user as recommended or not recommended, with a one-line reason, and the
  user confirms each one.
- **Log what was injected.** Every hook appends what it injected, and why, to
  `~/.local/state/ai-memory/injections.jsonl`, outside the synced vault. The
  sweep report reads it to count misses and reuse.
- **Supersede in place.** A contradicting fact gets a new note that links the
  old one, and the old note turns `status: superseded` and moves to
  `AREA/archive/`. CLAUDE.md beats a memory.
- **Cap** what one domain can inject. When it's full, a new pinned note has to
  replace one. The lint warns once the pinned lines pass 4000 characters.
- **Review** the active notes whose `updated` is older than 90 days, oldest
  first. Archive what nobody misses.
- **Measure** reuse as "the injected line or the note changed what a session
  did", not as file opens, because retrieval delivers the line without an
  open.

### Supersede or archive a note

A correction the user gives in the session is the confirmation to supersede the
note it contradicts.

In an interactive main session, a memory you find wrong on your own goes to
the user at once, in the question dialog: supersede it, archive it, or keep it,
the recommended answer first and marked (Recommended), with a one-line
reason. The user's answer is the
confirmation, and the steps below follow it. When no answer can come, because
the user said not to ask or the run is a hook, a cron run, a subagent or
`--print`, change nothing. Add one bullet under the session note's *Memory
candidates* instead: the word `archive`, a bare wikilink to the note, a colon,
and why it is wrong.

```markdown
- archive [[pkill-f-kills-the-claude-code-bash-wrapper]]: why it is wrong, in one line.
```

A run that writes no session note, such as a subagent, puts that bullet in its
report. The sweep report lists it under *Archive proposals*, never as a
candidate, and the weekly review puts it to the user.

Anything else, a supersede or an archival without a successor, is a proposal
for the weekly review, and these steps wait until the user has confirmed it.

1. Write the new note, and link the old one from it with a bare wikilink.
2. In the old note, set `status: superseded`. Leave its `updated` alone,
   because it records when the old claim was last verified.
3. Move it into the archive. Check `test -d "<vault.root>/.obsidian"`. With
   that folder the vault is an Obsidian vault, so move it with Obsidian, which
   rewrites the links that point at it:

   ```bash
   obsidian move path="AREA/memory/FILENAME.md" to="AREA/archive" < /dev/null
   ```

   The CLI exits 0 even when the move fails, so read its stdout for `Error:`.
   Without that folder, use a plain move, because a bare wikilink resolves by
   filename and the filename does not change:

   ```bash
   mv -n "<vault>/AREA/memory/FILENAME.md" "<vault>/AREA/archive/"
   ```

   Then run `test -e` on the target. Never `rm` and never rename a note.

A note that nobody misses is archived without a successor, once the user has
confirmed it: steps 2 and 3, `status: superseded`, then the move. Every note
in `AREA/archive/` is superseded, so none of them shows in the *Active* view.

### Review a note

The review queue is the active notes whose `updated` is older than 90 days,
oldest first. The sweep report lists it under *Review queue*, and a vault
with a `Memory.base` at its root may show it as a view. For each one, re-check the claim against
the thing it describes. Still true: set `updated` to today and add the version
if it matters. Wrong or gone: propose to supersede or archive it, with a
recommendation, and wait for the user.

## Check it

```bash
python3 -B "${CLAUDE_SKILL_DIR}/scripts/lint.py"
```

It prints one `LEVEL rel: message` line per finding and exits 1 on any ERROR,
and 2 with "set `vault.root` in `PATH`", PATH being the config file, when the
skill is not set up: then stop and tell the user. The same holds for an exit 2 of lint or sweep
that names `vault.area`: stop and tell the user which value to fix in which
file.
`--vault PATH` points it at another vault, and `--summary` adds counts per
folder and kind and the pinned characters against their budget. A vault with
a check of its own (a `vault-check` script, say) can run the same lint, and
then that check's exit 0 gates every vault commit.

**Commit.** When Values lists `vault.commit`, commit a memory note with that
command and never with `git commit`, as `COMMAND MESSAGE PATH...`, naming
each file (`COMMAND "docs(ai): add a memory" "AREA/memory/FILE.md"`). Exit 0
may mean the command queued the commit, and exit 1 means try again later.
When `vault.commit` is not set, leave the note uncommitted and tell the user
so.
