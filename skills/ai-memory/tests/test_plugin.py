"""The plugin around the skill: the hooks it registers and the first line
of SKILL.md, which renders the Values block when the skill loads."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
PLUGIN = SKILL.parents[1]
ADAPTER = re.compile(
    r'^python3 -B "\$\{CLAUDE_PLUGIN_ROOT\}/(skills/ai-memory/adapters/claude/[a-z]+\.py)" \|\| true$')


class Hooks(unittest.TestCase):
    def test_each_event_runs_its_adapter_once(self):
        hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
        expected = {"SessionStart": "sessionstart.py", "UserPromptSubmit": "userpromptsubmit.py",
                    "PostToolUseFailure": "posttoolfailure.py"}
        self.assertEqual(set(hooks), set(expected))
        for event, script in expected.items():
            with self.subTest(event=event):
                [group] = hooks[event]
                [hook] = group["hooks"]
                match = ADAPTER.match(hook["command"])
                self.assertIsNotNone(match, hook["command"])
                self.assertEqual(Path(match[1]).name, script)
                self.assertTrue((PLUGIN / match[1]).is_file())
                self.assertEqual(hook["timeout"], 5)


class SkillText(unittest.TestCase):
    def setUp(self):
        self.text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    def test_the_first_line_after_the_title_renders_the_values(self):
        body = self.text.split("\n# ai-memory\n", 1)[1]
        first = next(line for line in body.splitlines() if line.strip())
        self.assertEqual(first, '!`python3 -B "${CLAUDE_SKILL_DIR}/scripts/skill_values.py" render`')

    def test_no_placeholder_is_left(self):
        self.assertNotIn("{" * 2, self.text)

    def test_the_description_names_no_path(self):
        front = self.text.split("---", 2)[1]
        self.assertNotRegex(front, r"~/|/home/|\$HOME")
