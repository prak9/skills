#!/usr/bin/env python3
"""Read-only integrity checks for native research packages; not a fact checker."""
from __future__ import annotations

import argparse
import ast
import csv
from decimal import Decimal, DecimalException
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


COLUMNS = {
    "sources.csv": "id title url file type root discovery_path published_at accessed_at access caveat",
    "claims.csv": "id claim status confidence rationale limitations evidence_ids dissent_ids excluded_reason",
    "evidence.csv": "id claim_id source_id relation kind text locator authority root",
    "numbers.csv": "id claim_id value unit kind formula inputs source_ids as_of tolerance",
    "outline.csv": "section claim_ids",
}
GENRES = {"qa", "explainer", "comparison", "decision", "landscape", "validation", "custom"}
CLAIM_STATES = {"supported", "conditional", "contested", "insufficient", "contradicted"}
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def ids(value):
    return [item.strip() for item in value.split(";") if item.strip()]


def decimal(value):
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError("number must be finite")
    return result


def calculate(expression, inputs):
    """Evaluate bounded arithmetic, never Python calls, attributes or subscripts."""
    if len(expression) > 512:
        raise ValueError("formula too long")
    tree = ast.parse(expression, mode="eval")
    if sum(1 for _ in ast.walk(tree)) > 128:
        raise ValueError("formula too complex")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return decimal(node.value)
        if isinstance(node, ast.Name) and node.id in inputs:
            return decimal(inputs[node.id]["value"])
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            result = visit(node.operand)
            return -result if isinstance(node.op, ast.USub) else result
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Pow) and abs(right) <= 12:
                return left ** right
        raise ValueError("unsupported formula operation or unknown input")

    return decimal(visit(tree))


def validate(directory):
    root = Path(directory).resolve()
    errors, limits = [], []
    files = set()

    def problem(message):
        errors.append(message)

    def file(name):
        if not isinstance(name, str) or not name or Path(name).is_absolute():
            raise ValueError(f"invalid package path: {name!r}")
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"path escapes package: {name}")
        if not path.is_file() or not path.stat().st_size:
            raise ValueError(f"missing or empty file: {name}")
        files.add(name)
        return path

    manifest = json.loads(file("research.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("genre") not in GENRES:
        raise ValueError("unsupported schema_version or genre")
    if not manifest.get("as_of"):
        problem("missing research as_of")
    report_name = manifest.get("report")
    report = file(report_name).read_text(encoding="utf-8")
    memo = file("memo.md").read_text(encoding="utf-8")
    for name in ("plan.md", "state.md", "review.md", "refresh.md"):
        file(name)

    tables = {}
    for name, columns in COLUMNS.items():
        with file(name).open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames or not set(columns.split()) <= set(reader.fieldnames):
                raise ValueError(f"missing columns: {name}")
            rows = list(reader)
            if any(None in row or any(v is None for v in row.values()) for row in rows):
                raise ValueError(f"malformed CSV row: {name}")
        if name in {"claims.csv", "outline.csv"} and not rows:
            problem(f"empty table: {name}")
        tables[name] = rows

    def index(name):
        result = {}
        for row in tables[name]:
            key = row["id"]
            if not key or key in result:
                problem(f"empty or duplicate id in {name}: {key}")
            result[key] = row
        return result

    sources, claims = index("sources.csv"), index("claims.csv")
    evidence, numbers = index("evidence.csv"), index("numbers.csv")
    source_texts = {}
    for sid, row in sources.items():
        try:
            source_texts[sid] = file(row["file"]).read_text(encoding="utf-8")
        except ValueError as exc:
            problem(f"source {sid}: {exc}")
        for key in ("title", "url", "root", "discovery_path", "published_at", "accessed_at"):
            if not row[key]:
                problem(f"source {sid}: missing {key}")
        if row["access"] not in {"full", "partial", "blocked", "unknown"}:
            problem(f"source {sid}: invalid access")

    for eid, row in evidence.items():
        if row["claim_id"] not in claims or row["source_id"] not in sources:
            problem(f"evidence {eid}: unknown claim/source")
        if row["relation"] not in {"supports", "contradicts", "context"}:
            problem(f"evidence {eid}: invalid relation")
        if row["kind"] not in {"quote", "paraphrase"}:
            problem(f"evidence {eid}: invalid kind")
        if row["authority"] not in {"qualified", "limited", "unknown"}:
            problem(f"evidence {eid}: invalid authority")
        if not row["text"] or not row["locator"] or not row["root"]:
            problem(f"evidence {eid}: missing text/locator/root")
        if row["kind"] == "quote" and row["source_id"] in source_texts:
            if " ".join(row["text"].split()) not in " ".join(source_texts[row["source_id"]].split()):
                problem(f"evidence {eid}: quote absent from source card")

    active = {cid for cid, row in claims.items() if not row["excluded_reason"]}
    for cid, row in claims.items():
        if row["status"] not in CLAIM_STATES or row["confidence"] not in {"low", "medium", "high"}:
            problem(f"claim {cid}: invalid status/confidence")
        if not row["claim"] or not row["rationale"]:
            problem(f"claim {cid}: missing claim/rationale")
        supporting = ids(row["evidence_ids"])
        dissent = ids(row["dissent_ids"])
        for eid in supporting + dissent:
            if eid not in evidence or evidence[eid]["claim_id"] != cid:
                problem(f"claim {cid}: invalid evidence reference {eid}")
        for eid in dissent:
            if eid in evidence and evidence[eid]["relation"] != "contradicts":
                problem(f"claim {cid}: dissent {eid} is not counterevidence")
        actual_dissent = {eid for eid, ev in evidence.items() if ev["claim_id"] == cid and ev["relation"] == "contradicts"}
        if not actual_dissent <= set(dissent):
            problem(f"claim {cid}: dropped dissent {sorted(actual_dissent - set(dissent))}")
        supports = [evidence[eid] for eid in supporting if eid in evidence and evidence[eid]["relation"] == "supports"]
        if cid in active and row["status"] in {"supported", "conditional"} and not supports:
            problem(f"claim {cid}: no supporting evidence")
        if row["confidence"] == "high":
            if row["status"] != "supported":
                problem(f"claim {cid}: confidence high with {row['status']}")
            if not any(ev["authority"] == "qualified" and ev["root"] != "unknown" and sources.get(ev["source_id"], {}).get("access") in {"full", "partial"} for ev in supports):
                problem(f"claim {cid}: high confidence lacks qualified support")
        if row["status"] != "supported" and not row["limitations"]:
            problem(f"claim {cid}: missing limitations")

    questions = manifest.get("questions")
    if not isinstance(questions, list) or not questions:
        raise ValueError("questions must be a nonempty array")
    question_ids = set()
    for question in questions:
        qid = question.get("id")
        if not qid or qid in question_ids or not question.get("question"):
            problem(f"empty or duplicate question: {qid}")
        question_ids.add(qid)
        mapped = question.get("claim_ids", [])
        if not isinstance(mapped, list) or any(cid not in active for cid in mapped):
            problem(f"question {qid}: missing/excluded claim")
        status = question.get("status")
        if status == "open" or status not in {"answered", "insufficient"}:
            problem(f"question {qid}: open or invalid status")
        if status == "answered" and not mapped:
            problem(f"question {qid}: answered without evidence claims")
        if status == "insufficient":
            if not question.get("reason"):
                problem(f"question {qid}: insufficient without reason")
            limits.append(f"question {qid}: evidence insufficient")

    mapped_claims = set()
    headings = set(re.findall(r"^#{1,6}\s+(.+?)\s*$", report, re.MULTILINE))
    for row in tables["outline.csv"]:
        if row["section"] not in headings:
            problem(f"outline: section absent from report: {row['section']}")
        for cid in ids(row["claim_ids"]):
            if cid not in claims:
                problem(f"outline: unknown claim {cid}")
            mapped_claims.add(cid)
    for cid in active - mapped_claims:
        problem(f"outline: unmapped claim {cid}")

    for name, content in ((report_name, report), ("memo.md", memo)):
        links = LINK.findall(content)
        for label, target in links:
            target = target.strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            try:
                resolved = str((Path(name).parent / unquote(parsed.path)))
                file(resolved)
            except ValueError as exc:
                problem(f"{name}: broken link {target}: {exc}")
            if target == "claims.csv" and label not in claims:
                problem(f"{name}: unknown claim link {label}")
            if target == "numbers.csv" and label not in numbers:
                problem(f"{name}: unknown number link {label}")
        if name == report_name:
            linked = {label for label, target in links if target == "claims.csv"}
            for cid in active - linked:
                problem(f"report: missing claim link {cid}")

    for nid, row in numbers.items():
        try:
            value, tolerance = decimal(row["value"]), decimal(row["tolerance"])
            if tolerance < 0:
                raise ValueError("negative tolerance")
            if row["claim_id"] not in claims or not row["unit"] or not row["as_of"]:
                raise ValueError("missing claim/unit/as_of")
            source_ids = ids(row["source_ids"])
            if not source_ids or any(sid not in sources for sid in source_ids):
                raise ValueError("unknown number source")
            if row["kind"] == "derived":
                inputs = json.loads(row["inputs"])
                if not isinstance(inputs, dict) or not inputs:
                    raise ValueError("formula inputs must be a nonempty object")
                for item in inputs.values():
                    decimal(item["value"])
                    if item["source_id"] not in source_ids or not item.get("locator"):
                        raise ValueError("unknown input source or missing locator")
                try:
                    computed = calculate(row["formula"], inputs)
                except (ValueError, SyntaxError, DecimalException) as exc:
                    raise ValueError(f"formula: {exc}") from exc
                if abs(computed - value) > tolerance:
                    problem(f"number {nid}: arithmetic mismatch ({computed} vs {value})")
            elif row["kind"] != "verbatim":
                raise ValueError("invalid number kind")
        except (ValueError, TypeError, KeyError, DecimalException) as exc:
            problem(f"number {nid}: {exc}")

    required_inputs = set(files)
    receipt = json.loads(file(".verify/review.json").read_text(encoding="utf-8"))
    if not receipt.get("reviewer") or not receipt.get("method"):
        problem("review receipt lacks reviewer/method")
    hashes = receipt.get("input_hashes", {})
    for name in required_inputs:
        if hashes.get(name) != hashlib.sha256((root / name).read_bytes()).hexdigest():
            problem(f"stale or missing input fingerprint: {name}")
    checks = {}
    for check in receipt.get("checks", []):
        key = (check.get("kind"), check.get("target"))
        if key in checks:
            problem(f"duplicate review check: {key}")
        checks[key] = check
        if check.get("status") not in {"pass", "limited", "fail"} or not check.get("reason"):
            problem(f"invalid review check: {key}")
        if check.get("status") == "fail":
            problem(f"failed review check: {key}")
        if check.get("status") == "limited":
            limits.append(f"{key}: {check.get('reason')}")
            if key[1] in active and claims[key[1]]["confidence"] == "high":
                problem(f"claim {key[1]}: high confidence with limited {key[0]}")
    required = {(kind, cid) for cid in active for kind in ("authority", "support", "qualifiers")}
    required.update(("access", sid) for sid in sources)
    required.update((kind, "report") for kind in ("constructs", "counterevidence", "numbers"))
    for key in required - checks.keys():
        problem(f"missing review check: {key}")
    return {"ok": not errors, "errors": errors, "limits": limits,
            "scope": "Package integrity and recorded checks only; not independent semantic verification."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.directory)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
