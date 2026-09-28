"""Grade captured replay output against explicit semantics, never self-approval."""
import argparse
import json
from pathlib import Path


def grade(case, artifact):
    rows = []

    def check(name, passed, evidence):
        rows.append({"id": name, "status": "pass" if passed else "fail", "evidence": evidence})

    if case == "pipeline-contract":
        for name in ("normal-input", "unhashable-input", "reordered-categories"):
            position = 1 if name == "reordered-categories" else 0
            expected = [{"id": "x", "amount": 0, "category": position}] * 3
            actual = artifact.get(name, {})
            matches = json.dumps(actual.get("rows"), sort_keys=True) == json.dumps(expected, sort_keys=True)
            check(name, matches, f"{name}: observed {actual!r}; expected three integer-valued rows with category index {position}")
    else:
        claims = artifact.get("claims", [])
        by_id = {row["id"]: row for row in claims}
        complete = len(claims) == len(by_id) == 3 and set(by_id) == {"q2-profit", "q3-profit", "q4-profit"}
        predictions = [by_id.get(name, {}).get("forecast") for name in ("q2-profit", "q3-profit", "q4-profit")]
        errors = [by_id.get(name, {}).get("error") for name in ("q2-profit", "q3-profit")]
        actuals = [by_id.get(name, {}).get("actual") for name in ("q2-profit", "q3-profit")]
        resolved = all(by_id.get(name, {}).get("resolution") == "resolved" for name in ("q2-profit", "q3-profit"))
        # Frozen Q2/Q3 forecasts remain 2800/2560; realized profits are 2040/1960.
        check("original-forecast", complete and predictions == [2800, 2560, 2560], f"original forecasts observed: {predictions}")
        check("forecast-error", complete and actuals == [2040, 1960] and errors == [-760, -600] and resolved, f"actuals {actuals}; actual minus original forecast {errors}; resolved {resolved}")
        pending = by_id.get("q4-profit", {})
        check("pending-outcome", complete and pending.get("resolution") == "not_due" and "actual" in pending and "error" in pending and pending["actual"] is None and pending["error"] is None, f"Q4 unresolved outcome: {pending}")
    return {"criteria": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=("pipeline-contract", "forecast-reconciliation"))
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    print(json.dumps(grade(args.case, json.loads(args.artifact.read_text()))))
