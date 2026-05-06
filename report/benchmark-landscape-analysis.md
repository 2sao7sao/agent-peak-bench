# Agent / LLM Benchmark Landscape Analysis

版本：`2026-05-06`

## 目标

这份分析只回答一个问题：`哪些 benchmark 对模型落地能力最有帮助，哪些不够？`

我们不追求“列全”，而是挑出对 agent 落地最有代表性的 benchmark 家族，并抽取它们对 MiniMax 使用评估真正有用的方法论。

## 1. 关键 benchmark 家族

### 1.1 SWE-bench / SWE-bench Pro

代表能力：

- 真实软件仓库问题修复
- 长链路代码理解与修改
- 可执行测试验证

优点：

- 真实 repo
- 可执行测试
- 对 coding agent 很有代表性

局限：

- 只覆盖软件工程
- 对非 coding agent 帮助有限
- `SWE-bench Verified` 已被 OpenAI 明确认为不再适合衡量前沿能力

来源：
[Why SWE-bench Verified no longer measures frontier coding capabilities](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/)  
[SWE-Bench Pro](https://arxiv.org/abs/2509.16941)

对我们设计的启发：

- 要有真实环境
- 要有执行式 validator
- 但不能把“coding 成绩”误当成“通用落地能力”

### 1.2 Terminal-Bench 2.0

代表能力：

- CLI / shell / repo / tools 的综合执行能力

优点：

- 89 个任务来自真实 workflow
- 每题有唯一环境、人写解法和 comprehensive tests

局限：

- 偏 terminal/coding 运维
- 不覆盖多轮用户交互与企业策略遵循

来源：
[Terminal-Bench 2.0](https://arxiv.org/abs/2601.11868)

对我们设计的启发：

- benchmark 必须有唯一环境与自动验证
- 任务要来自真实 workflow，而不是合成 prompt

### 1.3 τ-bench

代表能力：

- 多轮对话
- 用户交互
- API 工具调用
- domain-specific policy adherence

优点：

- 明确评估“用户 + agent + tools + policy”
- 使用 end-state 判断而不是表层文本
- 提出 `pass^k`

局限：

- 域较窄，主要是 retail / airline
- 企业级复杂 UI / 多系统协同覆盖不足

来源：
[τ-bench](https://arxiv.org/abs/2406.12045)

对我们设计的启发：

- 需要多轮任务
- 需要策略约束
- 需要 `pass@k`
- 最终状态比文本措辞更重要

### 1.4 GAIA

代表能力：

- 一般性 assistant
- 工具使用
- 浏览、推理、多模态

优点：

- 任务对人概念上简单、对模型困难
- 强调“像普通人一样稳健地完成真实问题”

局限：

- 偏 open-world QA / research assistant
- 很难直接映射到企业工作流

来源：
[GAIA](https://ai.meta.com/research/publications/gaia-a-benchmark-for-general-ai-assistants/)

对我们设计的启发：

- 不要只追越来越难的人类都难的题
- 真实落地更看“简单但多步骤”的鲁棒性

### 1.5 BrowseComp

代表能力：

- persistent browsing
- multi-hop web retrieval

优点：

- 短答案、易验证
- 专门隔离“浏览能力”

局限：

- OpenAI 自己明确承认，它与真实开放用户分布相关性不完全清楚
- 适合测核心 browsing skill，不适合独立代表整体 agent

来源：
[BrowseComp paper](https://arxiv.org/abs/2504.12516)  
[BrowseComp OpenAI page](https://openai.com/index/browsecomp/)

对我们设计的启发：

- 单能力 benchmark 很有用
- 但必须明确告诉用户它是“核心能力代理指标”，不是完整落地指标

### 1.6 WorkArena

代表能力：

- 企业软件中的知识工作
- 浏览器中的实际业务流程

优点：

- 真实企业软件环境
- 更接近知识工作 automation

局限：

- 强依赖特定平台
- 对模型一般能力的横向比较没那么宽

来源：
[WorkArena](https://arxiv.org/abs/2403.07718)

对我们设计的启发：

- 企业落地 benchmark 必须引入真实业务 UI / 软件流程
- consumer web 和 enterprise web 不是一回事

### 1.7 OSWorld

代表能力：

- computer use
- 多应用、多系统、多模态 GUI 操作

优点：

- 真实计算机环境
- execution-based evaluation

局限：

- 更偏 multimodal computer use
- 搭建和运行成本高

来源：
[OSWorld](https://arxiv.org/abs/2404.07972)

对我们设计的启发：

- 如果要测 computer-use agent，必须用真实操作环境
- 纯文字 benchmark 不足以覆盖 GUI grounding

### 1.8 PaperBench / MLE-bench

代表能力：

- AI 研究复现
- 机器学习工程

优点：

- 任务长、难、可执行
- 更接近“真实工程项目”

局限：

- 成本高
- 运行时间长
- 不适合作为日常快速迭代 benchmark

来源：
[PaperBench](https://arxiv.org/abs/2504.01848)  
[MLE-bench](https://arxiv.org/abs/2410.07095)

对我们设计的启发：

- 长程 benchmark 必须和成本、时间一起评估
- 不能只看成功率

## 2. 企业落地视角下，这些 benchmark 共同暴露了什么问题

### 2.1 单次成功率不够

`τ-bench`、`ReliabilityBench`、`CLEAR` 都在提醒同一件事：

- 单次通过不代表稳定
- 必须看 `pass@k`

来源：
[τ-bench](https://arxiv.org/abs/2406.12045)  
[ReliabilityBench](https://arxiv.org/abs/2601.06112)  
[CLEAR](https://arxiv.org/abs/2511.14136)

### 2.2 benchmark 和现实之间存在结构性落差

MiniMax 官方也明确承认了这个问题：模型可能 benchmark 很强，但换个框架或真实任务就掉。  
来源：
[MiniMax Agent Generalization](https://platform.minimax.io/docs/guides/text-m2-agent-generalization)

### 2.3 end-state 比文本表面更重要

`τ-bench` 看数据库终态，`Terminal-Bench` 和 `OSWorld` 看执行脚本结果，`ReliabilityBench` 强调 end-state equivalence。

这意味着我们自己的 benchmark 也必须尽量走：

- state-based validators
- executable validators
- semantic equivalence

### 2.4 企业环境需要多维度，不是 accuracy-only

`CLEAR` 最直接：企业场景必须同时看 `Cost, Latency, Efficacy, Assurance, Reliability`。  
来源：
[CLEAR](https://arxiv.org/abs/2511.14136)

## 3. 对我们自建 benchmark 的设计要求

基于上面这些 benchmark，比较合理的设计应分三层：

### 3.1 Core Capability Canaries

小而硬，便于频繁运行：

- memory
- structured extraction
- grounded decision
- tool error honesty
- context robustness

### 3.2 Workflow Benchmarks

更接近真实工作流：

- chatbot with memory
- simple tool workflow
- multi-agent coordination
- coding / CLI

### 3.3 Enterprise Stress Layer

针对真实落地问题：

- prompt perturbation
- tool noise
- API failure
- latency / cost ceilings
- policy compliance
- abstain / escalate behavior

## 4. 为什么这比“继续堆一些 case”更合理

因为它把 benchmark 的三个目标拆开了：

1. `持续回归`
用 canaries 快速发现退化

2. `能力验证`
用 workflow benchmark 测真实任务

3. `上线判断`
用 enterprise stress 看生产可行性

这比只做一套分数更接近真实落地。

## 5. 对 MiniMax 的特殊要求

MiniMax 官方文档里有几个设计约束值得直接纳入 benchmark：

- 多轮 function call 时必须保留完整 assistant response，包含 thinking/tool blocks  
  来源：[Tool Use & Interleaved Thinking](https://platform.minimax.io/docs/guides/text-m2-function-call)

- 长任务更适合 multi-window workflow，而不是单窗口堆满  
  来源：[M2.7 Usage Tips](https://platform.minimax.io/docs/token-plan/best-practices)

- 官方 Mini-Agent 把 `Persistent Memory`、`Intelligent Context Management`、`Comprehensive Logging` 当成核心功能  
  来源：[Mini-Agent](https://platform.minimax.io/docs/token-plan/mini-agent)

因此，针对 MiniMax 的 benchmark 不应该只测回答质量，还应该测：

- history preservation correctness
- long-session memory
- multi-window strategy
- tool loop continuity
- logging completeness

## 6. 结论

更合理的 benchmark 不该试图用一个分数解释一切。

它至少应同时回答：

- 这个模型在什么任务族里能稳定成功
- 这个模型在什么扰动下会退化
- 这个模型应该如何被使用，才能逼近最佳效果
