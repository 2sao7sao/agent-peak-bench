# Business Goal Profiles

Business goal profiles are the product-facing entrypoint for Agent Peak Bench.
They describe a real commercial objective before it becomes a benchmark suite.

The intended workflow is:

```text
Business goal profile -> capability map -> generated suite skeleton -> repeated eval -> cookbook
```

## Generate a Suite Skeleton

```bash
python3 scripts/generate_business_goal_suite.py \
  evals/business_goals/security_review_acceleration.yaml \
  evals/business_goals/support_refund_automation.yaml \
  --out /tmp/business_goal_suite.json
```

The generated suite is a starting point. A serious benchmark still needs
reviewed mock tools, scoring rubrics, end-state checks, and repeated trials.

## Required Fields

| Field | Meaning |
| --- | --- |
| `business_goal_id` | Stable id used in generated scenario names. |
| `commercial_objective` | Business outcome, not an AI feature request. |
| `stakeholders` | People or teams affected by the agent. |
| `business_metrics` | Metrics that connect eval results to business value. |
| `risk_tolerance` | What kind of errors are acceptable or unacceptable. |
| `systems` | Enterprise systems or data sources involved. |
| `side_effects` | Actions that may change customer, finance, legal, production, or user state. |
| `human_approval_points` | Actions that require human approval before execution. |
| `capability_items` | Model and harness capabilities that must be tested. |
| `sample_user_request` | Realistic user phrasing with implicit intent. |

## Product Principle

Agent Peak Bench should not start from "can the model call tools?" It should
start from "does this business process deserve an agent, and what must be true
before the agent can safely move it forward?"
