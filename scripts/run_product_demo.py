#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from generate_business_goal_suite import build_scenario, read_profile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILES = [
    ROOT / "evals/business_goals/security_review_acceleration.yaml",
    ROOT / "evals/business_goals/support_refund_automation.yaml",
    ROOT / "evals/business_goals/renewal_risk_diagnosis.yaml",
]
DEFAULT_CAMPAIGN = ROOT / "evals/campaigns/harness_engineering_campaign_v1.json"


@dataclass(frozen=True)
class ProductMetric:
    key: str
    value: float
    numerator: int
    denominator: int
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": round(self.value, 4),
            "numerator": self.numerator,
            "denominator": self.denominator,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class ProductDemoReport:
    profile_count: int
    generated_scenario_count: int
    capability_count: int
    required_tool_count: int
    forbidden_tool_count: int
    campaign_batches: list[str]
    cookbook_topologies: dict[str, str]
    metrics: dict[str, ProductMetric]

    @property
    def passed(self) -> bool:
        return all(metric.value >= 1.0 for metric in self.metrics.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "PASS" if self.passed else "FAIL",
            "profile_count": self.profile_count,
            "generated_scenario_count": self.generated_scenario_count,
            "capability_count": self.capability_count,
            "required_tool_count": self.required_tool_count,
            "forbidden_tool_count": self.forbidden_tool_count,
            "campaign_batches": self.campaign_batches,
            "cookbook_topologies": self.cookbook_topologies,
            "metrics": {key: metric.to_dict() for key, metric in self.metrics.items()},
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Agent Peak Bench product demo without calling a model."
    )
    parser.add_argument(
        "--profile",
        action="append",
        default=[],
        help="Business-goal profile YAML. Defaults to the three public profiles.",
    )
    parser.add_argument("--campaign", default=str(DEFAULT_CAMPAIGN))
    parser.add_argument("--json-out", default="", help="Optional machine-readable report path.")
    return parser.parse_args()


def run_product_demo(
    profiles: list[Path] | None = None,
    campaign_path: Path = DEFAULT_CAMPAIGN,
) -> ProductDemoReport:
    profile_paths = profiles or DEFAULT_PROFILES
    profile_data = [read_profile(path) for path in profile_paths]
    scenarios = [build_scenario(profile, repeat=7) for profile in profile_data]
    campaign = json.loads(campaign_path.read_text(encoding="utf-8"))

    capability_items = {
        item
        for scenario in scenarios
        for item in scenario.get("capability_items", [])
    }
    required_tools = {
        tool
        for scenario in scenarios
        for tool in scenario.get("expected", {}).get("required_tool_names", [])
    }
    forbidden_tools = {
        tool
        for scenario in scenarios
        for tool in scenario.get("expected", {}).get("forbidden_tool_names", [])
    }
    cookbook_topologies = {
        profile["business_goal_id"]: profile.get("recommended_cookbook", {}).get("topology", "")
        for profile in profile_data
    }
    metrics = _build_metrics(
        profiles=profile_data,
        scenarios=scenarios,
        campaign=campaign,
        capability_items=capability_items,
        forbidden_tools=forbidden_tools,
    )

    with tempfile.TemporaryDirectory(prefix="agent-peak-demo-") as temp_dir:
        out = Path(temp_dir) / "generated-business-goal-suite.json"
        suite = {
            "suite_name": "product_demo_generated_business_goal_suite",
            "version": "2026-05-11",
            "benchmark_family": "structured_workflow",
            "default_repeat": 7,
            "scenarios": scenarios,
        }
        out.write_text(json.dumps(suite, ensure_ascii=False, indent=2), encoding="utf-8")

    return ProductDemoReport(
        profile_count=len(profile_data),
        generated_scenario_count=len(scenarios),
        capability_count=len(capability_items),
        required_tool_count=len(required_tools),
        forbidden_tool_count=len(forbidden_tools),
        campaign_batches=[batch["id"] for batch in campaign.get("campaign_batches", [])],
        cookbook_topologies=cookbook_topologies,
        metrics=metrics,
    )


def format_report(report: ProductDemoReport) -> str:
    lines = [
        "# Agent Peak Bench Product Demo",
        "",
        f"status: {'PASS' if report.passed else 'FAIL'}",
        f"business_profiles: {report.profile_count}",
        f"generated_scenarios: {report.generated_scenario_count}",
        f"capability_items: {report.capability_count}",
        f"required_tools: {report.required_tool_count}",
        f"forbidden_side_effect_tools: {report.forbidden_tool_count}",
        "",
        "## 1. Product metrics",
    ]
    for metric in report.metrics.values():
        lines.append(
            f"- {metric.key}: {metric.value:.2f} "
            f"({metric.numerator}/{metric.denominator}) - {metric.explanation}"
        )
    lines.extend(
        [
            "",
            "## 2. Campaign batches",
            *[f"- {batch}" for batch in report.campaign_batches],
            "",
            "## 3. Cookbook topology by business goal",
            *[
                f"- {goal}: {topology}"
                for goal, topology in sorted(report.cookbook_topologies.items())
            ],
        ]
    )
    return "\n".join(lines) + "\n"


def _build_metrics(
    *,
    profiles: list[dict[str, Any]],
    scenarios: list[dict[str, Any]],
    campaign: dict[str, Any],
    capability_items: set[str],
    forbidden_tools: set[str],
) -> dict[str, ProductMetric]:
    required_cookbook_fields = {"topology", "memory", "rag", "tools", "skills", "verifier"}
    cookbook_complete = [
        required_cookbook_fields <= set((profile.get("recommended_cookbook") or {}).keys())
        for profile in profiles
    ]
    scenario_contracts = [
        bool(scenario.get("capability_items"))
        and bool(scenario.get("benchmark_mappings"))
        and bool(scenario.get("expected", {}).get("json_keys"))
        for scenario in scenarios
    ]
    governance_contracts = [
        bool(profile.get("human_approval_points"))
        and bool(profile.get("side_effects"))
        and bool(scenario.get("expected", {}).get("forbidden_tool_names"))
        for profile, scenario in zip(profiles, scenarios, strict=True)
    ]
    campaign_batches = campaign.get("campaign_batches", [])
    repeat_values = {int(batch.get("force_repeat", 0)) for batch in campaign_batches}
    campaign_has_confidence_ladder = {7, 30, 100} <= repeat_values
    pass_k_values = set(campaign.get("confidence_policy", {}).get("required_pass_k", []))
    campaign_has_passk_contract = {1, 3, 5, 7, 10} <= pass_k_values
    decision_objective_ids = {
        item.get("id")
        for item in campaign.get("decision_objectives", [])
        if item.get("id")
    }
    has_decision_objectives = bool(campaign.get("decision_objectives"))

    return {
        "business_goal_to_suite_rate": ProductMetric(
            key="business_goal_to_suite_rate",
            value=_ratio(len(scenarios), len(profiles)),
            numerator=len(scenarios),
            denominator=len(profiles),
            explanation="business profiles converted into benchmark scenarios",
        ),
        "capability_mapping_rate": ProductMetric(
            key="capability_mapping_rate",
            value=_ratio(sum(scenario_contracts), len(scenario_contracts)),
            numerator=sum(scenario_contracts),
            denominator=len(scenario_contracts),
            explanation="scenarios include capabilities, benchmark mappings, and output contracts",
        ),
        "governance_contract_rate": ProductMetric(
            key="governance_contract_rate",
            value=_ratio(sum(governance_contracts), len(governance_contracts)),
            numerator=sum(governance_contracts),
            denominator=len(governance_contracts),
            explanation="side-effect tools are modeled as forbidden without approval",
        ),
        "cookbook_completeness_rate": ProductMetric(
            key="cookbook_completeness_rate",
            value=_ratio(sum(cookbook_complete), len(cookbook_complete)),
            numerator=sum(cookbook_complete),
            denominator=len(cookbook_complete),
            explanation="business profiles contain topology, memory, RAG, tools, skills, and verifier guidance",
        ),
        "campaign_confidence_contract_rate": ProductMetric(
            key="campaign_confidence_contract_rate",
            value=float(
                campaign_has_confidence_ladder
                and campaign_has_passk_contract
                and has_decision_objectives
            ),
            numerator=int(
                campaign_has_confidence_ladder
                and campaign_has_passk_contract
                and has_decision_objectives
            ),
            denominator=1,
            explanation="campaign defines r7/r30/r100, pass@k, and deployment decision objectives",
        ),
        "capability_surface_presence_rate": ProductMetric(
            key="capability_surface_presence_rate",
            value=float(bool(capability_items) and bool(forbidden_tools) and bool(decision_objective_ids)),
            numerator=int(bool(capability_items) and bool(forbidden_tools) and bool(decision_objective_ids)),
            denominator=1,
            explanation="demo exposes capabilities, required tools, forbidden tools, and campaign objective metadata",
        ),
    }


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def main() -> int:
    args = parse_args()
    profiles = [Path(item) for item in args.profile] if args.profile else None
    report = run_product_demo(profiles=profiles, campaign_path=Path(args.campaign))
    print(format_report(report), end="")
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
