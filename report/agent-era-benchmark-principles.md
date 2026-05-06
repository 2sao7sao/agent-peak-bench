# Agent 时代的 Benchmark 原则

版本：`2026-05-06`

## 1. 核心判断

Agent 时代最合理的 benchmark 不应只测“模型会不会回答”，而要测：

- 模型在系统脚手架中能否持续工作
- 系统设计是否释放了模型能力
- 任务分布是否接近真实落地
- 失败是否能被定位到模型、工具、上下文、权限、状态或验证链路

一个更接近生产的 benchmark 应该是 `model + harness + environment + validator + distribution` 的组合，而不是孤立 prompt 集。

## 2. 从参考资料抽取的方法论

### 2.1 Seedance 2.0 论文：多维任务覆盖与主客观混合评估

Seedance 2.0 的评测框架虽然是视频生成领域，但它对 agent benchmark 很有启发：它没有只给一个总分，而是把能力拆成多模态任务跟随、生成一致性、运动质量、叙事质量、审美、音视频同步等维度，并区分客观指标和专家主观评审。

对 agent benchmark 的启发：

- 单一总分不足以指导使用
- 需要按真实工作流拆任务组
- 客观 validator 和专家/LLM-as-judge 可以并存
- 任务分布要覆盖组合任务，而不仅是单能力任务
- 评测预算小时，要控制样本方差

来源：[Seedance 2.0](https://arxiv.org/pdf/2604.14148)

### 2.2 Anthropic harness 设计：复杂任务需要 planner / generator / evaluator

Anthropic 的长程应用开发 harness 给出几个关键结论：

- 长任务里模型会失去连贯性，也可能因接近上下文限制而提前收尾
- compaction 不总是足够，context reset + structured handoff 有时更有效
- 自我评价偏乐观，独立 evaluator 是重要杠杆
- sprint contract 能把高层 spec 转成可测试的完成标准
- harness 组件必须定期做 load-bearing ablation，因为模型变强后旧脚手架可能变成成本

对 agent benchmark 的启发：

- benchmark 需要测 solo 与 harness 的差值
- evaluator 本身也要被测试
- task decomposition 应作为变量，而不是固定假设
- pass/fail 应绑定 sprint contract 和可执行验证

来源：[Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

### 2.3 OpenAI harness engineering：把仓库做成模型可读系统

OpenAI 的 Codex 工程经验强调：

- 早期慢不是模型无能，而是环境规范不清、工具/抽象/结构不足
- 人类工作的重心转向设计环境、明确意图、构建反馈回路
- UI、日志、指标、trace 要对 agent 可读
- 短 `AGENTS.md` 应作为地图，真实知识放在结构化 `docs/`
- 代码仓库是记录系统，执行计划、质量评分、设计规则都应版本化
- 严格边界、结构测试、自定义 linter 会放大 agent 产能

对 agent benchmark 的启发：

- 要测“环境可读性”对模型表现的提升
- 要测日志/指标/trace 是否能帮助 agent 修复问题
- 要测 AGENTS.md 是地图还是巨大手册
- 要测结构约束是否降低架构漂移

来源：[Harness engineering](https://openai.com/zh-Hans-CN/index/harness-engineering/)

### 2.4 OpenAI Agents SDK：模型原生运行框架和沙箱状态

新版 Agents SDK 强调：

- 只有模型不够，需要运行框架支撑文件审查、命令执行、代码修改和长周期协作
- harness 应包含 memory、sandbox-aware orchestration、文件系统工具、MCP、skills、AGENTS.md、shell、apply patch
- sandbox/manifest 给模型一个可预测工作空间
- 状态外部化、snapshot 和 rehydration 能让长任务跨容器恢复
- 子 agent 和隔离环境能提升扩展性

对 agent benchmark 的启发：

- 要测 sandbox、manifest、memory、snapshot 是否真实提高可靠性
- 要测工具权限和敏感数据隔离
- 要测恢复能力，而不是只测一次性完成

来源：[Agents SDK evolution](https://openai.com/zh-Hans-CN/index/the-next-evolution-of-the-agents-sdk/)

### 2.5 open-claude-code：Claude Code 类系统依赖的模型能力

`open-claude-code` 的 README 和 ADR 展示了一个 Claude Code 类 CLI 的系统边界：

- async generator agent loop
- 25+ built-in tools
- permission modes
- hooks
- context manager
- MCP transports
- settings chain
- streaming handler
- custom agents and skills
- session management
- prompt caching

它的 ADR 还强调：

- tool input schema 和 edge case behavior 要深度匹配
- thinking block、tool input streaming、context compaction、prompt cache 都是高影响模块
- 最后 50% 是 edge cases、error handling、跨平台兼容和 UX polish

对 agent benchmark 的启发：

- 不应只测工具调用“有没有”，还要测工具 schema、权限、hooks、错误恢复、上下文压缩和 session resume
- 要把“实现深度”作为系统能力，而不是只看功能清单
- 要测系统是否让模型保持在高效工作状态

来源：[open-claude-code](https://github.com/ruvnet/open-claude-code)

## 3. 一个更合理的任务分布

初始建议分布如下：

| Task Family | Weight | 目标 |
| --- | ---: | --- |
| Chat / Memory | 10% | 多轮偏好、长期记忆、历史压缩 |
| Structured Workflows | 15% | 证据收集、状态更新、业务流程完成 |
| Tool Use / Error Recovery | 15% | 工具选择、失败处理、重试与降级 |
| Coding / CLI / Repo | 15% | 可执行修改、测试、调试 |
| Long-Running Harness | 15% | planner/generator/evaluator、handoff、resume |
| Context Engineering | 10% | map vs manual、compaction、reset、窗口压力 |
| Multi-Agent Coordination | 10% | 角色分工、handoff、冲突解决 |
| System Governance | 10% | 权限、sandbox、hooks、日志、审计 |

这个分布的目标不是平均覆盖所有能力，而是覆盖 agent 落地最常见的失效链路。

## 4. 系统视角下如何评估模型能力

每个任务都应该同时输出两类分数。

### 4.1 Model Capability Score

衡量模型本身：

- 指令遵循
- 工具选择
- 规划
- 记忆提取
- 错误识别
- 完成诚实度
- 输出稳定性

### 4.2 Harness Fit Score

衡量系统是否释放模型能力：

- 环境是否可读
- 工具 schema 是否明确
- 状态是否外部化
- 验证是否可执行
- 权限是否合理
- trace 是否足够诊断
- handoff 是否完整

最终报告不应只说“模型强/弱”，而应说：

- 在什么 harness 里强
- 在什么任务分布里强
- 哪个系统组件是 load-bearing
- 哪个组件已经是成本

## 5. “尖峰时刻”的定义

让模型保持尖峰状态，不是靠更长 prompt，而是让系统持续满足这些条件：

- 当前目标小而明确
- 可用工具少而相关
- 证据可读且接近任务
- 状态外部化，不靠模型硬记
- 验证立即可运行
- 失败反馈具体、可行动
- 上下文中没有陈旧噪声
- 权限边界清楚

benchmark 应测试这些条件被破坏时，模型表现如何下降。

## 6. 需要新增的测试类型

### 6.1 Load-Bearing Ablation

逐个移除系统组件：

- 无 planner
- 无 evaluator
- 无 sprint contract
- 无 memory
- 无 hooks
- 无 sandbox
- 无 structured handoff

观察 pass@k、latency、token、错误类型变化。

### 6.2 Harness Readability Test

同一任务对比：

- 巨大 AGENTS.md
- 短 AGENTS.md + docs index
- 可执行计划 + quality score

观察模型是否更快定位正确资料。

### 6.3 Context Strategy Test

对比：

- raw long history
- compaction
- reset + handoff
- micro-compaction

观察早停、遗忘、任务漂移。

### 6.4 Tool Surface Test

对比：

- 3 个核心工具
- 8 个工具含 distractors
- 25 个工具含权限/危险操作
- ToolSearch 延迟加载

观察工具精度与冗余调用。

### 6.5 Evaluator Quality Test

独立测 evaluator：

- 是否过度乐观
- 是否能发现关键 bug
- 是否能区分 display-only 和 functional
- 是否能给出可行动反馈

## 7. 结论

Agent 时代的 benchmark 应该从“模型考试”升级为“系统能力审计”。

最合理的评估不是问模型一次，而是在可观测、有状态、有权限、有验证的系统中，看模型是否能长期保持高质量执行，并判断哪些系统设计真正帮助了它。
