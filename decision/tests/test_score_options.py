from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "score_options.py"


class ScoreOptionsTests(unittest.TestCase):
    def run_cli(self, data: dict) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            input_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-B", str(SCRIPT), str(input_path)],
                check=False, capture_output=True, text=True,
            )

    def run_score(self, data: dict) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            input_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            process = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), str(input_path), "--format", "json"],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(0, process.returncode, process.stderr)
        return json.loads(process.stdout)

    @staticmethod
    def base_input() -> dict:
        return {
            "criteria": [{"name": "交付价值", "weight": 100}],
            "options": [
                {
                    "name": "方案A",
                    "scores": {"交付价值": 5},
                    "vetoes": [
                        {
                            "name": "超过工期硬约束",
                            "triggered": True,
                            "detail": "预计 12 周，硬上限 8 周",
                        }
                    ],
                },
                {
                    "name": "方案B",
                    "scores": {"交付价值": 4},
                    "vetoes": [
                        {"name": "超过工期硬约束", "triggered": False}
                    ],
                },
            ],
            "vetoes": [],
        }

    def test_option_veto_does_not_exclude_feasible_alternative(self) -> None:
        result = self.run_score(self.base_input())
        options = {item["option"]: item for item in result["results"]}

        self.assertFalse(result["global_vetoed"])
        self.assertFalse(options["方案A"]["feasible"])
        self.assertIsNone(options["方案A"]["rank"])
        self.assertEqual("超过工期硬约束", options["方案A"]["triggered_vetoes"][0]["name"])
        self.assertTrue(options["方案B"]["feasible"])
        self.assertEqual(1, options["方案B"]["rank"])
        self.assertNotIn("硬性否决", options["方案B"]["recommendation"])

    def test_global_veto_excludes_every_option(self) -> None:
        data = self.base_input()
        data["vetoes"] = [{"name": "决策本身违法", "triggered": True}]

        result = self.run_score(data)

        self.assertTrue(result["global_vetoed"])
        self.assertTrue(all(not item["feasible"] for item in result["results"]))
        self.assertTrue(all(item["rank"] is None for item in result["results"]))

    def test_v2_unknown_score_is_null_with_unrenormalized_range(self) -> None:
        data = {
            "schema_version": 2,
            "criteria": [
                {"name": "交付价值", "weight": 60},
                {"name": "维护成本", "weight": 40},
            ],
            "options": [
                {
                    "name": "方案A",
                    "scores": {"交付价值": 5, "维护成本": 5},
                    "vetoes": [{"name": "超过工期", "triggered": True}],
                },
                {
                    "name": "方案B",
                    "scores": {"交付价值": 4, "维护成本": None},
                    "vetoes": [{"name": "超过工期", "triggered": False}],
                    "validation_actions": [
                        {
                            "criterion": "维护成本",
                            "action": "委托一周完整成本审计",
                            "cost": 8,
                            "cost_unit": "小时",
                            "could_change_decision": True,
                        },
                        {
                            "criterion": "维护成本",
                            "action": "做两小时运维演练并记录人时",
                            "cost": 2,
                            "cost_unit": "小时",
                            "could_change_decision": True,
                        }
                    ],
                },
            ],
            "vetoes": [],
        }

        result = self.run_score(data)
        options = {item["option"]: item for item in result["results"]}

        self.assertEqual(2, result["schema_version"])
        self.assertEqual("ineligible", options["方案A"]["eligibility"])
        self.assertEqual("eligible", options["方案B"]["eligibility"])
        self.assertIsNone(options["方案B"]["total_score"])
        self.assertEqual({"min": 56.0, "max": 88.0}, options["方案B"]["score_range"])
        self.assertEqual(["维护成本"], options["方案B"]["missing_scores"])
        self.assertEqual(
            "做两小时运维演练并记录人时",
            result["next_validation_action"]["action"],
        )

    def test_v2_unknown_veto_makes_only_that_option_unresolved(self) -> None:
        data = {
            "schema_version": 2,
            "criteria": [{"name": "价值", "weight": 100}],
            "options": [
                {
                    "name": "A",
                    "scores": {"价值": 5},
                    "vetoes": [{"name": "合规审批", "triggered": None}],
                },
                {"name": "B", "scores": {"价值": 4}, "vetoes": []},
            ],
            "vetoes": [],
        }

        result = self.run_score(data)
        options = {item["option"]: item for item in result["results"]}

        self.assertEqual("unresolved", options["A"]["eligibility"])
        self.assertIsNone(options["A"]["feasible"])
        self.assertEqual("eligible", options["B"]["eligibility"])
        self.assertTrue(options["B"]["feasible"])

    def test_v2_reports_preference_flip_under_grounded_scenario(self) -> None:
        data = {
            "schema_version": 2,
            "criteria": [
                {"name": "交付价值", "weight": 60},
                {"name": "维护便利", "weight": 40},
            ],
            "options": [
                {"name": "A", "scores": {"交付价值": 5, "维护便利": 2}},
                {"name": "B", "scores": {"交付价值": 4, "维护便利": 5}},
            ],
            "scenarios": [
                {
                    "name": "交付价值优先",
                    "basis": "产品负责人确认首发窗口失约成本显著高于维护成本",
                    "weights": {"交付价值": 90, "维护便利": 10},
                }
            ],
        }

        result = self.run_score(data)

        self.assertEqual("B", result["comparison"]["preferred_option"])
        self.assertFalse(result["stability"]["stable_under_tested_scenarios"])
        self.assertEqual(
            {"scenario": "交付价值优先", "from": "B", "to": "A"},
            result["stability"]["preference_flips"][0],
        )

    def test_v1_rejects_null_scores_instead_of_treating_them_as_three(self) -> None:
        data = self.base_input()
        data["options"][0]["scores"]["交付价值"] = None
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "input.json"
            input_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            process = subprocess.run(
                [sys.executable, "-B", str(SCRIPT), str(input_path), "--format", "json"],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(2, process.returncode)
        self.assertIn("must be numeric", process.stderr)

    def test_markdown_reports_all_stability_states_and_scenario_basis(self) -> None:
        for score, expected in ((None, "无法判定"), (5, "保持首选"), (2, "首选从 A 变为 B")):
            with self.subTest(score=score):
                data = {
                    "schema_version": 2,
                    "criteria": [{"name": "价值", "weight": 100}],
                    "options": [
                        {"name": "A", "scores": {"价值": 5}},
                        {"name": "B", "scores": {"价值": 4}},
                    ],
                    "scenarios": [{
                        "name": "供应商成本变化", "basis": "已收到供应商报价范围",
                        "score_overrides": {"A": {"价值": score}},
                    }],
                }
                process = self.run_cli(data)
                self.assertEqual(0, process.returncode, process.stderr)
                self.assertIn(expected, process.stdout)
                self.assertIn("供应商成本变化", process.stdout)
                self.assertIn("已收到供应商报价范围", process.stdout)
                if score is None:
                    self.assertIn("unresolved_score_ranges", process.stdout)
                    self.assertNotIn("未发现首选翻转", process.stdout)
                data["scenarios"] = []
                self.assertIn("稳定性未测试", self.run_cli(data).stdout)

    def test_missing_veto_triggered_fails_validation_without_traceback(self) -> None:
        for scope in ("global", "option"):
            with self.subTest(scope=scope):
                data = self.base_input()
                data["schema_version"] = 2
                target = data if scope == "global" else data["options"][0]
                target["vetoes"] = [{"name": "审批状态"}]
                process = self.run_cli(data)
                self.assertEqual(2, process.returncode)
                self.assertIn("triggered", process.stderr)
                self.assertNotIn("Traceback", process.stderr)


if __name__ == "__main__":
    unittest.main()
