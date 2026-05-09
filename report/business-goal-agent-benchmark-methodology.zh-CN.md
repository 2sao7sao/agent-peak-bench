# 商业目标驱动的 Agent Benchmark 方法论

版本：`2026-05-09`

定位：把“模型能力评测”升级为“商业目标 -> 能力拆解 -> benchmark -> 失败归因 -> agent 搭建 cookbook -> 模型厂商反馈”的闭环。

## 1. 为什么需要业务目标层

单纯测试模型能力，通常只能回答“模型是否会调用工具、是否能输出 JSON、是否能完成某类标准任务”。但 toB 落地更关心：

| 商业问题 | Benchmark 必须补上的问题 |
| --- | --- |
| 这个 Agent 能不能缩短安全评审、续约判断、合同红线、财务关账等具体流程？ | 需要从业务目标反推能力项，而不是从模型能力正向造题。 |
| 模型失败后，到底是模型问题、harness 问题、工具问题，还是业务流程没有设计好？ | 需要把 failure taxonomy 和业务影响绑定。 |
| 模型 A 应该怎么在这个业务里部署？ | 需要输出 agent cookbook：single/multi agent、memory、RAG、MCP、skills、verifier、审批。 |
| 如何反馈给模型厂商优化？ | 需要可复现失败簇、最小复现 trace、置信度标签和回归 suite。 |

因此，Agent Peak Bench 新增 [`business_goal_agent_synthesis_v1.json`](../evals/suites/business_goal_agent_synthesis_v1.json)。它不是替代原有 benchmark，而是在原有 agent/harness 评测上方增加商业目标映射层。

## 2. 外部 Benchmark 借鉴

本轮通过浏览器和联网下载了公开 benchmark 的轻量资料，下载索引见 [`research/benchmark_sources/source_index.json`](../research/benchmark_sources/source_index.json)，原始 README/评估说明见 [`research/benchmark_sources/raw/`](../research/benchmark_sources/raw/)。

| Benchmark | 可借鉴点 | 对 Agent Peak Bench 的使用方式 |
| --- | --- | --- |
| AgentBench | 多环境、交互式 agent 评测，强调长期推理、决策和 instruction following 失败。 | 用于构建跨环境能力 taxonomy，但不满足业务 cookbook 输出。 |
| WebArena | 真实网站环境、长任务、功能正确性评价。 | 用于端到端 task success 和真实 web workflow 设计。 |
| SWE-bench | 真实 GitHub issue、test patch、可执行验证。 | 用于 coding/harness 任务的“不是看答案，而是跑测试”。 |
| tau-bench | tool-agent-user、多轮对话、领域 policy、数据库 end-state、pass^k。 | 直接影响 pass@k、重复一致性、政策约束工具使用。 |
| OSWorld | 真实桌面环境、执行后状态验证、GUI grounding。 | 用于 computer-use / MCP side-effect 任务，不把 browser-only 当成全部 agent 能力。 |
| WorkArena | ServiceNow 企业工作流、知识工作者任务。 | 用于企业业务流程真实性。 |
| TheAgentCompany | 模拟软件公司、多应用、多角色、result + subcheckpoint scoring。 | 最接近 toB 数字员工评测；本仓库在此基础上增加商业目标拆解和 cookbook。 |
| Terminal-Bench | sandbox、任务目录、验证脚本、oracle solution。 | 用于 CLI/DevOps/data 任务的可执行验证。 |
| PaperBench | 层级 rubric、长周期研究复制、judge calibration。 | 用于把商业目标拆成可评分子要求。 |
| BrowseComp | 难检索事实、搜索毅力、短答案验证、反泄漏要求。 | 用于资料查询能力；遵守其不要公开数据样例的要求。 |
| BFCL | function calling、多工具、AST/API-style validation。 | 用于工具调用底层质量指标。 |

关键判断：这些 benchmark 都有价值，但没有一个直接回答“某个模型针对某个商业目标应该如何搭 agent”。Agent Peak Bench 的差异点就是把 benchmark 结果转成 deployment cookbook 和 vendor feedback。

## 3. 业务目标到评测集的转换协议

每个商业目标都应按以下协议拆解：

| 层级 | 输出 |
| --- | --- |
| `Business Objective` | 要优化的业务指标，例如安全评审耗时、续约风险准确率、关账异常定位时间。 |
| `Stakeholders` | 业务 owner、审批人、风险承接人，例如 sales、legal、finance、SRE。 |
| `Capability Map` | 模型/agent 必须具备的能力：潜台词理解、证据检索、工具选择、政策遵守、可执行验证。 |
| `Benchmark Mapping` | 该能力对应哪些 benchmark 思路：tau-bench、SWE-bench、PaperBench 等。 |
| `Eval Scenario` | 用 mock MCP / fixture / sandbox 构造可重复任务。 |
| `Metrics` | pass@k、CI95、tool precision、required-tool coverage、schema pass、latency、failure taxonomy。 |
| `Diagnosis` | 失败归因到模型能力、harness、工具、上下文、权限、业务流程。 |
| `Cookbook` | 给业务落地的 agent 搭建方案。 |
| `Vendor Feedback` | 给模型厂商的可复现失败簇和优化建议。 |

## 4. 最终报告合同

针对任意模型 A，业务目标驱动报告必须至少包含四块。

### 4.1 模型 A 的综合能力评估

| 必填项 | 说明 |
| --- | --- |
| 综合分布 | 各 suite、各 family、各 business goal 的通过率和样本量。 |
| 稳定性 | pass@1、pass@3、pass@5、pass@7、pass@10 与 CI95。 |
| 工具能力 | required-tool coverage、tool precision、forbidden tool calls、重复调用。 |
| 输出可靠性 | JSON/schema pass、缺口诚实、引用/证据覆盖、输出一致性。 |
| 成本与体验 | p50/p95 latency、token cost、tool rounds。 |
| 失败归因 | top failure clusters 和代表性脱敏 trace。 |

### 4.2 模型 A 的定向业务表现

| 必填项 | 说明 |
| --- | --- |
| 商业目标 | 例如安全评审、续约风险、退款自动化、关账异常、合同红线。 |
| 业务指标映射 | 评测指标如何对应业务 KPI。 |
| 任务拆解 | 子能力和端到端任务列表。 |
| 业务可用等级 | `not_ready`、`assistant_only`、`human_in_loop`、`guarded_autonomy`、`autonomous_low_risk`。 |
| 业务风险 | 哪些失败会导致客户误导、合规风险、生产事故或财务损失。 |

### 4.3 模型 A 针对商业目标的最佳 Agent 搭建方案

| 决策 | 报告必须给出 |
| --- | --- |
| single vs multi-agent | 什么时候单 agent 足够，什么时候需要 planner / executor / verifier / domain specialist。 |
| memory | 是否需要 session memory、long-term memory、profile memory；哪些记忆必须审批。 |
| RAG | 哪些事实必须检索，引用字段如何设计，缺失证据如何处理。 |
| MCP / tools | 直接暴露几个工具，何时使用 router，哪些工具必须审批或隔离。 |
| skills | 需要哪些 procedural skills，输出 contract 如何写。 |
| harness | 是否需要 sprint contract、verifier、repair loop、trace export、CI gate。 |

### 4.4 给模型厂商的优化反馈

| 反馈类型 | 示例 |
| --- | --- |
| 能力缺口 | 单源偏见、长上下文 schema drift、工具选择混乱、权限错误后过度声称完成。 |
| 最小复现 | 脱敏 prompt、tool schema、tool result、期望输出、失败输出。 |
| 频率和置信度 | failure cluster 出现次数、样本量、CI95、是否跨 business goal 复现。 |
| 优化方向 | tool-use training、policy following、long-context contract retention、evidence conflict handling。 |
| 回归 suite | 修复后必须重跑的 suite 和 passing threshold。 |

## 5. Business Goal Suite 设计

[`business_goal_agent_synthesis_v1.json`](../evals/suites/business_goal_agent_synthesis_v1.json) 当前包含 8 个商业目标：

| 场景 | 商业目标 | 主要能力 |
| --- | --- | --- |
| `biz-security-review-to-agent-cookbook` | 缩短安全评审材料准备时间。 | 业务目标拆解、证据检索、owner routing、RAG/MCP cookbook。 |
| `biz-renewal-risk-to-model-diagnosis` | 提升续约风险判断。 | CRM/support/usage/email 跨源冲突处理。 |
| `biz-support-refund-policy-agent` | 缩短客服退款处理，同时避免违规退款。 | policy following、approval gate、forbidden tool avoidance。 |
| `biz-finance-close-anomaly-agent` | 缩短财务关账异常定位。 | SQL/ERP/表格证据、计算严谨性、auditability。 |
| `biz-codebase-migration-agent-topology` | 降低内部工程迁移成本。 | repo navigation、测试选择、single vs multi-agent 边界。 |
| `biz-compliance-contract-redline-agent` | 提升合同红线处理效率。 | clause extraction、政策证据、human approval。 |
| `biz-launch-content-harness-split` | 提升发布内容生产效率。 | content engineer + harness engineer 分工、claim grounding。 |
| `biz-model-vendor-feedback-pack` | 把评测失败转成模型厂商优化反馈。 | failure clustering、vendor feedback、回归设计。 |

这些场景的输出不是普通答案，而是统一 JSON：

```json
{
  "business_goal": "...",
  "capability_map": "...",
  "benchmark_plan": "...",
  "model_risk_diagnosis": "...",
  "agent_architecture": "...",
  "cookbook": "...",
  "vendor_feedback": "..."
}
```

这样同一次测试既能判断模型是否理解业务目标，也能评估它是否能产生可落地的 agent 方案和可复现模型反馈。

## 6. 置信度与运行策略

业务目标 suite 不应该只跑一次。

| 阶段 | repeat | 用途 |
| --- | ---: | --- |
| pilot | 7 | 验证任务是否合理、评分是否能区分模型行为。 |
| calibration | 30 | 形成方向性商业部署建议。 |
| confirmatory | 100 | 支撑强边界结论和模型厂商反馈。 |

报告时必须区分：

| 标签 | 条件 |
| --- | --- |
| `pilot` | `n < 30` 或 CI95 太宽。 |
| `directional` | `n >= 30`，failure cluster 已稳定。 |
| `actionable` | `n >= 30` 且 CI95 宽度足够小，可影响 agent 设计。 |
| `confirmed` | `n >= 100`，并在 confirmatory batch 复现。 |

## 7. 与 Harness 工程的关系

业务目标层不是弱化 harness，而是让 harness 决策更有商业指向。

| Harness 设计 | 由什么评测决定 |
| --- | --- |
| 是否使用 multi-agent | 看单 agent 在业务目标中的 role blur、handoff missing、verification miss 是否高。 |
| 是否使用 memory | 看业务是否跨 session、是否需要客户/项目状态；同时测 memory 泄漏与过期风险。 |
| 是否使用 RAG | 看事实密度、证据要求、上下文窗口压力和缺失证据失败率。 |
| 是否使用 MCP router | 看工具数量、工具相似度、tool precision 和 forbidden tool calls。 |
| 是否使用 skills | 看 procedural skill 是否提升 pass@1、schema pass、missing evidence honesty。 |
| 是否需要 verifier | 看 pass@1 与 pass@k 差距，以及 completion dishonesty。 |

最终 cookbook 不应是泛泛建议，而应写成业务部署决策：

> 对安全评审 Agent，模型 A 在直接暴露 12 个 MCP 工具时 tool precision 下降；建议使用 security-doc router、ticket router、owner lookup 三层工具面，外加 evidence verifier。不要开放自动发送客户邮件。

## 8. 后续扩展

1. 为每个真实客户业务目标生成一份 `business_goal_profile`。
2. 从 profile 自动派生 suite skeleton、mock tools、评分 contract 和 confidence policy。
3. 用模型 A/B/C 跑同一 business suite。
4. 输出三类 artifact：综合能力报告、业务目标报告、模型厂商反馈包。
5. 把修复后的模型版本或 harness 版本纳入回归 campaign。
