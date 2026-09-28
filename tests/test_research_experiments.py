from __future__ import annotations

import importlib.util
import hashlib
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research-craft/scripts/run_experiment.py"


class ResearchExperimentTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("research_experiment", SCRIPT)
        self.runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.runner)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.candidate = self.root / "candidate.py"
        self.candidate.write_text("print('42')\n", encoding="utf-8")
        self.grader = self.root / "grader.py"
        self.grader.write_text(
            "import json, pathlib, sys\n"
            "answer = pathlib.Path(sys.argv[1]).read_text().strip()\n"
            "print(json.dumps({'criteria': [{'id': 'answer', "
            "'status': 'pass' if answer == '42' else 'fail', "
            "'evidence': 'Compared captured stdout with expected answer 42'}]}))\n",
            encoding="utf-8",
        )

    def config(self, run_id="run-1"):
        return {
            "schema_version": 1,
            "run_id": run_id,
            "candidate_id": "candidate-v1",
            "stage": "probe",
            "case": {
                "id": "answer-1", "family": "arithmetic", "dataset_version": "v1",
                "split": "development", "exposure": "visible", "source": "synthetic test",
            },
            "context": {"model": "not-applicable", "environment": "local-python"},
            "cwd": str(self.root),
            "candidate_command": [sys.executable, "-B", str(self.candidate)],
            "grader_command": [sys.executable, "-B", str(self.grader), "{artifact}"],
            "criteria": ["answer"],
            "files": [
                {"path": str(self.candidate), "role": "candidate"},
                {"path": str(self.grader), "role": "evaluator"},
            ],
            "timeout_seconds": {"candidate": 2, "grader": 2},
        }

    def run_case(self, config=None, name="run"):
        return self.runner.run_experiment(config or self.config(), self.root / name)

    def test_captures_evidence_and_observed_cost_without_inventing_telemetry(self):
        record = self.run_case()
        self.assertEqual("completed", record["status"])
        self.assertEqual("pass", record["verdict"])
        self.assertEqual("artifact_only", record["evidence_scope"])
        self.assertGreater(record["timings"]["wall_seconds"], 0)
        self.assertIsNone(record["resources"]["tokens"])
        self.assertIsNone(record["resources"]["tool_calls"])
        self.assertEqual([], self.runner.verify_packet(self.root / "run"))

    def test_candidate_self_approval_cannot_override_independent_failure(self):
        self.candidate.write_text("print('{\"behavior_pass\": true}')\n", encoding="utf-8")
        record = self.run_case()
        self.assertEqual("completed", record["status"])
        self.assertEqual("fail", record["verdict"])

    def test_missing_or_duplicate_criterion_is_grader_error(self):
        for index, criteria in enumerate(([], [
            {"id": "answer", "status": "pass", "evidence": "x"},
            {"id": "answer", "status": "pass", "evidence": "x"},
        ])):
            self.grader.write_text(f"print({json.dumps({'criteria': criteria})!r})\n", encoding="utf-8")
            record = self.run_case(name=f"bad-{index}")
            self.assertEqual("grader_failed", record["status"])
            self.assertEqual("unresolved", record["verdict"])

    def test_unresolved_is_not_a_pass_or_an_execution_failure(self):
        self.grader.write_text(
            "print('{\"criteria\":[{\"id\":\"answer\",\"status\":\"unresolved\",\"evidence\":\"source missing\"}]}')\n",
            encoding="utf-8",
        )
        record = self.run_case()
        self.assertEqual("completed", record["status"])
        self.assertEqual("unresolved", record["verdict"])

    def test_nonzero_candidate_preserves_failure_and_skips_grading(self):
        self.candidate.write_text("raise RuntimeError('original failure')\n", encoding="utf-8")
        record = self.run_case()
        self.assertEqual("execution_failed", record["status"])
        self.assertEqual(1, len(record["processes"]))
        self.assertIn("original failure", (self.root / "run/candidate.stderr").read_text())

    def test_grader_crash_is_distinct_from_a_valid_negative_result(self):
        self.grader.write_text("raise RuntimeError('grader unavailable')\n", encoding="utf-8")
        record = self.run_case()
        self.assertEqual("grader_failed", record["status"])
        self.assertEqual("unresolved", record["verdict"])
        self.assertEqual([], self.runner.verify_packet(self.root / "run"))

    def test_packet_preserves_links_and_the_exact_runner(self):
        config = self.config()
        config["links"] = {"finding_id": "F-001", "change_id": "candidate-revision"}
        record = self.run_case(config)
        self.assertEqual(config["links"], record["links"])
        self.assertEqual("run-1/grade", record["grade_id"])
        self.assertEqual(SCRIPT.read_bytes(), (self.root / "run/runner.py").read_bytes())

    def test_timeout_is_recorded_not_retried_or_counted_as_pass(self):
        self.candidate.write_text("import time\ntime.sleep(10)\n", encoding="utf-8")
        config = self.config()
        config["timeout_seconds"]["candidate"] = 0.05
        record = self.run_case(config)
        self.assertEqual("execution_failed", record["status"])
        self.assertEqual("timeout", record["processes"][0]["status"])

    def test_changed_evaluator_invalidates_run_before_grading(self):
        self.candidate.write_text(
            f"from pathlib import Path\nPath({str(self.grader)!r}).write_text('print(42)')\nprint(42)\n",
            encoding="utf-8",
        )
        record = self.run_case()
        self.assertEqual("protocol_changed", record["status"])
        self.assertEqual(1, len(record["processes"]))

    def test_grader_cannot_change_the_answer_it_graded(self):
        self.grader.write_text(
            "import pathlib, sys\npathlib.Path(sys.argv[1]).write_text('replaced')\n"
            "print('{\"criteria\":[{\"id\":\"answer\",\"status\":\"pass\",\"evidence\":\"x\"}]}')\n",
            encoding="utf-8",
        )
        self.assertEqual("protocol_changed", self.run_case()["status"])

    def test_fresh_output_is_required(self):
        self.run_case()
        with self.assertRaises(FileExistsError):
            self.run_case()

    def test_visible_case_cannot_be_labeled_independent_confirmation(self):
        config = self.config()
        config["stage"] = "confirmation"
        with self.assertRaises(ValueError):
            self.run_case(config)
        self.assertFalse((self.root / "run").exists())

    def test_tampered_artifact_and_verdict_are_detected(self):
        self.run_case()
        (self.root / "run/candidate.stdout").write_text("wrong", encoding="utf-8")
        self.assertTrue(self.runner.verify_packet(self.root / "run"))
        self.run_case(self.config("run-2"), "second")
        path = self.root / "second/record.json"
        record = json.loads(path.read_text())
        record["verdict"] = "fail"
        path.write_text(json.dumps(record), encoding="utf-8")
        self.assertTrue(self.runner.verify_packet(self.root / "second"))

    def test_changed_comparison_context_cannot_regroup_a_packet(self):
        self.run_case()
        path = self.root / "run/record.json"
        record = json.loads(path.read_text())
        record["comparison"]["context"]["model"] = "different-model"
        record["comparison_key"] = self.runner.digest(self.runner.json_bytes(record["comparison"]))
        path.write_text(json.dumps(record), encoding="utf-8")
        self.assertTrue(self.runner.verify_packet(self.root / "run"))

    def test_candidate_fingerprint_changes_even_when_display_name_does_not(self):
        first = self.run_case()
        self.candidate.write_text("print(43)\n", encoding="utf-8")
        second = self.run_case(self.config("run-2"), "second")
        self.assertNotEqual(first["candidate_key"], second["candidate_key"])
        self.assertEqual(first["comparison_key"], second["comparison_key"])

    def test_incomplete_packet_remains_visible(self):
        self.run_case()
        path = self.root / "run/record.json"
        record = json.loads(path.read_text())
        record["status"] = "running"
        path.write_text(json.dumps(record), encoding="utf-8")
        self.assertEqual(["incomplete packet"], self.runner.verify_packet(self.root / "run"))

    def test_invalid_setup_never_launches_a_command(self):
        for index, field in enumerate(("case", "context", "timeout_seconds")):
            config = self.config()
            config[field] = []
            with self.assertRaises(ValueError):
                self.run_case(config, f"invalid-{index}")
            self.assertFalse((self.root / f"invalid-{index}").exists())

    def test_missing_runtime_identity_is_explicitly_rejected(self):
        config = self.config()
        del config["context"]["model"]
        with self.assertRaises(ValueError):
            self.run_case(config)
        self.assertFalse((self.root / "run").exists())

    def test_history_survives_later_source_changes(self):
        self.run_case()
        self.candidate.write_text("print('new candidate')\n", encoding="utf-8")
        self.assertEqual([], self.runner.verify_packet(self.root / "run"))

    def test_summary_keeps_failures_costs_and_comparison_groups(self):
        self.run_case()
        self.candidate.write_text("print('wrong')\n", encoding="utf-8")
        self.run_case(self.config("run-2"), "second")
        config = self.config("run-3")
        config["case"]["dataset_version"] = "v2"
        self.run_case(config, "third")
        summary = self.runner.summarize([self.root / name for name in ("run", "second", "third")])
        self.assertEqual(3, summary["provided_runs"])
        self.assertEqual(2, len(summary["groups"]))
        self.assertEqual({"pass": 1, "fail": 2, "unresolved": 0}, summary["verdicts"])
        self.assertGreater(summary["summed_run_seconds"], 0)
        self.assertEqual("provided_packets_only", summary["coverage"])

    def test_duplicate_run_ids_are_rejected_instead_of_inflating_sample(self):
        self.run_case()
        self.run_case(name="second")
        with self.assertRaises(ValueError):
            self.runner.summarize([self.root / "run", self.root / "second"])

    def test_missing_packet_is_visible_and_not_zero_cost_success(self):
        summary = self.runner.summarize([self.root / "missing"])
        self.assertEqual(1, summary["invalid_packets"])
        self.assertEqual(0, summary["verdicts"]["pass"])
        self.assertIsNone(summary["summed_run_seconds"])

    def test_malformed_packet_returns_diagnostic_instead_of_crashing(self):
        self.run_case()
        (self.root / "run/record.json").write_text("[]", encoding="utf-8")
        summary = self.runner.summarize([self.root / "run"])
        self.assertEqual(1, summary["invalid_packets"])

    def test_pipeline_grader_preserves_integer_output_contract(self):
        grade = runpy.run_path(str(ROOT / "research-craft/evals/flywheel/grader.py"))["grade"]
        artifact = {"normal-input": {"rows": [{"id": "x", "amount": False, "category": 0}] * 3}}
        row = grade("pipeline-contract", artifact)["criteria"][0]
        self.assertEqual("fail", row["status"])

    def test_domain_grader_accepts_contract_valid_reference_behavior(self):
        process = runpy.run_path(str(ROOT / "iterate/evals/fixtures/pipeline/pipeline.py"))["process"]
        grade = runpy.run_path(str(ROOT / "research-craft/evals/flywheel/grader.py"))["grade"]
        class UnhashableString(str):
            __hash__ = None
        raw = '{"id":"x","category":" A "}'
        observations = {
            "normal-input": {"rows": process([raw] * 3, ["a"])},
            "unhashable-input": {"rows": process([UnhashableString(raw)] * 3, ["a"])},
            "reordered-categories": {"rows": process([raw] * 3, ["b", "a"])},
        }
        self.assertTrue(all(row["status"] == "pass" for row in grade("pipeline-contract", observations)["criteria"]))

    def test_documented_pilot_preserves_expected_failures_across_three_domains(self):
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "research-craft/evals/flywheel/run_pilot.py"), "--output", str(self.root / "pilot")],
            capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        summary = json.loads(result.stdout)
        self.assertTrue(summary["inventory_complete"])
        self.assertEqual(3, len(summary["groups"]))
        self.assertEqual({"pass": 3, "fail": 6, "unresolved": 0}, summary["verdicts"])

    def test_decision_grader_distinguishes_completion_history_and_perturbations(self):
        produce = runpy.run_path(str(ROOT / "research-craft/evals/flywheel/candidate.py"))["decision"]
        grade = runpy.run_path(str(ROOT / "research-craft/evals/flywheel/grader.py"))["grade"]
        failures = {
            "contract-aware": set(),
            "score-only": {"completion", "history", "meaningful-boundary"},
            "history-blind": {"history"},
            "wording-sensitive": {"irrelevant-change"},
            "boundary-blind": {"meaningful-boundary"},
        }
        for arm, expected in failures.items():
            with self.subTest(arm=arm):
                rows = grade("decision-contract", produce(arm))["criteria"]
                self.assertEqual(expected, {row["id"] for row in rows if row["status"] == "fail"})

    def test_decision_fixture_pairs_preserve_their_declared_controls(self):
        fixture = json.loads((ROOT / "research-craft/evals/flywheel/decision-input.json").read_text())
        rows = {row["id"]: {key: value for key, value in row.items() if key != "id"} for row in fixture["observations"]}
        baseline = rows["complete"]
        for name, field in (("exposed-history", "history"), ("irrelevant-label", "label"), ("permission-boundary", "publish_authorized"), ("low-quality", "quality")):
            with self.subTest(pair=name):
                changed = {key for key in baseline if baseline[key] != rows[name][key]}
                self.assertEqual({field}, changed)
        reordered = rows["reordered-items"]
        for field in ("required", "verified"):
            self.assertNotEqual(baseline[field], reordered[field])
            self.assertEqual(set(baseline[field]), set(reordered[field]))
        self.assertEqual(baseline["required"], rows["allowed-deferral"]["required"])
        self.assertGreater(rows["high-score-incomplete"]["quality"], baseline["quality"])
        self.assertFalse(set(rows["high-score-incomplete"]["required"]) <= set(rows["high-score-incomplete"]["verified"]))

    def test_research_decision_packet_has_valid_pairs_and_visible_development_cases(self):
        cases = [json.loads(line) for line in (ROOT / "tests/research-decision-cases.jsonl").read_text().splitlines()]
        self.assertEqual(len(cases), len({case["id"] for case in cases}))
        pairs = {}
        for case in cases:
            self.assertEqual("development", case["split"])
            self.assertTrue((ROOT / case["skill"] / "SKILL.md").is_file())
            self.assertTrue(case["prompt"] and case["criteria"])
            if "pair_id" in case:
                pairs.setdefault(case["pair_id"], []).append(case)
        self.assertEqual({"confirmation-history", "irrelevant-wording"}, set(pairs))
        self.assertTrue(all(len(pair) == 2 for pair in pairs.values()))

    def test_decision_grader_rejects_constant_actions_and_missing_or_duplicate_pairs(self):
        produce = runpy.run_path(str(ROOT / "research-craft/evals/flywheel/candidate.py"))["decision"]
        grade = runpy.run_path(str(ROOT / "research-craft/evals/flywheel/grader.py"))["grade"]
        artifact = produce("contract-aware")
        for row in artifact["decisions"]:
            row["action"] = "keep-local"
        self.assertTrue(any(row["status"] == "fail" for row in grade("decision-contract", artifact)["criteria"]))
        for mutation in ("missing", "duplicate", "extra", "malformed"):
            artifact = produce("contract-aware")
            if mutation == "missing":
                artifact["decisions"].pop()
            elif mutation == "duplicate":
                artifact["decisions"].append(artifact["decisions"][0])
            elif mutation == "extra":
                artifact["decisions"].append({"id": "extra", "action": "ready-to-publish"})
            else:
                artifact["decisions"][0] = None
            with self.subTest(mutation=mutation):
                self.assertTrue(all(row["status"] == "fail" for row in grade("decision-contract", artifact)["criteria"]))

    def test_high_score_cannot_override_completion_in_captured_experiment(self):
        base = ROOT / "research-craft/evals/flywheel"
        records = []
        for arm in ("score-only", "contract-aware"):
            config = self.config(arm)
            config["candidate_id"] = arm
            config["case"] = {"id": "decision-contract", "family": "decision-contract", "dataset_version": "decision-v1", "source": "synthetic contract", "split": "development", "exposure": "visible"}
            config["criteria"] = ["completion", "history", "irrelevant-change", "meaningful-boundary"]
            config["candidate_command"] = [sys.executable, "-B", str(base / "candidate.py"), "decision-contract", arm]
            config["grader_command"] = [sys.executable, "-B", str(base / "grader.py"), "decision-contract", "{artifact}"]
            config["files"] = [{"path": str(base / name), "role": role} for name, role in (("candidate.py", "candidate"), ("grader.py", "evaluator"), ("decision-input.json", "input"))]
            record = self.run_case(config, arm)
            self.assertEqual("completed", record["status"])
            self.assertEqual([], self.runner.verify_packet(self.root / arm))
            records.append(record)
        self.assertEqual(["fail", "pass"], [row["verdict"] for row in records])
        self.assertEqual(records[0]["comparison_key"], records[1]["comparison_key"])

    def test_forecast_grader_rejects_invented_actual_even_with_correct_error(self):
        grade = runpy.run_path(str(ROOT / "research-craft/evals/flywheel/grader.py"))["grade"]
        artifact = {"claims": [
            {"id": "q2-profit", "forecast": 2800, "actual": 9999, "error": -760, "resolution": "resolved"},
            {"id": "q3-profit", "forecast": 2560, "actual": 1960, "error": -600, "resolution": "resolved"},
            {"id": "q4-profit", "forecast": 2560, "actual": None, "error": None, "resolution": "not_due"},
        ]}
        rows = grade("forecast-reconciliation", artifact)["criteria"]
        self.assertEqual("fail", next(row["status"] for row in rows if row["id"] == "forecast-error"))

    def test_cli_distinguishes_valid_negative_run_from_invalid_summary(self):
        self.candidate.write_text("print('wrong')\n", encoding="utf-8")
        manifest = self.root / "manifest.json"
        manifest.write_text(json.dumps(self.config()), encoding="utf-8")
        run = subprocess.run([sys.executable, "-B", str(SCRIPT), "run", str(manifest), "--output", str(self.root / "run")], capture_output=True, text=True, timeout=10)
        self.assertEqual(1, run.returncode, run.stderr)
        self.assertEqual("fail", json.loads(run.stdout)["verdict"])
        summary = subprocess.run([sys.executable, "-B", str(SCRIPT), "summarize", str(self.root / "run")], capture_output=True, text=True, timeout=10)
        self.assertEqual(0, summary.returncode, summary.stderr)
        self.assertEqual(1, json.loads(summary.stdout)["verdicts"]["fail"])

    def test_archived_observations_bind_raw_outputs_and_independent_grades(self):
        archive = json.loads((ROOT / "research-craft/evals/flywheel/observed.json").read_text())
        counts = {"pass": 0, "fail": 0, "unresolved": 0}
        ids = []
        for run in archive["runs"]:
            record = run["record"]
            ids.append(record["run_id"])
            hashes = {item["path"]: item["sha256"] for item in record["artifacts"]}
            for stage in ("candidate", "grader"):
                self.assertEqual(hashes[f"{stage}.stdout"], hashlib.sha256(run[f"{stage}_stdout"].encode()).hexdigest())
            criteria, verdict = self.runner.grade_output(run["grader_stdout"], record["comparison"]["criteria"])
            self.assertEqual(criteria, record["criteria"])
            self.assertEqual(verdict, record["verdict"])
            counts[verdict] += 1
        self.assertEqual(sorted(ids), sorted(archive["summary"]["expected_runs"]))
        self.assertEqual(counts, archive["summary"]["verdicts"])


if __name__ == "__main__":
    unittest.main()
