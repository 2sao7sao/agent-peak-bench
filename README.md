# Agent Peak Bench

<p align="center">
  <strong>Harness-first benchmark for agent deployment: realistic tasks, failure attribution, engineering design, and model usage guidance.</strong>
</p>

<p align="center">
  <a href="https://2sao7sao.github.io/agent-peak-bench/"><img alt="Live Report" src="https://img.shields.io/badge/report-live-0f766e?style=for-the-badge"></a>
  <a href="./report/agent-peak-bench-integrated-report.zh-CN.md"><img alt="Integrated Report" src="https://img.shields.io/badge/report-integrated-111827?style=for-the-badge"></a>
  <a href="./evals/benchmark_manifest_v2.json"><img alt="Benchmark Manifest" src="https://img.shields.io/badge/benchmark-v3.0-2563eb?style=for-the-badge"></a>
  <img alt="No Secrets" src="https://img.shields.io/badge/secrets-not_published-b91c1c?style=for-the-badge">
</p>

<p align="center">
  <a href="./README.zh-CN.md">中文</a>
  ·
  <a href="./report/agent-peak-bench-integrated-report.zh-CN.md">Integrated report</a>
  ·
  <a href="./docs/evaluation-samples.zh-CN.md">Evaluation samples</a>
  ·
  <a href="https://2sao7sao.github.io/agent-peak-bench/">GitHub Pages</a>
</p>

## Purpose

Agent Peak Bench is not a single-score leaderboard. It is designed to answer a deployment question:

> Under which harness, tool, MCP, skill, context, and verification conditions can a model reliably complete real agent tasks?

The main entry point is the [integrated report](./report/agent-peak-bench-integrated-report.zh-CN.md), which consolidates methodology, enterprise scenarios, OpenClaw-inspired complex tasks, tool/skill/MCP attribution, and MiniMax M2.7 High usage guidance.

Early smoke/canary results are kept only for runner validation and are not presented as README-level model conclusions.

## Primary Suites

| Suite | Purpose | What it evaluates |
| --- | --- | --- |
| [`enterprise_agent_landing_v3.json`](./evals/suites/enterprise_agent_landing_v3.json) | Realistic enterprise-agent tasks | Implicit intent, enterprise knowledge retrieval, multi-MCP tool use, governance, complex decomposition, long-running resume. |
| [`tool_skill_mcp_ablation_v3.json`](./evals/suites/tool_skill_mcp_ablation_v3.json) | Engineering attribution | Focused 3-tool surface vs flat 14-tool overload vs router layering vs procedural skill contracts. |
| [`openclaw_complex_agent_tasks_v1.json`](./evals/suites/openclaw_complex_agent_tasks_v1.json) | OpenClaw-style complex tasks | Personal OS, voice-driven production fix, async GitHub, multi-agent ops, plugin governance, persistent memory security. |

## Evaluation Loop

```mermaid
flowchart LR
  A["Realistic Task"] --> B["Capability Observation"]
  B --> C["End-to-End Reliability"]
  C --> D["pass@k Stability"]
  D --> E["Failure Attribution"]
  E --> F["Harness Design"]
  F --> G["Model Usage Guide"]
```

## Key Questions

| Question | Evaluation path |
| --- | --- |
| Can the model infer implicit user intent rather than only follow explicit instructions? | Security review, renewal risk, analytics, OpenClaw personal OS tasks. |
| How many tools can be exposed before stability degrades? | 3 focused tools vs 14 flat tools vs router-layered ablation. |
| When do MCP and skills help or hurt? | `tool_skill_mcp_ablation_v3`. |
| How should complex systems be decomposed? | Enterprise knowledge-agent architecture, multi-agent handoff, OpenClaw complex tasks. |
| Is persistent memory safe? | OpenClaw workspace memory and prompt-injection scenarios. |
| What if pass@1 is low but pass@7 is high? | Use retry, verifier, repair loops, and permission gates rather than direct autonomous execution. |

## Run

```bash
export MINIMAX_API_KEY="your_key"
export MINIMAX_MODEL="MiniMax-M2.7-highspeed"
export MINIMAX_API_BASE="https://api.minimaxi.com/anthropic/v1/messages"
```

Run the primary suites:

```bash
python3 scripts/run_minimax_evals.py \
  --suite evals/suites/enterprise_agent_landing_v3.json \
  --pass-k 1,3,5,7 \
  --out results/minimax-enterprise-agent-v3.json

python3 scripts/run_minimax_evals.py \
  --suite evals/suites/tool_skill_mcp_ablation_v3.json \
  --pass-k 1,3,5,7 \
  --out results/minimax-tool-skill-mcp-ablation-v3.json

python3 scripts/run_minimax_evals.py \
  --suite evals/suites/openclaw_complex_agent_tasks_v1.json \
  --pass-k 1,3,5,7 \
  --out results/minimax-openclaw-complex-v1.json
```

Check benchmark distribution:

```bash
python3 scripts/check_benchmark_distribution.py
```

## Repository Map

| Path | Purpose |
| --- | --- |
| [`report/agent-peak-bench-integrated-report.zh-CN.md`](./report/agent-peak-bench-integrated-report.zh-CN.md) | Single integrated report. |
| [`docs/evaluation-samples.zh-CN.md`](./docs/evaluation-samples.zh-CN.md) | Realistic sample design and scoring examples. |
| [`evals/suites/`](./evals/suites) | Evaluation suites. |
| [`scripts/run_minimax_evals.py`](./scripts/run_minimax_evals.py) | MiniMax-compatible evaluator runner. |
| [`scripts/summarize_eval_results.py`](./scripts/summarize_eval_results.py) | Result summarizer. |
| [`scripts/check_benchmark_distribution.py`](./scripts/check_benchmark_distribution.py) | Task-family distribution checker. |

## Security

- Do not commit API keys, tokens, cookies, raw traces, or private tool outputs.
- `results/` is local-only and gitignored.
- Public releases should contain only sanitized summaries, aggregate metrics, failure taxonomy, and engineering guidance.
