# MiniMax Harness 实践评估方案

版本：`2026-05-06`

这份文档把通用模型评测，收紧成 `harness 工程实践` 视角。目标不是只回答“模型强不强”，而是回答四个工程问题：

1. 这个模型在不同运行模式下是否稳定
2. 它的性格和行为模式是否可预测
3. 它是否适合落在可观测、可回归、可迭代的 harness 中
4. 在 `chatbot / simple agent / multi-agent` 三个层级上，MiniMax 最佳使用姿势分别是什么

## 1. 评估总框架

建议把评估分成三层：

### 1.1 模型层

看模型本体的能力与行为：

- 记忆稳定性
- 指令遵循
- 上下文抗干扰能力
- 性格稳定性
- “懒惰”或过早收尾倾向

### 1.2 Harness 层

看模型进入工程系统后的执行效果：

- history 持久化是否正确
- memory 模块是否能提炼长期状态
- tool loop 是否可追踪
- prompt caching 是否有效
- API latency / token usage 是否可观测

### 1.3 场景层

看不同应用模式的综合表现：

- 纯 chatbot
- simple agent / workflow
- multi-agent

## 2. 三类实践测试怎么设计

### 2.1 纯 Chatbot

目标：验证 MiniMax 在没有复杂工具链时，是否能作为一个稳定、有记忆、有风格一致性的长对话模型。

重点测：

- `history recall`
是否能从 5 到 20 轮前的对话中正确找回事实。

- `memory module quality`
是否能把对话压缩成长期状态，而不是简单摘抄。

- `persona stability`
长对话后是否仍保持回答风格、角色边界与输出纪律。

- `api latency`
首轮耗时、总耗时、长历史下的耗时抬升。

建议指标：

- memory recall accuracy
- contradiction rate
- persona drift rate
- first round latency
- total latency
- token efficiency

推荐 harness 结构：

1. `history store`
保存完整对话历史。

2. `memory extractor`
每 N 轮提炼一次长期记忆。

3. `response runner`
调用 MiniMax API，记录 latency / usage。

4. `quality judge`
检查是否记错、是否跑题、是否风格漂移。

### 2.2 Simple Agent / Workflow

目标：验证 MiniMax 是否适合做单代理执行链，而不是只做聊天。

重点测：

- 是否会先拿证据再下结论
- 是否会在必要时用工具
- 是否能在有限轮数里完成 tool loop
- 是否会把计划写得像结果
- 是否能给出验证与退出条件

推荐工作流：

1. read context
2. inspect tool output
3. synthesize answer
4. verify
5. update state

建议指标：

- tool call precision
- tool call redundancy
- groundedness
- completion honesty
- workflow completeness
- exit-criteria clarity

### 2.3 Multi-Agent

目标：验证 MiniMax 是否适合放进分工明确的双代理或多代理系统。

这里推荐的不是“多个模型一起自由讨论”，而是 `role split + explicit handoff`。

推荐最小双角色：

- `Content Engineer`
负责：
评测样本设计、任务文案、persona 与效果观察、失败案例归类、最佳实践文档输出。

- `Harness Engineer`
负责：
runner、history/memory 机制、latency 和 token 指标、tool traces、结果持久化、回归执行。

协调层负责：

- 汇总两个角色的输出
- 对冲单边偏见
- 产出共同决策

建议指标：

- role separation quality
- handoff completeness
- integration quality
- duplicated work rate
- traceability

## 3. 一个可执行的评估矩阵

| 维度 | Chatbot | Simple Agent | Multi-Agent |
| --- | --- | --- | --- |
| 记忆 | 高优先级 | 中优先级 | 中优先级 |
| latency | 高优先级 | 高优先级 | 高优先级 |
| tool use | 低 | 高 | 高 |
| persona | 高 | 中 | 中 |
| groundedness | 中 | 高 | 高 |
| 角色分工 | 低 | 低 | 高 |
| 工程可观测性 | 中 | 高 | 高 |

## 4. MiniMax 的性格画像，放到 Harness 里怎么理解

对 MiniMax-M2.7-highspeed，实践里更值得关注的不是“它聪不聪明”，而是它怎么失误。

### 4.1 常见优点

- 目标清楚时，执行意图强
- 对工程化任务拆解相对自然
- 对 tool-use / workflow 的接受度高
- 适合被脚本、状态文件和硬规则约束

### 4.2 常见风险

- 历史很长时，可能提前收尾
- 没有外部状态约束时，可能把讨论当完成
- 任务含糊时，容易给出漂亮但未验证的答案
- 多目标并列时，容易挑一两个先完成，然后默认整体已完成

### 4.3 Harness 层面的抑制方法

- 强制 `Done / Risks / Remaining Work`
- 把 todo 和验证状态外置成 JSON
- 给 tool loop 设最大轮数
- 保留完整 assistant 历史
- 用缓存减少前缀重复成本，但不要把动态状态缓存进去

## 5. 推荐的工程落地方式

### 5.1 Chatbot Harness

推荐模块：

- `history_store`
- `memory_store`
- `latency_recorder`
- `response_guard`

最佳实践：

- 每轮都记录 usage 和耗时
- 每 5 到 10 轮做一次 memory extraction
- 对历史压缩后仍保留最近若干轮原文

### 5.2 Simple Agent Harness

推荐模块：

- `task_runner`
- `tool_router`
- `state_store`
- `verification_runner`

最佳实践：

- 工具先少后多
- tool schema 要硬
- 退出条件写进 system prompt

### 5.3 Multi-Agent Harness

推荐模块：

- `role_dispatcher`
- `content_track`
- `harness_track`
- `integration_judge`

最佳实践：

- 角色写清楚，不要人格重叠
- handoff 输出格式固定
- 协调层只整合，不重做底层工作

## 6. 当前仓库里的对应实现

本仓库现在已经有三组新增 suite：

- [evals/suites/chatbot_memory_latency.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/chatbot_memory_latency.json)
- [evals/suites/agent_workflow_practice.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/agent_workflow_practice.json)
- [evals/suites/multi_agent_content_harness.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/multi_agent_content_harness.json)

同时 runner 现在会记录：

- `first_round_latency_ms`
- `total_latency_ms`
- `round_metrics`
- `input/output/cache tokens`

对应 runner：

- [scripts/run_minimax_evals.py](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/scripts/run_minimax_evals.py)

## 7. 给 MiniMax 的最佳实用指南

如果目标是把 MiniMax 放进真实 harness，而不是单次试玩，建议默认这么用：

1. 模型默认选 `MiniMax-M2.7-highspeed`
适合高频评测和 workflow 执行。

2. 默认走 `Anthropic-compatible` 接口
更贴合 thinking / tool use / caching 的官方路径。

3. 用短系统 prompt，不用长人格 prompt
让 harness 规则承担更多纪律约束。

4. 把记忆、状态、验证外置
不要指望模型自己一直记得。

5. 用三层评估看它
chatbot、simple agent、multi-agent 分开测，不要混成一个总分。

6. 重点观察“是否提前收尾”
这是比“答得不华丽”更危险的工程问题。

## 8. 下一步建议

如果你要把这套方案继续推进，最值钱的下一步不是再写文档，而是做下面三件事：

1. 跑一轮真实 API 评测，采集 latency / usage / trace
2. 把失败案例沉淀成固定 regression suite
3. 为 chatbot、agent、multi-agent 分别定义 production gate

这样最后得到的不是“模型印象”，而是一套可以反复复用的 MiniMax harness 能力基线。
