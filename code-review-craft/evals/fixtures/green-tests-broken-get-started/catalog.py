import argparse
import json
from pathlib import Path


def render_catalog(items):
    return {"count": len(items), "names": [item["name"] for item in items]}


def main():
    parser = argparse.ArgumentParser(description="Export a JSON item catalog.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    items = json.loads(args.input.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "catalog.json").write_text(
        json.dumps(render_catalog(items)) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
