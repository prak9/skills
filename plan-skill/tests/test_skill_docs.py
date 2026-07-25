from __future__ import annotations

import unittest
from pathlib import Path


PLAN_SKILL_ROOT = Path(__file__).resolve().parents[1]


class SkillDocsTests(unittest.TestCase):
    def test_skill_is_a_compact_router_with_progressive_disclosure(self) -> None:
        skill = (PLAN_SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        reference = PLAN_SKILL_ROOT / "references" / "status-and-completion.md"
        abstraction_reference = PLAN_SKILL_ROOT / "references" / "abstraction-quality.md"
        readiness_reference = PLAN_SKILL_ROOT / "references" / "pre-execution-grill.md"
        loop_reference = PLAN_SKILL_ROOT / "references" / "loop-contract.md"
        agent_config = (PLAN_SKILL_ROOT / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )

        self.assertTrue(reference.is_file())
        self.assertIn("references/status-and-completion.md", skill)
        self.assertIn("references/pre-execution-grill.md", skill)
        self.assertIn("references/abstraction-quality.md", skill)
        self.assertIn("references/loop-contract.md", skill)
        self.assertNotIn("### Size Work", skill)
        self.assertNotIn("## Memory Discipline", skill)
        self.assertLessEqual(len(skill.splitlines()), 130)
        self.assertIn("lightest", agent_config.lower())

        details = reference.read_text(encoding="utf-8")
        self.assertIn("# Status And Completion Contract", details)
        self.assertIn("## Status Transitions", details)
        self.assertIn("## Completion Bar", details)
        self.assertTrue(abstraction_reference.is_file())
        self.assertIn("references/abstraction-quality.md", skill)
        self.assertTrue(readiness_reference.is_file())
        self.assertIn("references/pre-execution-grill.md", skill)

        abstraction = abstraction_reference.read_text(encoding="utf-8")
        self.assertIn("# Abstraction Quality Gate", abstraction)
        self.assertIn("## Gate Fields", abstraction)
        self.assertIn("Concept count / indirection", abstraction)

        readiness = readiness_reference.read_text(encoding="utf-8")
        self.assertIn("# Pre-Execution Grill And Readiness Gate", readiness)
        self.assertIn("## Run The Grill", readiness)
        self.assertIn("False-positive loop", readiness)

        loop = loop_reference.read_text(encoding="utf-8")
        self.assertIn("# Loop Contract", loop)
        self.assertIn("Max iterations", loop)
        self.assertIn("Current Loop Attempt", loop)

    def test_default_context_surfaces_have_explicit_budgets(self) -> None:
        skill = (PLAN_SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        lite = (PLAN_SKILL_ROOT / "assets" / "program-lite.template.md").read_text(
            encoding="utf-8"
        )
        markdown = "\n".join(
            path.read_text(encoding="utf-8")
            for path in PLAN_SKILL_ROOT.rglob("*.md")
        )

        self.assertLessEqual(len(skill.splitlines()), 130)
        self.assertLessEqual(len(lite.splitlines()), 45)
        self.assertLessEqual(markdown.count("tasks/output/"), 35)


if __name__ == "__main__":
    unittest.main()
