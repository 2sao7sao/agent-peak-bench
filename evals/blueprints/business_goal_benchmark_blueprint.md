# Business Goal Benchmark Blueprint

This blueprint defines how to turn a commercial objective into an Agent Peak Bench suite.

For product-facing inputs, start with a YAML profile in
[`evals/business_goals/`](../business_goals/) and generate a reviewable suite
skeleton with:

```bash
python3 scripts/generate_business_goal_suite.py \
  evals/business_goals/security_review_acceleration.yaml \
  --out /tmp/business-goal-suite.json
```

## Input

```json
{
  "business_goal_id": "renewal-risk-agent",
  "commercial_objective": "Improve renewal risk diagnosis before executive review.",
  "stakeholders": ["CFO", "sales", "CSM", "support", "product"],
  "business_metrics": ["renewal_risk_precision", "time_to_account_brief"],
  "risk_tolerance": "high",
  "systems": ["CRM", "support", "usage telemetry", "email"],
  "side_effects": ["send_customer_email", "update_forecast"],
  "human_approval_points": ["forecast update", "customer-facing commitment"]
}
```

## Transformation

1. Convert the commercial objective into 3-7 capability items.
2. Map each capability to benchmark patterns:
   - `tau-bench` for policy, tool-agent-user interaction, and pass^k consistency.
   - `TheAgentCompany` / `WorkArena` for business workflow realism.
   - `SWE-bench` / `Terminal-Bench` for executable verification.
   - `PaperBench` for hierarchical rubric decomposition.
   - `BFCL` for function/tool-call quality.
   - `BrowseComp` for hard evidence search, without publishing hidden examples.
3. Define mock tools or live adapters for each business system.
4. Define expected output contract:
   - `business_goal`
   - `capability_map`
   - `benchmark_plan`
   - `model_risk_diagnosis`
   - `agent_architecture`
   - `cookbook`
   - `vendor_feedback`
5. Add failure taxonomy and harness hypothesis.
6. Run pilot `r7`, calibration `r30`, and confirmatory `r100` when the business decision depends on the result.

## Output Requirements

Each scenario must answer four deployment questions:

| Question | Required output |
| --- | --- |
| What can the model do overall? | Capability score, pass@k, tool metrics, schema adherence, latency, failure clusters. |
| How does it perform for this business goal? | Business-level readiness and risk assessment. |
| How should the agent be built? | Single/multi-agent topology, memory, RAG, MCP, skills, harness, verifier, approval gates. |
| What should the model vendor fix? | Reproducible failure clusters, sanitized traces, optimization targets, regression suite. |

## Acceptance Criteria

- Scenario contains implicit business language, not only explicit tool instructions.
- Required tools cover at least two systems when the business task is cross-functional.
- Dangerous side-effect tools are either forbidden or approval-gated.
- Expected output includes both cookbook and vendor feedback.
- Failure taxonomy distinguishes model issues from harness and tool-design issues.
