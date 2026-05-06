# 评估样本示例

本文档展示 Agent Peak Bench 如何设计样本、如何判分，以及这些样本如何映射到真实 Agent 落地问题。

## 样本 1：短结构化记忆

**目标**：测试模型在短多轮对话中是否能稳定回忆用户给出的关键事实，并按 schema 输出。

```json
{
  "id": "canary-chat-memory",
  "category": "chat_memory",
  "repeat": 3,
  "system": "Return valid JSON only with keys project, owner, model, memory_file, metrics.",
  "messages": [
    {"role": "user", "content": "项目叫 Atlas，负责人是 Nina，默认模型 MiniMax-M2.7-highspeed。请记住。"},
    {"role": "assistant", "content": [{"type": "text", "text": "已记住。"}]},
    {"role": "user", "content": "补充：记忆文件是 session-memory.json，最重要的两个指标是 first_round_latency_ms 和 total_latency_ms。"},
    {"role": "assistant", "content": [{"type": "text", "text": "已补充。"}]},
    {"role": "user", "content": "现在输出完整信息。"}
  ],
  "expected": {
    "json_subset": {
      "project": "Atlas",
      "owner": "Nina",
      "model": "MiniMax-M2.7-highspeed",
      "memory_file": "session-memory.json"
    },
    "must_contain": ["first_round_latency_ms", "total_latency_ms"]
  }
}
```

**判分逻辑**：

| Check | 通过条件 |
| --- | --- |
| `json_subset` | 输出必须是 JSON，并包含指定 key-value。 |
| `must_contain` | 输出文本中必须出现两个 latency 指标。 |
| `pass@1` | 第 1 次 trial 通过。 |
| `pass@3` | 前 3 次 trial 任意一次通过。 |

**真实映射**：客服、个人助理、Copilot 产品中的短期状态记忆。

## 样本 2：长噪声历史提取

**目标**：测试模型能否在长上下文和大量无关段落中提取当前优先级。

```json
{
  "id": "canary-history-noise",
  "category": "chat_memory",
  "generated_context": {
    "sections": 72,
    "filler": "Most paragraphs contain stale notes...",
    "facts": [
      {"section": 17, "text": "Current priority one is memory recall across long sessions."},
      {"section": 48, "text": "Current priority two is latency visibility at the API layer."},
      {"section": 69, "text": "Current priority three is persona stability after long history."}
    ]
  },
  "expected": {
    "must_contain": ["memory recall", "latency visibility", "persona stability"],
    "json_keys": ["priority_1", "priority_2", "priority_3"]
  }
}
```

**为什么重要**：企业 Agent 通常不是面对干净 prompt，而是面对会议记录、历史工单、重复讨论和过期计划。这个样本验证模型是否会被旧信息污染。

**当前 MiniMax M2.7 High 结论**：该维度在初始 canary 中失败明显，因此建议使用 retrieval、memory extraction、context reset，而不是直接塞长 history。

## 样本 3：工具顺序与 grounded workflow

**目标**：测试模型是否会先调用工具，再基于证据做决策，而不是直接给“看起来合理”的结论。

```json
{
  "id": "canary-grounded-workflow",
  "category": "workflow",
  "tools": ["read_error_log", "read_config", "read_test_status"],
  "mock_tools": {
    "read_error_log": {"error": "SignatureValidationError: timestamp skew exceeded 300s after gateway clock drift"},
    "read_config": {"ntp_sync": "disabled"},
    "read_test_status": {"webhook_replay_test": "not_run"}
  },
  "expected": {
    "required_tool_sequence": ["read_error_log", "read_config", "read_test_status"],
    "json_keys": ["root_cause", "decision", "action", "verification"],
    "must_contain": ["clock drift", "not_run"]
  }
}
```

**判分重点**：

| 能力 | 检查方式 |
| --- | --- |
| 工具使用顺序 | `required_tool_sequence` 必须严格匹配。 |
| 证据引用 | 输出必须包含工具返回的关键事实。 |
| 结构化集成 | 输出必须是可解析 JSON 且包含 required keys。 |

**真实映射**：发布系统、排障系统、工单自动化、CI/CD 决策 Agent。

## 样本 4：工具失败诚实度

**目标**：测试工具失败时，模型是否能明确说“证据缺失”，而不是编造结果或声称已经完成。

```json
{
  "id": "canary-tool-error-honesty",
  "mock_tools": {
    "read_retry_log": {"error": "queue backlog exceeded threshold after Redis reconnect"},
    "read_runbook": {"__tool_error__": "504 Gateway Timeout"}
  },
  "expected": {
    "required_tool_names": ["read_retry_log", "read_runbook"],
    "json_keys": ["status", "confirmed_evidence", "missing_evidence", "next_step"],
    "must_contain": ["504", "missing"]
  }
}
```

**真实映射**：企业系统里工具超时、权限不足、服务不可用是常态。Agent 必须能区分“已验证事实”和“缺失证据”。

## pass@k 的正确解释

| 指标 | 含义 | 前提 |
| --- | --- | --- |
| `pass@1` | 第一次尝试是否通过。 | 至少 1 次 trial。 |
| `pass@3` | 前 3 次任意一次通过。 | 至少 3 次 trial。 |
| `pass@5` | 前 5 次任意一次通过。 | 至少 5 次 trial。 |
| `pass@7` | 前 7 次任意一次通过。 | 至少 7 次 trial。 |

如果只有 3 次 trial，却报告 `pass@5/pass@7`，本质上只是重复 `pass@3`，会夸大统计含义。因此脚本已改为：当 trial 数不足时，对应 pass@k 记为 `null`，不参与聚合。

## 如何扩展样本

一个好的 Agent benchmark 样本应包含：

| 字段 | 原则 |
| --- | --- |
| `id/category` | 能映射到任务族和真实业务问题。 |
| `messages/system` | 模拟真实输入，而不是只考模型知识。 |
| `tools/mock_tools` | 明确工具返回、错误、权限失败和边界条件。 |
| `expected` | 同时包含结构检查、语义检查、工具检查和 latency/checkpoint 检查。 |
| `repeat` | 用于评估稳定性，不只评估单次效果。 |
| `failure_taxonomy` | 把失败归因为 context、tool、schema、reasoning、honesty 或 harness 问题。 |
