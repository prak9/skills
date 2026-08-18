from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVESTMENT_SKILL = "invest"

# Skills whose content was folded into a surviving skill. A live reference to one
# of these names is a dangling pointer for anyone following the instructions.
REMOVED_SKILLS = (
    "judgment-craft",
    "define-problem",
    "alpha-research",
    "linux-perf",
    "performance-patterns",
)


# Files a SKILL.md points at inside its own bundle. Bare filenames are excluded:
# several skills name files they create at runtime (`memory.md`, `manifest.json`).
BUNDLED_DIRS = ("references", "assets", "scripts", "evals", "agents")
PATH_IN_BACKTICKS = re.compile(
    r"`((?:" + "|".join(BUNDLED_DIRS) + r")/[A-Za-z0-9_./-]+)`"
)
MARKDOWN_LINK = re.compile(r"\]\(([^)]+)\)")


def skill_dirs() -> list[Path]:
    return sorted(
        d
        for d in ROOT.iterdir()
        if not d.name.startswith(".") and (d / "SKILL.md").is_file()
    )


def skill_text(name: str) -> str:
    return (ROOT / name / "SKILL.md").read_text(encoding="utf-8")


def description(name: str) -> str:
    match = re.search(r"^description:\s*(.+)$", skill_text(name), flags=re.MULTILINE)
    if match is None:
        raise AssertionError(f"{name} has no one-line description")
    return match.group(1).strip().strip('"')


class SkillContractTests(unittest.TestCase):
    def test_specialized_equity_modes_do_not_claim_bare_tickers(self) -> None:
        text = skill_text(INVESTMENT_SKILL)
        self.assertIn("Do not trigger Modes B, C, or E from a bare ticker", text)
        self.assertIn(
            "Do not trigger from a bare ticker or generic stock-analysis request",
            text,
        )

    def test_investment_skill_requires_explicit_external_mutation(self) -> None:
        text = skill_text(INVESTMENT_SKILL)
        self.assertNotIn("install with `pip install edgartools`", text)
        self.assertNotIn('set_identity("name@example.com")', text)
        self.assertIn("archive only when the user explicitly asks", text)

    def test_buy_side_memos_default_to_the_invest_notion_target(self) -> None:
        text = skill_text(INVESTMENT_SKILL)
        self.assertIn("## Notion Delivery", text)
        self.assertIn("named `Invest`", text)
        self.assertIn("Notion archive pending", text)

    def test_gf_dma_uses_percentage_weights_and_available_fallbacks(self) -> None:
        text = skill_text(INVESTMENT_SKILL)

        self.assertIn(
            "HealthScore = 0.40*S_GrowthMatch + 0.25*S_Divergence "
            "+ 0.20*S_Parallel + 0.15*S_Revision",
            text,
        )
        self.assertNotIn("If gross profit or EPS is missing", text)
        self.assertIn("EPS missing", text)

    def test_every_skill_has_openai_interface_metadata(self) -> None:
        for skill_dir in sorted(ROOT.iterdir()):
            if skill_dir.name.startswith(".") or not (skill_dir / "SKILL.md").is_file():
                continue
            with self.subTest(skill=skill_dir.name):
                self.assertTrue((skill_dir / "agents" / "openai.yaml").is_file())

    def test_no_skill_references_a_removed_skill(self) -> None:
        for skill_dir in sorted(ROOT.iterdir()):
            if skill_dir.name.startswith(".") or not (skill_dir / "SKILL.md").is_file():
                continue
            text = skill_text(skill_dir.name)
            for removed in REMOVED_SKILLS:
                with self.subTest(skill=skill_dir.name, removed=removed):
                    self.assertNotIn(removed, text)

    def test_skill_file_paths_resolve(self) -> None:
        for skill_dir in skill_dirs():
            text = skill_text(skill_dir.name)
            targets = set(PATH_IN_BACKTICKS.findall(text))
            targets.update(
                link
                for link in MARKDOWN_LINK.findall(text)
                if not link.startswith(("http://", "https://", "#"))
            )
            for target in sorted(targets):
                with self.subTest(skill=skill_dir.name, path=target):
                    self.assertTrue(
                        (skill_dir / target.split("#", 1)[0]).exists(),
                        f"{skill_dir.name}/SKILL.md points at missing {target}",
                    )

    def test_argument_audit_keeps_its_domain_adapters(self) -> None:
        self.assertIn("Argument integrity", skill_text("research-craft"))
        self.assertIn("Audit The Approval Argument", skill_text("code-review-craft"))
        self.assertIn("核心概念一致", skill_text("writing"))
        self.assertIn("是否分清事实、假设和推断", skill_text("decision"))

    def test_model_boundary_audit_has_domain_guardrails(self) -> None:
        self.assertIn("latent construct / model boundary", skill_text("research-craft"))

        invest = skill_text(INVESTMENT_SKILL)
        self.assertIn("not independent confirmations", invest)
        self.assertIn("inverse problem, not a unique observable", invest)
        self.assertIn("mark GrowthMatch `N/A`", invest)
        self.assertIn("状态：Unscorable", invest)
        self.assertIn("latent demand hypothesis", invest)
        self.assertIn("label the conclusion `model-sensitive`", invest)

    def test_result_analysis_daily_loop_keeps_live_and_research_gates_separate(
        self,
    ) -> None:
        skill = skill_text("result-analysis")
        daily = (
            ROOT
            / "result-analysis"
            / "references"
            / "daily-decision-loop.md"
        ).read_text(encoding="utf-8")

        self.assertIn("references/daily-decision-loop.md", skill)
        self.assertIn("PREAPPROVED_LIVE", daily)
        self.assertIn("REAL_OBSERVED", daily)
        self.assertIn("POSTHOC_CANDIDATE", daily)
        self.assertIn("KEEP_CURRENT", daily)
        self.assertIn("日报不能凭单日 SIM 盈利新增实盘品种", daily)
        self.assertIn("1 个同身份日：只能 `OBSERVE/MEASURE`", daily)
        self.assertIn("policy-conditional cohort", daily)
        self.assertIn("不自动落盘", daily)


if __name__ == "__main__":
    unittest.main()
