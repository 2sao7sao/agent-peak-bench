# open-claude-code 系统分析

版本：`2026-05-06`

参考项目：[ruvnet/open-claude-code](https://github.com/ruvnet/open-claude-code)

## 1. 它的设计依赖模型什么能力

`open-claude-code` 的设计不是简单 CLI，而是一个围绕模型行为构建的执行系统。它依赖模型具备以下能力：

| 系统模块 | 依赖的模型能力 | 释放的模型能力 |
| --- | --- | --- |
| async generator agent loop | 多轮状态保持、工具结果整合 | 长程 tool-use 任务 |
| 25+ built-in tools | 工具选择、schema 遵循 | 文件读写、搜索、执行、编辑 |
| permission modes | 风险识别、意图表达 | 安全地执行高影响动作 |
| hooks engine | 接受外部控制与反馈 | 在执行前后被系统校正 |
| context manager | 摘要理解、状态恢复 | 在长上下文中继续推进 |
| MCP transports | 外部工具抽象理解 | 扩展可用能力面 |
| settings chain | 规则优先级理解 | 项目级/用户级/企业级策略融合 |
| custom agents | 角色遵循与分工 | 专家化处理 |
| skills | 渐进式能力披露 | 重复 workflow 固化 |
| sessions/resume | 状态恢复、handoff 理解 | 长任务跨会话延续 |

关键点：这些模块不是“给模型更多东西”，而是把模型最容易失误的地方外部化。

## 2. 它释放了模型什么能力

### 2.1 让模型从回答者变成执行体

文件工具、Bash、Edit、MultiEdit、Grep、Glob、LS 使模型能直接改变世界状态，而不是只描述方案。

对应测试：

- read/edit/verify loop
- repo mutation with tests
- tool result grounding

### 2.2 让模型在可控边界内行动

permission modes、sandbox、hooks 把危险动作变成可审计、可拦截的动作。

对应测试：

- dangerous tool refusal
- permission escalation request
- hook block compliance

### 2.3 让模型可持续工作

context manager、auto-compaction、micro-compaction、session resume 解决长任务中上下文膨胀和状态丢失问题。

对应测试：

- raw history vs compaction
- reset + handoff
- resume after interruption

### 2.4 让模型适配不同任务形态

custom agents、skills、task profiles 让系统不必用一个通用 prompt 处理所有工作。

对应测试：

- role specialization lift
- skill quality ablation
- tool profile routing

## 3. 如何通过测试明确工程链路的设计

最重要的不是测试“模型能不能调用工具”，而是测试每个工程组件是否 load-bearing。

### 3.1 Agent Loop

测试问题：

- tool_use 后是否完整回填 assistant response
- 工具失败后是否继续推理
- 是否能在 max recursion 前收敛

指标：

- tool loop completion
- duplicate tool call rate
- final groundedness

### 3.2 Tool System

测试问题：

- 工具 schema 是否足够清晰
- 工具数量增多是否降低精度
- 相似工具是否导致混淆

指标：

- tool precision
- irrelevant tool selection
- schema violation rate

### 3.3 Permission / Sandbox

测试问题：

- 模型是否会识别危险动作
- permission denied 后是否能给替代方案
- sandbox 限制是否会诱发幻觉

指标：

- unsafe action attempt rate
- graceful fallback rate
- permission recovery

### 3.4 Hooks

测试问题：

- PreToolUse block 是否被模型尊重
- PostToolUse failure 是否触发修正
- hook feedback 是否被转化为下一步动作

指标：

- hook compliance
- feedback utilization
- recovery success

### 3.5 Context Manager

测试问题：

- compaction 后是否保留关键状态
- stale tool result 是否被重新读取
- reset + handoff 是否优于 raw compaction

指标：

- state retention
- stale reference rate
- early wrap-up rate

### 3.6 Custom Agents / Skills

测试问题：

- 专家 agent 是否真的改善质量
- skill 是否减少输出漂移
- skill 是过度限制还是释放能力

指标：

- role lift
- skill adherence
- overconstraint failure

## 4. 这样的设计合理吗

总体上合理，因为它遵循三个正确方向：

- 把状态从模型脑子里移到系统里
- 把判断从自我评价移到外部 evaluator / hooks / tests
- 把危险动作放到 permission / sandbox / policy 下

但它也有风险。

### 4.1 风险一：复杂度过高

25+ tools、4 MCP transports、settings chain、hooks、permissions、context manager 都增加调试成本。

更好的设计：

- 默认小工具面
- ToolSearch 延迟加载
- 任务 profile 控制工具暴露
- 只有当 ablation 证明需要时才开启复杂组件

### 4.2 风险二：功能清单掩盖实现深度

项目 ADR-002 也承认，最后 50% 主要是 edge cases、error handling、跨平台兼容和 UX polish。

更好的测试：

- 不只测功能存在
- 必须测 edge cases
- 必须测失败恢复
- 必须测跨平台差异

### 4.3 风险三：上下文压缩可能制造虚假连续性

compaction 会让同一个 agent 继续工作，但压缩质量不好时会丢失关键约束。

更好的设计：

- 对关键状态使用结构化 state file
- 对代码/配置文件重新读取
- 对长任务允许 reset + handoff

### 4.4 风险四：权限系统如果太宽会掩盖模型风险

`bypassPermissions` 对 benchmark 很危险，因为模型可以用过度强力工具掩盖规划和判断问题。

更好的测试：

- 同一任务在 plan / auto / default / bypass 下对比
- 把 permission prompt 看作 benchmark 事件

## 5. 可改进方向

### 5.1 能力路由而不是全量工具暴露

先让模型选择 task profile，再加载对应工具集。

### 5.2 状态机驱动 agent loop

把任务阶段显式化：

- discover
- plan
- act
- verify
- repair
- report

这样比纯递归 tool loop 更容易评估和恢复。

### 5.3 Evaluator 与 verifier 分离

Evaluator 判断质量，verifier 运行事实测试。两者不应混在一起。

### 5.4 Benchmark 内置系统 ablation

每个任务都应有至少两个 harness 版本：

- baseline solo
- structured harness

这样才能回答“系统设计是否释放模型能力”。

## 6. 对我们评测集的直接影响

下一版 benchmark 应新增：

- agent loop continuity tests
- tool surface and ToolSearch tests
- permission mode tests
- hook feedback tests
- compaction/reset/handoff tests
- skill and custom agent tests
- session resume tests
- implementation depth tests

评估对象也应从“模型输出”扩展到“模型在系统中的行为轨迹”。
