"""Trusted replay/synthetic producers, not model executors or proposed Skill changes."""
import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class UnhashableString(str):
    __hash__ = None


def pipeline(arm):
    archive = json.loads((ROOT / "iterate/evals/execution-evidence.json").read_text())
    sha = archive["runs"][arm]["files"]["workspace/pipeline.py"]
    source = archive["blobs"][sha]
    assert hashlib.sha256(source.encode()).hexdigest() == sha
    scope = {}
    exec(compile(source, f"archived:{sha}", "exec"), scope)
    raw = '{"id":"x","category":" A "}'
    cases = {
        "normal-input": ([raw] * 3, ["a"]),
        "unhashable-input": ([UnhashableString(raw)] * 3, ["a"]),
        "reordered-categories": ([raw] * 3, ["b", "a"]),
    }
    observations = {}
    for name, (records, categories) in cases.items():
        try:
            observations[name] = {"rows": scope["process"](records, categories)}
        except Exception as error:
            observations[name] = {"error": type(error).__name__}
    return observations


def forecast(arm):
    fixture = json.loads(Path(__file__).with_name("forecast-input.json").read_text())
    rows = []
    for claim in fixture["claims"]:
        prediction = claim["forecast"]
        if arm == "rewritten" and claim["actual"] is not None:
            prediction = claim["actual"]
        rows.append({
            "id": claim["id"], "forecast": prediction, "actual": claim["actual"],
            "error": None if claim["actual"] is None else claim["actual"] - prediction,
            "resolution": claim["resolution"],
        })
    return {"claims": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=("pipeline-contract", "forecast-reconciliation"))
    parser.add_argument("arm")
    args = parser.parse_args()
    if args.case == "pipeline-contract":
        assert args.arm in {"candidate-resume", "candidate-pipeline"}
        result = pipeline(args.arm)
    else:
        assert args.arm in {"retained", "rewritten"}
        result = forecast(args.arm)
    print(json.dumps(result))
