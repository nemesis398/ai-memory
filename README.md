# ai-memory

A [Claude Code](https://claude.com/claude-code) plugin that keeps an agent's
memory as notes in an [Obsidian](https://obsidian.md) vault: one fact per
note in `AI/memory/`, and a `description` that the hooks inject as a single
line when a session needs it.

Most memory stores grow into a pile of session logs that nobody reads. This
one asks four questions before a note is written (not derivable, changes
behavior, lasts, verified), sends a fact to a better home first (a skill, the
agent instructions, a machine's runbook), and injects only the lines a prompt
or an error message points at.

## What it does

- **The skill** says when a memory is worth writing, the format the hooks
  and the lint read, and how to supersede, archive and review a note.
- **Three hooks** inject the notes:

  | Event | Injects |
  | --- | --- |
  | `SessionStart` | the lines of the pinned notes, once per session |
  | `UserPromptSubmit` | the notes whose domain keywords or symptom the prompt names |
  | `PostToolUseFailure` | the notes whose symptom string is in the error |

  A subagent gets nothing. Every hook exits 0 whatever happens and logs a
  failure to `~/.local/state/ai-memory/hook.log`, a directory that
  `AI_MEMORY_STATE_ROOT` moves. `AI_MEMORY_DISABLED=1` turns them off.
- **`scripts/lint.py`** checks the notes: frontmatter, description length,
  unknown domains, private IPv4 addresses and token-like runs, and the
  Markdown with `markdownlint-cli2`.
- **`scripts/sweep.py report --since YYYY-MM-DD`** prints the report a weekly
  review with the user starts from: memory candidates from the session notes
  since that day, archive proposals, recurring misses and the notes due for
  review. It decides nothing: the user confirms each promotion and archival.

## Install

In Claude Code, add the repository as a marketplace and install the plugin:

```text
/plugin marketplace add nemesis398/ai-memory
/plugin install ai-memory@ai-memory
```

It needs Python 3.10 or later as `python3` on the `PATH`, and nothing
outside the standard library. For the Markdown check the lint runs the
binary `AI_MEMORY_MDLINT` names, else `markdownlint-cli2` on the `PATH`;
with neither, it prints one WARN and checks everything else.

## Configure

The values live in `${XDG_CONFIG_HOME:-~/.config}/ai-memory/config.json`, or
in the file `AI_MEMORY_CONFIG` names. `config.example.json` shows the shape.

| Key | Type | What it is |
| --- | --- | --- |
| `user.name` | string | how the skill names the user; optional, never stops the skill |
| `vault.root` | string, an absolute path | the vault; `AI_MEMORY_VAULT` wins over it |
| `vault.commit` | string, a command | what commits a note, run as `COMMAND MESSAGE PATH...`; the skill then never runs `git commit`. Without it the commit step is off: the note stays uncommitted and the skill says so |
| `memory.domains` | object, a list of keywords per domain | the domain vocabulary; without it the lint checks no domain and no digest is injected, and a mistyped one is a lint ERROR and one stderr line from the prompt hook, which still injects the symptom matches. `AI_MEMORY_DOMAINS` may name a JSON file instead |

The skill renders the values into its text when it loads. A key that is not
set says so there, naming the key and the file. A missing, empty or
malformed file counts as no values: the skill stops, `lint.py` and
`sweep.py` exit 2 with the same sentence, and each hook injects nothing and
says it on one stderr line.

## The vault

The notes sit in fixed places of the vault: `AI/memory/`, `AI/archive/` and
`AI/sessions/`. The skill expects the vault to provide:

- the Obsidian command line, `obsidian`, with the app running: a superseded
  note moves to `AI/archive/` with `obsidian move`, because only Obsidian
  rewrites the links that point at it;
- session notes in `AI/sessions/` with `type: session` in their frontmatter
  and a `## Memory candidates` heading, where a candidate waits for the
  weekly review and where `sweep.py` reads it;
- optionally, a `Memory.base` at the vault root with views of the active,
  pinned and stale notes. The skill works without one.

## Use

Ask in your own words. The skill fires on requests such as:

- "remember this"
- "save a memory: ..."
- a correction of the way the agent works: "no, never pass `-x`"
- "this memory is wrong, supersede it"

## Tests

The scripts and the hooks have unit tests:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/ai-memory/tests
```

`evals/` holds cases for `claude plugin eval`: a request to remember a fix, a
correction, a surprise the agent verified on its own, a session log that is no
memory, and a note that is wrong. They
run against a model, on your own account:

```sh
claude plugin eval . --runs 3 --allow-tools 'Bash(python3:*)' --no-publish
```

Each case allows Bash, and the grant narrows it to `python3`, so that the
skill's first line can render its Values block. Run them on a machine whose
eval sandbox permits Bash: where it is refused, every case loads the skill
without its values. `--no-publish` keeps the report local.

CI checks the manifests, the tests, the Markdown, and that no em dash
slipped in.

## License

[MIT](LICENSE)
