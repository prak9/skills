from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_evals.py"
AGGREGATOR = SKILL_ROOT / "scripts" / "aggregate_evals.py"


def eval_contract() -> dict:
    return {
        "schema_version": 1,
        "skill_name": "example-skill",
        "acceptance": {
            "min_candidate_pass_rate": 1.0,
            "max_required_failures": 0,
            "min_pass_rate_delta": 0.4,
        },
        "evals": [
            {
                "id": "summary-quality",
                "prompt": "Summarize the attached report for an executive reader.",
                "expected_output": "A concise summary grounded in the report.",
                "files": [],
                "assertions": [
                    {
                        "id": "states-decision",
                        "text": "The summary states the decision the report supports.",
                        "kind": "model",
                        "required": True,
                    },
                    {
                        "id": "no-invented-facts",
                        "text": "The summary contains no facts absent from the report.",
                        "kind": "human",
                        "required": True,
                    },
                ],
            }
        ],
    }


class EvalToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.evals_path = self.root / "evals.json"
        self.evals_path.write_text(json.dumps(eval_contract()), encoding="utf-8")

    def run_script(
        self, script: Path, *args: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(script), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def write_grading(
        self,
        iteration: Path,
        configuration: str,
        run_number: int,
        passed: tuple[bool, bool],
        timing: dict | None = None,
    ) -> None:
        run_dir = (
            iteration
            / "eval-summary-quality"
            / configuration
            / f"run-{run_number}"
        )
        run_dir.mkdir(parents=True)
        grading = {
            "assertions": [
                {
                    "id": "states-decision",
                    "passed": passed[0],
                    "evidence": "The first paragraph states the decision.",
                },
                {
                    "id": "no-invented-facts",
                    "passed": passed[1],
                    "evidence": "Compared every factual statement with the source.",
                },
            ],
            "notes": [],
        }
        (run_dir / "grading.json").write_text(
            json.dumps(grading), encoding="utf-8"
        )
        if timing is not None:
            (run_dir / "timing.json").write_text(
                json.dumps(timing), encoding="utf-8"
            )

    def test_validator_accepts_complete_contract(self) -> None:
        process = self.run_script(VALIDATOR, str(self.evals_path), "--json")

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        result = json.loads(process.stdout)
        self.assertTrue(result["valid"])
        self.assertEqual(1, result["eval_count"])
        self.assertEqual(2, result["assertion_count"])

    def test_validator_rejects_fixture_path_escape(self) -> None:
        contract = eval_contract()
        contract["evals"][0]["files"] = ["../secret.txt"]
        self.evals_path.write_text(json.dumps(contract), encoding="utf-8")

        process = self.run_script(VALIDATOR, str(self.evals_path))

        self.assertNotEqual(0, process.returncode)
        self.assertIn("stay within", process.stderr)

    def test_aggregator_computes_paired_acceptance_without_fake_tokens(self) -> None:
        iteration = self.root / "iteration-1"
        self.write_grading(
            iteration,
            "candidate",
            1,
            (True, True),
            {"duration_seconds": 2.0},
        )
        self.write_grading(
            iteration,
            "baseline",
            1,
            (True, False),
            {"duration_seconds": 1.0, "total_tokens": 100},
        )

        process = self.run_script(
            AGGREGATOR, str(iteration), "--evals", str(self.evals_path)
        )

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        benchmark = json.loads((iteration / "benchmark.json").read_text())
        self.assertEqual(1.0, benchmark["configurations"]["candidate"]["pass_rate"])
        self.assertEqual(0.5, benchmark["configurations"]["baseline"]["pass_rate"])
        self.assertEqual(0.5, benchmark["delta"]["pass_rate"])
        self.assertTrue(benchmark["acceptance"]["passed"])
        token_stats = benchmark["configurations"]["candidate"]["total_tokens"]
        self.assertEqual(0, token_stats["samples"])
        self.assertIsNone(token_stats["mean"])
        self.assertTrue((iteration / "benchmark.md").is_file())

    def test_aggregator_rejects_unpaired_runs(self) -> None:
        iteration = self.root / "iteration-1"
        self.write_grading(iteration, "candidate", 1, (True, True))
        self.write_grading(iteration, "candidate", 2, (True, True))
        self.write_grading(iteration, "baseline", 1, (True, False))

        process = self.run_script(
            AGGREGATOR, str(iteration), "--evals", str(self.evals_path)
        )

        self.assertNotEqual(0, process.returncode)
        self.assertIn("paired", process.stderr.lower())

    def test_aggregator_rejects_missing_assertion_grade(self) -> None:
        iteration = self.root / "iteration-1"
        self.write_grading(iteration, "candidate", 1, (True, True))
        self.write_grading(iteration, "baseline", 1, (True, False))
        grading_path = (
            iteration
            / "eval-summary-quality"
            / "candidate"
            / "run-1"
            / "grading.json"
        )
        grading = json.loads(grading_path.read_text())
        grading["assertions"].pop()
        grading_path.write_text(json.dumps(grading), encoding="utf-8")

        process = self.run_script(
            AGGREGATOR, str(iteration), "--evals", str(self.evals_path)
        )

        self.assertNotEqual(0, process.returncode)
        self.assertIn("missing assertion", process.stderr.lower())


if __name__ == "__main__":
    unittest.main()
