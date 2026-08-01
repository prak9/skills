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

    def test_default_lite_scaffold_is_single_file_and_structurally_valid(self) -> None:
        process = self.run_initializer(
            "--title",
            "Timeout Validation",
            "--owner",
            "Platform Team",
        )

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        program = (self.root / "program.md").read_text(encoding="utf-8")
        self.assertIn("# Program: Timeout Validation", program)
        self.assertIn("- Profile: `Lite`", program)
        self.assertIn("## Outcome", program)
        self.assertIn("## Acceptance", program)
        self.assertIn("## Plan", program)
        self.assertNotRegex(program, r"(?m)^##\s+\d+\.")
        self.assertIn("- Overall status: `待开始`", program)
        self.assertIn("- Clean state: `Not due`", program)
        self.assertIn("- Last clean: `Not run`", program)
        self.assertIn("- Owner: `Platform Team`", program)
        self.assertIn("| Node | Status | Action | Verification | Evidence |", program)
        self.assertLessEqual(len(program.splitlines()), 45)
        self.assertFalse((self.root / "tasks").exists())
        self.assertFalse((self.root / "memory.md").exists())
        self.assertFalse((self.root / ".gitignore").exists())
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
        self.assertIn("- Execution readiness: `Blocked`", program)
        self.assertIn("- Clean state: `Not due`", program)
        self.assertIn("- Last clean: `Not run`", program)
        self.assertIn("## Execution Readiness Gate", program)
        self.assertNotRegex(program, r"(?m)^##\s+\d+\.")
        self.assertIn("## Outcome", program)
        self.assertIn("## Node Index", program)
        self.assertIn("| Node | Task package | Dependencies | Acceptance |", program)
        self.assertNotIn("## Task List", program)
        self.assertNotIn("| Node | Status | Task package | Evidence |", program)
        self.assertNotIn("TASK-002", program)
        self.assertTrue(task.exists())
        task_text = task.read_text(encoding="utf-8")
        self.assertIn("| Node | Status | Action | Verification | Evidence |", task_text)
        self.assertIn("## Completion Review", task_text)
        self.assertNotIn("## Standing Checklist", task_text)
        self.assertNotIn("## Pre-completion Red Team", task_text)
        self.assertNotIn("## Output Artifacts", task_text)
        memory = self.root / "memory.md"
        self.assertTrue(memory.exists())
        memory_text = memory.read_text(encoding="utf-8")
        self.assertIn("## Decisions", memory_text)
        self.assertIn("## Findings", memory_text)
        self.assertIn("## Runs", memory_text)
        self.assertIn("During Clean, preserve stable IDs and evidence", memory_text)
        self.assertNotRegex(memory_text, r"(?m)^##\s+\d+\.")
        self.assertLessEqual(len(memory_text.splitlines()), 24)
        generated_lines = sum(
            len(path.read_text(encoding="utf-8").splitlines())
            for path in (self.root / "program.md", task, memory)
        )
        placeholder_count = sum(
            len(re.findall(r"<[^>\n]+>", path.read_text(encoding="utf-8")))
            for path in (self.root / "program.md", task, memory)
        )
        self.assertLessEqual(generated_lines, 180)
        self.assertLessEqual(placeholder_count, 20)
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

    def test_existing_gitignore_is_not_changed_by_full_scaffold(self) -> None:
        self.root.mkdir(parents=True)
        (self.root / ".gitignore").write_text("dist/\n", encoding="utf-8")

        process = self.run_initializer("--profile", "full", "--title", "Preserve Ignore")

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        lines = (self.root / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertEqual(["dist/"], lines)

    def test_slug_cannot_escape_tasks_directory(self) -> None:
        process = self.run_initializer(
            "--profile",
            "full",
            "--title",
            "Unsafe",
            "--slug",
            "../outside",
        )

        self.assertNotEqual(0, process.returncode)
        self.assertIn("slug", process.stderr.lower())
        self.assertFalse(self.root.exists())

    def test_non_file_tasks_path_fails_without_creating_partial_plan(self) -> None:
        self.root.mkdir(parents=True)
        (self.root / "tasks").write_text("not a directory\n", encoding="utf-8")

        process = self.run_initializer("--profile", "full", "--title", "Atomic Init")

        self.assertNotEqual(0, process.returncode)
        self.assertIn("not a directory", process.stderr)
        self.assertFalse((self.root / "program.md").exists())


if __name__ == "__main__":
    unittest.main()
