from __future__ import annotations

import unittest
from pathlib import Path


PLAN_SKILL_ROOT = Path(__file__).resolve().parents[1]


class SkillDocsTests(unittest.TestCase):
    def test_skill_routes_detailed_completion_rules_to_reference(self) -> None:
        skill = (PLAN_SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        reference = PLAN_SKILL_ROOT / "references" / "status-and-completion.md"
        abstraction_reference = PLAN_SKILL_ROOT / "references" / "abstraction-quality.md"

        self.assertTrue(reference.is_file())
        self.assertIn("references/status-and-completion.md", skill)
        self.assertNotIn("## Standing Completion Bar", skill)
        self.assertLessEqual(len(skill.splitlines()), 290)

        details = reference.read_text(encoding="utf-8")
        self.assertIn("# Status And Completion Contract", details)
        self.assertIn("## Status Transitions", details)
        self.assertIn("## Completion Bar", details)
        self.assertTrue(abstraction_reference.is_file())
        self.assertIn("references/abstraction-quality.md", skill)

        abstraction = abstraction_reference.read_text(encoding="utf-8")
        self.assertIn("# Abstraction Quality Gate", abstraction)
        self.assertIn("## Gate Fields", abstraction)
        self.assertIn("Concept count / indirection", abstraction)


if __name__ == "__main__":
    unittest.main()
