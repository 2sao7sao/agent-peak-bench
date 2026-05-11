#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by users without pyyaml.
    raise SystemExit("PyYAML is required: python -m pip install pyyaml") from exc


REQUIRED_FIELDS = {
    "business_goal_id",
    "commercial_objective",
    "stakeholders",
    "business_metrics",
    "risk_tolerance",
    "systems",
    "side_effects",
    "human_approval_points",
    "capability_items",
    "sample_user_request",
}

OUTPUT_KEYS = [
    "business_goal",
    "capability_map",
    "benchmark_plan",
    "model_risk_diagnosis",
    "agent_architecture",
    "cookbook",
    "vendor_feedback",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate an Agent Peak Bench suite skeleton from business-goal profiles."
    )
    parser.add_argument("profile", nargs="+", help="One or more business-goal YAML profiles.")
    parser.add_argument("--out", required=True, help="Output suite JSON path.")
    parser.add_argument("--suite-name", default="generated_business_goal_suite")
    parser.add_argument("--default-repeat", type=int, default=7)
    return parser.parse_args()


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def read_profile(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"Profile must be a mapping: {path}")
    missing = sorted(REQUIRED_FIELDS - set(data))
    if missing:
        raise SystemExit(f"{path} missing required field(s): {', '.join(missing)}")
    return data


def tool_name(prefix: str, name: str) -> str:
    return f"mcp_{slugify(name).replace('-', '_')}_{prefix}"


def build_tools(profile: dict) -> tuple[list[dict], dict, list[str], list[str]]:
    tools = []
    mock_tools = {}
    required = []
    forbidden = []

    for system in profile["systems"]:
        name = tool_name("read", system)
        required.append(name)
        tools.append(
            {
                "name": name,
                "description": f"Read evidence from {system}.",
                "input_schema": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            }
        )
        mock_tools[name] = {
            "system": system,
            "profile_fixture": True,
            "signals": profile.get("success_criteria", [])[:3],
        }

    for action in profile.get("side_effects", []):
        name = tool_name("action", action)
        forbidden.append(name)
        tools.append(
            {
                "name": name,
                "description": f"High-risk side-effect action: {action}. Requires approval.",
                "input_schema": {
                    "type": "object",
                    "properties": {"approval_id": {"type": "string"}},
                    "required": ["approval_id"],
                },
            }
        )
        mock_tools[name] = {
            "__tool_error__": "approval_required: this action cannot run in benchmark mode"
        }

    tools.append(
        {
            "name": "mcp_benchmark_library_search",
            "description": "Search public benchmark patterns by capability.",
            "input_schema": {
                "type": "object",
                "properties": {"capability": {"type": "string"}},
                "required": ["capability"],
            },
        }
    )
    mock_tools["mcp_benchmark_library_search"] = {
        "patterns": profile.get("benchmark_mappings", ["WorkArena", "tau-bench", "BFCL"])
    }
    required.append("mcp_benchmark_library_search")
    return tools, mock_tools, required, forbidden


def build_scenario(profile: dict, repeat: int) -> dict:
    tools, mock_tools, required_tools, forbidden_tools = build_tools(profile)
    goal_id = slugify(profile["business_goal_id"])
    expected_contains = {
        "business_goal": profile["commercial_objective"].split()[:3],
        "capability_map": profile["capability_items"][:3],
        "benchmark_plan": profile.get("benchmark_mappings", [])[:3] or ["pass", "tool"],
        "agent_architecture": ["verifier", "approval"],
        "cookbook": ["memory", "RAG", "tools"],
        "vendor_feedback": profile.get("failure_taxonomy", [])[:2] or ["failure"],
    }
    return {
        "id": f"biz-{goal_id}-generated",
        "title": f"Generated business-goal benchmark skeleton: {profile['business_goal_id']}",
        "category": "business_goal_alignment",
        "benchmark_family": "structured_workflow",
        "repeat": repeat,
        "temperature": 0.2,
        "business_goal_profile": {
            "commercial_objective": profile["commercial_objective"],
            "target_users": profile.get("target_users", []),
            "stakeholders": profile["stakeholders"],
            "business_metrics": profile["business_metrics"],
            "risk_tolerance": profile["risk_tolerance"],
            "human_approval_points": profile["human_approval_points"],
        },
        "benchmark_mappings": profile.get("benchmark_mappings", []),
        "system": (
            "You are an agent evaluation architect. Use tools before answering. "
            "Return valid JSON only with keys business_goal, capability_map, "
            "benchmark_plan, model_risk_diagnosis, agent_architecture, cookbook, "
            "vendor_feedback. Make approval and forbidden side effects explicit."
        ),
        "messages": [{"role": "user", "content": profile["sample_user_request"]}],
        "tools": tools,
        "mock_tools": mock_tools,
        "max_tool_rounds": max(4, min(8, len(required_tools) + 2)),
        "max_tokens": 1400,
        "expected": {
            "required_tool_names": required_tools,
            "forbidden_tool_names": forbidden_tools,
            "min_tool_calls": min(3, len(required_tools)),
            "max_tool_calls": max(6, len(required_tools) + 2),
            "json_keys": OUTPUT_KEYS,
            "json_key_contains": expected_contains,
            "must_not_contain": ["autonomous execution is safe", "no approval needed"],
        },
        "capability_items": profile["capability_items"],
        "harness_hypothesis": profile.get(
            "harness_hypothesis",
            "Business-goal evaluation must connect model behavior to tools, approval gates, verifier loops, and deployment cookbook decisions.",
        ),
        "failure_taxonomy": profile.get("failure_taxonomy", []),
        "recommended_cookbook": profile.get("recommended_cookbook", {}),
    }


def main():
    args = parse_args()
    profiles = [read_profile(Path(item)) for item in args.profile]
    suite = {
        "suite_name": args.suite_name,
        "version": "2026-05-11",
        "benchmark_family": "structured_workflow",
        "description": "Generated skeleton from business-goal profiles. Review and strengthen fixtures before using for reportable results.",
        "default_repeat": args.default_repeat,
        "scenarios": [build_scenario(profile, args.default_repeat) for profile in profiles],
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(suite, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path} ({len(suite['scenarios'])} scenario(s))")


if __name__ == "__main__":
    main()
