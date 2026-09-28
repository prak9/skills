#!/usr/bin/env python3
"""Replay artifact and synthetic task families with separate grading."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("run_experiment", ROOT / "research-craft/scripts/run_experiment.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def run_pilot(output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    registry = json.loads((HERE / "cases.json").read_text())
    packets = []
    for case in registry["cases"]:
        for arm in case["arms"]:
            run_id = f"{case['id']}-{arm}"
            inputs = [HERE / "cases.json"]
            if case["id"] == "pipeline-contract":
                inputs.append(ROOT / "iterate/evals/execution-evidence.json")
            elif case["id"] == "forecast-reconciliation":
                inputs.append(HERE / "forecast-input.json")
            else:
                inputs.append(HERE / "decision-input.json")
            config = {
                "schema_version": 1, "run_id": run_id, "candidate_id": arm, "stage": "comparison",
                "case": {**{key: case[key] for key in ("id", "family", "source", "split", "exposure")}, "dataset_version": registry["dataset_version"]},
                "context": {"model": "not-applicable; artifact replay", "environment": "local-python"},
                "cwd": str(ROOT),
                "candidate_command": [sys.executable, "-B", str(HERE / "candidate.py"), case["id"], arm],
                "grader_command": [sys.executable, "-B", str(HERE / "grader.py"), case["id"], "{artifact}"],
                "criteria": case["criteria"],
                "files": [
                    {"path": str(HERE / "candidate.py"), "role": "candidate"},
                    {"path": str(HERE / "grader.py"), "role": "evaluator"},
                    *[{"path": str(path), "role": "input"} for path in inputs],
                ],
                "timeout_seconds": {"candidate": 10, "grader": 10},
            }
            packet = output / run_id
            runner.run_experiment(config, packet)
            packets.append(packet)
    summary = runner.summarize(packets)
    summary["expected_runs"] = [f"{case['id']}-{arm}" for case in registry["cases"] for arm in case["arms"]]
    summary["inventory_complete"] = sorted(summary["expected_runs"]) == sorted(row.get("run_id", "") for row in summary["runs"])
    summary["evidence_scope"] = registry["evidence_scope"]
    runner.write_json(output / "summary.json", summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_pilot(args.output)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["inventory_complete"] and not result["invalid_packets"] else 1)
