from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLAN_SKILL_ROOT = Path(__file__).resolve().parents[1]
INITIALIZER = PLAN_SKILL_ROOT / "scripts" / "init_plan.py"
UPGRADER = PLAN_SKILL_ROOT / "scripts" / "upgrade_plan.py"
VALIDATOR = PLAN_SKILL_ROOT / "scripts" / "validate_plan.py"


class UpgradePlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name) / "project"
        process = subprocess.run(
            [
                sys.executable,
                "-B",
                str(INITIALIZER),
                str(self.root),
                "--title",
                "Upgrade Test",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, process.returncode, process.stdout + process.stderr)

    def run_upgrader(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(UPGRADER), str(self.root), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def replace(self, path: Path, old: str, new: str) -> None:
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def validate(self) -> dict:
        process = subprocess.run(
            [sys.executable, "-B", str(VALIDATOR), str(self.root), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        return json.loads(process.stdout)

    def test_upgrade_preserves_lite_content_and_existing_memory(self) -> None:
        program_path = self.root / "program.md"
        task_path = self.root / "tasks" / "TASK-001-upgrade-test.md"
        self.replace(
            program_path,
            "<Current problem, why it matters, constraints, and non-goals.>",
            "UNIQUE LITE PROBLEM",
        )
        self.replace(
            task_path,
            "<Observable result this task delivers.>",
            "UNIQUE LITE TASK RESULT",
        )
        self.replace(
            program_path,
            "- Pending memory write: None",
            "- Pending memory write: CHG-001",
        )
        memory = (PLAN_SKILL_ROOT / "assets" / "memory-starter.template.md").read_text(
            encoding="utf-8"
        )
        memory = memory.replace("<Project Name>", "Upgrade Test").replace(
            "None yet.", "UNIQUE MEMORY NOTE", 1
        )
        memory = memory.replace(
            "## Run Logs",
            "Existing CHG-001: retained before profile upgrade.\n\n## Run Logs",
        )
        (self.root / "memory.md").write_text(memory, encoding="utf-8")

        process = self.run_upgrader()

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        program = program_path.read_text(encoding="utf-8")
        task = task_path.read_text(encoding="utf-8")
        upgraded_memory = (self.root / "memory.md").read_text(encoding="utf-8")
        self.assertIn("- Profile: `Full`", program)
        self.assertIn("- Execution readiness: `Blocked`", program)
        self.assertIn("## Execution Readiness Gate", program)
        self.assertIsNone(re.search(r"(?m)^##\s+\d+\.", program))
        self.assertIn("UNIQUE LITE PROBLEM", program)
        self.assertIn("## Context And References", program)
        self.assertIn("UNIQUE LITE TASK RESULT", task)
        self.assertIn("## Verification Matrix", task)
        self.assertIn("- Evidence: CHG-002", task)
        self.assertIn("UNIQUE MEMORY NOTE", upgraded_memory)
        self.assertIn("CHG-001", upgraded_memory)
        self.assertIn("CHG-002", upgraded_memory)
        self.assertIn("- Pending memory write: CHG-001", program)
        result = self.validate()
        self.assertEqual("Full", result["profile"])
        self.assertEqual([], result["errors"])

    def test_upgrade_without_memory_creates_compact_memory(self) -> None:
        process = self.run_upgrader()

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        memory_path = self.root / "memory.md"
        self.assertTrue(memory_path.is_file())
        self.assertIn("CHG-001", memory_path.read_text(encoding="utf-8"))
        self.assertIn(
            "## Execution Readiness Gate",
            (self.root / "program.md").read_text(encoding="utf-8"),
        )
        generated = [
            self.root / "program.md",
            self.root / "tasks" / "TASK-001-upgrade-test.md",
            memory_path,
        ]
        placeholder_count = sum(
            len(re.findall(r"<[^>\n]+>", path.read_text(encoding="utf-8")))
            for path in generated
        )
        self.assertLessEqual(placeholder_count, 60)
        result = self.validate()
        self.assertEqual("Full", result["profile"])
        self.assertEqual([], result["errors"])

    def test_upgrade_adds_readiness_gate_to_legacy_lite_plan(self) -> None:
        program_path = self.root / "program.md"
        program = program_path.read_text(encoding="utf-8")
        program = program.replace("- Execution readiness: `Blocked`\n", "")
        program = re.sub(
            r"\n## Execution Readiness Gate\n.*?(?=\n## Problem Definition)",
            "",
            program,
            flags=re.DOTALL,
        )
        program_path.write_text(program, encoding="utf-8")

        process = self.run_upgrader()

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        upgraded = program_path.read_text(encoding="utf-8")
        self.assertIn("- Execution readiness: `Not required`", upgraded)
        self.assertIn(
            "This legacy Lite plan predates the readiness gate",
            upgraded,
        )
        self.assertEqual([], self.validate()["errors"])

    def test_upgrade_accepts_lite_plan_without_active_task(self) -> None:
        program_path = self.root / "program.md"
        self.replace(
            program_path,
            "- Active task package: `tasks/TASK-001-upgrade-test.md`",
            "- Active task package: `None`",
        )
        self.replace(
            program_path,
            "- Active plan node: `NODE-001`",
            "- Active plan node: `None`",
        )

        process = self.run_upgrader()

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        program = program_path.read_text(encoding="utf-8")
        self.assertIn("- Active plan node: `None`", program)
        self.assertIn("- Next plan node: `None`", program)
        self.assertEqual([], self.validate()["errors"])

    def test_dry_run_reports_changes_without_writing(self) -> None:
        before = (self.root / "program.md").read_text(encoding="utf-8")

        process = self.run_upgrader("--dry-run")

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        self.assertIn("Would upgrade", process.stdout)
        self.assertEqual(before, (self.root / "program.md").read_text(encoding="utf-8"))
        self.assertFalse((self.root / "memory.md").exists())

    def test_invalid_lite_plan_is_rejected_without_writes(self) -> None:
        task_path = self.root / "tasks" / "TASK-001-upgrade-test.md"
        self.replace(task_path, "# TASK-001:", "# TASK-999:")
        before_program = (self.root / "program.md").read_text(encoding="utf-8")
        before_task = task_path.read_text(encoding="utf-8")

        process = self.run_upgrader()

        self.assertNotEqual(0, process.returncode)
        self.assertIn("invalid", process.stderr.lower())
        self.assertEqual(before_program, (self.root / "program.md").read_text(encoding="utf-8"))
        self.assertEqual(before_task, task_path.read_text(encoding="utf-8"))
        self.assertFalse((self.root / "memory.md").exists())

    def test_already_full_plan_is_rejected(self) -> None:
        self.replace(self.root / "program.md", "- Profile: `Lite`", "- Profile: `Full`")

        process = self.run_upgrader()

        self.assertNotEqual(0, process.returncode)
        self.assertIn("already Full", process.stderr)


class UpgradePlanExampleTests(unittest.TestCase):
    def test_filled_lite_example_upgrades_without_losing_domain_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "lite-change"
            shutil.copytree(PLAN_SKILL_ROOT / "examples" / "lite-change", root)

            process = subprocess.run(
                [sys.executable, "-B", str(UPGRADER), str(root)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(0, process.returncode, process.stdout + process.stderr)
            program = (root / "program.md").read_text(encoding="utf-8")
            task = (root / "tasks" / "TASK-001-validate-timeout.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Reject non-positive timeout values", program)
            self.assertIn("Do not change retry or request semantics", task)
            validation = subprocess.run(
                [sys.executable, "-B", str(VALIDATOR), str(root), "--json"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, validation.returncode, validation.stdout + validation.stderr)
            self.assertEqual([], json.loads(validation.stdout)["errors"])


if __name__ == "__main__":
    unittest.main()
