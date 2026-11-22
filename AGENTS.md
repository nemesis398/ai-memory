# Agent rules for ai-memory

These rules apply to every AI agent that works in this repository.

## What this repository is

A Claude Code plugin with one skill, `ai-memory`, and three hooks that inject
memory notes from an Obsidian vault. It holds no personal value: a user keeps
theirs in `${XDG_CONFIG_HOME:-~/.config}/ai-memory/config.json` (or the file
`AI_MEMORY_CONFIG` names), and `config.example.json` shows the shape.

| Path | Holds |
| --- | --- |
| `.claude-plugin/` | the plugin manifest and the marketplace of one |
| `hooks/hooks.json` | the three hooks, each running one adapter |
| `skills/ai-memory/SKILL.md` | the skill; its first line renders the Values block |
| `skills/ai-memory/scripts/` | the note reader, retrieval, state, lint, sweep and the config reader |
| `skills/ai-memory/adapters/claude/` | the hook adapters |
| `skills/ai-memory/tests/` | the tests, stdlib `unittest` |
| `evals/` | cases for `claude plugin eval` |

## Rules

1. **Nothing personal enters this repository.** No name, mail address,
   hostname, IP address, path of a real home or secret, in a file or in a
   commit message. A personal value is a key of the config file, and the
   tests and examples use made-up ones (`Alice`, `/home/alice/Notes`).
2. **A hook never fails a session.** Every adapter runs under
   `_common.run`, exits 0 and prints nothing but its one JSON line. A
   missing, empty or malformed config file is no failure: the hook says on
   one stderr line which key to set in which file.
3. **Tests first.** A change to a script or an adapter comes with its test,
   and the suite is green before a commit:

   ```sh
   PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/ai-memory/tests
   ```

4. **Python is stdlib only**, run as `python3 -B`, and writes no
   `__pycache__`.
5. **Prose has no em dash** and uses American spelling. CI checks the em
   dash.
6. **Commits follow Conventional Commits 1.0.0.**
