from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "check_semantic_fidelity.py"


class SemanticFidelityTests(unittest.TestCase):
    def run_check(self, source: str, revision: str, *extra: str) -> dict:
        process = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--source", source, "--revision", revision, *extra],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, process.returncode, process.stderr)
        return json.loads(process.stdout)

    def test_flags_modality_and_causal_strengthening(self) -> None:
        result = self.run_check("试点结果提示可能改善。", "试点结果已证明有效。")

        self.assertEqual("review_required", result["status"])
        categories = {item["category"] for item in result["findings"]}
        self.assertIn("modality", categories)
        self.assertIn("causal_strength", categories)

    def test_flags_negation_and_number_changes(self) -> None:
        result = self.run_check("收入未下降，样本为 120 家。", "收入下降，样本为 100 家。")

        categories = {item["category"] for item in result["findings"]}
        self.assertIn("negation", categories)
        self.assertIn("numbers", categories)

    def test_flags_causal_weakening_as_semantic_change(self) -> None:
        result = self.run_check("随机试验证明干预导致改善。", "结果与改善相关。")

        categories = {item["category"] for item in result["findings"]}
        self.assertIn("causal_strength", categories)

    def test_protected_subject_and_attribution_must_survive(self) -> None:
        result = self.run_check(
            "根据审计委员会报告，项目可能延期。",
            "项目可能延期。",
            "--protected-term",
            "审计委员会",
        )

        categories = {item["category"] for item in result["findings"]}
        self.assertIn("protected_terms", categories)
        self.assertIn("attribution", categories)

    def test_unchanged_meaning_markers_pass(self) -> None:
        result = self.run_check(
            "若需求不变，收入可能增长约 10%。",
            "若需求保持不变，收入可能增长约 10%。",
        )

        self.assertEqual("pass", result["status"])
        self.assertEqual([], result["findings"])


if __name__ == "__main__":
    unittest.main()
