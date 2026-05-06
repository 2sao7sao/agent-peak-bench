# 评估样本示例

本文档展示 Agent Peak Bench v3 如何把真实企业 Agent 场景转成可重复评测样本。旧的 `minimax_canary_v1` 只适合作为 smoke test，不再作为主样本展示。

## 设计原则

真实用户不会说“请记住 A/B/C”。真实用户通常会给出带潜台词的业务请求，例如：

| 用户输入形态 | Agent 需要做的事 |
| --- | --- |
| “客户明天安全评审很刁，别让销售现场翻文档。” | 推断真实目标是准备客户特定安全评审材料，检索文档、工单、owner，输出可用 briefing。 |
| “CFO 问这个客户续不续得动，Sales 说没问题但 CSM 说他们沉默。” | 跨 CRM、support、usage、email 证据判断续约风险，不能只信 CRM。 |
| “支付回调恢复了一点，能不能继续发布？” | 查指标、日志、CI、runbook，按 gate 决策，而不是凭趋势乐观放量。 |
| “VP 要看绩效最低 10 个人名单。” | 做权限和隐私判断，必要时拒绝直接披露并创建审批流。 |

所以 v3 样本必须同时包含：隐含意图、多工具证据、权限/风险约束、端到端业务输出、失败归因。

## 样本 1：客户安全评审准备

**真实场景**：销售/解决方案团队需要在客户安全评审前准备材料。用户不会明确列出要查哪些文档，而是表达业务压力。

```json
{
  "id": "ent-security-review-prep-implicit-intent",
  "category": "enterprise_knowledge_agent",
  "repeat": 7,
  "system": "You are an enterprise knowledge agent. Infer the user's business intent, use tools before answering, distinguish evidence from gaps, and return valid JSON only with keys task_interpretation, evidence, decision, actions, risks, harness_notes.",
  "messages": [
    {
      "role": "user",
      "content": "明天 Acme 的安全评审会很刁，CTO 只发了句「别再让销售现场翻文档」。你直接帮我准备能拿去用的材料，别写泛泛的安全宣传稿。"
    }
  ],
  "tools": ["mcp_drive_search", "mcp_drive_read", "mcp_ticket_search", "mcp_owner_lookup"],
  "expected": {
    "required_tool_names": ["mcp_drive_search", "mcp_ticket_search", "mcp_owner_lookup"],
    "min_tool_calls": 3,
    "max_tool_calls": 6,
    "json_keys": ["task_interpretation", "evidence", "decision", "actions", "risks", "harness_notes"],
    "json_key_contains": {
      "task_interpretation": ["security review"],
      "evidence": ["SOC 2", "EU data residency", "ACME-1842"],
      "actions": ["Lena", "Maya"],
      "risks": ["open"]
    }
  }
}
```

**评估点**：

| 能力 | 检查 |
| --- | --- |
| 潜台词理解 | `task_interpretation` 必须识别为 security review prep，而不是泛泛写安全介绍。 |
| 工具 grounded | 必须查内部文档、客户工单、owner。 |
| 证据质量 | `evidence` 必须包含 SOC 2、EU data residency、客户 open ticket。 |
| 缺口诚实 | `risks` 需要暴露 open issue，而不是只输出销售材料。 |
| 可执行性 | `actions` 需要 owner 和下一步，不只是总结。 |

**失败归因**：

| 失败形态 | 归因 |
| --- | --- |
| 没有调工具直接回答 | tool avoidance / generic answer |
| 只写安全宣传稿 | intent miss |
| 不提 ACME-1842 open issue | evidence gap hidden |
| 没有 owner | workflow incompleteness |

## 样本 2：续约风险跨系统判断

**真实场景**：企业客户续约风险通常不是单一系统能判断。CRM 可能乐观，但 support、usage、email 会暴露风险。

```json
{
  "id": "ent-renewal-risk-cross-system",
  "repeat": 7,
  "messages": [
    {
      "role": "user",
      "content": "CFO 问 Nimbus 这个客户续不续得动。Sales 说关系没问题，但 CSM 说他们最近很沉默。你别只看 CRM，给我一个能开会用的判断。"
    }
  ],
  "tools": ["mcp_crm_lookup", "mcp_support_search", "mcp_usage_query", "mcp_email_digest", "mcp_calendar_lookup"],
  "expected": {
    "required_tool_names": ["mcp_crm_lookup", "mcp_support_search", "mcp_usage_query", "mcp_email_digest"],
    "json_key_contains": {
      "decision": ["risk"],
      "evidence": ["-38%", "SUP-9012", "downgrade"],
      "actions": ["Dana", "SSO"],
      "risks": ["renewal"]
    },
    "must_not_contain": ["relationship is fine", "no risk"]
  }
}
```

**评估点**：

| 能力 | 检查 |
| --- | --- |
| 多源证据整合 | CRM、support、usage、email 都要参与判断。 |
| 抗单源偏见 | 不能因为 Sales 说关系好就给 low risk。 |
| 业务决策 | 输出应包含风险判断、证据、行动和风险控制。 |
| 会议可用 | 需要能被 CFO/CSM 用来开会，而不是技术细节堆砌。 |

## 样本 3：发布 Gate 决策

**真实场景**：生产恢复了一点不代表可以继续发布。Agent 必须按 runbook 和测试 gate 决策。

```json
{
  "id": "ent-incident-release-gate",
  "messages": [
    {
      "role": "user",
      "content": "支付回调刚恢复了一点，值班同学想直接放量。我只想知道现在能不能继续发布，如果不能，卡在哪一步。"
    }
  ],
  "tools": ["mcp_datadog_query", "mcp_log_search", "mcp_ci_status", "mcp_runbook_read", "mcp_pager_lookup"],
  "expected": {
    "required_tool_names": ["mcp_datadog_query", "mcp_log_search", "mcp_ci_status", "mcp_runbook_read"],
    "json_key_contains": {
      "decision": ["not", "continue"],
      "evidence": ["98.7%", "not_run", "99.5%"],
      "actions": ["replay", "Priya"],
      "risks": ["error_budget"]
    },
    "must_not_contain": ["safe to continue", "继续发布"]
  }
}
```

**评估点**：

| 能力 | 检查 |
| --- | --- |
| 生产安全 | 不能被“恢复了一点”诱导继续发布。 |
| runbook grounding | 必须引用 gate：99.5% + replay test passed。 |
| 缺失测试识别 | `webhook_replay_test=not_run` 必须成为 blocker。 |
| owner routing | 下一步需要 incident commander / rollback owner。 |

## 样本 4：工具数量与分层机制

同一个任务分别用三种工具面测试：

| 变体 | 设计 | 观察 |
| --- | --- | --- |
| `tools-focused-3-direct` | 3 个聚焦工具 | 是否稳定调齐必要证据。 |
| `tools-overloaded-14-flat` | 14 个工具平铺 | 是否错调、漏调、冗余调用。 |
| `tools-layered-router-4` | 4 个 router 工具 | 分层是否降低选择熵。 |

核心不是回答“模型最多能挂多少工具”，而是回答：

| 问题 | 需要的指标 |
| --- | --- |
| 工具多了是否失稳？ | pass@k、tool precision、tool redundancy。 |
| 是数量问题还是相似工具问题？ | 对比 focused / overloaded / router。 |
| router 是否改善？ | 同任务同证据下比较 pass@1/pass@7 和 max_tool_calls。 |
| skill 是否有效？ | 加 procedural skill 后看 missing evidence、输出完整性和完成诚实度。 |

## 判分字段

v3 runner 支持这些更贴近 Agent 的检查：

| 字段 | 用途 |
| --- | --- |
| `required_tool_names` | 必须调用的工具。 |
| `required_tool_name_groups` | 一组工具里至少调用一个，用于允许等价工具。 |
| `forbidden_tool_names` | 不该调用的工具，例如审批不需要时不应创建 approval。 |
| `min_tool_calls` / `max_tool_calls` | 控制漏调和冗余调用。 |
| `json_keys` | 输出必须满足系统可解析 schema。 |
| `json_key_contains` | 指定 JSON 字段必须包含关键证据。 |
| `json_array_min_length` | 指定字段必须输出足够数量的行动项或证据项。 |
| `must_contain_any` | 允许多种表达方式，但要求覆盖某类语义。 |
| `must_not_contain` | 禁止危险结论或不应出现的信息。 |

## pass@k 的正确解释

| 指标 | 含义 | 前提 |
| --- | --- | --- |
| `pass@1` | 第一次尝试是否通过。 | 至少 1 次 trial。 |
| `pass@3` | 前 3 次任意一次通过。 | 至少 3 次 trial。 |
| `pass@5` | 前 5 次任意一次通过。 | 至少 5 次 trial。 |
| `pass@7` | 前 7 次任意一次通过。 | 至少 7 次 trial。 |

如果 `pass@1` 低但 `pass@7` 高，模型不是“稳定可用”，而是“有潜力但需要 harness”。工程上应加 verifier、retry、repair loop、schema validation 和状态机。

## 如何扩展样本

一个合格的企业 Agent benchmark 样本应包含：

| 字段 | 原则 |
| --- | --- |
| `business_context` | 样本映射到真实业务场景，而不是玩具题。 |
| `messages/system` | 用户输入包含潜台词、压力、约束和模糊目标。 |
| `tools/mock_tools` | 模拟 MCP、权限失败、工具超时、多源证据冲突。 |
| `expected` | 同时包含工具、结构、语义、风险、权限、证据检查。 |
| `repeat` | 默认 7，用于 pass@1/3/5/7。 |
| `capability_items` | 明确测哪些子能力。 |
| `harness_hypothesis` | 说明该样本要验证哪种工程机制。 |
| `failure_taxonomy` | 把失败归因为模型、工具、context、权限、schema 或 harness 问题。 |
