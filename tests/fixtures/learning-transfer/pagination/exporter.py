from source import fetch_page


def export_rows():
    page = fetch_page()
    return {"status": page["status"], "rows": page["items"]}
