#!/usr/bin/env python3
"""The personal values of the ai-memory skill, read from its config file.

The file is the one `AI_MEMORY_CONFIG` names, else
`${XDG_CONFIG_HOME:-~/.config}/ai-memory/config.json`: one JSON object,
values only, never a secret.

    skill_values.py render

prints the Values block that SKILL.md opens with: `## Values` and one line
per key of TEXT_KEYS. A key that is not set prints, instead of its line,
the sentence to stop with, or for a key of STEPS the step that is off and
how to go on without it, or for a key of OPTIONAL nothing at all. It exits 0 whatever happens, because it runs
while the skill loads.

A key that is missing, of another type, or an empty string counts as not
set. A file that is missing, empty or not a JSON object reads as no values
at all. Nothing here raises except `require`, whose message is the one
sentence every script and hook stops with.

Stdlib only and no work at import time: hooks import it on every turn.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# The keys the skill's text uses, in the order the Values block lists them,
# each with the type it must have.
TEXT_KEYS = [
    ("user.name", str),
    ("vault.root", str),
    ("vault.commit", str),
]

# Keys whose absence turns one step off, not the skill:
# key -> (the step, how to go on without it).
STEPS = {
    "vault.commit": (
        "Commit",
        "leave the note uncommitted and say so; never commit it with `git commit`.",
    ),
}

# Keys that never stop anything: printed when set, left out when not.
OPTIONAL = {"user.name"}

ENV = "AI_MEMORY_CONFIG"
NAME = "ai-memory"
MISSING = "set `{key}` in `{path}`"


class Missing(LookupError):
    """A value the skill needs is not set."""

    def __init__(self, key: str) -> None:
        super().__init__(key)
        self.key = key

    def __str__(self) -> str:
        return MISSING.format(key=self.key, path=path())


def path() -> Path:
    named = os.environ.get(ENV)
    if named:
        return Path(named)
    config = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(config) / NAME / "config.json"


def load() -> dict:
    try:
        loaded = json.loads(path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def get(key: str, kind: type = str, values: dict | None = None):
    """The value at the dotted `key`, or None when it is not set as `kind`."""
    node = load() if values is None else values
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    if kind is not bool and isinstance(node, bool):
        return None
    if not isinstance(node, kind):
        return None
    if isinstance(node, str) and not node.strip():
        return None
    return node


def require(key: str, kind: type = str, values: dict | None = None):
    """The value at `key`, or raise Missing naming it."""
    value = get(key, kind, values)
    if value is None:
        raise Missing(key)
    return value


def show(value) -> str:
    """A value as one line: a string with its white space run together, a
    list or object as compact JSON."""
    if isinstance(value, str):
        return " ".join(value.split())
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def render() -> str:
    """The Values block, one line per key of TEXT_KEYS."""
    values = load()
    where = path()
    lines = ["## Values", ""]
    for key, kind in TEXT_KEYS:
        value = get(key, kind, values)
        if value is not None:
            lines.append(f"- `{key}`: {show(value)}")
        elif key in OPTIONAL:
            continue
        elif key in STEPS:
            step, without = STEPS[key]
            lines.append(f"**Step {step} is off** until `{key}` is set in `{where}`: {without}")
        else:
            lines.append(f"**Stop.** Set `{key}` in `{where}` before you use this skill.")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    if argv != ["render"]:
        print("usage: skill_values.py render", file=sys.stderr)
        return 2
    try:
        sys.stdout.write(render())
    except Exception as exc:  # noqa: BLE001  the skill still has to load
        print(f"**Stop.** The values could not be read: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
