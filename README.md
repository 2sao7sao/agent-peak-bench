# Agent Peak Bench

Agent Peak Bench is a harness-first benchmark kit for evaluating whether agentic models can stay in a high-performing operating state under realistic system conditions.

The first published model case is `MiniMax-M2.7-highspeed`, reported as `MiniMax M2.7 High`.

## Public Report

- [docs/index.html](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/docs/index.html): public report page with radar chart and dimension scores
- [public/minimax-m27-high-summary.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/public/minimax-m27-high-summary.json): sanitized public result summary
- [report/public-release-summary.md](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/report/public-release-summary.md): release summary

Current MiniMax M2.7 High live canary:

- `pass@1 = 25%`
- `pass@3 = 50%`
- best dimension: short schema-constrained memory
- riskiest dimensions: long noisy history, strict workflow orchestration, skill-only control

This repository includes:

- A Chinese `system card` style report modeled after Anthropic's long-form release notes
- A harness-oriented practical evaluation playbook for chatbot / agent / multi-agent scenarios
- A MiniMax agent usage handbook covering skills, tools, windows, decomposition, and unsuitable scenarios
- A polished single-page HTML report that can be exported to PDF
- An automated evaluation harness for smoke tests, ablations, and benchmark prototyping

## Files

- [report/minimax-m27-system-card.md](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/report/minimax-m27-system-card.md)
- [report/minimax-m27-system-card.html](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/report/minimax-m27-system-card.html)
- [report/minimax-harness-eval-playbook.md](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/report/minimax-harness-eval-playbook.md)
- [report/minimax-agent-usage-handbook.md](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/report/minimax-agent-usage-handbook.md)
- [report/benchmark-framework-review.md](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/report/benchmark-framework-review.md)
- [report/agent-era-benchmark-principles.md](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/report/agent-era-benchmark-principles.md)
- [report/open-claude-code-system-analysis.md](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/report/open-claude-code-system-analysis.md)
- [evals/README.md](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/README.md)
- [evals/benchmark_manifest_v2.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/benchmark_manifest_v2.json)
- [evals/blueprints/minimax_real_task_benchmark.md](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/blueprints/minimax_real_task_benchmark.md)
- [scripts/run_minimax_evals.py](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/scripts/run_minimax_evals.py)
- [scripts/check_benchmark_distribution.py](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/scripts/check_benchmark_distribution.py)
- [evals/suites/context_windows.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/context_windows.json)
- [evals/suites/tool_and_workflow.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/tool_and_workflow.json)
- [evals/suites/complex_systems.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/complex_systems.json)
- [evals/suites/behavior_and_rigor.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/behavior_and_rigor.json)
- [evals/suites/chatbot_memory_latency.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/chatbot_memory_latency.json)
- [evals/suites/agent_workflow_practice.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/agent_workflow_practice.json)
- [evals/suites/multi_agent_content_harness.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/multi_agent_content_harness.json)
- [evals/suites/repeatability_passk.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/repeatability_passk.json)
- [evals/suites/skill_design_ablation.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/skill_design_ablation.json)
- [evals/suites/tool_count_ablation.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/tool_count_ablation.json)
- [evals/suites/window_and_decomposition_ablation.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/window_and_decomposition_ablation.json)
- [evals/suites/agent_harness_design_v2.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/agent_harness_design_v2.json)
- [evals/suites/harness_load_bearing_ablation_v2.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/harness_load_bearing_ablation_v2.json)
- [evals/suites/agent_landing_distribution_v2.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/agent_landing_distribution_v2.json)

## Run the evaluator

Set your API key and choose the model:

```bash
export MINIMAX_API_KEY="your_key"
export MINIMAX_MODEL="MiniMax-M2.7-highspeed"
python3 scripts/run_minimax_evals.py --suite evals/suites/repeatability_passk.json --repeat 5 --pass-k 1,3,5
python3 scripts/run_minimax_evals.py --suite evals/suites/skill_design_ablation.json
python3 scripts/run_minimax_evals.py --suite evals/suites/tool_count_ablation.json --include-skipped
python3 scripts/run_minimax_evals.py --suite evals/suites/window_and_decomposition_ablation.json
python3 scripts/run_minimax_evals.py --suite evals/suites/agent_harness_design_v2.json --repeat 3 --pass-k 1,3
python3 scripts/run_minimax_evals.py --suite evals/suites/harness_load_bearing_ablation_v2.json --repeat 3 --pass-k 1,3
python3 scripts/run_minimax_evals.py --suite evals/suites/agent_landing_distribution_v2.json --repeat 3 --pass-k 1,3
python3 scripts/run_minimax_evals.py --suite evals/suites/chatbot_memory_latency.json
python3 scripts/run_minimax_evals.py --suite evals/suites/agent_workflow_practice.json
python3 scripts/run_minimax_evals.py --suite evals/suites/multi_agent_content_harness.json
python3 scripts/run_minimax_evals.py --suite evals/suites/context_windows.json
python3 scripts/run_minimax_evals.py --suite evals/suites/tool_and_workflow.json
```

Useful environment variables:

```bash
export MINIMAX_API_BASE="https://api.minimax.io/anthropic"
export MINIMAX_MODEL="MiniMax-M2.7"
export MINIMAX_TIMEOUT_SECONDS="300"
```

Results are written under [results](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/results).

Check task-family coverage:

```bash
python3 scripts/check_benchmark_distribution.py
```

## Harness-Oriented Coverage

- `repeatability_passk.json`: repeated simple-task tests for pass@k, consistency, and jitter
- `skill_design_ablation.json`: compare vague vs structured skill-writing styles
- `tool_count_ablation.json`: compare focused vs overloaded tool surfaces
- `window_and_decomposition_ablation.json`: compare compact vs expanded context and single-shot vs phased task decomposition
- `agent_harness_design_v2.json`: system-level checks for maps, contracts, evaluator separation, context reset, and governance
- `harness_load_bearing_ablation_v2.json`: ablation canaries for planner/evaluator/contracts/resume/ToolSearch
- `agent_landing_distribution_v2.json`: distribution-balancing cases for coding, workflow, tool recovery, multi-agent coordination, and governance
- `chatbot_memory_latency.json`: pure chatbot tests for memory recall, history stability, and latency
- `agent_workflow_practice.json`: simple agent/workflow tests for grounded execution and exit criteria
- `multi_agent_content_harness.json`: multi-agent role split tests for `Content Engineer` + `Harness Engineer`
- `context_windows.json`: long-context retrieval and anti-drift tests
- `tool_and_workflow.json`: interleaved tool use and synthesis tests
- `complex_systems.json`: architecture and multi-window design tests
- `behavior_and_rigor.json`: anti-laziness and completion-honesty tests

## Important Scope

- Current `evals/suites/*.json` are `smoke + ablation` assets, not a production-grade benchmark.
- Their purpose is to compare prompting, skills, tools, windows, and workflow designs.
- Real benchmark work should follow the blueprint in `evals/blueprints/` and the critique in `report/benchmark-framework-review.md`.

## Notes

- The report assumes the user means `MiniMax-M2.7-highspeed` when saying `m2.7high`.
- The evaluator uses the Anthropic-compatible endpoint because MiniMax officially recommends it for thinking blocks, interleaved thinking, and prompt-cache workflows.
- The evaluator records `first_round_latency_ms`, `total_latency_ms`, per-round metrics, final token usage, repeated-trial summaries, and `pass@k`.
- Large context tests can be expensive. The suite marks some high-token cases as `skip_by_default`.
