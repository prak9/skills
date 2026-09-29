"""Narrow portability checks for live instructions, not a comprehensive secret scan."""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SkillHygieneTests(unittest.TestCase):
    def test_live_instructions_and_scripts_do_not_embed_personal_home_paths(self):
        private_home = re.compile(r"/(?:home|Users)/[A-Za-z0-9_.-]+/")
        violations = []
        for skill in ROOT.iterdir():
            if skill.name.startswith(".") or not (skill / "SKILL.md").is_file():
                continue
            for path in skill.rglob("*"):
                if path.suffix not in {".md", ".py"} or not path.is_file():
                    continue
                if {"tests", "evals", "examples"}.intersection(path.relative_to(skill).parts):
                    continue
                if private_home.search(path.read_text(encoding="utf-8")):
                    violations.append(str(path.relative_to(ROOT)))
        self.assertEqual([], violations, "Use explicit project configuration or /path/to examples")


if __name__ == "__main__":
    unittest.main()
