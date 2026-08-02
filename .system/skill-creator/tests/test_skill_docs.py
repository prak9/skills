from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


class SkillDocsTests(unittest.TestCase):
    def test_skill_routes_eval_work_to_progressive_references(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertLessEqual(len(skill.splitlines()), 500)
        self.assertIn("references/evaluation.md", skill)
        self.assertIn("references/grading.md", skill)
        self.assertIn("scripts/validate_evals.py", skill)
        self.assertIn("scripts/aggregate_evals.py", skill)
        self.assertNotIn("claude -p", skill)

    def test_eval_resources_exist_and_use_one_coherent_layout(self) -> None:
        evaluation = SKILL_ROOT / "references" / "evaluation.md"
        grading = SKILL_ROOT / "references" / "grading.md"

        self.assertTrue(evaluation.is_file())
        self.assertTrue(grading.is_file())
        evaluation_text = evaluation.read_text(encoding="utf-8")
        self.assertIn("candidate/run-1", evaluation_text)
        self.assertIn("baseline/run-1", evaluation_text)
        self.assertIn("contract/evals/evals.json", evaluation_text)
        self.assertNotIn("without_skill", evaluation_text)
        self.assertNotIn("with_skill", evaluation_text)

    def test_ui_metadata_mentions_evaluation(self) -> None:
        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )

        self.assertIn("Create and evaluate Codex skills", metadata)


if __name__ == "__main__":
    unittest.main()
