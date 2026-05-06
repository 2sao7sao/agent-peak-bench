# 企业级 Agent Benchmark 方法论 v3

这份方法论回应一个核心问题：Agent 评测不能停留在“模型答题得分”，而必须形成一条闭环：

`真实任务设计 -> 子能力观测 -> 端到端完成率 -> 失败归因 -> harness 设计 -> 模型使用指南`

## 1. 为什么原 canary 不够

`minimax_canary_v1` 的价值只在 smoke test：验证 API、工具调用、JSON 解析、pass@k 聚合是否能跑通。它不能代表真实企业 Agent 能力，原因是：

| 问题 | 后果 |
| --- | --- |
| 任务过于显式 | 用户真实需求通常有潜台词、上下文缺失、业务目标和隐含约束。 |
| 工具过少且路径直接 | 真实 Agent 会面对多个 MCP、重复工具、权限失败、工具超时和不完整证据。 |
| 评估只看局部输出 | 真实落地要看是否能推进业务流程，而不是只回答一个字段。 |
| 缺少归因链路 | 失败后不知道是模型能力问题、工具设计问题、context 问题，还是 harness 问题。 |
| 缺少工程建议 | benchmark 必须反推架构：工具如何分层、skills 如何写、什么时候要 verifier。 |

因此，canary 在本项目中只作为 `L0 smoke`，不能作为主 benchmark。

## 2. v3 的评估对象

企业级 Agent 不是单次聊天，而是一个系统。v3 评估对象包括：

| 层级 | 评估问题 | 例子 |
| --- | --- | --- |
| 子能力 | 模型是否能完成某个关键动作？ | 推断潜台词、选择工具、识别权限边界、引用证据。 |
| 场景任务 | 模型是否能完成一个业务片段？ | 安全评审准备、续约风险判断、发布 gate 决策。 |
| 端到端链路 | 模型是否能在多工具、多约束下推进目标？ | 从用户模糊请求到证据、判断、行动、风险控制。 |
| 工程机制 | 哪种 harness 让模型更稳定？ | 3 工具直连、14 工具平铺、router 分层、skill contract。 |
| 使用指南 | 模型适合怎么用，不适合怎么用？ | 什么时候直接挂工具，什么时候必须分层、验证、审批。 |

## 3. 新增主评测集

### `enterprise_agent_landing_v3.json`

主评测集，面向真实企业 Agent 落地。每个场景默认 `repeat=7`，用于有效计算 `pass@1/pass@3/pass@5/pass@7`。

| 场景 | 测试能力 | 真实映射 |
| --- | --- | --- |
| `ent-security-review-prep-implicit-intent` | 潜台词理解、企业知识检索、证据合成、owner routing | 客户安全评审准备 |
| `ent-renewal-risk-cross-system` | CRM/support/usage/email 跨系统综合判断 | 续约风险诊断 |
| `ent-incident-release-gate` | 发布 gate、runbook grounding、生产安全 | Incident 发布决策 |
| `ent-policy-access-governance` | 权限、隐私、审批流、安全替代方案 | HR 敏感数据请求 |
| `ent-analytics-root-cause` | 模糊高管问题、数据查询、假设与事实分离 | 业务分析 Agent |
| `ent-product-requirement-decomposition` | 复杂需求拆解、架构设计、工具分层、成本控制 | 企业知识 Agent 方案设计 |
| `ent-multi-agent-content-harness-handoff` | Content Engineer + Harness Engineer 角色拆分 | Demo 与评测一体化设计 |
| `ent-long-running-project-resume` | 上下文 reset 后恢复项目状态 | 长任务 Agent resume |

### `tool_skill_mcp_ablation_v3.json`

工程机制评测集，核心问题不是“模型答对没”，而是“什么工具/skill/MCP 设计让模型更稳定”。

| 变体 | 设计 | 要观察的问题 |
| --- | --- | --- |
| `tools-focused-3-direct` | 3 个聚焦工具直连 | 模型是否能稳定调齐必要工具。 |
| `tools-overloaded-14-flat` | 14 个工具平铺 | 是否出现错调、冗余调用、偏离主线。 |
| `tools-layered-router-4` | 4 个 router 工具分层 | 分层是否降低选择熵、保持证据质量。 |
| `skills-contract-with-tools` | procedural skill + 聚焦工具 | skill 是否提升完整性、诚实度和输出契约。 |

## 4. 子能力与端到端能力

v3 不再只看一个总分，而是拆成能力项：

| 能力项 | 观测信号 | 失败归因 |
| --- | --- | --- |
| `implicit_intent_inference` | 能否从潜台词识别真实任务 | 把模糊请求当普通问答 |
| `tool_selection` | 是否调用必要工具、避免无关工具 | 工具描述差、工具面过载、模型路由弱 |
| `evidence_synthesis` | 是否把多工具证据合成判断 | 单源偏见、证据冲突处理弱 |
| `gap_honesty` | 是否说明缺失证据和不确定性 | completion dishonesty |
| `permission_awareness` | 是否遵守权限和隐私边界 | governance failure |
| `workflow_gatekeeping` | 是否按 runbook / policy 阻断危险动作 | premature action |
| `handoff_quality` | 是否输出可交接 artifact | multi-agent role blur |
| `state_reconstruction` | reset 后是否能从 memory/artifact 恢复 | starts-over failure |

## 5. pass@k 的使用方式

v3 默认建议 `repeat=7`：

| 指标 | 解释 | 落地含义 |
| --- | --- | --- |
| `pass@1` | 第一次就完成 | 适合实时交互和低风险流程 |
| `pass@3` | 三次内可恢复 | 适合 retry + verifier 的 workflow |
| `pass@5` | 五次内可恢复 | 说明模型有能力但稳定性不足，成本需评估 |
| `pass@7` | 七次内可恢复 | 主要用于诊断潜力，不代表可直接上线 |

如果 `pass@1` 低、`pass@7` 高，结论不是“模型很好”，而是“模型需要强 harness 才能发挥”。这类场景应该使用自动重试、错误修复、verifier、状态机，而不是直接开放 autonomous execution。

## 6. 工具数量不是唯一变量

“最多可以挂多少工具”不能只按数量回答。稳定性取决于：

| 因素 | 影响 |
| --- | --- |
| 工具数量 | 数量越多，选择熵越高。 |
| 工具相似度 | 相似工具越多，错调概率越高。 |
| 命名清晰度 | `mcp_ticket_search` 比 `search` 更稳定。 |
| 输入 schema | schema 越明确，越容易形成正确调用。 |
| 错误反馈 | 工具错误如果不可解释，模型容易过度自信。 |
| 工具分层 | router 可以降低选择面，代价是多一层系统设计。 |
| verifier | 能把“看似完成”变成“可验证完成”。 |

初步工程假设：

| 工具设计 | 建议 |
| --- | --- |
| 1-3 个聚焦工具 | 可以直接暴露给模型。 |
| 4-8 个同域工具 | 需要 tool selection policy 和 schema validation。 |
| 9-15 个混合工具 | 建议用 router / ToolSearch / task-phase gating。 |
| 15+ 个工具 | 不建议平铺；按任务阶段、权限和领域分层。 |

这个假设需要用 `tool_skill_mcp_ablation_v3.json` 通过 pass@k、tool precision、redundancy 和 failure taxonomy 验证。

## 7. 评估结果如何转化为工程设计

| 评估发现 | 工程动作 |
| --- | --- |
| 工具漏调 | 缩小工具面，增强 tool description，增加 required evidence contract。 |
| 冗余调用 | 引入 router、tool budget、max_tool_calls。 |
| JSON 不稳定 | schema validator + repair loop，不把自由文本直接接入业务系统。 |
| 权限误用 | permission gate 前置，敏感工具需要 approval mode。 |
| 长上下文失效 | retrieval + memory extraction + context reset，不直接塞完整 history。 |
| pass@1 低但 pass@k 高 | 使用 verifier/retry，不做实时无监督执行。 |
| role blur | multi-agent 必须有 handoff artifact 和 integration owner。 |
| 过度自信 | 强制 missing_evidence 字段，完成前必须有 verification evidence。 |

## 8. 推荐运行方式

主评测：

```bash
python3 scripts/run_minimax_evals.py \
  --suite evals/suites/enterprise_agent_landing_v3.json \
  --pass-k 1,3,5,7 \
  --out results/minimax-enterprise-agent-v3.json
```

工具/skill/MCP 归因评测：

```bash
python3 scripts/run_minimax_evals.py \
  --suite evals/suites/tool_skill_mcp_ablation_v3.json \
  --pass-k 1,3,5,7 \
  --out results/minimax-tool-skill-mcp-ablation-v3.json
```

如果只想复测某个 suite 的重复次数，可以使用：

```bash
python3 scripts/run_minimax_evals.py \
  --suite evals/suites/enterprise_agent_landing_v3.json \
  --force-repeat 7 \
  --pass-k 1,3,5,7
```

## 9. 最终产出应是什么

一次完整模型评估不应该只输出分数，而应该输出：

| 产出 | 说明 |
| --- | --- |
| 模型能力卡 | 哪些子能力强，哪些弱。 |
| 场景适配矩阵 | 哪些企业场景适合，哪些不适合。 |
| 工具设计建议 | 直接工具、router、MCP、ToolSearch 的使用边界。 |
| Skill 写法规范 | 哪些 skill 有效，哪些只是 prompt 装饰。 |
| Context 策略 | 多大窗口、何时 reset、何时 retrieval。 |
| Failure taxonomy | 失败到底来自模型、工具、上下文还是 harness。 |
| Engineering playbook | 如何把模型放进真实生产系统。 |

这才是 Agent Peak Bench 的目标：不是排行榜，而是模型落地说明书。
