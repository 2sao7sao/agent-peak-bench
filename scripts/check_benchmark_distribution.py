#!/usr/bin/env python3

import argparse
import json
from collections import Counter
from pathlib import Path


CATEGORY_ALIASES = {
    "agent_workflow": "structured_workflow",
    "architecture": "long_running_harness",
    "chatbot": "chat_memory",
    "context": "context_engineering",
    "decomposition": "long_running_harness",
    "decomposition_ablation": "long_running_harness",
    "multi_agent": "multi_agent_coordination",
    "repeatability": "chat_memory",
    "rigor": "system_governance",
    "skill_ablation": "long_running_harness",
    "skills": "long_running_harness",
    "tool_ablation": "tool_recovery",
    "tool_use": "tool_recovery",
    "window_ablation": "context_engineering",
    "workflow": "structured_workflow",
    "ablation_solo": "long_running_harness",
    "ablation_structured_harness": "long_running_harness",
    "evaluator_quality": "long_running_harness",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Check benchmark suite coverage against a manifest.")
    parser.add_argument("--manifest", default="evals/benchmark_manifest_v2.json")
    parser.add_argument("--suite-dir", default="evals/suites")
    return parser.parse_args()


def main():
    args = parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    suite_dir = Path(args.suite_dir)
    expected = {item["id"]: item["weight"] for item in manifest["families"]}

    counts = Counter()
    total = 0
    unknown = Counter()

    for suite_path in sorted(suite_dir.glob("*.json")):
        suite = json.loads(suite_path.read_text(encoding="utf-8"))
        default_family = suite.get("benchmark_family")
        for scenario in suite.get("scenarios", []):
            category = scenario.get("category")
            family = scenario.get("benchmark_family")
            if not family and category in expected:
                family = category
            if not family and category in CATEGORY_ALIASES:
                family = CATEGORY_ALIASES[category]
            if not family:
                family = default_family or category or "unknown"
            total += 1
            if family in expected:
                counts[family] += 1
            else:
                unknown[family] += 1

    print("== Benchmark Distribution ==")
    print(f"total_scenarios={total}")
    for family, weight in expected.items():
        actual = counts[family] / total if total else 0
        print(
            json.dumps(
                {
                    "family": family,
                    "expected_weight": weight,
                    "actual_weight": round(actual, 3),
                    "scenario_count": counts[family],
                },
                ensure_ascii=False,
            )
        )

    if unknown:
        print("\n== Unmapped Categories ==")
        for name, count in sorted(unknown.items()):
            print(json.dumps({"category": name, "scenario_count": count}, ensure_ascii=False))


if __name__ == "__main__":
    main()
