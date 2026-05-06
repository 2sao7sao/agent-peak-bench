# Benchmark Framework Review

版本：`2026-05-06`

## 结论

当前仓库中的评测内容，严格来说只能算：

- `smoke tests`
- `ablation harness`
- `prompt/tool/workflow probes`

它们还不能被称为“可信的真实 benchmark”。

这不是措辞问题，而是方法论问题。

## 当前框架为什么不够合理

### 1. 任务过于合成化

当前大多数 case 是人工拼出来的短任务、短上下文、mock tool 返回值和字符串匹配检查。

这类 case 有价值，但它们只能回答：

- 接口能不能通
- 模型是否大致遵循格式
- 某种 prompt 或工具配置是否相对更稳定

它们不能回答：

- 模型能否完成真实业务任务
- 模型在真实环境中的成功率是多少
- 模型在企业环境里的失败模式是什么

### 2. 验证器过弱

当前 runner 主要依赖：

- `must_contain`
- `must_not_contain`
- `json_keys`
- 长度阈值

这属于 `surface-level correctness`，不是 `task correctness`。

它的问题是：

- 容易错杀语义正确但措辞不同的输出
- 容易放过格式正确但内容空洞的输出
- 无法判断动作是否真的完成

### 3. 过度依赖 mock tools

当前 tool 场景大多是离线 mock。

这有助于快速实验，但无法覆盖生产里最重要的扰动：

- tool latency
- malformed tool output
- partial failure
- stale data
- permission failure
- timeout and retry

而这些恰恰是 agent 在企业环境里最常见的失败来源。

### 4. 没有真实环境与可执行验证

可信 benchmark 的核心不是 prompt，而是：

- `environment`
- `ground truth`
- `test/validator`

当前仓库缺的是像 `Terminal-Bench`、`SWE-bench`、`tau-bench` 那样的环境级验证结构。

没有这些，最后只能得到“回答看起来不错”，而不是“任务真的完成了”。

### 5. 没有扰动鲁棒性设计

MiniMax 官方关于 agent generalization 的文章，核心观点不是“多挂工具就行”，而是 agent 必须对整个 operational space 的扰动稳定，包括：

- tool info
- system prompt
- user prompt
- environment
- tool responses

来源：
[Aligning to What? Rethinking Agent Generalization in MiniMax M2](https://platform.minimax.io/docs/guides/text-m2-agent-generalization)

当前仓库虽然做了一点 context noise 和 tool-count ablation，但还没有形成系统化的 `perturbation benchmark`。

### 6. pass@k 只是刚起步，还不够

我已经把 runner 扩到了 repeated trials 和 `pass@k`，但这仍然只是可靠性度量的开端。

还缺：

- 语义等价判分
- 失败类型聚类
- latency percentile
- cost variance
- tool trace 质量
- retry sensitivity

### 7. 没有数据集分层

一个成熟框架至少要区分：

1. `smoke`
2. `ablation`
3. `benchmark`
4. `deployment canaries`

当前仓库之前把这些混在一起了，这是不严谨的。

### 8. 没有真实企业任务分布

企业级 agent 失败往往不是因为它不会回答，而是因为：

- 任务长链条
- 工具脏
- 数据不齐
- 权限受限
- 用户表达不稳定
- 成功标准不是单句答案，而是完成一个流程

这类分布在当前仓库里几乎还没有体现。

## 外部依据

以下公开资料支持上述批评：

- MiniMax 官方文章明确指出：benchmark 好不等于真实任务好，重点是对全链路扰动的泛化。  
  来源：[MiniMax Agent Generalization](https://platform.minimax.io/docs/guides/text-m2-agent-generalization)

- `ReliabilityBench` 明确提出，生产级 agent 需要看 repeated execution 的 `pass^k`、语义扰动鲁棒性、工具/API 故障容忍。  
  来源：[ReliabilityBench](https://arxiv.org/abs/2601.06112)

- `CLEAR` 指出评估不能只看准确率，还必须同时看 cost、latency、assurance、reliability。  
  来源：[CLEAR](https://arxiv.org/abs/2511.14136)

- `UNDERWRITE` 表明研究级 agent 在企业级承保任务里会被专有知识、噪声工具和真实 workflow 放大缺陷。  
  来源：[UNDERWRITE](https://arxiv.org/abs/2602.00456)

- `Terminal-Bench 2.0` 强调真实 benchmark 需要唯一环境、人写参考解和可执行测试。  
  来源：[Terminal-Bench 2.0](https://arxiv.org/abs/2601.11868)

- `tau-bench` 强调真实工具代理评测应包含多轮对话、策略约束和 domain-specific APIs。  
  来源：[tau-bench](https://arxiv.org/abs/2406.12045)

## 重新定位当前仓库

从现在开始，当前仓库里的现有 suite 应被视为：

- `Exploration Harness`
- `Smoke + Ablation Layer`

而不是：

- `Production-grade benchmark`
- `Model leaderboard`

## 接下来必须怎么改

### 第一层：保留现有 smoke/ablation

保留的原因：

- 适合快速发现 prompt、skill、tool surface、window 的方向性问题
- 适合做 MiniMax 最佳实践探索

### 第二层：新增 benchmark blueprint

需要新增一套真实 benchmark 设计蓝图，要求每个任务都具备：

- task spec
- environment
- ground truth
- executable validator
- perturbations
- retry protocol
- cost/latency collection

### 第三层：新增 deployment canaries

需要加入小规模真实 API 在线回归：

- 真实工具
- 真实延迟
- 真实失败码
- 真实 history/memory 状态

## 一个更合理的最终目标

这套系统最终不该产出“一个总分”，而该产出三类结果：

1. `能力画像`
模型在 chatbot、workflow、multi-agent、coding、office、retrieval 等任务上的实际边界。

2. `使用指南`
skills 怎么写、工具怎么挂、窗口怎么选、复杂任务怎么拆。

3. `不适用场景`
哪些环境下即使模型看起来很强，也不应该直接上生产。
