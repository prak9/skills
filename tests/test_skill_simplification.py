"""Structural regression guards; these do not measure agent behavior or quality."""

import hashlib
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SkillSimplificationTests(unittest.TestCase):
    def test_retired_entries_leave_reusable_evaluation_assets(self):
        for name in ("iterate", "eli5"):
            with self.subTest(skill=name):
                self.assertFalse((ROOT / name / "SKILL.md").exists())
                self.assertFalse((ROOT / name / "agents/openai.yaml").exists())
                self.assertTrue((ROOT / name / "evals").is_dir())
        self.assertTrue((ROOT / "iterate/evals/fixtures/pipeline/pipeline.py").is_file())
        self.assertTrue((ROOT / "iterate/evals/archived-instruction.md").is_file())

    def test_specialist_research_methods_remain_resolvable(self):
        for relative in (
            "scripts/run_experiment.py",
            "scripts/validate_research.py",
            "references/prediction-validation.md",
            "references/quant-strategy-iteration.md",
            "references/ablation-design.md",
            "references/instruction-migration.md",
        ):
            with self.subTest(path=relative):
                self.assertTrue((ROOT / "research-craft" / relative).is_file())

    def test_retired_iteration_snapshot_is_frozen(self):
        snapshot = ROOT / "iterate/evals/archived-instruction.md"
        self.assertEqual(
            "c860e28c9e9339c6a6c74ddc6f096ccb7909de648d8e23a34448b2c3ccd08518",
            hashlib.sha256(snapshot.read_bytes()).hexdigest(),
        )

    def test_invest_has_only_one_cross_skill_link(self):
        import re

        text = (ROOT / "invest/SKILL.md").read_text()
        targets = re.findall(r"\]\((\.\./[^)]+/SKILL\.md)\)", text)
        self.assertEqual(["../writing/SKILL.md"], targets)

    def test_default_invest_path_does_not_read_heuristic_models(self):
        text = (ROOT / "invest/references/mode-a-buy-side.md").read_text()
        self.assertNotIn("mode-c-gf-dma.md", text)
        self.assertNotIn("mode-e-tam-adj-peg.md", text)
        self.assertIn("business-quality.md", text)
        self.assertIn("mode-b-bayesian-growth.md", text)
        self.assertIn("underwriting-loop.md", text)

    def test_default_lite_does_not_require_cleanup_metadata(self):
        text = (ROOT / "plan-skill/assets/program-lite.template.md").read_text()
        self.assertNotIn("Clean state:", text)
        self.assertNotIn("Last clean:", text)
        self.assertIn("Contract status:", text)
        self.assertIn("## Acceptance", text)


if __name__ == "__main__":
    unittest.main()
