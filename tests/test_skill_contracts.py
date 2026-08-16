from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVESTMENT_SKILL = "invest"


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

    def test_judgment_craft_has_no_missing_alpha_research_dependency(self) -> None:
        self.assertNotIn("alpha-research", skill_text("judgment-craft"))

    def test_argument_audit_has_one_canonical_core_and_domain_adapters(self) -> None:
        judgment = skill_text("judgment-craft")
        audit_path = (
            ROOT
            / "judgment-craft"
            / "references"
            / "argument-and-concept-audit.md"
        )
        audit = audit_path.read_text(encoding="utf-8")

        self.assertIn("references/argument-and-concept-audit.md", judgment)
        self.assertIn("# Argument And Concept Audit", audit)
        self.assertIn("Explicit premises", audit)
        self.assertIn("Hidden assumptions", audit)
        self.assertIn("necessary from sufficient", audit)
        self.assertIn("Strongest countercase", audit)
        self.assertIn("Update trigger", audit)

        self.assertIn("Concept test", skill_text("define-problem"))
        self.assertIn("Argument integrity", skill_text("research-craft"))
        self.assertIn("Audit The Approval Argument", skill_text("code-review-craft"))
        self.assertIn("核心概念一致", skill_text("writing"))

    def test_model_boundary_audit_has_domain_guardrails(self) -> None:
        audit = (
            ROOT
            / "judgment-craft"
            / "references"
            / "argument-and-concept-audit.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Audit The Model Boundary", audit)
        self.assertIn("reality, observed data, and the model distinct", audit)
        self.assertIn("rival states consistent with the same output", audit)
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
