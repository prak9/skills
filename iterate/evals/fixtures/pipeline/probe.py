"""Run a candidate against independent expected outputs and count actual work."""

import argparse
import hashlib
import json
from pathlib import Path
import random


def dataset(name):
    width, size, repeats = {"small": (17, 24, 3), "wide": (97, 72, 4)}[name]
    rng = random.Random(701 + width)
    categories = [f"tag-{i:03d}" for i in range(width)]
    pool = [json.dumps({"id": f"row-{i}", "amount": rng.randrange(-50, 500),
                        "category": " " + rng.choice(categories).upper() + " "})
            for i in range(size)]
    records = pool * repeats
    rng.shuffle(records)
    records += ["{", "null", "[]", "7", None, 42, "{}",
                '{"id":"missing"}', '{"id":"unknown","category":"unknown"}',
                '{"id":"negative","amount":-9,"category":"TAG-000"}',
                '{"id":"float","amount":1.5}', '{"id":"bool","amount":true}',
                '{"id":"null","category":null}', '{"id":2}',
                '{"id":"empty","category":"  "}', '{"id":"unicode","category":"Straße"}']
    return records, categories


def reference(records, categories):
    result = []
    for raw in records:
        if not isinstance(raw, str):
            continue
        try:
            item = json.JSONDecoder().decode(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            continue
        amount, category = item.get("amount", 0), item.get("category", "")
        if type(amount) is not int or not isinstance(category, str):
            continue
        key = category.strip().casefold()
        position = categories.index(key) if key in categories else -1
        result.append(dict(id=item["id"], amount=amount, category=position))
    return result


def measure(candidate, name):
    source = candidate.read_bytes()
    records, categories = dataset(name)
    batches = [(records, categories), (list(reversed(records)), list(reversed(categories)))]
    expected = [reference(rows, labels) for rows, labels in batches]
    work = {"decode": 0, "lookup": 0}

    class Key(str):
        def __eq__(self, other):
            work["lookup"] += 1
            return str.__eq__(self, other)

        def __hash__(self):
            work["lookup"] += 1
            return str.__hash__(self)

    original_decode = json.JSONDecoder.decode

    def decode(self, *args, **kwargs):
        work["decode"] += 1
        return original_decode(self, *args, **kwargs)

    report = {"candidate_sha256": hashlib.sha256(source).hexdigest(),
              "dataset_id": name + "-v1", "correctness": False, "work": work}
    try:
        namespace = {"__name__": "candidate", "__file__": str(candidate)}
        exec(compile(source, str(candidate), "exec"), namespace)
        json.JSONDecoder.decode = decode
        try:
            actual = [namespace["process"](list(rows), [Key(label) for label in labels])
                      for rows, labels in batches]
        finally:
            json.JSONDecoder.decode = original_decode
        report["correctness"] = json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)
    except Exception as error:
        report["error"] = type(error).__name__ + ": " + str(error)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=Path(__file__).with_name("pipeline.py"))
    parser.add_argument("--dataset", choices=("small", "wide"), default="small")
    args = parser.parse_args()
    report = measure(args.candidate, args.dataset)
    print(json.dumps(report, sort_keys=True))
    return 0 if report["correctness"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
