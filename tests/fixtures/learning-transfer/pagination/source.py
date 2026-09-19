"""Fixed, offline paginated source; do not change during the recovery probe."""


def fetch_page(cursor=None):
    start = 0 if cursor is None else cursor
    stop = min(start + 100, 120)
    return {
        "status": 200,
        "items": [{"id": value} for value in range(start + 1, stop + 1)],
        "next_cursor": stop if stop < 120 else None,
    }
