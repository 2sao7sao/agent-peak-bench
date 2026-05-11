# Agent Peak Bench

<p align="center">
  <strong>Turn business goals into model benchmarks, failure diagnosis, and agent deployment cookbooks.</strong>
</p>

<p align="center">
  <a href="./README.zh-CN.md">简体中文</a>
  ·
  <a href="https://2sao7sao.github.io/agent-peak-bench/">Live Page</a>
  ·
  <a href="https://2sao7sao.github.io/agent-peak-bench/multi-model-dashboard.html">Dashboard</a>
  ·
  <a href="./report/agent-peak-bench-integrated-report.zh-CN.md">Integrated Report</a>
  ·
  <a href="./CONTRIBUTING.md">Contributing</a>
</p>

<p align="center">
  <img alt="Benchmark" src="https://img.shields.io/badge/benchmark-business--goal--driven-0f766e">
  <img alt="Scenarios" src="https://img.shields.io/badge/scenarios-104-2563eb">
  <img alt="Case Study" src="https://img.shields.io/badge/case_study-MiniMax_M2.7_High-b7410e">
  <img alt="No Secrets" src="https://img.shields.io/badge/secrets-not_published-b91c1c">
</p>

## Stop Asking "Which Model Is Best?"

Ask the question that actually matters:

> **Which model can move this business workflow forward, under which harness, with which risks, and with what engineering design?**

Agent Peak Bench is not a leaderboard. It is a harness-first evaluation kit for
turning commercial objectives into:

| Output | What it answers |
| --- | --- |
| Model capability report | What can the model do reliably across agent task families? |
| Business-goal report | Can it handle a concrete workflow such as renewal risk, refund automation, security review, or finance close? |
| Agent cookbook | Should the deployment use single-agent, multi-agent, memory, RAG, MCP routers, skills, verifier loops, or approval gates? |
| Vendor feedback pack | Which reproducible failure clusters should a model provider optimize? |

![Multi-model dashboard](docs/assets/multi-model-dashboard.svg)

> [!IMPORTANT]
> MiniMax M2.7 High is the first measured case study. Agent Peak Bench is
> model-agnostic. Dashboard rows for non-measured models are marked as fixtures
> and must not be interpreted as benchmark claims.

## The 30-Second Pitch

```text
Business goal -> Capability map -> Benchmark suite -> Repeated trials
-> Failure attribution -> Harness design -> Deployment cookbook -> Vendor feedback
```

Most benchmarks tell you whether a model solved a task. Agent deployment needs
to know whether the model can safely move a business process forward.

| Common benchmark | Agent Peak Bench |
| --- | --- |
| Starts from a task dataset | Starts from a business objective |
| Produces a score | Produces capability, risk, cookbook, and vendor feedback |
| Treats tools as a test detail | Tests tool surface, router design, side effects, and approval gates |
| Ignores harness design | Evaluates memory, RAG, skills, MCP, verifier, multi-agent, and context strategy |
| Reports one run | Supports r7 pilot, r30 calibration, and r100 confirmatory cells |

## Run The Business-Goal Workflow

Generate a suite skeleton from business profiles:

```bash
git clone https://github.com/2sao7sao/agent-peak-bench.git
cd agent-peak-bench
python3 scripts/generate_business_goal_suite.py \
  evals/business_goals/security_review_acceleration.yaml \
  evals/business_goals/support_refund_automation.yaml \
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

| Layer | Example questions |
| --- | --- |
| Business fit | Does the model recover the real objective from vague user language? |
| Tool use | Does it call the right systems and avoid dangerous side-effect tools? |
| Context pressure | Does performance degrade under long, noisy, or ambiguous context? |
| Skills and MCP | Do procedural skills, routers, and focused tools improve stability? |
| Multi-agent design | When does planner/executor/verifier beat a single agent? |
| Governance | Does it respect permissions, approvals, missing evidence, and audit needs? |
| Reliability | How do pass@1, pass@3, pass@5, pass@7, pass@10, CI95, latency, and consistency move? |

## Primary Suites

| Suite | Role |
| --- | --- |
| [`business_goal_agent_synthesis_v1`](./evals/suites/business_goal_agent_synthesis_v1.json) | Turns commercial objectives into capability maps, benchmark plans, cookbooks, and vendor feedback. |
| [`enterprise_agent_landing_v3`](./evals/suites/enterprise_agent_landing_v3.json) | End-to-end enterprise tasks with implicit intent, cross-system evidence, governance, and long-running resume. |
| [`tool_skill_mcp_ablation_v3`](./evals/suites/tool_skill_mcp_ablation_v3.json) | Focused tools vs flat overload vs router layering vs procedural skills. |
| [`tool_return_profiles_v1`](./evals/suites/tool_return_profiles_v1.json) | Short JSON, long noisy returns, conflicting evidence, permission errors, and large logs. |
| [`openclaw_complex_agent_tasks_v1`](./evals/suites/openclaw_complex_agent_tasks_v1.json) | Personal OS, voice-triggered production fixes, async GitHub, multi-agent ops, plugin governance, memory safety. |

## Current Evidence

The first measured public case study is **MiniMax M2.7 High r7 pilot**:

| Scope | Value |
| --- | ---: |
| Suites | `4` |
| Scenarios | `19` |
| Trials | `133` |
| Confidence label | `pilot` |

Public assets:

| Asset | Purpose |
| --- | --- |
| [Integrated report](./report/agent-peak-bench-integrated-report.zh-CN.md) | Full MiniMax case-study interpretation and methodology. |
| [Multi-model dashboard](./docs/multi-model-dashboard.html) | Static dashboard contract with measured/fixture status labels. |
| [Measured sample output](./public/benchmark-samples/minimax-r7-sample-output.json) | Sanitized aggregate benchmark sample. |
| [Dashboard JSON contract](./public/multi-model-dashboard-sample.json) | Example schema for comparing models without mixing fixture and measured rows. |

![Benchmark sample output](docs/assets/benchmark-sample-output.svg)

## How To Interpret Results

| Signal | Deployment meaning |
| --- | --- |
| Low pass@1, higher pass@k | The model may be useful with retry, verifier, or repair loops; not safe for direct autonomy. |
| Tool precision drops with flat tools | Use routers, focused tool surfaces, or role-specific agents. |
| Schema drift under long context | Add context compression, output contracts, or multi-window handoff. |
| Good content but weak evidence | Split content engineer and harness verifier roles. |
| Permission errors mishandled | Add approval gates and completion-honesty checks. |

## Repository Map

```text
evals/business_goals/     # business profiles that generate suite skeletons
evals/suites/             # benchmark suites
evals/campaigns/          # multi-day / multi-week campaign specs
scripts/                  # runner, campaign planner, summarizer, generator
docs/                     # GitHub Pages, dashboard, chart assets
public/                   # sanitized public result samples and dashboard contracts
report/                   # integrated report, methodology, system card, analysis
research/                 # benchmark source notes and GitHub repo review signals
```

## Roadmap

| Phase | Goal |
| --- | --- |
| OSS kit | Profiles, suite generator, CI, Pages, sample outputs. |
| Multi-model evidence | Run multiple providers on the same business goals with r30 calibration. |
| Cookbook engine | Generate deployment topology, harness, memory/RAG/MCP/skills/verifier recommendations. |
| Production-like canaries | Add sanitized live-adapter fixtures and recurring regression campaigns. |

## Security

Do not commit API keys, provider secrets, raw traces, customer data, private tool
outputs, or live system exports. Public releases should contain sanitized
summaries, aggregate metrics, failure taxonomy, and engineering guidance only.

## License

MIT. See [LICENSE](LICENSE).
