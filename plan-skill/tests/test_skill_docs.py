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
        preference_reference = PLAN_SKILL_ROOT / "references" / "preference-contract.md"
        unknowns_reference = PLAN_SKILL_ROOT / "references" / "unknowns-contract.md"
        reflection_reference = PLAN_SKILL_ROOT / "references" / "reflection-contract.md"
        foundation_reference = PLAN_SKILL_ROOT / "references" / "foundation-contract.md"
        loop_reference = PLAN_SKILL_ROOT / "references" / "loop-contract.md"
        clean_reference = PLAN_SKILL_ROOT / "references" / "clean-contract.md"
        agent_config = (PLAN_SKILL_ROOT / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )

        self.assertTrue(reference.is_file())
        self.assertIn("references/status-and-completion.md", skill)
        self.assertIn("references/pre-execution-grill.md", skill)
        self.assertIn("references/preference-contract.md", skill)
        self.assertIn("references/unknowns-contract.md", skill)
        self.assertIn("references/reflection-contract.md", skill)
        self.assertIn("references/foundation-contract.md", skill)
        self.assertIn("references/abstraction-quality.md", skill)
        self.assertIn("references/loop-contract.md", skill)
        self.assertIn("references/clean-contract.md", skill)
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

        self.assertTrue(preference_reference.is_file())
        preference = preference_reference.read_text(encoding="utf-8")
        self.assertIn("# Preference And Tradeoff Contract", preference)
        self.assertIn("## Find The Crux", preference)
        self.assertIn("Strategic", preference)
        self.assertIn("Tactical", preference)
        self.assertIn("Declarative", preference)
        self.assertIn("Imperative", preference)

        self.assertTrue(unknowns_reference.is_file())
        unknowns = unknowns_reference.read_text(encoding="utf-8")
        self.assertIn("# Unknowns Discovery Contract", unknowns)
        self.assertIn("Known knowns", unknowns)
        self.assertIn("Known unknowns", unknowns)
        self.assertIn("Unknown knowns", unknowns)
        self.assertIn("Unknown unknowns", unknowns)
        self.assertIn("blind-spot pass", unknowns)
        self.assertIn("implementation-notes.md", unknowns)

        self.assertTrue(reflection_reference.is_file())
        reflection = reflection_reference.read_text(encoding="utf-8")
        self.assertIn("# Node Reflection Contract", reflection)
        self.assertIn("## Close Every Node", reflection)
        self.assertIn("Wrong / changed", reflection)
        self.assertIn("Right / preserve", reflection)
        self.assertIn("hidden chain-of-thought", reflection)

        self.assertTrue(foundation_reference.is_file())
        foundation = foundation_reference.read_text(encoding="utf-8")
        self.assertIn("# Foundation Engineering Contract", foundation)
        self.assertIn("Intent / setpoint", foundation)
        self.assertIn("Verification must be finer than the change", foundation)
        self.assertIn("maker's narrative", foundation)
        self.assertIn("judgment coverage map", foundation)
        self.assertIn("Comprehension Debt", foundation)

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
        self.assertIn("Checker / independence", loop)
        self.assertIn("Sensor stack / evidence path", loop)
        self.assertIn("Granularity alignment", loop)
        self.assertIn("Evaluator version / calibration", loop)
        self.assertIn("Current Loop Attempt", loop)

        self.assertTrue(clean_reference.is_file())
        clean = clean_reference.read_text(encoding="utf-8")
        self.assertIn("# Clean Contract", clean)
        self.assertIn("## Triggers", clean)
        self.assertIn("## Preserve And Retire", clean)
        self.assertIn("## Completion Bar", clean)

    def test_default_context_surfaces_have_explicit_budgets(self) -> None:
        skill = (PLAN_SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        lite = (PLAN_SKILL_ROOT / "assets" / "program-lite.template.md").read_text(
            encoding="utf-8"
        )
        full = (
            PLAN_SKILL_ROOT / "assets" / "program-full-starter.template.md"
        ).read_text(encoding="utf-8")
        task = (
            PLAN_SKILL_ROOT / "assets" / "task-full-starter.template.md"
        ).read_text(encoding="utf-8")
        memory = (
            PLAN_SKILL_ROOT / "assets" / "memory-starter.template.md"
        ).read_text(encoding="utf-8")
        markdown = "\n".join(
            path.read_text(encoding="utf-8")
            for path in PLAN_SKILL_ROOT.rglob("*.md")
        )

        self.assertLessEqual(len(skill.splitlines()), 130)
        self.assertLessEqual(len(lite.splitlines()), 52)
        for text in (lite, full):
            self.assertIn("Strategic defaults", text)
            self.assertIn("Tactical objective", text)
            self.assertIn("Imperative bounds", text)
            self.assertIn("Negotiable space", text)
            self.assertIn("Active unknowns", text)
            self.assertIn("Escalate when", text)
        self.assertIn("Preference refs / tactical overrides", task)
        self.assertIn("Discovered unknowns / deviations", task)
        self.assertIn("## Reflection Log", lite)
        self.assertIn("| Node | Status | Action | Verification | Evidence | Reflection |", lite)
        self.assertIn("| Node | Status | Action | Verification | Evidence | Reflection |", task)
        self.assertIn("## Reflections", memory)
        self.assertIn("Wrong / changed", memory)
        self.assertIn("Right / preserve", memory)
        self.assertIn("Store trajectory events", memory)
        self.assertLessEqual(len(memory.splitlines()), 32)
        self.assertLessEqual(markdown.count("tasks/output/"), 35)

    def test_only_current_template_contracts_remain(self) -> None:
        assets = PLAN_SKILL_ROOT / "assets"
        templates = {path.name for path in assets.glob("*.template.md")}

        self.assertEqual(
            {
                "program-lite.template.md",
                "program-full-starter.template.md",
                "task-full-starter.template.md",
                "memory-starter.template.md",
            },
            templates,
        )


if __name__ == "__main__":
    unittest.main()
