#!/usr/bin/env python3
"""Capture a bounded command and a separate artifact grader; not an agent sandbox."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time


VERDICTS = {"pass", "fail", "unresolved"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_bytes(json_bytes(value) + b"\n")
    temporary.replace(path)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_config(config):
    if not isinstance(config, dict):
        raise ValueError("manifest must be an object")
    if type(config.get("schema_version")) is not int or config["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    for key in ("run_id", "candidate_id"):
        if not nonempty(config.get(key)):
            raise ValueError(f"{key} must be non-empty")
    case = config.get("case", {})
    if not isinstance(case, dict) or not isinstance(config.get("timeout_seconds"), dict):
        raise ValueError("case and timeout_seconds must be objects")
    for key in ("id", "family", "dataset_version", "source"):
        if not nonempty(case.get(key)):
            raise ValueError(f"case.{key} must be non-empty")
    if case.get("split") not in {"development", "regression", "confirmation", "representative", "challenge"}:
        raise ValueError("invalid case split")
    if case.get("exposure") not in {"visible", "unseen", "exposed"}:
        raise ValueError("invalid case exposure")
    if config.get("stage") not in {"probe", "comparison", "confirmation"}:
        raise ValueError("invalid experiment stage")
    if config["stage"] == "confirmation" and (case["split"], case["exposure"]) != ("confirmation", "unseen"):
        raise ValueError("confirmation requires a declared unseen confirmation case")
    context = config.get("context")
    if not isinstance(context, dict) or not all(nonempty(context.get(key)) for key in ("model", "environment")) or not all(nonempty(v) for v in context.values()):
        raise ValueError("context must name the model/environment; use unknown explicitly")
    links = config.get("links", {})
    if not isinstance(links, dict) or not all(nonempty(value) for value in links.values()):
        raise ValueError("links must map existing finding/change/baseline IDs to non-empty references")
    cwd = Path(config["cwd"]).resolve(strict=True)
    if not cwd.is_dir():
        raise ValueError("cwd must be an existing directory")
    for stage in ("candidate", "grader"):
        command = config.get(f"{stage}_command")
        if not isinstance(command, list) or not command or not all(nonempty(arg) for arg in command):
            raise ValueError(f"{stage}_command must be an argv array")
        timeout = config.get("timeout_seconds", {}).get(stage)
        if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError(f"{stage} timeout must be finite and positive")
    if "{artifact}" not in config["grader_command"]:
        raise ValueError("grader_command must receive the captured {artifact}")
    criteria = config.get("criteria")
    if not isinstance(criteria, list) or not criteria or not all(nonempty(c) for c in criteria) or len(set(criteria)) != len(criteria):
        raise ValueError("criteria must contain unique non-empty IDs")
    files = config.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("declare candidate, evaluator and relevant input files")
    paths, roles = set(), set()
    for item in files:
        if not isinstance(item, dict) or not nonempty(item.get("path")):
            raise ValueError("files must contain path/role objects")
        path = (cwd / item["path"]).resolve(strict=True)
        role = item["role"]
        if not path.is_file() or path in paths or role not in {"candidate", "evaluator", "input"}:
            raise ValueError("files need unique file paths and valid roles")
        paths.add(path)
        roles.add(role)
    if not {"candidate", "evaluator"} <= roles:
        raise ValueError("declare both candidate and evaluator source files")
    return cwd


def grade_output(raw, expected):
    rows = json.loads(raw)["criteria"]
    if not isinstance(rows, list) or len(rows) != len(expected):
        raise ValueError("grader must resolve every criterion exactly once")
    found = set()
    for row in rows:
        if row["id"] not in expected or row["id"] in found or row["status"] not in VERDICTS or not nonempty(row.get("evidence")):
            raise ValueError("invalid criterion ID, status or evidence")
        found.add(row["id"])
    statuses = {row["status"] for row in rows}
    return rows, "fail" if "fail" in statuses else "unresolved" if "unresolved" in statuses else "pass"


def capture(command, cwd, output, stage, timeout):
    started = time.monotonic()
    receipt = {"stage": stage, "argv": command, "status": "launch_error", "returncode": None}
    with (output / f"{stage}.stdout").open("wb") as stdout, (output / f"{stage}.stderr").open("wb") as stderr:
        try:
            process = subprocess.Popen(command, cwd=cwd, stdout=stdout, stderr=stderr, start_new_session=True)
        except OSError as error:
            stderr.write(str(error).encode())
        else:
            try:
                receipt["returncode"] = process.wait(timeout=timeout)
                receipt["status"] = "completed"
            except (subprocess.TimeoutExpired, KeyboardInterrupt) as error:
                # Only the new process group owned by this invocation is terminated.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                receipt["returncode"] = process.wait()
                receipt["status"] = "timeout" if isinstance(error, subprocess.TimeoutExpired) else "interrupted"
    receipt["elapsed_seconds"] = time.monotonic() - started
    return receipt


def sources_match(snapshots):
    try:
        return all(digest(Path(item["source_path"]).read_bytes()) == item["sha256"] for item in snapshots)
    except OSError:
        return False


def candidate_key(config, snapshots):
    return digest(json_bytes({
        "candidate_id": config["candidate_id"], "command": config["candidate_command"],
        "files": [s["sha256"] for s in snapshots if s["role"] == "candidate"],
    }))


def run_experiment(config, output):
    config = json.loads(json_bytes(config))
    cwd = validate_config(config)
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    write_json(output / "manifest.json", config)
    runner_source = Path(__file__).read_bytes()
    (output / "runner.py").write_bytes(runner_source)
    (output / "inputs").mkdir()
    snapshots = []
    for index, item in enumerate(config["files"]):
        source = (cwd / item["path"]).resolve()
        data = source.read_bytes()
        relative = f"inputs/{index:03d}-{source.name}"
        (output / relative).write_bytes(data)
        snapshots.append({"source_path": str(source), "path": relative, "role": item["role"], "sha256": digest(data)})
    comparison = {
        "case": config["case"], "stage": config["stage"], "context": config["context"],
        "criteria": config["criteria"], "grader_command": config["grader_command"],
        "timeout_seconds": config["timeout_seconds"],
        "fixed_files": [{"role": s["role"], "sha256": s["sha256"]} for s in snapshots if s["role"] != "candidate"],
        "runner_sha256": digest(runner_source),
        "python": platform.python_version(), "platform": platform.platform(),
    }
    record = {
        "schema_version": 1, "run_id": config["run_id"], "candidate_id": config["candidate_id"],
        "candidate_key": candidate_key(config, snapshots),
        "grade_id": f"{config['run_id']}/grade", "links": config.get("links", {}),
        "started_at": datetime.now(timezone.utc).isoformat(), "case": config["case"],
        "status": "running", "verdict": "unresolved", "evidence_scope": "artifact_only",
        "comparison": comparison, "comparison_key": digest(json_bytes(comparison)),
        "snapshots": snapshots, "processes": [], "criteria": [], "artifacts": [],
        "resources": {"tokens": None, "cost": None, "human_seconds": None, "tool_calls": None},
        "telemetry_limit": "Child stdout/stderr, exit and elapsed time only; no nested tool audit or sandbox.",
        "timings": {"wall_seconds": None},
    }
    write_json(output / "record.json", record)
    preparation_seconds = time.monotonic() - started
    artifact = output / "candidate.stdout"
    receipt = capture(config["candidate_command"], cwd, output, "candidate", config["timeout_seconds"]["candidate"])
    record["processes"].append(receipt)
    record["status"] = "execution_failed"
    write_json(output / "record.json", record)
    if not sources_match(snapshots):
        record["status"] = "protocol_changed"
    elif receipt["status"] == "completed" and receipt["returncode"] == 0:
        answer_hash = digest(artifact.read_bytes())
        command = [str(artifact) if arg == "{artifact}" else arg for arg in config["grader_command"]]
        receipt = capture(command, cwd, output, "grader", config["timeout_seconds"]["grader"])
        record["processes"].append(receipt)
        record["status"] = "grader_failed"
        if not sources_match(snapshots) or digest(artifact.read_bytes()) != answer_hash:
            record["status"] = "protocol_changed"
        elif receipt["status"] == "completed" and receipt["returncode"] == 0:
            try:
                record["criteria"], record["verdict"] = grade_output((output / "grader.stdout").read_text(), config["criteria"])
                record["status"] = "completed"
            except (ValueError, KeyError, TypeError) as error:
                record["grading_error"] = str(error)
    names = ["manifest.json", "runner.py"] + [s["path"] for s in snapshots]
    names += [f"{p['stage']}.{suffix}" for p in record["processes"] for suffix in ("stdout", "stderr")]
    record["artifacts"] = [{"path": name, "sha256": digest((output / name).read_bytes())} for name in names]
    record["timings"] = {
        "wall_seconds": time.monotonic() - started, "preparation_seconds": preparation_seconds,
        **{f"{p['stage']}_seconds": p["elapsed_seconds"] for p in record["processes"]},
    }
    write_json(output / "record.json", record)
    return record


def verify_packet(output):
    """Check internal consistency of a controller-owned packet, not authenticity."""
    errors = []
    try:
        output = output.resolve()
        record = json.loads((output / "record.json").read_text())
        manifest = json.loads((output / "manifest.json").read_text())
        if not isinstance(record, dict) or not isinstance(manifest, dict):
            return ["record and manifest must be objects"]
        if record.get("schema_version") != 1 or record.get("status") not in {"running", "completed", "execution_failed", "grader_failed", "protocol_changed"}:
            return ["unsupported packet schema or status"]
        if record["status"] == "running" or not record["artifacts"]:
            return ["incomplete packet"]
        names = set()
        for item in record["artifacts"]:
            path = (output / item["path"]).resolve()
            if not path.is_relative_to(output) or item["path"] in names or digest(path.read_bytes()) != item["sha256"]:
                errors.append(f"invalid artifact: {item['path']}")
            names.add(item["path"])
        expected = {"manifest.json", "runner.py"} | {s["path"] for s in record["snapshots"]}
        expected |= {f"{p['stage']}.{suffix}" for p in record["processes"] for suffix in ("stdout", "stderr")}
        if names != expected or record["run_id"] != manifest["run_id"] or record["candidate_id"] != manifest["candidate_id"] or record["case"] != manifest["case"]:
            errors.append("manifest or artifact coverage mismatch")
        if record["comparison_key"] != digest(json_bytes(record["comparison"])):
            errors.append("comparison identity mismatch")
        for key in ("case", "stage", "context", "criteria", "grader_command", "timeout_seconds"):
            if record["comparison"][key] != manifest[key]:
                errors.append(f"comparison does not match manifest: {key}")
        archived = {item["path"]: item["sha256"] for item in record["artifacts"]}
        if archived.get("runner.py") != record["comparison"]["runner_sha256"] or record["grade_id"] != f"{record['run_id']}/grade" or record["links"] != manifest.get("links", {}):
            errors.append("runner, grade or linked finding identity mismatch")
        for snapshot in record["snapshots"]:
            if archived.get(snapshot["path"]) != snapshot["sha256"]:
                errors.append("input snapshot identity mismatch")
        fixed = [{"role": s["role"], "sha256": s["sha256"]} for s in record["snapshots"] if s["role"] != "candidate"]
        if record["comparison"]["fixed_files"] != fixed or record["candidate_key"] != candidate_key(manifest, record["snapshots"]):
            errors.append("source identity mismatch")
        if errors:
            return errors
        if record["status"] == "completed":
            if [p["stage"] for p in record["processes"]] != ["candidate", "grader"] or any(p["status"] != "completed" or p["returncode"] != 0 for p in record["processes"]):
                errors.append("completed packet lacks successful execution and grading")
            criteria, verdict = grade_output((output / "grader.stdout").read_text(), manifest["criteria"])
            if criteria != record["criteria"] or verdict != record["verdict"]:
                errors.append("record verdict disagrees with grader artifact")
        elif record["verdict"] != "unresolved":
            errors.append("incomplete execution cannot claim a verdict")
        seconds = record["timings"]["wall_seconds"]
        if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds < 0:
            errors.append("missing or invalid wall time")
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append(f"uncheckable packet: {error}")
    return errors


def summarize(outputs):
    verdicts = dict.fromkeys(("pass", "fail", "unresolved"), 0)
    statuses, groups, seen, rows = Counter(), {}, set(), []
    total_seconds, timed_runs, invalid = 0.0, 0, 0
    for output in outputs:
        errors = verify_packet(output)
        if errors:
            invalid += 1
            rows.append({"path": str(output), "errors": errors})
            continue
        record = json.loads((output / "record.json").read_text())
        if record["run_id"] in seen:
            raise ValueError(f"duplicate run_id: {record['run_id']}")
        seen.add(record["run_id"])
        statuses[record["status"]] += 1
        verdicts[record["verdict"]] += 1
        total_seconds += record["timings"]["wall_seconds"]
        timed_runs += 1
        groups.setdefault(record["comparison_key"], []).append(record["run_id"])
        rows.append({"run_id": record["run_id"], "candidate_id": record["candidate_id"], "candidate_key": record["candidate_key"], "status": record["status"], "verdict": record["verdict"], "timings": record["timings"]})
    return {
        "coverage": "provided_packets_only", "provided_runs": len(outputs), "invalid_packets": invalid,
        "verdicts": verdicts, "statuses": dict(statuses), "groups": groups,
        "summed_run_seconds": total_seconds if timed_runs else None, "timed_runs": timed_runs,
        "resources": {"tokens": None, "cost": None, "human_seconds": None},
        "promotion": "not_decided; artifact checks and comparable identities do not establish uplift",
        "runs": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("manifest", type=Path)
    run.add_argument("--output", type=Path, required=True)
    summary = commands.add_parser("summarize")
    summary.add_argument("packets", type=Path, nargs="+")
    args = parser.parse_args()
    try:
        if args.command == "run":
            result = run_experiment(json.loads(args.manifest.read_text()), args.output)
            code = 0 if result["status"] == "completed" and result["verdict"] == "pass" else 1
        else:
            result = summarize(args.packets)
            code = 1 if result["invalid_packets"] else 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
