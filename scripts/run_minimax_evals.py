#!/usr/bin/env python3

import argparse
import copy
import datetime as dt
import json
import os
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


def replace_generated_context(node, generated: str):
    if isinstance(node, str):
        return node.replace("{{GENERATED_CONTEXT}}", generated)
    if isinstance(node, list):
        return [replace_generated_context(item, generated) for item in node]
    if isinstance(node, dict):
        return {key: replace_generated_context(value, generated) for key, value in node.items()}
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
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None


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


def run_scenario(scenario: dict, config: dict) -> dict:
    scenario = copy.deepcopy(scenario)

    generated = ""
    if scenario.get("generated_context"):
        generated = build_generated_context(scenario["generated_context"])
        scenario = replace_generated_context(scenario, generated)

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

    return {
        "id": scenario["id"],
        "title": scenario.get("title", scenario["id"]),
        "category": scenario.get("category"),
        "skip_by_default": scenario.get("skip_by_default", False),
        "generated_context_chars": len(generated),
        "tool_names_seen": tool_names_seen,
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
            "pass_at_k": {},
            "exact_output_consistency": 0.0,
            "unique_normalized_outputs": 0,
        }

    pass_bools = [trial["evaluation"]["passed"] for trial in trials]
    normalized_outputs = [normalize_text(trial["final_text"]) for trial in trials]
    non_empty_outputs = [item for item in normalized_outputs if item]
    counts = {}
    for item in non_empty_outputs:
        counts[item] = counts.get(item, 0) + 1

    dominant = max(counts.values()) if counts else 0
    trial_count = len(trials)
    pass_at_k = {}
    for k in pass_k_values:
        actual_k = min(k, trial_count)
        pass_at_k[str(k)] = any(pass_bools[:actual_k])

    total_latency = [trial["metrics"]["total_latency_ms"] for trial in trials]
    first_round_latency = [trial["metrics"]["first_round_latency_ms"] for trial in trials]

    return {
        "trial_count": trial_count,
        "pass_rate": round(sum(pass_bools) / trial_count, 3),
        "pass_at_k": pass_at_k,
        "exact_output_consistency": round(dominant / trial_count, 3) if trial_count else 0.0,
        "unique_normalized_outputs": len(counts),
        "avg_total_latency_ms": round(sum(total_latency) / trial_count, 2),
        "avg_first_round_latency_ms": round(sum(first_round_latency) / trial_count, 2),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MiniMax M2.7 evaluation suites.")
    parser.add_argument("--suite", action="append", required=True, help="Path to a suite JSON file.")
    parser.add_argument("--include-skipped", action="store_true", help="Run scenarios marked skip_by_default.")
    parser.add_argument("--model", default=os.environ.get("MINIMAX_MODEL", "MiniMax-M2.7-highspeed"))
    parser.add_argument(
        "--base-url",
        default=os.environ.get("MINIMAX_API_BASE", "https://api.minimax.io/anthropic"),
        help="Base URL, usually https://api.minimax.io/anthropic",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.environ.get("MINIMAX_TIMEOUT_SECONDS", "300")),
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
        "--pass-k",
        default="1,3,5",
        help="Comma-separated k values used when summarizing repeated trials.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get(
        "ANTHROPIC_AUTH_TOKEN"
    )
    if not api_key:
        print("Missing MINIMAX_API_KEY (or ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN).", file=sys.stderr)
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
    total_passed = 0
    aggregate_pass_at_k = {str(k): [] for k in pass_k_values}

    for suite_path in suites:
        suite = load_suite(suite_path)
        scenarios = suite.get("scenarios", [])
        suite_output = {
            "suite_path": str(suite_path),
            "suite_name": suite.get("suite_name", suite_path.stem),
            "description": suite.get("description", ""),
            "results": [],
        }
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
            repeat_count = int(scenario.get("repeat", args.repeat))
            trials = []
            for trial_index in range(repeat_count):
                print(f"  trial {trial_index + 1}/{repeat_count}", file=sys.stderr)
                trial_result = run_scenario(scenario, config)
                trial_result["trial_index"] = trial_index + 1
                trials.append(trial_result)
            summary = summarize_trials(trials, pass_k_values)
            for k, passed in summary["pass_at_k"].items():
                aggregate_pass_at_k[k].append(1 if passed else 0)
            result = {
                "id": scenario["id"],
                "title": scenario.get("title", scenario["id"]),
                "category": scenario.get("category"),
                "repeat_count": repeat_count,
                "trial_summary": summary,
                "trials": trials,
                "evaluation": trials[0]["evaluation"],
            }
            if summary["pass_at_k"].get("1", False):
                total_passed += 1
            suite_output["results"].append(result)
        suite_results.append(suite_output)

    summary = {
        "run_started_at": run_started_at,
        "run_finished_at": dt.datetime.now().isoformat(),
        "model": args.model,
        "endpoint": endpoint,
        "total_scenarios": total_scenarios,
        "total_passed": total_passed,
        "pass_rate": 0 if total_scenarios == 0 else round(total_passed / total_scenarios, 3),
        "pass_at_k": {
            key: round(sum(values) / len(values), 3) if values else 0.0 for key, values in aggregate_pass_at_k.items()
        },
    }

    output = {
        "summary": summary,
        "suites": suite_results,
    }

    out_path = Path(args.out).resolve() if args.out else ROOT / "results" / f"minimax-evals-{now_slug()}.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nWrote results to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
