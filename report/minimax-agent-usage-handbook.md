# MiniMax Agent 指导使用书

版本：`2026-05-06`

这份文档不是只讲模型参数，而是回答更实际的问题：

- 什么测试才能逼近真实 agent 任务
- 如何用 `pass@k` 和重复执行看稳定性
- 什么时候该用 skills
- 工具应该挂多少个
- 多大窗口内模型最稳
- 复杂任务如何拆解
- 哪些场景适合 MiniMax，哪些场景暂时不适合

本文把内容分成两类：

- `官方事实`：来自 MiniMax 官方文档
- `行业/研究信号`：来自近期 agent benchmark、企业观察和研究论文

## 1. 为什么不能只看一个 benchmark 分数

近期公开资料在这个问题上高度一致。

- MiniMax 官方自己在 `Agent Generalization` 文中明确说过：同一个模型可能在某个 agent benchmark 上很好，但在简单真实任务里失败；真正的问题是“benchmark 还是 reality”。  
  来源：<https://platform.minimax.io/docs/guides/text-m2-agent-generalization>

- `ReliabilityBench` 指出，很多 tool-using agent benchmark 只报单次成功率，遗漏了生产真正关心的可靠性；他们明确把 `pass^k`、语义扰动鲁棒性、工具/API 故障容忍度列为核心维度。  
  来源：<https://arxiv.org/abs/2601.06112>

- `CLEAR` 框架指出，只看 accuracy 会严重误导企业使用，因为还需要同时评估 cost、latency、assurance 和 reliability；文中提到一些 agent 单次精度看起来还行，但重复 8 次后稳定性显著下滑。  
  来源：<https://arxiv.org/abs/2511.14136>

- `UNDERWRITE` 证明了一个现实问题：研究环境中的好成绩并不等于企业落地能力，尤其在有噪声工具、专有知识和不完美用户时，pass^k 还会进一步下降。  
  来源：<https://arxiv.org/abs/2602.00456>

结论很直接：`真实 agent 能力 = 任务成功 × 稳定性 × 可观测性 × 成本/延迟 × 对环境扰动的适应能力`。

## 2. 需要新增哪些测试

建议把评测矩阵扩成五层：

### 2.1 重复简单任务测试

目的：看模型是不是“偶尔答对”，还是“稳定答对”。

做法：

- 同一个简单任务重复跑 `5` 到 `10` 次
- 记录 `pass@1 / pass@3 / pass@5`
- 记录 `exact output consistency`
- 记录 `平均延迟` 与 `方差`

适合的任务：

- JSON 抽取
- 二分类/三分类
- 简单对话记忆回忆
- 小型 workflow 判断

### 2.2 工具挂载 ablation

目的：回答“到底是工具太多不稳，还是工具类型设计不好导致不稳”。

做法：

- 同一任务分别给 `3 / 8 / 14` 个工具
- 保持核心工具不变，只增加无关 distractor
- 单独再做一组“同数量、不同类型相似工具”的实验

观察：

- tool call precision
- tool redundancy
- irrelevant tool selection rate
- latency increase
- pass@k 变化

### 2.3 Skill 写法 ablation

目的：回答“该不该用 skills”“skill 应该怎么写”。

做法：

- 同一任务比较 `vague skill` 和 `structured skill`
- structured skill 明确写：
  - Goal
  - Inputs
  - Required Output
  - Working Rules
  - Stop Condition

观察：

- 输出结构是否更稳
- 是否更少过早收尾
- pass@k 是否上升

### 2.4 窗口大小 ablation

目的：回答“多少窗口内效果最稳且最好”。

做法：

- 同一任务在 `compact / expanded / near-limit` 三种上下文规模下重复执行
- 只改变噪声量，不改变关键信息

观察：

- retrieval pass@k
- instruction drift
- early termination rate
- latency and token growth

### 2.5 任务拆解 ablation

目的：回答“复杂任务应该怎么拆”。

做法：

- 对比 `single-shot complex prompt` 和 `phased workflow`
- phased 方案至少拆为：
  1. scope
  2. evidence/tools
  3. action
  4. verification
  5. remaining work

观察：

- groundedness
- completion honesty
- verification coverage
- pass@k

## 3. 当前行业里做 agent 的真实痛点

### 3.1 Benchmark 和真实任务脱节

MiniMax 官方自己就点过这个问题：一个 agent 可能“crush a tool-use leaderboard but fail spectacularly at a simple, real-world task”。  
来源：<https://platform.minimax.io/docs/guides/text-m2-agent-generalization>

`AAR` 进一步说明，很多 benchmark 是线性的 2 到 5 步链路，但真实 agent 常常要在 DAG 结构里导航；论文发现很多失败不是“不会调工具”，而是“不会导航到正确位置”。  
来源：<https://arxiv.org/abs/2604.10261>

### 3.2 可观测性不足

IBM 的 `Observability in the Agentic Era` 提到，企业团队往往难以判断问题是模型本身、下游 API 还是 agent 的低效工具调用引起的，而且 agent 带来了新的观测对象，如决策树、工具日志和 memory 指标。  
来源：<https://www.ibm.com/think/insights/observability-in-the-agentic-era>

### 3.3 重复稳定性不足

`ReliabilityBench` 和 `CLEAR` 都强调，单次成功率不够；重复执行后的稳定性下降，是企业环境最关心的问题之一。  
来源：<https://arxiv.org/abs/2601.06112>  
来源：<https://arxiv.org/abs/2511.14136>

### 3.4 专有领域里的幻觉与脆弱性

`UNDERWRITE` 指出，即使有工具接入，模型仍可能 hallucinate domain knowledge；而且通用 agent 框架本身的脆弱性，也会扭曲评测结果。  
来源：<https://arxiv.org/abs/2602.00456>

## 4. 基于 MiniMax 的具体使用建议

### 4.1 什么时候用 Skills

建议在以下情况下用 skills：

- 任务是重复出现的
- 需要固定输出格式
- 需要明确的完成条件
- 想把 best practice 固化下来

不建议在以下情况下上来就用 skills：

- 任务探索性很强，范围还不清楚
- 工具和目标都还在频繁变化
- 你自己还没形成稳定 workflow

### 4.2 Skills 怎么写更适合 MiniMax

这里的建议是 `工程推断`，但跟 MiniMax 官方最佳实践一致。

官方说 M2.7 对明确、具体、解释了意图、给了 examples 的指令响应更好；长任务里要聚焦有限目标，不要并行处理一切。  
来源：<https://platform.minimax.io/docs/token-plan/best-practices>

因此更适合 MiniMax 的 skill 结构是：

1. `Goal`
2. `Inputs`
3. `Required Output`
4. `Working Rules`
5. `Stop Condition`
6. `Failure Fallback`

写法要求：

- 一 skill 一职责
- 输入边界清晰
- 输出格式硬
- 明确什么算完成
- 明确缺失信息时怎么处理

### 4.3 工具挂载多少个更稳

官方没有给“最佳工具数量”这一数字，但 MiniMax 在 `Agent Generalization` 文中直接说过：他们一开始也以为“tool scaling is agent generalization”，后来发现这是错的；真正要应对的是系统 prompt、user prompt、environment、tool responses 等全链路扰动。  
来源：<https://platform.minimax.io/docs/guides/text-m2-agent-generalization>

所以实用建议不是“固定挂 N 个工具”，而是：

- 从 `3` 个核心工具开始
- 再扩到 `6-8`
- 超过 `10` 个工具前必须做 ablation
- 将相似工具合并或做 router

要回答“是工具数量问题还是工具类型问题”，必须分开测：

- `数量型 ablation`
同一任务，增加无关工具

- `类型型 ablation`
同一数量，增加语义相近、容易混淆的工具

### 4.4 多少窗口内最稳

MiniMax 官方建议长任务使用 multi-window workflow，并指出接近上下文阈值时模型可能提前终止；还建议第一窗口搭框架、第二窗口按 todo 推进，并创建 `tests.py`/`tests.json` 与 `init.sh`。  
来源：<https://platform.minimax.io/docs/token-plan/best-practices>

结合这些约束，实际建议是：

- 日常 agent 执行优先放在中等窗口
- 复杂任务优先多窗口，不要长期单线程堆满
- 靠近上限的超长窗口只做边界测试，不做默认工作模式

### 4.5 复杂任务如何拆解更能激发效果

MiniMax 官方给出的核心信号有两个：

- 要保留完整 session history，包含 thinking
- 长任务要聚焦有限目标，分阶段推进

来源：<https://platform.minimax.io/docs/guides/text-m2-agent-generalization>  
来源：<https://platform.minimax.io/docs/guides/text-m2-function-call>  
来源：<https://platform.minimax.io/docs/token-plan/best-practices>

因此更适合 MiniMax 的复杂任务拆解方式是：

1. `Scope`
只定义当前子任务

2. `Evidence / Tools`
先取证，再决策

3. `Action`
执行最小必要动作

4. `Verification`
验证，不验证不算完成

5. `Remaining Work`
没有做完就显式报剩余项

## 5. 哪些场景适合 MiniMax

更适合：

- 明确 workflow 的代码/自动化 agent
- 有工具、有状态文件、有验证脚本的执行型任务
- 需要多轮 tool reasoning 的复杂问题
- 需要较强长任务状态追踪的场景

## 6. 哪些场景暂时不适合

不太适合直接上 MiniMax 单模型裸跑的场景：

- 没有 trace、没有 observability 的高风险企业任务
- 工具面极大、目标又很模糊的开放式自治代理
- 需要极低延迟且不允许 agent 回合开销的超短交互
- 领域知识高度封闭、又没有高质量企业 benchmark 的场景

## 7. 这套评测如何扩展到各个模型

建议把框架设计成模型无关，只把 `provider adapter` 抽出来。

跨模型共用的维度：

- pass@k
- consistency
- latency
- cost
- tool precision
- redundancy
- hallucination under tools
- completion honesty
- decomposition gain

模型特有的维度：

- thinking/history 保留要求
- prompt caching 机制
- tool schema 偏好
- 上下文边界行为

## 8. 当前仓库里已经落下来的部分

新的 suite：

- [evals/suites/repeatability_passk.json](../evals/suites/repeatability_passk.json)
- [evals/suites/skill_design_ablation.json](../evals/suites/skill_design_ablation.json)
- [evals/suites/tool_count_ablation.json](../evals/suites/tool_count_ablation.json)
- [evals/suites/window_and_decomposition_ablation.json](../evals/suites/window_and_decomposition_ablation.json)

runner 新能力：

- repeated trials
- `pass@k`
- exact output consistency
- average latency summary

对应脚本：

- [scripts/run_minimax_evals.py](../scripts/run_minimax_evals.py)

## 9. 最后的建议

如果你的目标是做“模型指导使用书”，不要再追求一个总分，而应该输出下面三类结论：

1. `这个模型在什么工作流里最好用`
2. `这个模型在哪些配置下会明显退化`
3. `为了激发最佳效果，prompt/skill/tool/window/decomposition 该怎么搭`

这才是能真正指导生产实践的结果。
