from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from plan_markdown import split_markdown_table_row  # noqa: E402


class MarkdownTableTests(unittest.TestCase):
    def test_splits_plain_table_row(self) -> None:
        self.assertEqual(["A", "B"], split_markdown_table_row("| A | B |"))

    def test_preserves_pipe_inside_inline_code(self) -> None:
        self.assertEqual(
            ["V-001", "`printf 'a|b'`", "完成"],
            split_markdown_table_row("| V-001 | `printf 'a|b'` | 完成 |"),
        )

    def test_preserves_escaped_pipe(self) -> None:
        self.assertEqual(
            ["A", "left|right", "B"],
            split_markdown_table_row(r"| A | left\|right | B |"),
        )

    def test_unclosed_code_span_does_not_hide_separator(self) -> None:
        self.assertEqual(
            ["A", "`left", "right", "B"],
            split_markdown_table_row("| A | `left|right | B |"),
        )


if __name__ == "__main__":
    unittest.main()
