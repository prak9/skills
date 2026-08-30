#!/usr/bin/env python3
"""Render a conservative Markdown subset as paste-ready WeChat article HTML."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html import escape
from pathlib import Path
from urllib.parse import urlsplit


THEMES = {
    "ink": {
        "name": "墨蓝刊读",
        "accent": "#365A7A",
        "accent_dark": "#243F57",
        "accent_soft": "#EAF0F5",
        "text": "#222A31",
        "muted": "#66727D",
        "surface": "#F6F8FA",
        "border": "#D8E0E7",
        "canvas": "#FFFFFF",
    },
    "moss": {
        "name": "苔绿笔记",
        "accent": "#537965",
        "accent_dark": "#315342",
        "accent_soft": "#EDF4EF",
        "text": "#26332C",
        "muted": "#68766E",
        "surface": "#F5F8F6",
        "border": "#D7E2DB",
        "canvas": "#FFFFFF",
    },
    "paper": {
        "name": "暖纸随笔",
        "accent": "#9A6948",
        "accent_dark": "#68452F",
        "accent_soft": "#F7EFE6",
        "text": "#392F29",
        "muted": "#7D7068",
        "surface": "#FBF7F1",
        "border": "#E7D9CB",
        "canvas": "#FFFDF9",
    },
}

COLOR_KEYS = {
    "accent",
    "accent_dark",
    "accent_soft",
    "text",
    "muted",
    "surface",
    "border",
    "canvas",
}
THEME_KEYS = COLOR_KEYS | {"name"}
HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
FENCE = re.compile(r"^\s*```([A-Za-z0-9_+.-]*)\s*$")
IMAGE = re.compile(r"^\s*!\[([^]]*)\]\(([^)]+)\)\s*$")
UNORDERED = re.compile(r"^\s*[-+*]\s+(.+)$")
ORDERED = re.compile(r"^\s*(\d+)[.)]\s+(.+)$")
QUOTE = re.compile(r"^\s*>\s?(.*)$")
RULE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
INLINE = re.compile(
    r"(`[^`\n]+`|\*\*[^*\n]+\*\*|==[^=\n]+==|\[[^]\n]+\]\([^)\n]+\))"
)
CJK = re.compile(r"[\u3400-\u9fff]")


def _rgb(color: str) -> tuple[int, int, int]:
    return tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))  # type: ignore[return-value]


def _luminance(color: str) -> float:
    channels = []
    for value in _rgb(color):
        channel = value / 255
        channels.append(channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(first: str, second: str) -> float:
    high, low = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def validate_theme(theme: dict[str, str]) -> None:
    missing = THEME_KEYS - theme.keys()
    unknown = theme.keys() - THEME_KEYS
    if missing:
        raise ValueError(f"主题缺少字段：{', '.join(sorted(missing))}")
    if unknown:
        raise ValueError(f"主题包含未知字段：{', '.join(sorted(unknown))}")
    if not isinstance(theme["name"], str) or not theme["name"].strip():
        raise ValueError("主题 name 必须是非空字符串")
    for key in COLOR_KEYS:
        if not isinstance(theme[key], str) or not HEX_COLOR.fullmatch(theme[key]):
            raise ValueError(f"主题 {key} 必须是六位十六进制颜色")
    if contrast_ratio(theme["text"], theme["canvas"]) < 4.5:
        raise ValueError("主题 text 与 canvas 对比度低于 4.5:1")
    if contrast_ratio(theme["accent_dark"], theme["accent_soft"]) < 4.5:
        raise ValueError("主题 accent_dark 与 accent_soft 对比度低于 4.5:1")


def load_theme(name: str = "ink", theme_file: Path | None = None) -> tuple[dict[str, str], str]:
    if theme_file is None:
        if name not in THEMES:
            raise ValueError(f"未知主题 {name!r}；可选：{', '.join(THEMES)}")
        theme = dict(THEMES[name])
        slug = name
    else:
        payload = json.loads(theme_file.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("自定义主题必须是 JSON 对象")
        theme = dict(THEMES["ink"])
        theme.update(payload)
        slug = re.sub(r"[^a-z0-9-]+", "-", theme_file.stem.lower()).strip("-") or "custom"
    validate_theme(theme)
    return theme, slug


def safe_url(value: str) -> str:
    value = value.strip()
    parsed = urlsplit(value)
    if not value or value.startswith("//") or (parsed.scheme and parsed.scheme not in {"http", "https"}):
        raise ValueError(f"不安全或不支持的 URL：{value!r}")
    return value


def leaf(text: str) -> str:
    return f'<span leaf="">{escape(text, quote=True)}</span>'


def render_inline(text: str, theme: dict[str, str]) -> str:
    parts: list[str] = []
    cursor = 0
    for match in INLINE.finditer(text):
        if match.start() > cursor:
            parts.append(leaf(text[cursor : match.start()]))
        token = match.group(0)
        if token.startswith("**"):
            parts.append(
                f'<strong style="font-weight:750;color:{theme["accent_dark"]};">'
                f"{leaf(token[2:-2])}</strong>"
            )
        elif token.startswith("=="):
            parts.append(
                f'<span style="background:{theme["accent_soft"]};color:{theme["accent_dark"]};'
                f'padding:1px 4px;border-radius:3px;">{leaf(token[2:-2])}</span>'
            )
        elif token.startswith("`"):
            parts.append(
                f'<span style="background:{theme["surface"]};color:{theme["accent_dark"]};'
                f'padding:1px 5px;border-radius:4px;font-family:Consolas,Monaco,monospace;'
                f'font-size:14px;">{leaf(token[1:-1])}</span>'
            )
        else:
            link = re.fullmatch(r"\[([^]]+)\]\(([^)]+)\)", token)
            if link is None:
                parts.append(leaf(token))
            else:
                href = escape(safe_url(link.group(2)), quote=True)
                parts.append(
                    f'<a href="{href}" style="color:{theme["accent_dark"]};'
                    f'text-decoration:underline;text-decoration-color:{theme["accent"]};">'
                    f"{leaf(link.group(1))}</a>"
                )
        cursor = match.end()
    if cursor < len(text):
        parts.append(leaf(text[cursor:]))
    return "".join(parts) or leaf("")


def _join_soft(lines: list[str]) -> str:
    result = ""
    for raw in lines:
        item = raw.strip()
        if not item:
            continue
        if not result:
            result = item
            continue
        separator = ""
        if not (CJK.search(result[-1]) and CJK.match(item[0])):
            separator = " "
        result += separator + item
    return result


def _frontmatter(lines: list[str]) -> tuple[dict[str, str], list[str]]:
    if not lines or lines[0].strip() != "---":
        return {}, lines
    for index in range(1, len(lines)):
        if lines[index].strip() != "---":
            continue
        metadata: dict[str, str] = {}
        for line in lines[1:index]:
            key, separator, value = line.partition(":")
            if separator and key.strip() in {"title", "author"}:
                metadata[key.strip()] = value.strip().strip('"\'')
        return metadata, lines[index + 1 :]
    return {}, lines


def _starts_block(line: str) -> bool:
    return bool(
        not line.strip()
        or FENCE.match(line)
        or HEADING.match(line)
        or IMAGE.match(line)
        or QUOTE.match(line)
        or RULE.match(line)
        or UNORDERED.match(line)
        or ORDERED.match(line)
    )


def _cover(title: str, theme: dict[str, str], author: str = "") -> str:
    byline = ""
    if author:
        byline = (
            f'<p style="margin:10px 0 0;font-size:13px;line-height:1.6;color:{theme["muted"]};">'
            f'{leaf(author)}</p>'
        )
    return (
        f'<section style="padding:8px 0 24px;margin:0 0 28px;border-bottom:1px solid {theme["border"]};">'
        f'<p style="margin:0;font-size:29px;line-height:1.35;font-weight:800;letter-spacing:-0.4px;'
        f'color:{theme["text"]};">{render_inline(title, theme)}</p>{byline}</section>'
    )


def _section_heading(number: int, title: str, theme: dict[str, str]) -> str:
    return (
        f'<section style="margin:34px 0 18px;padding:0 0 10px;border-bottom:1px solid {theme["border"]};">'
        f'<p style="margin:0 0 5px;font-size:12px;line-height:1.2;letter-spacing:2px;'
        f'font-weight:700;color:{theme["accent"]};">{leaf(f"SECTION {number:02d}")}</p>'
        f'<p style="margin:0;font-size:22px;line-height:1.45;font-weight:800;color:{theme["text"]};">'
        f'{render_inline(title, theme)}</p></section>'
    )


def _subheading(title: str, theme: dict[str, str]) -> str:
    return (
        f'<p style="margin:27px 0 12px;padding-left:11px;border-left:3px solid {theme["accent"]};'
        f'font-size:17px;line-height:1.55;font-weight:750;color:{theme["text"]};">'
        f'{render_inline(title, theme)}</p>'
    )


def _paragraph(text: str, theme: dict[str, str]) -> str:
    return (
        f'<p style="margin:0 0 18px;font-size:16px;line-height:1.85;letter-spacing:0.15px;'
        f'color:{theme["text"]};text-align:left;">{render_inline(text, theme)}</p>'
    )


def _quote(text: str, theme: dict[str, str]) -> str:
    return (
        f'<section style="margin:4px 0 22px;padding:15px 17px;background:{theme["accent_soft"]};'
        f'border-left:4px solid {theme["accent"]};border-radius:0 8px 8px 0;">'
        f'<p style="margin:0;font-size:16px;line-height:1.8;font-weight:650;color:{theme["accent_dark"]};">'
        f'{render_inline(text, theme)}</p></section>'
    )


def _list(items: list[tuple[str, str]], theme: dict[str, str]) -> str:
    rows = []
    for marker, text in items:
        rows.append(
            f'<section style="display:flex;margin:0 0 10px;align-items:flex-start;">'
            f'<span style="display:inline-block;min-width:28px;margin-right:8px;color:{theme["accent"]};'
            f'font-size:14px;line-height:1.85;font-weight:750;">{leaf(marker)}</span>'
            f'<p style="margin:0;flex:1;font-size:16px;line-height:1.85;color:{theme["text"]};">'
            f'{render_inline(text, theme)}</p></section>'
        )
    return (
        f'<section style="margin:2px 0 20px;padding:14px 16px;background:{theme["surface"]};'
        f'border:1px solid {theme["border"]};border-radius:9px;">{"".join(rows)}</section>'
    )


def _code_line(line: str) -> str:
    expanded = line.expandtabs(4)
    indent = len(expanded) - len(expanded.lstrip(" "))
    raw = "&nbsp;" * indent + escape(expanded[indent:], quote=True)
    return raw or "&#8203;"


def _code(lines: list[str], language: str, theme: dict[str, str]) -> str:
    rendered = "".join(
        f'<p style="margin:0;font-family:Consolas,Monaco,monospace;font-size:13px;line-height:1.65;'
        f'color:#E7ECF1;overflow-wrap:anywhere;">'
        f'<span leaf="">{_code_line(line)}</span></p>'
        for line in lines
    )
    return (
        '<section style="margin:4px 0 22px;border-radius:8px;overflow:hidden;background:#202A33;">'
        f'<p style="margin:0;padding:8px 13px;background:#182129;font-family:Consolas,Monaco,monospace;'
        f'font-size:11px;line-height:1.4;letter-spacing:1px;color:#9EADB9;">'
        f'{leaf((language or "CODE").upper())}</p>'
        f'<section style="padding:12px 14px;">{rendered}</section></section>'
    )


def _image(alt: str, source: str, theme: dict[str, str]) -> str:
    src = escape(safe_url(source), quote=True)
    caption = ""
    if alt.strip():
        caption = (
            f'<p style="margin:8px 0 0;text-align:center;font-size:12px;line-height:1.6;'
            f'color:{theme["muted"]};">{leaf(alt.strip())}</p>'
        )
    return (
        f'<section style="margin:4px 0 24px;padding:6px;background:{theme["canvas"]};'
        f'border:1px solid {theme["border"]};border-radius:9px;">'
        f'<span leaf=""><img src="{src}" alt="{escape(alt, quote=True)}" '
        f'style="max-width:100%;height:auto;display:block;margin:0 auto;border-radius:5px;"></span>'
        f'{caption}</section>'
    )


def render_document(markdown: str, theme: dict[str, str], fallback_title: str = "文章") -> str:
    validate_theme(theme)
    metadata, lines = _frontmatter(markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n"))
    title = metadata.get("title", "").strip()
    body = list(lines)
    for index, line in enumerate(body):
        match = HEADING.match(line)
        if match and len(match.group(1)) == 1:
            title = match.group(2).strip()
            del body[index]
            break
    title = title or fallback_title

    blocks = [_cover(title, theme, metadata.get("author", "").strip())]
    section_number = 0
    index = 0
    while index < len(body):
        line = body[index]
        if not line.strip():
            index += 1
            continue

        fence = FENCE.match(line)
        if fence:
            language = fence.group(1)
            code_lines: list[str] = []
            index += 1
            while index < len(body) and not FENCE.match(body[index]):
                code_lines.append(body[index])
                index += 1
            if index >= len(body):
                raise ValueError("代码块缺少结束的 ```")
            blocks.append(_code(code_lines, language, theme))
            index += 1
            continue

        heading = HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            if level == 2:
                section_number += 1
                blocks.append(_section_heading(section_number, heading.group(2), theme))
            else:
                blocks.append(_subheading(heading.group(2), theme))
            index += 1
            continue

        image = IMAGE.match(line)
        if image:
            blocks.append(_image(image.group(1), image.group(2), theme))
            index += 1
            continue

        quote = QUOTE.match(line)
        if quote:
            quote_lines = []
            while index < len(body):
                current = QUOTE.match(body[index])
                if current is None:
                    break
                quote_lines.append(current.group(1))
                index += 1
            blocks.append(_quote(_join_soft(quote_lines), theme))
            continue

        if RULE.match(line):
            blocks.append(
                f'<section style="margin:28px 0;border-top:1px solid {theme["border"]};"></section>'
            )
            index += 1
            continue

        unordered = UNORDERED.match(line)
        ordered = ORDERED.match(line)
        if unordered or ordered:
            items: list[tuple[str, str]] = []
            ordered_mode = ordered is not None
            while index < len(body):
                current_ordered = ORDERED.match(body[index])
                current_unordered = UNORDERED.match(body[index])
                if ordered_mode and current_ordered:
                    items.append((current_ordered.group(1).zfill(2), current_ordered.group(2)))
                elif not ordered_mode and current_unordered:
                    items.append(("•", current_unordered.group(1)))
                else:
                    break
                index += 1
            blocks.append(_list(items, theme))
            continue

        paragraph_lines = [line]
        index += 1
        while index < len(body) and not _starts_block(body[index]):
            paragraph_lines.append(body[index])
            index += 1
        blocks.append(_paragraph(_join_soft(paragraph_lines), theme))

    root_style = (
        f'max-width:677px;margin:0 auto;padding:24px 20px;box-sizing:border-box;'
        f'background:{theme["canvas"]};color:{theme["text"]};font-family:-apple-system,'
        "BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"
        f'font-size:16px;line-height:1.85;overflow-wrap:anywhere;'
    )
    return f'<section style="{root_style}">\n' + "\n".join(blocks) + "\n</section>\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Markdown input file")
    parser.add_argument("-o", "--output", type=Path, help="Output HTML fragment")
    parser.add_argument("--title", help="Fallback title when Markdown has no H1/frontmatter title")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--theme", choices=tuple(THEMES), help="Built-in theme (default: ink)")
    group.add_argument("--theme-file", type=Path, help="Project-level JSON theme overrides")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        theme, slug = load_theme(args.theme or "ink", args.theme_file)
        source = args.input.read_text(encoding="utf-8")
        output = args.output or args.input.with_name(f"{args.input.stem}-wechat-{slug}.html")
        fragment = render_document(source, theme, args.title or args.input.stem)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(fragment, encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Rendered {args.input} -> {output} ({theme['name']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
