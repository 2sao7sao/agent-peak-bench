# MiniMax Real-Task Benchmark Blueprint

## 目标

为 `MiniMax-M2.7` / `MiniMax-M2.7-highspeed` 设计一套更可信的真实任务 benchmark。

这套 blueprint 不直接等于“已经实现的 benchmark”，而是实现标准。

## 基本原则

### 1. 真实任务优先

不要再以“格式正确”代替“任务完成”。

每个 benchmark task 必须尽量接近真实工作：

- 客服/运营多轮对话
- 代码仓库修复
- CLI / shell 排障
- 文档整理与修订
- 业务流程型 workflow

### 2. 每题必须有 validator

validator 类型可选：

- executable tests
- state diff
- policy checker
- semantic grader + reference constraints

至少要有一种能区分：

- 真完成
- 假完成
- 只会说不会做

### 3. 每题都要能重复执行

为了支持 `pass@k`，每题必须能够多次独立运行，且有稳定判定器。

### 4. 每题都要有扰动版本

每题至少设计三种 perturbation：

- prompt perturbation
- tool perturbation
- environment perturbation

### 5. 每题都要有 trace

必须记录：

- full history
- full assistant response
- tool calls
- tool results
- latency
- token usage

## 推荐 benchmark families

### A. Chatbot Memory

真实任务：

- 长对话中追踪用户偏好
- 跨轮修订同一个任务
- 历史压缩后继续回答

validator：

- reference facts
- contradiction checker
- semantic consistency checker

### B. Tool Workflow

真实任务：

- 读取日志
- 读取配置
- 做出诊断
- 给出验证步骤

validator：

- groundedness checks
- required evidence checks
- tool redundancy checks

### C. Multi-Agent Coordination

真实任务：

- content engineer 设计评测样本
- harness engineer 设计执行与采集
- coordinator 产出最终评估计划

validator：

- role separation
- handoff completeness
- integration quality

### D. Coding / CLI

真实任务：

- bug fix
- config repair
- test restoration
- small feature implementation

validator：

- executable test suite
- diff constraints
- regression suite

### E. Enterprise Workflow

真实任务：

- policy-constrained customer support
- finance/ops workflow routing
- document + tool + policy multi-step completion

validator：

- policy adherence
- task completion
- human escalation correctness

## 必须输出的指标

### 核心成功指标

- task_success
- pass@1
- pass@3
- pass@5

### 稳定性指标

- exact consistency
- semantic consistency
- retry sensitivity

### 过程指标

- tool precision
- tool redundancy
- unnecessary steps
- completion honesty

### 系统指标

- p50 latency
- p95 latency
- token cost
- failure code distribution

## 面向使用指南的专项实验

这部分不是为了“模型排行”，而是为了指导实际使用。

必须单列四组实验：

1. `Skill Writing`
比较 vague vs structured skills。

2. `Tool Surface`
比较不同工具数量和不同工具类型混淆。

3. `Window Size`
比较 compact / medium / large / near-limit。

4. `Task Decomposition`
比较 single-shot / phased / multi-window。

## 最终应产出的不是一个分数

这套 benchmark 最终要产出的是：

1. `Best-use guide`
在什么工作流和配置下 MiniMax 最好用。

2. `Failure map`
在哪些扰动、哪些任务、哪些工具面下最容易退化。

3. `Do-not-use list`
哪些企业场景不适合直接上线。
