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

    def test_flags_english_negation_modality_and_conditions(self) -> None:
        for source, revision, expected in (
            ("The treatment may help and is not proven effective.", "The treatment is proven effective.", {"negation", "modality"}),
            ("Only if demand holds, we might expand.", "We will expand.", {"conditions", "modality"}),
            ("It does NOT work unless powered.", "It works.", {"negation", "conditions"}),
            ("It isn't ready and can’t run.", "It is ready and can run.", {"negation"}),
        ):
            with self.subTest(source=source):
                result = self.run_check(source, revision)
                self.assertEqual("review_required", result["status"])
                self.assertLessEqual(expected, {item["category"] for item in result["findings"]})

    def test_english_marker_matching_respects_word_boundaries(self) -> None:
        result = self.run_check("The notification differs.", "The notice differs.")
        self.assertEqual([], result["findings"])

    def test_unsupported_and_cross_language_inputs_are_not_a_pass(self) -> None:
        for source, revision in (
            ("Лечение помогает.", "Лечение эффективно."),
            ("Le traitement est efficace.", "Le traitement fonctionne."),
            ("疗法可能有效。", "The treatment may help."),
            ("API 可能失效。", "API 可能失效。"),
            ("试验 may help and is not proven effective.", "试验 is proven effective."),
            ("", ""),
        ):
            with self.subTest(source=source):
                result = self.run_check(source, revision)
                self.assertEqual("not_evaluated", result["status"])
                self.assertEqual("not_evaluated", result["coverage"]["marker_comparison"]["status"])

    def test_explicit_english_language_reports_partial_coverage(self) -> None:
        result = self.run_check(
            "The pilot may help.", "The pilot may help.",
            "--source-language", "en", "--revision-language", "en",
        )
        self.assertEqual("pass", result["status"])
        self.assertEqual(["negation", "conditions", "modality"], result["coverage"]["marker_comparison"]["evaluated"])
        self.assertIn("causal_strength", result["coverage"]["marker_comparison"]["not_evaluated"])
        self.assertIn("attribution", result["coverage"]["marker_comparison"]["not_evaluated"])

    def test_cross_language_still_reports_changed_numbers(self) -> None:
        result = self.run_check("样本 120 家。", "A sample of 100 firms.")
        self.assertEqual("review_required", result["status"])
        self.assertEqual(["numbers"], [item["category"] for item in result["findings"]])
        self.assertEqual("not_evaluated", result["coverage"]["marker_comparison"]["status"])


if __name__ == "__main__":
    unittest.main()
