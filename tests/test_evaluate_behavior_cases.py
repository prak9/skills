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
RUN_CONTEXT = {
    "model": "test-model",
    "reasoning_effort": "test-effort",
    "harness": "test-harness",
    "instruction_revision": "test-instructions",
    "skill_revision": "test-skills",
    "case_set_version": "core-v1",
    "run_at": "2026-09-05T00:00:00Z",
    "evaluator": "test-evaluator",
}


class BehaviorCaseEvaluatorTests(unittest.TestCase):
    def load_cases(self, suite: str = "core") -> list[dict]:
        cases = []
        if suite in ("core", "all"):
            for skill in SKILLS:
                path = ROOT / skill / "evals" / "behavior-cases.jsonl"
                cases.extend(
                    json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
                )
        if suite in ("instruction-migration", "all"):
            path = ROOT / "tests" / "instruction-migration-cases.jsonl"
            cases.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines())
        return cases

    def passing_results(self, suite: str = "core") -> list[dict]:
        results = []
        for case in self.load_cases(suite):
            required_tools = [f"{prefix}write" for prefix in case.get("required_tool_prefixes", [])]
            required_skills = case.get("required_skills")
            if required_skills is None and case.get("skill") in SKILLS:
                required_skills = [case["skill"]]
            results.append(
                {
                    "schema_version": 2,
                    "id": case["id"],
                    "run_context": {
                        **RUN_CONTEXT,
                        "case_set_version": (
                            "instruction-migration-v1"
                            if suite == "instruction-migration"
                            else "all-v1" if suite == "all" else "core-v1"
                        ),
                    },
                    "output": "；".join(case.get("must_include", [])),
                    "skills_loaded": required_skills or [],
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

    def run_evaluator(
        self,
        results: list[dict],
        split: str = "all",
        suite: str = "core",
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.jsonl"
            path.write_text(
                "\n".join(json.dumps(item, ensure_ascii=False) for item in results) + "\n",
                encoding="utf-8",
            )
            return subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT),
                    str(path),
                    "--split",
                    split,
                    "--suite",
                    suite,
                ],
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

    def test_instruction_migration_suite_passes_all_eight_cases(self) -> None:
        process = self.run_evaluator(
            self.passing_results("instruction-migration"),
            suite="instruction-migration",
        )

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual("instruction-migration", result["suite"])
        self.assertEqual(8, result["summary"]["passed"])

    def test_all_suite_passes_all_32_cases(self) -> None:
        process = self.run_evaluator(self.passing_results("all"), suite="all")

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        self.assertEqual(32, json.loads(process.stdout)["summary"]["passed"])

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

    def test_missing_run_context_fails_case(self) -> None:
        results = self.passing_results()
        del results[0]["run_context"]
        process = self.run_evaluator(results)

        self.assertEqual(1, process.returncode)
        report = json.loads(process.stdout)
        self.assertIn("run_context must be an object", report["cases"][0]["failures"])

    def test_forbidden_skill_activation_fails_case(self) -> None:
        results = self.passing_results("instruction-migration")
        results[0]["skills_loaded"].append("decision")
        process = self.run_evaluator(results, suite="instruction-migration")

        self.assertEqual(1, process.returncode)
        report = json.loads(process.stdout)
        self.assertIn("forbidden skill observed: decision", report["cases"][0]["failures"])

    def test_mixed_model_contexts_fail_the_outlying_case(self) -> None:
        results = self.passing_results()
        results[0]["run_context"]["model"] = "different-model"
        process = self.run_evaluator(results)

        self.assertEqual(1, process.returncode)
        report = json.loads(process.stdout)
        self.assertTrue(
            any("identity must match" in failure for failure in report["cases"][0]["failures"])
        )

    def test_wrong_case_set_version_fails_case(self) -> None:
        results = self.passing_results()
        for record in results:
            record["run_context"]["case_set_version"] = "stale-cases"
        process = self.run_evaluator(results)

        self.assertEqual(1, process.returncode)
        report = json.loads(process.stdout)
        self.assertTrue(
            any("must be core-v1" in failure for failure in report["cases"][0]["failures"])
        )


if __name__ == "__main__":
    unittest.main()
