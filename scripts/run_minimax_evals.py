#!/usr/bin/env python3

import argparse
import copy
import datetime as dt
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_suite(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def now_slug() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def normalize_base_url(raw: str) -> str:
    base = raw.rstrip("/")
    if base.endswith("/v1/messages"):
        return base
    if base.endswith("/anthropic"):
        return f"{base}/v1/messages"
    if base.endswith("/v1"):
        return f"{base}/messages"
    return f"{base}/v1/messages"


def ci_text(value: str) -> str:
    return value.casefold()


def normalize_text(value: str) -> str:
    return " ".join(value.split()).strip().casefold()


def percentile(values: list, q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(float(ordered[0]), 3)
    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return round(float(ordered[int(position)]), 3)
    lower_value = ordered[lower]
    upper_value = ordered[upper]
    return round(float(lower_value + (upper_value - lower_value) * (position - lower)), 3)


def wilson_interval(successes: int, total: int, z: float = 1.96) -> list:
    if total <= 0:
        return [0.0, 0.0]
    phat = successes / total
    denominator = 1 + z * z / total
    center = (phat + z * z / (2 * total)) / denominator
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total) / denominator
    return [round(max(0.0, center - margin), 3), round(min(1.0, center + margin), 3)]


def estimate_pass_at_k(total: int, successes: int, k: int):
    if total < k:
        return None
    if successes <= 0:
        return 0.0
    if total - successes < k:
        return 1.0
    # Unbiased pass@k estimator used by code-generation benchmarks.
    # It estimates whether at least one of k sampled attempts succeeds.
    product = 1.0
    for value in range(total - successes + 1, total + 1):
        product *= 1.0 - k / value
    return round(1.0 - product, 3)


def replace_generated_context(node, generated: str, placeholder: str = "{{GENERATED_CONTEXT}}"):
    if isinstance(node, str):
        return node.replace(placeholder, generated)
    if isinstance(node, list):
        return [replace_generated_context(item, generated, placeholder) for item in node]
    if isinstance(node, dict):
        return {key: replace_generated_context(value, generated, placeholder) for key, value in node.items()}
    return node


def build_generated_context(spec: dict) -> str:
    title = spec.get("title", "Synthetic context pack")
    filler = spec.get(
        "filler",
        "This section contains routine project notes, implementation trivia, and non-critical prose.",
    )
    sections = int(spec.get("sections", 24))
    facts = {int(item["section"]): item["text"] for item in spec.get("facts", [])}
    lines = [title]
    for index in range(1, sections + 1):
        lines.append(f"\n### Section {index}\n")
        lines.append(filler)
        lines.append(f" Repetition marker {index}.")
        if index in facts:
            lines.append(f" CRITICAL FACT: {facts[index]}")
    return "".join(lines)


def extract_text(content_blocks) -> str:
    if isinstance(content_blocks, str):
        return content_blocks
    parts = []
    for block in content_blocks or []:
        block_type = block.get("type")
        if block_type == "text":
            parts.append(block.get("text", ""))
    return "\n".join(part for part in parts if part)


def parse_json_from_text(text: str):
    candidates = [text.strip()]
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            candidates.append("\n".join(lines[1:-1]).strip())
    for match in re.finditer(r"```(?:json)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL):
        candidates.append(match.group(1).strip())
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        candidates.append(stripped[start : end + 1])
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None


def stringify_json_value(value) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def ordered_unique(items: list) -> list:
    seen = set()
    output = []
    for item in items:
        if item not in seen:
            seen.add(item)
            output.append(item)
    return output


def env_first(*names: str, default: str = "") -> str:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return default


def extract_tool_uses(content_blocks) -> list:
    calls = []
    for block in content_blocks or []:
        if block.get("type") == "tool_use":
            calls.append(block)
    return calls


def make_tool_result(tool_use_id: str, payload, is_error: bool = False) -> dict:
    if isinstance(payload, str):
        content = payload
    else:
        content = json.dumps(payload, ensure_ascii=False)
    return {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": content,
        "is_error": is_error,
    }


def compute_tool_metrics(expected: dict, tool_names_seen: list) -> dict:
    required_tools = expected.get("required_tool_names", [])
    required_groups = expected.get("required_tool_name_groups", [])
    forbidden_tools = expected.get("forbidden_tool_names", [])
    unique_seen = ordered_unique(tool_names_seen)

    required_hits = sum(1 for tool in required_tools if tool in tool_names_seen)
    group_hits = sum(1 for group in required_groups if any(tool in tool_names_seen for tool in group))
    required_total = len(required_tools) + len(required_groups)
    required_coverage = (required_hits + group_hits) / required_total if required_total else None

    expected_tool_surface = set(required_tools)
    for group in required_groups:
        expected_tool_surface.update(group)
    forbidden_call_count = sum(1 for tool in tool_names_seen if tool in forbidden_tools)
    repeated_call_count = max(0, len(tool_names_seen) - len(unique_seen))

    if tool_names_seen and expected_tool_surface:
        precision_proxy = sum(1 for tool in tool_names_seen if tool in expected_tool_surface) / len(tool_names_seen)
    elif tool_names_seen:
        precision_proxy = None
    else:
        precision_proxy = 0.0 if expected_tool_surface else None

    return {
        "tool_call_count": len(tool_names_seen),
        "unique_tool_call_count": len(unique_seen),
        "tools_seen": unique_seen,
        "required_tool_coverage": round(required_coverage, 3) if required_coverage is not None else None,
        "tool_precision_proxy": round(precision_proxy, 3) if precision_proxy is not None else None,
        "forbidden_tool_call_count": forbidden_call_count,
        "repeated_tool_call_count": repeated_call_count,
    }


def compute_output_metrics(final_text: str, evaluation: dict) -> dict:
    structural_checks = []
    for check in evaluation.get("checks", []):
        name = check.get("check", "")
        if name.startswith("json_keys:") or name.startswith("json_subset:") or name in {"json_equals"}:
            structural_checks.append(check)
    return {
        "output_chars": len(final_text),
        "json_contract_passed": all(check.get("passed") for check in structural_checks) if structural_checks else None,
        "json_check_count": len(structural_checks),
    }


def scenario_metadata(scenario: dict, suite: dict) -> dict:
    keys = [
        "benchmark_family",
        "category",
        "ablation_axis",
        "harness_mode",
        "plan_mode",
        "agent_topology",
        "context_profile",
        "tool_profile",
        "skill_profile",
        "ambiguity_profile",
        "personality_profile",
        "hypothesis",
    ]
    metadata = {key: scenario[key] for key in keys if key in scenario}
    if "benchmark_family" not in metadata and suite.get("benchmark_family"):
        metadata["benchmark_family"] = suite["benchmark_family"]
    return metadata


def api_call(url: str, api_key: str, payload: dict, timeout_seconds: int) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def evaluate_text(text: str, spec: dict, tool_names: list, metrics: dict) -> dict:
    checks = []
    lowered = ci_text(text)
    parsed_json = None

    for needle in spec.get("must_contain", []):
        passed = ci_text(needle) in lowered
        checks.append({"check": f"must_contain:{needle}", "passed": passed})

    for needle in spec.get("must_not_contain", []):
        passed = ci_text(needle) not in lowered
        checks.append({"check": f"must_not_contain:{needle}", "passed": passed})

    for index, item in enumerate(spec.get("must_contain_any", []), start=1):
        options = item.get("options", []) if isinstance(item, dict) else item
        label = item.get("name", str(index)) if isinstance(item, dict) else str(index)
        passed = any(ci_text(option) in lowered for option in options)
        checks.append({"check": f"must_contain_any:{label}", "passed": passed})

    if "min_chars" in spec:
        passed = len(text) >= int(spec["min_chars"])
        checks.append({"check": f"min_chars:{spec['min_chars']}", "passed": passed})

    if "max_chars" in spec:
        passed = len(text) <= int(spec["max_chars"])
        checks.append({"check": f"max_chars:{spec['max_chars']}", "passed": passed})

    required_tools = spec.get("required_tool_names", [])
    for tool in required_tools:
        passed = tool in tool_names
        checks.append({"check": f"required_tool:{tool}", "passed": passed})

    for index, group in enumerate(spec.get("required_tool_name_groups", []), start=1):
        passed = any(tool in tool_names for tool in group)
        checks.append({"check": f"required_tool_group:{index}", "passed": passed})

    for tool in spec.get("forbidden_tool_names", []):
        passed = tool not in tool_names
        checks.append({"check": f"forbidden_tool:{tool}", "passed": passed})

    if "min_tool_calls" in spec:
        passed = len(tool_names) >= int(spec["min_tool_calls"])
        checks.append({"check": f"min_tool_calls:{spec['min_tool_calls']}", "passed": passed})

    if "max_tool_calls" in spec:
        passed = len(tool_names) <= int(spec["max_tool_calls"])
        checks.append({"check": f"max_tool_calls:{spec['max_tool_calls']}", "passed": passed})

    if spec.get("required_tool_sequence"):
        required = spec["required_tool_sequence"]
        passed = tool_names[: len(required)] == required
        checks.append({"check": f"required_tool_sequence:{'->'.join(required)}", "passed": passed})

    if spec.get("json_keys"):
        parsed_json = parse_json_from_text(text)
        passed = isinstance(parsed_json, dict) and all(key in parsed_json for key in spec["json_keys"])
        checks.append({"check": f"json_keys:{','.join(spec['json_keys'])}", "passed": passed})

    if spec.get("json_subset"):
        if parsed_json is None:
            parsed_json = parse_json_from_text(text)
        subset = spec["json_subset"]
        passed = isinstance(parsed_json, dict) and all(parsed_json.get(key) == value for key, value in subset.items())
        checks.append({"check": f"json_subset:{','.join(subset.keys())}", "passed": passed})

    for key, needles in spec.get("json_key_contains", {}).items():
        if parsed_json is None:
            parsed_json = parse_json_from_text(text)
        value_text = stringify_json_value(parsed_json.get(key, "")) if isinstance(parsed_json, dict) else ""
        value_text = ci_text(value_text)
        passed = all(ci_text(needle) in value_text for needle in needles)
        checks.append({"check": f"json_key_contains:{key}", "passed": passed})

    for key, min_length in spec.get("json_array_min_length", {}).items():
        if parsed_json is None:
            parsed_json = parse_json_from_text(text)
        value = parsed_json.get(key) if isinstance(parsed_json, dict) else None
        passed = isinstance(value, list) and len(value) >= int(min_length)
        checks.append({"check": f"json_array_min_length:{key}:{min_length}", "passed": passed})

    if spec.get("json_equals"):
        if parsed_json is None:
            parsed_json = parse_json_from_text(text)
        expected_json = spec["json_equals"]
        passed = parsed_json == expected_json
        checks.append({"check": "json_equals", "passed": passed})

    if spec.get("normalized_equals"):
        expected_text = normalize_text(spec["normalized_equals"])
        passed = normalize_text(text) == expected_text
        checks.append({"check": "normalized_equals", "passed": passed})

    if spec.get("normalized_equals_any"):
        allowed = [normalize_text(item) for item in spec["normalized_equals_any"]]
        passed = normalize_text(text) in allowed
        checks.append({"check": "normalized_equals_any", "passed": passed})

    if "max_total_latency_ms" in spec:
        passed = metrics["total_latency_ms"] <= int(spec["max_total_latency_ms"])
        checks.append({"check": f"max_total_latency_ms:{spec['max_total_latency_ms']}", "passed": passed})

    if "max_first_round_latency_ms" in spec:
        passed = metrics["first_round_latency_ms"] <= int(spec["max_first_round_latency_ms"])
        checks.append(
            {"check": f"max_first_round_latency_ms:{spec['max_first_round_latency_ms']}", "passed": passed}
        )

    if "max_round_count" in spec:
        passed = metrics["round_count"] <= int(spec["max_round_count"])
        checks.append({"check": f"max_round_count:{spec['max_round_count']}", "passed": passed})

    total = len(checks)
    passed_count = sum(1 for check in checks if check["passed"])
    score = 1.0 if total == 0 else round(passed_count / total, 3)
    return {
        "score": score,
        "passed": passed_count == total,
        "checks": checks,
    }


def run_scenario(scenario: dict, config: dict, suite=None) -> dict:
    scenario = copy.deepcopy(scenario)
    suite = suite or {}

    generated_context_chars = {}
    if scenario.get("generated_context"):
        generated = build_generated_context(scenario["generated_context"])
        scenario = replace_generated_context(scenario, generated)
        generated_context_chars["GENERATED_CONTEXT"] = len(generated)

    for name, spec in scenario.get("generated_contexts", {}).items():
        generated = build_generated_context(spec)
        placeholder = "{{" + name + "}}"
        scenario = replace_generated_context(scenario, generated, placeholder)
        generated_context_chars[name] = len(generated)

    system = scenario.get("system")
    messages = scenario["messages"]
    tools = scenario.get("tools", [])
    mock_tools = scenario.get("mock_tools", {})
    max_tool_rounds = int(scenario.get("max_tool_rounds", 4))

    payload = {
        "model": config["model"],
        "max_tokens": scenario.get("max_tokens", 1200),
        "messages": messages,
    }
    if system is not None:
        payload["system"] = system
    if "temperature" in scenario:
        payload["temperature"] = scenario["temperature"]
    if "thinking" in scenario:
        payload["thinking"] = scenario["thinking"]
    if tools:
        payload["tools"] = tools
    if "tool_choice" in scenario:
        payload["tool_choice"] = scenario["tool_choice"]

    history = copy.deepcopy(messages)
    tool_names_seen = []
    raw_rounds = []
    round_metrics = []
    final_response = None

    for round_index in range(max_tool_rounds + 1):
        round_payload = dict(payload)
        round_payload["messages"] = history
        started_at = time.perf_counter()
        response = api_call(config["endpoint"], config["api_key"], round_payload, config["timeout"])
        latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
        raw_rounds.append(response)
        usage = response.get("usage", {})
        round_metrics.append(
            {
                "round_index": round_index + 1,
                "latency_ms": latency_ms,
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0),
                "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0),
            }
        )
        final_response = response

        content = response.get("content", [])
        history.append({"role": "assistant", "content": content})
        tool_uses = extract_tool_uses(content)

        if not tool_uses:
            break

        results = []
        for tool_use in tool_uses:
            tool_name = tool_use.get("name", "")
            tool_names_seen.append(tool_name)
            mock = mock_tools.get(tool_name)
            if mock is None:
                results.append(make_tool_result(tool_use["id"], f"No mock configured for {tool_name}", True))
            elif isinstance(mock, dict) and "__tool_error__" in mock:
                results.append(make_tool_result(tool_use["id"], mock["__tool_error__"], True))
            else:
                results.append(make_tool_result(tool_use["id"], mock, False))

        history.append({"role": "user", "content": results})

        if round_index == max_tool_rounds:
            break

    final_text = extract_text((final_response or {}).get("content", []))
    usage = (final_response or {}).get("usage", {})
    aggregate_metrics = {
        "round_count": len(raw_rounds),
        "first_round_latency_ms": round_metrics[0]["latency_ms"] if round_metrics else 0,
        "total_latency_ms": round(sum(item["latency_ms"] for item in round_metrics), 2),
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0),
        "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0),
    }
    evaluation = evaluate_text(final_text, scenario.get("expected", {}), tool_names_seen, aggregate_metrics)
    tool_metrics = compute_tool_metrics(scenario.get("expected", {}), tool_names_seen)
    output_metrics = compute_output_metrics(final_text, evaluation)

    return {
        "id": scenario["id"],
        "title": scenario.get("title", scenario["id"]),
        "category": scenario.get("category"),
        "metadata": scenario_metadata(scenario, suite),
        "skip_by_default": scenario.get("skip_by_default", False),
        "generated_context_chars": sum(generated_context_chars.values()),
        "generated_context_char_map": generated_context_chars,
        "tool_names_seen": tool_names_seen,
        "tool_metrics": tool_metrics,
        "output_metrics": output_metrics,
        "evaluation": evaluation,
        "usage": usage,
        "metrics": aggregate_metrics,
        "round_metrics": round_metrics,
        "final_text": final_text,
        "round_count": len(raw_rounds),
        "raw_rounds": raw_rounds,
    }


def summarize_trials(trials: list, pass_k_values: list) -> dict:
    if not trials:
        return {
            "trial_count": 0,
            "pass_rate": 0.0,
            "pass_rate_ci95": [0.0, 0.0],
            "pass_at_k": {},
            "prefix_pass_at_k": {},
            "exact_output_consistency": 0.0,
            "unique_normalized_outputs": 0,
        }

    pass_bools = [trial["evaluation"]["passed"] for trial in trials]
    evaluation_scores = [trial["evaluation"]["score"] for trial in trials]
    normalized_outputs = [normalize_text(trial["final_text"]) for trial in trials]
    non_empty_outputs = [item for item in normalized_outputs if item]
    counts = {}
    for item in non_empty_outputs:
        counts[item] = counts.get(item, 0) + 1

    dominant = max(counts.values()) if counts else 0
    trial_count = len(trials)
    successes = sum(pass_bools)
    pass_at_k = {}
    prefix_pass_at_k = {}
    for k in pass_k_values:
        pass_at_k[str(k)] = estimate_pass_at_k(trial_count, successes, k)
        prefix_pass_at_k[str(k)] = any(pass_bools[:k]) if trial_count >= k else None

    total_latency = [trial["metrics"]["total_latency_ms"] for trial in trials]
    first_round_latency = [trial["metrics"]["first_round_latency_ms"] for trial in trials]
    round_counts = [trial["metrics"]["round_count"] for trial in trials]
    output_chars = [trial["output_metrics"]["output_chars"] for trial in trials]
    context_chars = [trial.get("generated_context_chars", 0) for trial in trials]
    tool_call_counts = [trial["tool_metrics"]["tool_call_count"] for trial in trials]
    required_tool_coverage = [
        trial["tool_metrics"]["required_tool_coverage"]
        for trial in trials
        if trial["tool_metrics"].get("required_tool_coverage") is not None
    ]
    tool_precision_proxy = [
        trial["tool_metrics"]["tool_precision_proxy"]
        for trial in trials
        if trial["tool_metrics"].get("tool_precision_proxy") is not None
    ]
    forbidden_tool_calls = [trial["tool_metrics"]["forbidden_tool_call_count"] for trial in trials]
    repeated_tool_calls = [trial["tool_metrics"]["repeated_tool_call_count"] for trial in trials]
    json_contract_values = [
        trial["output_metrics"]["json_contract_passed"]
        for trial in trials
        if trial["output_metrics"].get("json_contract_passed") is not None
    ]

    return {
        "trial_count": trial_count,
        "success_count": successes,
        "pass_rate": round(successes / trial_count, 3),
        "pass_rate_ci95": wilson_interval(successes, trial_count),
        "pass_at_k": pass_at_k,
        "prefix_pass_at_k": prefix_pass_at_k,
        "avg_evaluation_score": round(sum(evaluation_scores) / trial_count, 3),
        "exact_output_consistency": round(dominant / trial_count, 3) if trial_count else 0.0,
        "unique_normalized_outputs": len(counts),
        "avg_total_latency_ms": round(sum(total_latency) / trial_count, 2),
        "p50_total_latency_ms": percentile(total_latency, 0.5),
        "p95_total_latency_ms": percentile(total_latency, 0.95),
        "avg_first_round_latency_ms": round(sum(first_round_latency) / trial_count, 2),
        "p95_first_round_latency_ms": percentile(first_round_latency, 0.95),
        "avg_round_count": round(sum(round_counts) / trial_count, 3),
        "avg_output_chars": round(sum(output_chars) / trial_count, 1),
        "avg_generated_context_chars": round(sum(context_chars) / trial_count, 1),
        "avg_tool_call_count": round(sum(tool_call_counts) / trial_count, 3),
        "avg_required_tool_coverage": round(sum(required_tool_coverage) / len(required_tool_coverage), 3)
        if required_tool_coverage
        else None,
        "avg_tool_precision_proxy": round(sum(tool_precision_proxy) / len(tool_precision_proxy), 3)
        if tool_precision_proxy
        else None,
        "avg_forbidden_tool_calls": round(sum(forbidden_tool_calls) / trial_count, 3),
        "avg_repeated_tool_calls": round(sum(repeated_tool_calls) / trial_count, 3),
        "json_contract_pass_rate": round(sum(1 for item in json_contract_values if item) / len(json_contract_values), 3)
        if json_contract_values
        else None,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Agent Peak Bench evaluation suites.")
    parser.add_argument("--suite", action="append", required=True, help="Path to a suite JSON file.")
    parser.add_argument("--include-skipped", action="store_true", help="Run scenarios marked skip_by_default.")
    parser.add_argument(
        "--model",
        default=env_first("MODEL_NAME", "MINIMAX_MODEL", default="MiniMax-M2.7-highspeed"),
    )
    parser.add_argument(
        "--base-url",
        default=env_first("MODEL_API_BASE", "MINIMAX_API_BASE", default="https://api.minimax.io/anthropic"),
        help="Anthropic-compatible base URL. MODEL_API_BASE is preferred; MINIMAX_API_BASE is kept as a compatibility alias.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(env_first("MODEL_TIMEOUT_SECONDS", "MINIMAX_TIMEOUT_SECONDS", default="300")),
        help="Per-request timeout in seconds.",
    )
    parser.add_argument(
        "--out",
        default="",
        help="Optional explicit output file path. Defaults to results/<timestamp>.json",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Default number of repeated trials per scenario for pass@k and consistency metrics.",
    )
    parser.add_argument(
        "--force-repeat",
        type=int,
        default=0,
        help="Override scenario-level repeat values. Use this for pass@k sweeps such as pass@5/pass@7.",
    )
    parser.add_argument(
        "--pass-k",
        default="1,3,5,7,10",
        help="Comma-separated k values used when summarizing repeated trials.",
    )
    parser.add_argument(
        "--campaign-id",
        default=os.environ.get("EVAL_CAMPAIGN_ID", ""),
        help="Optional long-running campaign identifier written into result metadata.",
    )
    parser.add_argument(
        "--run-notes",
        default=os.environ.get("EVAL_RUN_NOTES", ""),
        help="Optional notes for this batch run.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = env_first("MODEL_API_KEY", "MINIMAX_API_KEY", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")
    if not api_key:
        print(
            "Missing MODEL_API_KEY. Compatibility aliases: MINIMAX_API_KEY, ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN.",
            file=sys.stderr,
        )
        return 2

    endpoint = normalize_base_url(args.base_url)
    suites = [Path(item).resolve() for item in args.suite]

    config = {
        "api_key": api_key,
        "endpoint": endpoint,
        "model": args.model,
        "timeout": args.timeout,
    }
    pass_k_values = sorted({int(item) for item in args.pass_k.split(",") if item.strip()})

    run_started_at = dt.datetime.now().isoformat()
    suite_results = []
    total_scenarios = 0
    first_trial_passed = 0
    scenarios_with_any_success = 0
    total_trials = 0
    total_successes = 0
    aggregate_pass_at_k = {str(k): [] for k in pass_k_values}
    scenario_pass_rates = []

    for suite_path in suites:
        suite = load_suite(suite_path)
        scenarios = suite.get("scenarios", [])
        suite_output = {
            "suite_path": str(suite_path),
            "suite_name": suite.get("suite_name", suite_path.stem),
            "description": suite.get("description", ""),
            "results": [],
        }
        suite_default_repeat = int(suite.get("default_repeat", args.repeat))
        for scenario in scenarios:
            if scenario.get("skip_by_default") and not args.include_skipped:
                suite_output["results"].append(
                    {
                        "id": scenario["id"],
                        "title": scenario.get("title", scenario["id"]),
                        "skipped": True,
                        "reason": "skip_by_default",
                    }
                )
                continue

            print(f"Running {scenario['id']}...", file=sys.stderr)
            total_scenarios += 1
            repeat_count = int(args.force_repeat or scenario.get("repeat", suite_default_repeat))
            trials = []
            for trial_index in range(repeat_count):
                print(f"  trial {trial_index + 1}/{repeat_count}", file=sys.stderr)
                trial_result = run_scenario(scenario, config, suite)
                trial_result["trial_index"] = trial_index + 1
                trials.append(trial_result)
            summary = summarize_trials(trials, pass_k_values)
            for k, passed in summary["pass_at_k"].items():
                if passed is not None:
                    aggregate_pass_at_k[k].append(float(passed))
            scenario_pass_rates.append(summary["pass_rate"])
            total_trials += summary["trial_count"]
            total_successes += summary["success_count"]
            if summary["success_count"] > 0:
                scenarios_with_any_success += 1
            result = {
                "id": scenario["id"],
                "title": scenario.get("title", scenario["id"]),
                "category": scenario.get("category"),
                "metadata": scenario_metadata(scenario, suite),
                "repeat_count": repeat_count,
                "trial_summary": summary,
                "trials": trials,
                "evaluation": trials[0]["evaluation"],
            }
            if summary["prefix_pass_at_k"].get("1", False):
                first_trial_passed += 1
            suite_output["results"].append(result)
        suite_results.append(suite_output)

    summary = {
        "run_started_at": run_started_at,
        "run_finished_at": dt.datetime.now().isoformat(),
        "campaign_id": args.campaign_id,
        "run_notes": args.run_notes,
        "model": args.model,
        "endpoint": endpoint,
        "total_scenarios": total_scenarios,
        "total_trials": total_trials,
        "total_successes": total_successes,
        "first_trial_passed_scenarios": first_trial_passed,
        "scenarios_with_any_success": scenarios_with_any_success,
        "pass_rate": 0 if total_trials == 0 else round(total_successes / total_trials, 3),
        "pass_rate_ci95": wilson_interval(total_successes, total_trials),
        "mean_scenario_pass_rate": round(sum(scenario_pass_rates) / len(scenario_pass_rates), 3)
        if scenario_pass_rates
        else 0.0,
        "pass_at_k": {
            key: round(sum(values) / len(values), 3) if values else None for key, values in aggregate_pass_at_k.items()
        },
    }

    output = {
        "summary": summary,
        "suites": suite_results,
    }

    out_path = Path(args.out).resolve() if args.out else ROOT / "results" / f"agent-peak-evals-{now_slug()}.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nWrote results to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
