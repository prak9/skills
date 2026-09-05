from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tests" / "evaluate_behavior_cases.py"
SKILLS = ("decision", "writing", "invest", "plan-skill")


class BehaviorCaseEvaluatorTests(unittest.TestCase):
    def load_cases(self) -> list[dict]:
        cases = []
        for skill in SKILLS:
            path = ROOT / skill / "evals" / "behavior-cases.jsonl"
            cases.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines())
        return cases

    def passing_results(self) -> list[dict]:
        results = []
        for case in self.load_cases():
            required_tools = [f"{prefix}write" for prefix in case.get("required_tool_prefixes", [])]
            results.append(
                {
                    "id": case["id"],
                    "output": "；".join(case.get("must_include", [])),
                    "tool_calls": required_tools,
                    "metrics": {
                        "reference_reads": 0,
                        "followup_questions": 0,
                        "external_mutations": len(required_tools),
                        "operations": len(required_tools),
                    },
                    "behavior_pass": True,
                    "behavior_evidence": "independent evaluator confirmed the expected behavior",
                }
            )
        return results

    def run_evaluator(self, results: list[dict], split: str = "all") -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.jsonl"
            path.write_text(
                "\n".join(json.dumps(item, ensure_ascii=False) for item in results) + "\n",
                encoding="utf-8",
            )
            return subprocess.run(
                [sys.executable, "-B", str(SCRIPT), str(path), "--split", split],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

    def test_complete_results_pass_all_24_cases(self) -> None:
        process = self.run_evaluator(self.passing_results())

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual(24, result["summary"]["passed"])
        self.assertEqual(0, result["summary"]["failed"])

    def test_acceptance_split_requires_all_eight_holdouts(self) -> None:
        results = [item for item in self.passing_results() if "holdout" in item["id"]]
        process = self.run_evaluator(results, split="acceptance")

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        self.assertEqual(8, json.loads(process.stdout)["summary"]["passed"])

    def test_missing_required_content_fails_case(self) -> None:
        results = self.passing_results()
        results[0]["output"] = ""
        process = self.run_evaluator(results)

        self.assertEqual(1, process.returncode)
        report = json.loads(process.stdout)
        self.assertGreater(report["summary"]["failed"], 0)
        self.assertIn("missing required output", report["cases"][0]["failures"][0])

    def test_cost_limit_requires_recorded_operation_count(self) -> None:
        results = self.passing_results()
        results[0]["metrics"]["operations"] = 99
        process = self.run_evaluator(results)

        self.assertEqual(1, process.returncode)
        report = json.loads(process.stdout)
        self.assertTrue(any("operations" in failure for failure in report["cases"][0]["failures"]))


if __name__ == "__main__":
    unittest.main()
