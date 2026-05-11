# Contributing to Agent Peak Bench

Agent Peak Bench is a harness-first benchmark system for turning business goals
into model capability tests, failure attribution, and agent deployment cookbooks.

## Development Setup

```bash
python -m pip install pyyaml
python scripts/check_benchmark_distribution.py
python scripts/generate_business_goal_suite.py \
  evals/business_goals/security_review_acceleration.yaml \
  --out /tmp/business-goal-suite.json
```

## Good Contributions

| Area | Examples |
| --- | --- |
| Business profiles | Realistic B2B objectives, stakeholder maps, KPI mappings, approval points. |
| Suites | End-to-end tasks with mock tools, expected contracts, and failure taxonomy. |
| Scoring | Better pass@k, CI95, tool precision, evidence quality, and readiness metrics. |
| Harness design | Router, skills, memory, RAG, verifier, approval, and multi-agent ablations. |
| Reports | Clearer charts, model cards, business cookbooks, and vendor feedback packs. |

## Quality Bar

- Keep benchmark tasks model-agnostic.
- Do not publish API keys, raw private traces, or customer data.
- Mark pilot results as pilot; do not overclaim from small `r7` runs.
- Prefer reproducible mock fixtures before adding live tools.
- Every new suite should explain which business decision it informs.

## Pull Request Checklist

- `python scripts/check_benchmark_distribution.py` passes.
- New business profiles can generate a suite skeleton.
- README or eval docs are updated if the user workflow changes.
- Failure taxonomy distinguishes model, tool, context, and harness issues.
