from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLAN_SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PLAN_SKILL_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import slim_plan  # noqa: E402


class SlimPlanTests(unittest.TestCase):
    def _run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "slim_plan.py"), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def _run_validate(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "validate_plan.py"), *extra, str(root)],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_dry_run_and_apply_archive_banners_sections_and_terminal_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            banners = "\n\n".join(f"> 2026-11-{20 - i:02d} banner {i}" for i in range(7))
            rows = [
                f"| NODE-{i:03d} | 完成 | done action {i} | ok | ev-{i} | - |"
                for i in range(1, 9)
            ]
            rows.append("| NODE-009 | 进行中 | active action | check | - | - |")
            program = (
                f"{banners}\n\n"
                "# Program: Demo\n\n"
                "- Clean state: `Due`\n"
                "- Last clean: `Not run`\n\n"
                "## Current Status\n\nActive work.\n\n"
                "## Historical Execution Readiness Gate\n\nOld gate details.\n\n"
                "## 2026-09-17 权威接力：TASK-071\n\nOld handoff.\n\n"
                "## Node Status\n\n"
                "| Node | Status | Action | Verification | Evidence | Reflection |\n"
                "|---|---|---|---|---|---|\n"
                + "\n".join(rows)
                + "\n"
            )
            (root / "program.md").write_text(program, encoding="utf-8")

            dry = self._run_cli("--dry-run", "--json", str(root))
            self.assertEqual(dry.returncode, 0, dry.stderr)
            dry_report = json.loads(dry.stdout)
            self.assertTrue(dry_report["dry_run"])
            self.assertEqual(dry_report["archived_banners"], 4)
            self.assertEqual(len(dry_report["archived_sections"]), 2)
            self.assertEqual(dry_report["archived_table_rows"], 3)
            self.assertFalse((root / "archive").exists())
            self.assertEqual((root / "program.md").read_text(encoding="utf-8"), program)

            applied = slim_plan.slim_plan(root, today="2026-11-20")
            self.assertTrue(applied["changed_program"])
            self.assertLess(applied["after_lines"], applied["before_lines"])

            slimmed = (root / "program.md").read_text(encoding="utf-8")
            archive_path = root / "archive" / "program-archive-2026-11-20.md"
            self.assertTrue(archive_path.is_file())
            archived_text = archive_path.read_text(encoding="utf-8")

            # Active content and recent banners/rows preserved
            self.assertIn("## Current Status", slimmed)
            self.assertIn("NODE-009", slimmed)
            self.assertIn("NODE-008", slimmed)
            self.assertIn("banner 0", slimmed)
            self.assertIn("banner 2", slimmed)
            self.assertIn("- Clean state: `Not due`", slimmed)
            self.assertIn("- Last clean: `2026-11-20`", slimmed)
            self.assertIn("## Archive Index", slimmed)

            # Displaced content preserved verbatim in archive
            self.assertNotIn("banner 6", slimmed)
            self.assertIn("banner 6", archived_text)
            self.assertNotIn("## Historical Execution Readiness Gate", slimmed)
            self.assertIn("## Historical Execution Readiness Gate", archived_text)
            self.assertNotIn("NODE-001", slimmed)
            self.assertIn("NODE-001", archived_text)

            # Idempotent on second run
            second = slim_plan.slim_plan(root, today="2026-11-20")
            self.assertFalse(second["changed_program"])
            self.assertEqual(second["archived_banners"], 0)
            self.assertEqual(second["archived_sections"], [])
            self.assertEqual(second["archived_table_rows"], 0)

    def test_memory_index_and_validate_context_budget_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIR / "init_plan.py"),
                    str(root),
                    "--title",
                    "Budget Check",
                    "--profile",
                    "full",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(init.returncode, 0, init.stderr)

            # Bloat memory.md past 500 lines
            mem_path = root / "memory.md"
            mem_text = mem_path.read_text(encoding="utf-8")
            extra_findings = "\n".join(
                f"- **F-{i:03d}**: verified finding {i}" for i in range(1, 520)
            )
            mem_path.write_text(mem_text + "\n" + extra_findings + "\n", encoding="utf-8")

            val_before = self._run_validate(root, "--json")
            data_before = json.loads(val_before.stdout)
            self.assertTrue(
                any("memory-index.jsonl" in w for w in data_before["warnings"]),
                data_before["warnings"],
            )

            report = slim_plan.slim_plan(root, today="2026-11-20")
            self.assertTrue(report["memory_indexed"])
            self.assertGreaterEqual(report["memory_index_entries"], 519)
            index_path = root / "archive" / "memory-index.jsonl"
            self.assertTrue(index_path.is_file())
            first_entry = json.loads(index_path.read_text(encoding="utf-8").splitlines()[0])
            self.assertIn("id", first_entry)
            self.assertIn("line", first_entry)

            val_after = self._run_validate(root, "--json")
            data_after = json.loads(val_after.stdout)
            self.assertFalse(
                any("memory-index.jsonl" in w for w in data_after["warnings"]),
                data_after["warnings"],
            )

    def test_checked_checklist_items_archived_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checked = "\n".join(f"- [x] NODE-{i:03d}: completed task {i}" for i in range(1, 10))
            program = (
                "# Program: Checklist Demo\n\n"
                "## Implementation Plan\n\n"
                f"{checked}\n"
                "- [ ] NODE-010: still open\n"
            )
            (root / "program.md").write_text(program, encoding="utf-8")

            first = slim_plan.slim_plan(root, keep_checked_items=3, today="2026-11-20")
            self.assertTrue(first["changed_program"])
            self.assertEqual(first["archived_checked_items"], 6)
            slimmed = (root / "program.md").read_text(encoding="utf-8")
            self.assertIn("NODE-010", slimmed)
            self.assertIn("NODE-009", slimmed)
            self.assertNotIn("NODE-001", slimmed)
            archived = (root / "archive" / "program-archive-2026-11-20.md").read_text(encoding="utf-8")
            self.assertIn("NODE-001", archived)

            second = slim_plan.slim_plan(root, keep_checked_items=3, today="2026-11-20")
            self.assertFalse(second["changed_program"])
            self.assertEqual(second["archived_checked_items"], 0)


if __name__ == "__main__":
    unittest.main()
