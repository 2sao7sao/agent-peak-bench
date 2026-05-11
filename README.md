# Agent Peak Bench

<p align="center">
  <strong>Turn a business goal into model capability tests, failure diagnosis, and an agent deployment cookbook.</strong>
</p>

<p align="center">
  <a href="./README.zh-CN.md">简体中文</a>
  ·
  <a href="https://2sao7sao.github.io/agent-peak-bench/">Live Page</a>
  ·
  <a href="https://2sao7sao.github.io/agent-peak-bench/multi-model-dashboard.html">Dashboard</a>
  ·
  <a href="./public/benchmark-samples/agent-peak-product-demo-output.json">Product Demo Output</a>
  ·
  <a href="./CONTRIBUTING.md">Contributing</a>
</p>

<p align="center">
  <img alt="Benchmark" src="https://img.shields.io/badge/benchmark-business--goal--driven-0f766e">
  <img alt="Scenarios" src="https://img.shields.io/badge/scenarios-104-2563eb">
  <img alt="Product demo" src="https://img.shields.io/badge/product_demo-PASS-167b63">
  <img alt="Case Study" src="https://img.shields.io/badge/case_study-MiniMax_M2.7_High-b7410e">
</p>

## Stop Asking "Which Model Is Best?"

The deployment question is narrower and more useful:

> **Given this business workflow, which model capability boundaries matter, what harness is required, and what should the final agent architecture look like?**

Agent Peak Bench is a harness-first evaluation kit. It starts from commercial
objectives such as security review acceleration, refund automation, renewal risk
diagnosis, and finance close. Then it turns those objectives into capability
probes, repeated benchmark campaigns, model failure attribution, and deployment
cookbooks.

![Business-goal product demo](docs/assets/business-goal-demo.svg)

> [!IMPORTANT]
> MiniMax M2.7 High is the first measured case study. The benchmark framework is
> model-agnostic. Non-measured dashboard rows are fixtures and must not be read
> as benchmark claims.

## 30-Second Product Path

```text
Business goal
  -> capability map
  -> benchmark suite
  -> repeated trials
  -> failure attribution
  -> harness design
  -> deployment cookbook
  -> model-vendor feedback
```

| If you have... | Agent Peak Bench produces... |
| --- | --- |
| A vague business idea | Required model capabilities and evaluation scope |
| A target workflow | Suite skeletons with tools, approvals, expected outputs, and failure taxonomy |
| A candidate model | pass@k, CI95, tool precision, schema adherence, latency, and consistency signals |
| A deployment decision | Single-agent vs multi-agent, memory/RAG/MCP/skills/verifier/approval guidance |
| A model-provider discussion | Reproducible failure clusters and optimization feedback |

## 5-Minute Product Demo

Run the dry-run product path. It does not call a model or use provider secrets.

```bash
git clone https://github.com/2sao7sao/agent-peak-bench.git
cd agent-peak-bench
python3 -m pip install pyyaml
python3 scripts/run_product_demo.py
```

Expected shape:

```text
# Agent Peak Bench Product Demo

status: PASS
business_profiles: 3
generated_scenarios: 3
capability_items: 15
required_tools: 13
forbidden_side_effect_tools: 8

## Product metrics
- business_goal_to_suite_rate: 1.00 (3/3)
- capability_mapping_rate: 1.00 (3/3)
- governance_contract_rate: 1.00 (3/3)
- cookbook_completeness_rate: 1.00 (3/3)
- campaign_confidence_contract_rate: 1.00 (1/1)
```

The machine-readable sample is published at
[`public/benchmark-samples/agent-peak-product-demo-output.json`](./public/benchmark-samples/agent-peak-product-demo-output.json).

## What The Demo Proves

The demo validates the project itself, not a model score.

| Metric | What it checks | Why it matters |
| --- | --- | --- |
| `business_goal_to_suite_rate` | Business profiles become benchmark scenarios | Evaluation starts from user/commercial goals, not random tasks |
| `capability_mapping_rate` | Scenarios include capabilities, benchmark mappings, and output contracts | Results can be traced back to deployment requirements |
| `governance_contract_rate` | Side-effect actions are forbidden without approval | Agent benchmarks must test safety and authority boundaries |
| `cookbook_completeness_rate` | Profiles include topology, memory, RAG, tools, skills, and verifier guidance | Scores turn into engineering decisions |
| `campaign_confidence_contract_rate` | Campaign defines r7/r30/r100 and pass@k policy | Boundary claims require repeated trials, not one-off runs |
| `capability_surface_presence_rate` | Required tools, forbidden tools, and decision objectives are visible | Harness design is first-class, not hidden in prose |

## Run The Core Workflows

Generate a suite skeleton from business profiles:

```bash
python3 scripts/generate_business_goal_suite.py \
  evals/business_goals/security_review_acceleration.yaml \
  evals/business_goals/support_refund_automation.yaml \
  evals/business_goals/renewal_risk_diagnosis.yaml \
  --out /tmp/business-goal-suite.json
```

Plan a campaign without calling a model:

```bash
python3 scripts/run_eval_campaign.py \
  evals/campaigns/harness_engineering_campaign_v1.json \
  --batch business_goal_mapping_pilot
```

Run one suite with an Anthropic-compatible provider:

```bash
export MODEL_API_KEY="your_key"
export MODEL_NAME="target-model"
export MODEL_API_BASE="https://provider.example.com/anthropic/v1/messages"

python3 scripts/run_minimax_evals.py \
  --suite evals/suites/business_goal_agent_synthesis_v1.json \
  --pass-k 1,3,5,7,10 \
  --out results/model-business-goal-agent-synthesis-v1.json
```

## What Gets Tested

| Layer | Example deployment question |
| --- | --- |
| Business fit | Can the model recover the real objective from vague stakeholder language? |
| Tool use | Can it call the right systems and avoid dangerous side-effect tools? |
| Context pressure | Where do long, noisy, or ambiguous contexts cause drift? |
| Skills and MCP | Do procedural skills, routers, and focused tools improve stability? |
| Multi-agent design | When does planner/executor/verifier beat a single agent? |
| Governance | Does it respect permissions, approvals, missing evidence, and audit needs? |
| Reliability | How do pass@1/3/5/7/10, CI95, latency, and consistency move? |

## Primary Suites

| Suite | Role |
| --- | --- |
| [`business_goal_agent_synthesis_v1`](./evals/suites/business_goal_agent_synthesis_v1.json) | Turns commercial objectives into capability maps, benchmark plans, cookbooks, and vendor feedback. |
| [`enterprise_agent_landing_v3`](./evals/suites/enterprise_agent_landing_v3.json) | End-to-end enterprise tasks with implicit intent, cross-system evidence, governance, and long-running resume. |
| [`tool_skill_mcp_ablation_v3`](./evals/suites/tool_skill_mcp_ablation_v3.json) | Focused tools vs flat overload vs router layering vs procedural skills. |
| [`tool_return_profiles_v1`](./evals/suites/tool_return_profiles_v1.json) | Short JSON, long noisy returns, conflicting evidence, permission errors, and large logs. |
| [`openclaw_complex_agent_tasks_v1`](./evals/suites/openclaw_complex_agent_tasks_v1.json) | Personal OS, voice-triggered production fixes, async GitHub, multi-agent ops, plugin governance, and memory safety. |

## Current Evidence

The first public measured case study is **MiniMax M2.7 High r7 pilot**:

| Scope | Value |
| --- | ---: |
| Suites | `4` |
| Scenarios | `19` |
| Trials | `133` |
| Confidence label | `pilot` |

Public assets:

| Asset | Purpose |
| --- | --- |
| [Integrated report](./report/agent-peak-bench-integrated-report.zh-CN.md) | MiniMax case-study interpretation and methodology. |
| [Multi-model dashboard](./docs/multi-model-dashboard.html) | Static dashboard contract with measured/fixture status labels. |
| [Measured sample output](./public/benchmark-samples/minimax-r7-sample-output.json) | Sanitized aggregate benchmark sample. |
| [Product demo output](./public/benchmark-samples/agent-peak-product-demo-output.json) | Deterministic project workflow sample. |

![Benchmark sample output](docs/assets/benchmark-sample-output.svg)

## Stable vs Prototype

| Layer | Current status |
| --- | --- |
| Business-goal profiles and suite generator | Supported project path |
| Campaign planner and summarizer | Supported for dry-run planning and result aggregation |
| Provider runner | Works with Anthropic-compatible APIs, requires user credentials |
| MiniMax report | Pilot case study only, not a final leaderboard |
| Multi-model dashboard | Contract and sample UI; non-measured rows are fixtures |
| Strong deployment claims | Require r30/r100 cells, CI95, and stable failure taxonomy |

## Repository Map

```text
evals/business_goals/     business profiles that generate suite skeletons
evals/suites/             benchmark suites
evals/campaigns/          multi-day / multi-week campaign specs
scripts/                  product demo, runner, campaign planner, summarizer, generator
docs/                     GitHub Pages, dashboard, chart assets
public/                   sanitized result samples and dashboard contracts
report/                   integrated report, methodology, system card, analysis
```

## Security

Do not commit API keys, provider secrets, raw traces, customer data, private tool
outputs, or live system exports. Public releases should contain sanitized
summaries, aggregate metrics, failure taxonomy, and engineering guidance only.

## License

MIT. See [LICENSE](LICENSE).
