from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLAN_SKILL_ROOT = Path(__file__).resolve().parents[1]
INITIALIZER = PLAN_SKILL_ROOT / "scripts" / "init_plan.py"
VALIDATOR = PLAN_SKILL_ROOT / "scripts" / "validate_plan.py"


class InitPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name) / "project"

    def run_initializer(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(INITIALIZER), str(self.root), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def validate_generated_plan(self) -> dict:
        process = subprocess.run(
            [sys.executable, "-B", str(VALIDATOR), str(self.root), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        return json.loads(process.stdout)

    def test_default_lite_scaffold_is_linked_and_structurally_valid(self) -> None:
        process = self.run_initializer(
            "--title",
            "Timeout Validation",
            "--owner",
            "Platform Team",
        )

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        program = (self.root / "program.md").read_text(encoding="utf-8")
        task = (
            self.root / "tasks" / "TASK-001-timeout-validation.md"
        ).read_text(encoding="utf-8")
        self.assertIn("# Program: Timeout Validation", program)
        self.assertIn("- Profile: `Lite`", program)
        self.assertIn("## Concept Refinement", program)
        self.assertNotRegex(program, r"(?m)^##\s+\d+\.")
        self.assertIn("- Overall status: `待开始`", program)
        self.assertIn("- Memory: `None`", program)
        self.assertIn(
            "- Active task package: `tasks/TASK-001-timeout-validation.md`",
            program,
        )
        self.assertIn("- Owner: `Platform Team`", program)
        self.assertIn("# TASK-001: Timeout Validation", task)
        self.assertIn(
            "| Node | Status | Task package | Evidence |",
            program,
        )
        self.assertIn(
            "| Node | Size | Dependencies | Acceptance | Updated |",
            program,
        )
        self.assertNotIn("| Acceptance / Verification |", program)
        self.assertIn("tasks/output/TASK-001-timeout-validation/", task)
        self.assertFalse((self.root / "memory.md").exists())
        self.assertIn("/tasks/output/", (self.root / ".gitignore").read_text())
        self.assertIn("validate_plan.py", process.stdout)
        self.assertIn("--strict", process.stdout)
        result = self.validate_generated_plan()
        self.assertEqual("Lite", result["profile"])
        self.assertTrue(result["warnings"])

    def test_full_scaffold_creates_memory_and_only_first_task(self) -> None:
        process = self.run_initializer(
            "--profile",
            "full",
            "--title",
            "CSV Export",
            "--slug",
            "csv-export",
        )

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        program = (self.root / "program.md").read_text(encoding="utf-8")
        task = self.root / "tasks" / "TASK-001-csv-export.md"
        self.assertIn("- Profile: `Full`", program)
        self.assertIn("- Plan mode: `Linear`", program)
        self.assertNotRegex(program, r"(?m)^##\s+\d+\.")
        self.assertIn("## Optional State", program)
        self.assertNotIn("### Key Context", program)
        self.assertIn(
            "| Node | Status | Task package | Evidence |",
            program,
        )
        self.assertIn(
            "| Node | Size | Dependencies | Acceptance | Updated |",
            program,
        )
        self.assertNotIn("TASK-002", program)
        self.assertTrue(task.exists())
        task_text = task.read_text(encoding="utf-8")
        self.assertIn(
            "| Node | Status | Depends on | Action | Verification | Evidence |",
            task_text,
        )
        self.assertIn("Add `V-001` rows before `待验收` or `完成`", task_text)
        self.assertNotIn("| Check | Covers | Method/command |", task_text)
        self.assertNotIn("| Field | Value |", task_text)
        memory = self.root / "memory.md"
        self.assertTrue(memory.exists())
        memory_text = memory.read_text(encoding="utf-8")
        self.assertIn("## Durable State", memory_text)
        self.assertIn("## Changelog", memory_text)
        self.assertIn("## Run Logs", memory_text)
        self.assertNotRegex(memory_text, r"(?m)^##\s+\d+\.")
        self.assertLessEqual(len(memory_text.splitlines()), 28)
        generated_lines = sum(
            len(path.read_text(encoding="utf-8").splitlines())
            for path in (self.root / "program.md", task, memory)
        )
        placeholder_count = sum(
            len(re.findall(r"<[^>\n]+>", path.read_text(encoding="utf-8")))
            for path in (self.root / "program.md", task, memory)
        )
        self.assertLessEqual(generated_lines, 310)
        self.assertLessEqual(placeholder_count, 35)
        result = self.validate_generated_plan()
        self.assertEqual("Full", result["profile"])
        self.assertEqual([], result["errors"])
        self.assertLessEqual(result["warning_count"], 3)

    def test_existing_files_are_never_partially_overwritten(self) -> None:
        first = self.run_initializer("--title", "Safe Plan")
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        program_path = self.root / "program.md"
        program_path.write_text("keep me\n", encoding="utf-8")

        second = self.run_initializer("--title", "Safe Plan")

        self.assertNotEqual(0, second.returncode)
        self.assertIn("Refusing to overwrite", second.stderr)
        self.assertEqual("keep me\n", program_path.read_text(encoding="utf-8"))

    def test_existing_gitignore_is_preserved_and_output_rule_is_idempotent(self) -> None:
        self.root.mkdir(parents=True)
        (self.root / ".gitignore").write_text("dist/\n", encoding="utf-8")

        process = self.run_initializer("--title", "Preserve Ignore")

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        lines = (self.root / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("dist/", lines)
        self.assertEqual(1, lines.count("/tasks/output/"))

    def test_slug_cannot_escape_tasks_directory(self) -> None:
        process = self.run_initializer(
            "--title",
            "Unsafe",
            "--slug",
            "../outside",
        )

        self.assertNotEqual(0, process.returncode)
        self.assertIn("slug", process.stderr.lower())
        self.assertFalse(self.root.exists())

    def test_non_file_gitignore_fails_without_creating_partial_plan(self) -> None:
        self.root.mkdir(parents=True)
        (self.root / ".gitignore").mkdir()

        process = self.run_initializer("--title", "Atomic Init")

        self.assertNotEqual(0, process.returncode)
        self.assertIn("non-file", process.stderr)
        self.assertFalse((self.root / "program.md").exists())
        self.assertFalse((self.root / "tasks").exists())


if __name__ == "__main__":
    unittest.main()
