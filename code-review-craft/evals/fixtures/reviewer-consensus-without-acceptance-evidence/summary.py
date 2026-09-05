import argparse
import json
from pathlib import Path


def summarize(orders):
    return {
        "count": len(orders),
        "total_cents": sum(order["amount_cents"] for order in orders),
    }


def main():
    parser = argparse.ArgumentParser(description="Summarize validated orders.")
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    orders = json.loads(args.input.read_text(encoding="utf-8"))
    print(json.dumps(summarize(orders)))


if __name__ == "__main__":
    main()
