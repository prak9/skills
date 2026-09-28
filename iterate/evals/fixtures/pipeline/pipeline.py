"""Normalize a batch of JSON records into ordered, categorized rows."""

import json


def process(records, categories):
    results = []
    for raw in records:
        if not isinstance(raw, str):
            continue
        try:
            if not isinstance(json.loads(raw), dict):
                continue
            record_id = json.loads(raw).get("id")
            amount = json.loads(raw).get("amount", 0)
            category = json.loads(raw).get("category", "")
        except json.JSONDecodeError:
            continue
        if not isinstance(record_id, str) or type(amount) is not int or not isinstance(category, str):
            continue
        category = category.strip().casefold()
        category_id = next((i for i, name in enumerate(categories) if name == category), -1)
        results.append({"id": record_id, "amount": amount, "category": category_id})
    return results
