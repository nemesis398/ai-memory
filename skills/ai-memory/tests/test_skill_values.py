"""skill_values.py, the one reader of the skill's config file.

What it pins: where the file is looked for, that anything other than a JSON
object reads as no values, that a key of the wrong type or an empty string
counts as not set, the one sentence a missing key produces, and the Values
block that `render` prints into SKILL.md when the skill loads.
"""
from __future__ import annotations

import json
import subprocess
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import skill_values as sv  # noqa: E402


class Where(unittest.TestCase):
    def test_the_variable_names_the_file(self):
        with mock.patch.dict(os.environ, {"AI_MEMORY_CONFIG": "/x/values.json"}):
            self.assertEqual(sv.path(), Path("/x/values.json"))

    def test_without_it_the_xdg_config_home(self):
        env = {"XDG_CONFIG_HOME": "/cfg", "HOME": "/home/tester"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(sv.path(), Path("/cfg/ai-memory/config.json"))

    def test_without_both_the_home_config(self):
        with mock.patch.dict(os.environ, {"HOME": "/home/tester"}, clear=True):
            self.assertEqual(sv.path(), Path("/home/tester/.config/ai-memory/config.json"))

    def test_an_empty_variable_counts_as_unset(self):
        env = {"AI_MEMORY_CONFIG": "", "XDG_CONFIG_HOME": "", "HOME": "/h"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(sv.path(), Path("/h/.config/ai-memory/config.json"))


class Reading(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.file = Path(self.tmp.name) / "values.json"
        patcher = mock.patch.dict(os.environ, {"AI_MEMORY_CONFIG": str(self.file)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def write(self, text: str) -> None:
        self.file.write_text(text, encoding="utf-8")

    def test_a_missing_file_is_no_values(self):
        self.assertEqual(sv.load(), {})

    def test_malformed_json_is_no_values(self):
        self.write("{not json")
        self.assertEqual(sv.load(), {})

    def test_a_list_is_no_values(self):
        self.write("[1, 2]")
        self.assertEqual(sv.load(), {})

    def test_bytes_that_are_not_utf8_are_no_values(self):
        self.file.write_bytes(b"\xff\xfe{}")
        self.assertEqual(sv.load(), {})

    def test_a_directory_is_no_values(self):
        self.file.mkdir()
        self.assertEqual(sv.load(), {})

    def test_a_dotted_key_walks_the_objects(self):
        self.write(json.dumps({"user": {"name": "Alice"}}))
        self.assertEqual(sv.get("user.name"), "Alice")

    def test_a_missing_key_is_none(self):
        self.write(json.dumps({"user": {}}))
        self.assertIsNone(sv.get("user.name"))
        self.assertIsNone(sv.get("nothing.at.all"))

    def test_a_key_under_a_string_is_none(self):
        self.write(json.dumps({"user": "Alice"}))
        self.assertIsNone(sv.get("user.name"))

    def test_the_wrong_type_is_none(self):
        self.write(json.dumps({"user": {"name": ["Alice"]}, "n": 3, "flag": True}))
        self.assertIsNone(sv.get("user.name"))
        self.assertIsNone(sv.get("n"))
        self.assertIsNone(sv.get("flag", dict))

    def test_an_empty_or_blank_string_is_not_set(self):
        self.write(json.dumps({"a": "", "b": "  \n"}))
        self.assertIsNone(sv.get("a"))
        self.assertIsNone(sv.get("b"))

    def test_objects_and_lists_by_kind(self):
        self.write(json.dumps({"m": {"x": [1]}, "l": ["a"]}))
        self.assertEqual(sv.get("m", dict), {"x": [1]})
        self.assertEqual(sv.get("l", list), ["a"])

    def test_values_can_be_handed_in(self):
        self.assertEqual(sv.get("a.b", values={"a": {"b": "c"}}), "c")

    def test_require_names_the_key(self):
        self.write("{}")
        with self.assertRaises(sv.Missing) as caught:
            sv.require("vault.root")
        self.assertEqual(str(caught.exception),
                         f"set `vault.root` in `{self.file}`")
        self.assertEqual(caught.exception.key, "vault.root")

    def test_require_returns_a_value_that_is_set(self):
        self.write(json.dumps({"vault": {"root": "/v"}}))
        self.assertEqual(sv.require("vault.root"), "/v")

    def test_a_huge_file_reads(self):
        self.write(json.dumps({"k": "x" * 2_000_000}))
        self.assertEqual(len(sv.get("k")), 2_000_000)


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "skill_values.py"
FULL = {"user": {"name": "Alice"}, "vault": {"root": "/notes", "commit": "vault-commit"},
        "memory": {"domains": {"homelab": ["docker"]}}}


class Render(unittest.TestCase):
    """`skill_values.py render`, the first line of SKILL.md: one line per
    key of TEXT_KEYS, or the sentence that says which key to set where."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.file = Path(tmp.name) / "config.json"

    def render(self) -> list[str]:
        env = {k: v for k, v in os.environ.items() if k != "AI_MEMORY_CONFIG"}
        env["AI_MEMORY_CONFIG"] = str(self.file)
        done = subprocess.run([sys.executable, "-B", str(SCRIPT), "render"],
                              capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual((done.returncode, done.stderr), (0, ""))
        return done.stdout.splitlines()

    def stop(self, key: str) -> str:
        return f"**Stop.** Set `{key}` in `{self.file}` before you use this skill."

    def commit_off(self) -> str:
        step, without = sv.STEPS["vault.commit"]
        return f"**Step {step} is off** until `vault.commit` is set in `{self.file}`: {without}"

    def test_the_text_keys(self):
        self.assertEqual(sv.TEXT_KEYS, [("user.name", str), ("vault.root", str),
                                        ("vault.commit", str)])

    def test_a_full_file(self):
        self.file.write_text(json.dumps(FULL), encoding="utf-8")
        self.assertEqual(self.render(), ["## Values", "", "- `user.name`: Alice",
                                         "- `vault.root`: /notes",
                                         "- `vault.commit`: vault-commit"])

    def test_a_missing_key(self):
        self.file.write_text(json.dumps({"user": {"name": "Alice"},
                                         "vault": {"commit": "vault-commit"}}), encoding="utf-8")
        self.assertEqual(self.render(), ["## Values", "", "- `user.name`: Alice",
                                         self.stop("vault.root"),
                                         "- `vault.commit`: vault-commit"])

    def test_a_mistyped_key_is_missing(self):
        self.file.write_text(json.dumps({**FULL, "vault": {"root": ["/notes"]}}), encoding="utf-8")
        self.assertEqual(self.render()[3], self.stop("vault.root"))

    def test_the_name_never_stops_the_skill(self):
        self.assertEqual(sv.OPTIONAL, {"user.name"})
        for name in (None, "", ["Alice"]):
            with self.subTest(name=name):
                user = {} if name is None else {"name": name}
                self.file.write_text(json.dumps({**FULL, "user": user}), encoding="utf-8")
                self.assertEqual(self.render(), ["## Values", "", "- `vault.root`: /notes",
                                                 "- `vault.commit`: vault-commit"])

    def test_commit_off_means_uncommitted_never_git_commit(self):
        step, without = sv.STEPS["vault.commit"]
        self.assertEqual(step, "Commit")
        self.assertEqual(without, "leave the note uncommitted and say so; "
                                  "never commit it with `git commit`.")

    def test_a_step_key_stops_its_step_only(self):
        self.file.write_text(json.dumps({"user": {"name": "Alice"},
                                         "vault": {"root": "/notes"}}), encoding="utf-8")
        self.assertEqual(self.render(), ["## Values", "", "- `user.name`: Alice",
                                         "- `vault.root`: /notes", self.commit_off()])

    def assertAllMissing(self) -> None:
        self.assertEqual(self.render(), ["## Values", "", self.stop("vault.root"),
                                         self.commit_off()])

    def test_a_missing_file(self):
        self.assertAllMissing()

    def test_an_empty_file(self):
        self.file.write_text("", encoding="utf-8")
        self.assertAllMissing()

    def test_a_malformed_file(self):
        self.file.write_text("{not json", encoding="utf-8")
        self.assertAllMissing()

    def test_a_list_or_object_is_compact_json(self):
        self.assertEqual(sv.show({"homelab": ["docker", "caddy"]}),
                         '{"homelab":["docker","caddy"]}')
        self.assertEqual(sv.show(["a", "b"]), '["a","b"]')

    def test_a_string_runs_onto_one_line(self):
        self.assertEqual(sv.show("two\n  lines"), "two lines")

    def test_an_unknown_command_is_a_usage_error(self):
        done = subprocess.run([sys.executable, "-B", str(SCRIPT), "paint"],
                              capture_output=True, text=True, timeout=30)
        self.assertEqual(done.returncode, 2)
        self.assertIn("usage:", done.stderr)


if __name__ == "__main__":
    unittest.main()
