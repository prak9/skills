#!/usr/bin/env python3
"""Validate a WeChat article HTML fragment against a conservative contract."""

from __future__ import annotations

import argparse
import re
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ALLOWED_TAGS = {"section", "p", "span", "strong", "em", "a", "br", "img"}
VOID_TAGS = {"br", "img"}
ALLOWED_ATTRS = {
    "section": {"style"},
    "p": {"style"},
    "span": {"style", "leaf"},
    "strong": {"style"},
    "em": {"style"},
    "a": {"style", "href"},
    "br": {"style"},
    "img": {"style", "src", "alt"},
}
FORBIDDEN_STYLE = (
    (re.compile(r"position\s*:\s*(?:fixed|absolute|sticky)", re.I), "不支持固定或绝对定位"),
    (re.compile(r"float\s*:", re.I), "不支持 float"),
    (re.compile(r"display\s*:\s*grid", re.I), "不支持 display:grid"),
    (re.compile(r"var\s*\(\s*--", re.I), "不支持 CSS 变量"),
    (re.compile(r"@(?:media|keyframes|import)", re.I), "不支持 CSS at-rule"),
    (re.compile(r"white-space\s*:\s*pre(?:-wrap)?", re.I), "不支持 pre/pre-wrap 空白模式"),
    (re.compile(r"expression\s*\(|javascript\s*:", re.I), "包含危险 CSS 表达式"),
    (re.compile(r"url\s*\(", re.I), "正文内联样式不允许 url()"),
)


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def _url_error(value: str) -> str | None:
    value = unescape(value).strip()
    parsed = urlsplit(value)
    if not value:
        return "URL 为空"
    if value.startswith("//"):
        return "不接受省略协议的 URL"
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return f"不支持 URL 协议 {parsed.scheme!r}"
    return None


class FragmentChecker(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.leaf_depth = 0
        self.leaf_count = 0
        self.root_count = 0
        self.root_tags: list[str] = []
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.text_nodes = 0

    def _check_attrs(self, tag: str, attrs: list[tuple[str, str | None]]) -> bool:
        names = [name for name, _ in attrs]
        if len(names) != len(set(names)):
            self.errors.append(f"<{tag}> 存在重复属性")
        allowed = ALLOWED_ATTRS.get(tag, set())
        values = dict(attrs)
        for name, value in attrs:
            if name.startswith("on"):
                self.errors.append(f"<{tag}> 不允许事件属性 {name}")
            elif name not in allowed:
                self.errors.append(f"<{tag}> 不允许属性 {name}")
            if name == "style" and value:
                for pattern, message in FORBIDDEN_STYLE:
                    if pattern.search(value):
                        self.errors.append(f"<{tag}> 样式违规：{message}")

        if tag == "a":
            href = values.get("href")
            if href is None:
                self.errors.append("<a> 缺少 href")
            elif error := _url_error(href):
                self.errors.append(f"<a> {error}")
        if tag == "img":
            src = values.get("src")
            if src is None:
                self.errors.append("<img> 缺少 src")
            elif error := _url_error(src):
                self.errors.append(f"<img> {error}")
            elif not urlsplit(unescape(src)).scheme:
                self.warnings.append(f"图片仍使用相对路径：{src}；粘贴前通常需要上传到微信素材库")
            if "alt" not in values:
                self.warnings.append("<img> 缺少 alt")
        return tag == "span" and "leaf" in values

    def _open(self, tag: str, attrs: list[tuple[str, str | None]], self_closing: bool) -> None:
        tag = tag.lower()
        if not self.stack:
            self.root_count += 1
            self.root_tags.append(tag)
        if tag not in ALLOWED_TAGS:
            self.errors.append(f"正文不允许 <{tag}> 标签")
        is_leaf = self._check_attrs(tag, attrs)
        if is_leaf:
            self.leaf_depth += 1
            self.leaf_count += 1
        if self_closing or tag in VOID_TAGS:
            if is_leaf:
                self.leaf_depth -= 1
            if self_closing and tag not in VOID_TAGS:
                self.errors.append(f"<{tag}> 不应自闭合")
            return
        self.stack.append((tag, is_leaf))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._open(tag, attrs, False)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._open(tag, attrs, True)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in VOID_TAGS:
            self.errors.append(f"<{tag}> 是空元素，不应有结束标签")
            return
        if not self.stack:
            self.errors.append(f"多余结束标签 </{tag}>")
            return
        opened, was_leaf = self.stack.pop()
        if opened != tag:
            self.errors.append(f"标签嵌套错误：<{opened}> 被 </{tag}> 关闭")
        if was_leaf:
            self.leaf_depth -= 1

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text:
            return
        self.text_nodes += 1
        if self.leaf_depth == 0:
            snippet = text[:28] + ("…" if len(text) > 28 else "")
            self.errors.append(f"文本未放在 <span leaf=\"\"> 内：{snippet!r}")

    def handle_comment(self, data: str) -> None:
        self.errors.append("干净正文不应包含 HTML 注释")

    def handle_decl(self, decl: str) -> None:
        self.errors.append("干净正文不应包含 DOCTYPE")

    def handle_pi(self, data: str) -> None:
        self.errors.append("干净正文不应包含处理指令")


def validate_html(content: str) -> tuple[list[str], list[str]]:
    checker = FragmentChecker()
    try:
        checker.feed(content)
        checker.close()
    except Exception as exc:  # HTMLParser is tolerant, but surface unexpected parser failures.
        checker.errors.append(f"HTML 解析失败：{exc}")

    if checker.stack:
        checker.errors.append("存在未闭合标签：" + ", ".join(f"<{tag}>" for tag, _ in checker.stack))
    if checker.root_count != 1 or checker.root_tags != ["section"]:
        checker.errors.append("正文必须且只能有一个顶层 <section>")
    if checker.text_nodes == 0:
        checker.errors.append("正文没有可见文本")
    if checker.leaf_count == 0:
        checker.errors.append("正文没有 <span leaf=\"\"> 包裹")
    return _unique(checker.errors), _unique(checker.warnings)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", type=Path, help="HTML fragment; omit with --stdin")
    parser.add_argument("--stdin", action="store_true", help="Read HTML from standard input")
    parser.add_argument("--strict-warnings", action="store_true", help="Return failure when warnings remain")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.stdin and args.file is None:
        print("ERROR: provide an HTML file or --stdin", file=sys.stderr)
        return 2
    try:
        content = sys.stdin.read() if args.stdin else args.file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors, warnings = validate_html(content)
    print(f"WeChat HTML validation: {args.file or '<stdin>'}")
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    if not errors and not warnings:
        print("PASS: fragment matches the conservative compatibility contract")
    elif not errors:
        print("PASS WITH WARNINGS: review warnings before delivery")
    return 1 if errors or (warnings and args.strict_warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
