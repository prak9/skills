"""Small Markdown primitives used by the plan validator."""

from __future__ import annotations

import re
from pathlib import Path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"File is not UTF-8: {path}") from exc
    except OSError as exc:
        reason = exc.strerror or type(exc).__name__
        raise RuntimeError(f"Cannot read file: {path}: {reason}") from exc


def read_text_for_validation(path: Path, errors: list[str]) -> str:
    """Read one validation input without turning an encoding error into a traceback."""
    try:
        return read_text(path)
    except RuntimeError as exc:
        errors.append(str(exc))
        return ""


def has_required(text: str, item: str) -> bool:
    """Match an exact Markdown heading or bold field label."""
    for line in text.splitlines():
        heading = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if heading:
            title = re.sub(r"^\d+\.\s*", "", heading.group(1).strip())
            if (item.endswith(" ") and title.startswith(item)) or title == item:
                return True
        bold = re.match(r"^(?:[-*+]\s+)?\*\*([^*]+?)\*\*\s*:?.*$", line)
        if bold and bold.group(1).rstrip(":").strip() == item.strip():
            return True
    return False


def check_required_items(path: Path, text: str, required: list, errors: list[str]) -> None:
    for item in required:
        options = (item,) if isinstance(item, str) else item
        if not any(has_required(text, option) for option in options):
            errors.append(f"{path} is missing required section or field: {' / '.join(options)}")


def metadata_value(text: str, *labels: str) -> str | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    match = re.search(
        rf"^-\s*(?:{label_pattern})[：:]\s*(.+?)\s*$",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    if not match:
        return None
    value = match.group(1).strip()
    if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
        value = value[1:-1].strip()
    return value


def find_placeholders(path: Path, text: str, warnings: list[str]) -> None:
    placeholders = len(re.findall(r"<[^>\n]{1,120}>", text))
    if placeholders:
        warnings.append(f"{path} still contains {placeholders} template placeholders")


def has_closing_code_delimiter(content: str, start: int, delimiter: int) -> bool:
    index = start
    while index < len(content):
        if content[index] != "`":
            index += 1
            continue
        end = index + 1
        while end < len(content) and content[end] == "`":
            end += 1
        if end - index == delimiter:
            return True
        index = end
    return False


def split_markdown_table_row(line: str) -> list[str]:
    """Split a pipe table row while preserving escaped pipes and inline-code pipes."""
    content = line.strip()[1:-1]
    cells: list[str] = []
    cell: list[str] = []
    code_delimiter = 0
    index = 0
    while index < len(content):
        character = content[index]
        if character == "`":
            end = index + 1
            while end < len(content) and content[end] == "`":
                end += 1
            delimiter = end - index
            if code_delimiter == 0 and has_closing_code_delimiter(
                content, end, delimiter
            ):
                code_delimiter = delimiter
            elif code_delimiter == delimiter:
                code_delimiter = 0
            cell.extend(content[index:end])
            index = end
            continue
        if character == "|" and code_delimiter == 0:
            trailing_backslashes = 0
            for previous in reversed(cell):
                if previous != "\\":
                    break
                trailing_backslashes += 1
            if trailing_backslashes % 2:
                cell.pop()
                cell.append("|")
            else:
                cells.append("".join(cell).strip())
                cell = []
            index += 1
            continue
        cell.append(character)
        index += 1
    cells.append("".join(cell).strip())
    return cells


def iter_table_rows(text: str):
    """Yield (header_cells, row_cells) for each data row of each Markdown table."""
    header: list[str] | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|") and len(stripped) > 2):
            header = None
            continue
        cells = split_markdown_table_row(stripped)
        if all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            continue
        if header is None:
            header = cells
        else:
            yield header, cells


def norm_cell(cell: str) -> str:
    return cell.strip("`").strip()


def check_table_shapes(path: Path, text: str, errors: list[str]) -> None:
    for header, cells in iter_table_rows(text):
        if len(cells) == len(header):
            continue
        row_id = norm_cell(cells[0]) if cells else "?"
        errors.append(
            f"{path} table row `{row_id}` has column count {len(cells)}; "
            f"expected {len(header)}"
        )


def markdown_heading_section(text: str, title: str) -> str | None:
    lines = text.splitlines()
    start: int | None = None
    level: int | None = None
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        heading_title = re.sub(r"^\d+\.\s*", "", match.group(2).strip())
        if start is None:
            if heading_title == title:
                start = index + 1
                level = len(match.group(1))
            continue
        if len(match.group(1)) <= level:
            return "\n".join(lines[start:index])
    if start is not None:
        return "\n".join(lines[start:])
    return None


def markdown_h2_section(text: str, title: str) -> str | None:
    return markdown_heading_section(text, title)


def bold_field_section(text: str, title: str) -> str | None:
    pattern = rf"^\*\*{re.escape(title)}:\*\*\s*(?P<body>.*?)(?=^\*\*[^\n]+?:\*\*|^##\s+|\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
    return match.group("body") if match else None


def table_as_mapping(section: str | None) -> dict[str, str]:
    if section is None:
        return {}
    for header, _ in iter_table_rows(section):
        normalized = [norm_cell(cell).lower() for cell in header]
        if "field" not in normalized or "content" not in normalized:
            continue
        field_idx = normalized.index("field")
        content_idx = normalized.index("content")
        result: dict[str, str] = {}
        for row_header, row_cells in iter_table_rows(section):
            if row_header != header or max(field_idx, content_idx) >= len(row_cells):
                continue
            result[norm_cell(row_cells[field_idx])] = norm_cell(row_cells[content_idx])
        return result
    return {}


def section_status_rows(section: str | None) -> list[tuple[str, str]]:
    if section is None:
        return []
    rows: list[tuple[str, str]] = []
    for header, cells in iter_table_rows(section):
        normalized = [norm_cell(cell).lower() for cell in header]
        if "status" not in normalized and "状态" not in normalized:
            continue
        status_idx = (
            normalized.index("status")
            if "status" in normalized
            else normalized.index("状态")
        )
        if status_idx >= len(cells):
            continue
        rows.append((norm_cell(cells[0]), norm_cell(cells[status_idx])))
    return rows


def checklist_unchecked(section: str | None) -> list[str]:
    if section is None:
        return []
    return re.findall(r"^\s*-\s+\[\s\]\s+(.+)$", section, flags=re.MULTILINE)


def checklist_items(section: str | None) -> list[str]:
    if section is None:
        return []
    return re.findall(r"^\s*-\s+\[[ xX]\]\s+(.+)$", section, flags=re.MULTILINE)


def bullet_field(section: str | None, label: str) -> str | None:
    if section is None:
        return None
    match = re.search(
        rf"^-\s*{re.escape(label)}[：:]\s*(.+?)\s*$",
        section,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    return match.group(1).strip() if match else None
