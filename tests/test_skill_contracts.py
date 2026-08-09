from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVESTMENT_SKILLS = (
    "bayesian-intrinsic-growth-valuation",
    "buy-side-equity-research-memo",
    "gf-dma-health-index",
    "serenity-alpha",
    "tam-adj-peg",
)
EXPLICIT_DELIVERY_SKILLS = tuple(
    name for name in INVESTMENT_SKILLS if name != "buy-side-equity-research-memo"
)


def skill_text(name: str) -> str:
    return (ROOT / name / "SKILL.md").read_text(encoding="utf-8")


def description(name: str) -> str:
    match = re.search(r"^description:\s*(.+)$", skill_text(name), flags=re.MULTILINE)
    if match is None:
        raise AssertionError(f"{name} has no one-line description")
    return match.group(1).strip().strip('"')


class SkillContractTests(unittest.TestCase):
    def test_specialized_equity_skills_do_not_claim_bare_tickers(self) -> None:
        self.assertNotIn(
            "user provides a ticker",
            description("gf-dma-health-index").lower(),
        )
        self.assertNotIn(
            "user provides a ticker",
            description("tam-adj-peg").lower(),
        )
        self.assertNotIn(
            "or company analysis based on fundamentals",
            description("bayesian-intrinsic-growth-valuation").lower(),
        )

    def test_investment_skills_require_explicit_external_mutation(self) -> None:
        for name in INVESTMENT_SKILLS:
            text = skill_text(name)
            with self.subTest(skill=name):
                self.assertNotIn("install with `pip install edgartools`", text)
                self.assertNotIn('set_identity("name@example.com")', text)

        for name in EXPLICIT_DELIVERY_SKILLS:
            with self.subTest(skill=name):
                self.assertIn(
                    "only when the user explicitly asks",
                    skill_text(name),
                )

    def test_buy_side_memos_default_to_the_invest_notion_target(self) -> None:
        text = skill_text("buy-side-equity-research-memo")
        self.assertIn("Default Notion Delivery", text)
        self.assertIn("named `Invest`", text)
        self.assertIn("Notion archive pending", text)

    def test_gf_dma_uses_percentage_weights_and_available_fallbacks(self) -> None:
        text = skill_text("gf-dma-health-index")
        reference = (
            ROOT / "gf-dma-health-index" / "references" / "original-framework.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "HealthScore = 0.40S_GrowthMatch + 0.25S_Divergence "
            "+ 0.20S_Parallel + 0.15S_Revision",
            text,
        )
        self.assertIn(
            "HealthScore = 0.40S_{GrowthMatch}+0.25S_{Divergence}"
            "+0.20S_{Parallel}+0.15S_{Revision}",
            reference,
        )
        self.assertNotIn("If gross profit or EPS is missing", text)
        self.assertIn("If EPS is missing", text)

    def test_storm_uses_runtime_neutral_tools_and_direct_links(self) -> None:
        text = skill_text("storm-deep-research")
        self.assertNotIn("WebSearch", text)
        self.assertNotIn("WebFetch", text)
        self.assertNotIn("本机 claude", text)
        self.assertNotIn("[n]", text)
        self.assertIn("Markdown", text)

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
        self.assertIn("论证与概念审计", skill_text("storm-deep-research"))

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

        bayesian = skill_text("bayesian-intrinsic-growth-valuation")
        self.assertIn("not independent confirmations", bayesian)
        self.assertIn("inverse problem, not a unique observable", bayesian)

        gf_dma = skill_text("gf-dma-health-index")
        self.assertIn("mark GrowthMatch `N/A`", gf_dma)
        self.assertIn("状态：Unscorable", gf_dma)

        self.assertIn("latent demand hypothesis", skill_text("serenity-alpha"))
        self.assertIn("label the conclusion `model-sensitive`", skill_text("tam-adj-peg"))


if __name__ == "__main__":
    unittest.main()
