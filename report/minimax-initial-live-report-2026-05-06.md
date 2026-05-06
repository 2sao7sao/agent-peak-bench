# MiniMax 初步 Live Benchmark 报告

日期：`2026-05-06`  
模型：`MiniMax-M2.7-highspeed`  
测试接口：`https://api.minimaxi.com/anthropic/v1/messages`

## 1. 背景

这份报告不是基于旧的 `smoke/ablation suites` 直接下结论，而是在做了三件事之后形成的：

1. 先审查现有框架为何不能算真实 benchmark  
   见：[benchmark-framework-review.md](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/report/benchmark-framework-review.md)

2. 先盘点公开 benchmark 的方法论，再抽取更合理的设计原则  
   见：[benchmark-landscape-analysis.md](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/report/benchmark-landscape-analysis.md)

3. 构建一套小而硬的 `canary benchmark` 做第一轮 live test  
   见：[minimax_canary_v1.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/evals/suites/minimax_canary_v1.json)

## 2. 对 benchmark 设计的先验结论

从 `Terminal-Bench`、`τ-bench`、`GAIA`、`BrowseComp`、`WorkArena`、`OSWorld`、`ReliabilityBench`、`CLEAR`、`UNDERWRITE` 这些 benchmark 看，比较一致的结论是：

- 不能只看单次成功率
- 不能只看格式或短答案
- 需要 `pass@k`
- 需要真实任务或至少接近真实 workflow
- 需要 end-state / executable / semantic validator
- 需要看 latency、cost、reliability，而不是 accuracy-only

对我们这次 MiniMax 初测，真正影响设计的 benchmark 原则主要来自：

- `τ-bench`：多轮、tool、policy、pass^k
- `Terminal-Bench`：真实环境 + 自动验证
- `ReliabilityBench`：重复执行、扰动、故障注入
- `CLEAR`：成本/时延/可靠性一起看
- MiniMax 官方 `Agent Generalization`：benchmark 好不代表真实任务就好，必须对全链路扰动稳定

## 3. 这次 live 测试实际怎么做的

### 3.1 任务族

`minimax_canary_v1` 一共 `8` 个场景，分为五类：

- `chat_memory`
- `workflow`
- `context`
- `decomposition`
- `skills`

### 3.2 评测维度

每题重复 `3` 次，采集：

- `pass@1`
- `pass@3`
- `exact_output_consistency`
- `avg_total_latency_ms`
- `tool sequence / tool presence`

### 3.3 两轮运行

第一轮直接跑，结果几乎全灭。检查后发现主要不是能力结论，而是 harness 校准问题：

- 你的 key 对应的是中国区 endpoint，国际区 `api.minimax.io` 返回 `401 invalid api key`
- MiniMax 默认会输出较长 `thinking`，若 `max_tokens` 太小，容易只返回 thinking 而没有最终 text

因此做了第二轮校准：

- 切换到 `https://api.minimaxi.com/anthropic`
- 提高 `max_tokens`
- 让 JSON 解析器接受 ```json code fences

第二轮结果才具备参考意义。

## 4. 第二轮校准后的结果

结果文件：

- [results/minimax-canary-v1-live-calibrated.json](/Users/caogang02/Documents/Codex/2026-05-06/github-https-www-cdn-anthropic-com/results/minimax-canary-v1-live-calibrated.json)

总体指标：

- `total_scenarios = 8`
- `pass_rate = 0.25`
- `pass@1 = 0.25`
- `pass@3 = 0.5`

按类别聚合：

| Category | Scenario Count | Avg Pass Rate | Avg Consistency | Avg Latency |
| --- | ---: | ---: | ---: | ---: |
| chat_memory | 2 | `0.50` | `0.50` | `5050.99 ms` |
| context | 2 | `0.167` | `0.167` | `4677.10 ms` |
| decomposition | 1 | `0.333` | `0.333` | `8246.76 ms` |
| skills | 1 | `0.0` | `0.333` | `11810.68 ms` |
| workflow | 2 | `0.167` | `0.333` | `10273.50 ms` |

按场景看：

| Scenario | Pass Rate | Pass@3 | Consistency | Avg Latency |
| --- | ---: | ---: | ---: | ---: |
| canary-chat-memory | `1.0` | `true` | `1.0` | `3111.06 ms` |
| canary-history-noise | `0.0` | `false` | `0.0` | `6990.92 ms` |
| canary-grounded-workflow | `0.0` | `false` | `0.333` | `12834.15 ms` |
| canary-tool-error-honesty | `0.333` | `true` | `0.333` | `7712.84 ms` |
| canary-window-compact | `0.333` | `true` | `0.333` | `4594.99 ms` |
| canary-window-expanded | `0.0` | `false` | `0.0` | `4759.20 ms` |
| canary-structured-decomposition | `0.333` | `true` | `0.333` | `8246.76 ms` |
| canary-structured-skill | `0.0` | `false` | `0.333` | `11810.68 ms` |

## 5. 初步解读

### 5.1 明显成立的结论

#### A. MiniMax 的短程结构化记忆表现很好

`canary-chat-memory` 的 `pass_rate=1.0`，而且三次输出完全一致。

这说明在：

- 历史长度可控
- 输出 schema 明确
- 任务目标简单

的情况下，MiniMax-M2.7-highspeed 的记忆型 chatbot 行为是稳的。

#### B. 更小的工作窗口明显更稳

`canary-window-compact = 0.333`，`canary-window-expanded = 0.0`。

虽然样本量还小，但方向性已经很清楚：

- 同一任务在更大噪声上下文下更容易失稳
- “窗口越大越好”这件事对 MiniMax 不成立

这与 MiniMax 官方关于单窗口容量边界和 multi-window workflow 的建议一致。

#### C. 工具错误场景下，模型有一定 honest behavior，但不稳定

`canary-tool-error-honesty` 的 `pass@3=true`，说明它并非完全不会处理工具错误。  
但 `pass@1=0.333`，而且部分 trial 会直接给出“resolved”之类过度乐观结论。

这意味着：

- 模型能识别一部分缺失证据
- 但在工具报错时，仍存在“过早下结论”的风险

### 5.2 暂时不应高估的能力

#### A. 长历史噪声下的记忆提炼还不稳

`canary-history-noise = 0.0`。

而且从第一轮与第二轮看，这里不仅是 correctness 问题，也存在明显的：

- thinking 占用输出预算
- 长上下文后输出纪律下降

这说明 MiniMax 如果被拿来做长对话 memory agent：

- 需要更强的 memory extraction 中间层
- 不能只依赖原始 history

#### B. grounded workflow 的“语义上经常对，结构上不稳定”

`canary-grounded-workflow = 0.0`，但人工看 trial 文本，会发现它经常已经抓住了：

- `clock drift`
- `ntp disabled`
- `webhook_replay_test not_run`
- 不能直接恢复上线

也就是说：

- 语义判断常常是对的
- 但 tool 顺序、JSON 纪律、输出格式稳定性不够

这类能力对企业落地很危险，因为它会让人误以为“模型会做”，但实际上 orchestration 层会因为格式和稳定性问题频繁断掉。

#### C. 结构化 skill prompt 能帮助质量，但不能直接保证稳定输出

`canary-structured-skill = 0.0`。

不是说模型完全答不好，而是：

- 它能遵循一部分章节标题
- 但不保证完整覆盖 `Root Cause / Evidence / Action / Verification`
- latency 明显升高，平均 `11.8s`

这说明 skill 本身不能只写“你应该分四段输出”，还需要：

- 更硬的 schema
- 更短的职责边界
- 更明确的 stop condition

### 5.3 Structured decomposition 有潜力，但也不稳定

`canary-structured-decomposition = 0.333`，而通过的 trial 质量其实不错。

这意味着：

- MiniMax 对“把复杂任务拆成 scope/metrics/workflow/risks”这种结构是吃得进去的
- 但重复三次后仍会出现两次失稳

所以对复杂任务更稳的用法不是“让模型自己每次重新组织”，而是：

- 把 decomposition 变成固定 workflow
- 用外部状态机承接阶段切换

## 6. 从这次 live run 得出的 MiniMax 初步使用建议

### 更适合的场景

- 中短历史的 chatbot
- 明确 schema 的结构化问答
- 有外部状态文件和验证层的简单 workflow
- 先拆阶段、再逐步推进的复杂任务

### 风险更大的场景

- 长 history 噪声很重的 memory agent
- 工具错误后不能容忍过早结论的高风险场景
- 需要严格稳定 JSON/固定 tool 顺序的弱编排系统
- 只靠 prompt/skill 不靠 verifier 的生产链路

### 现阶段最实用的工程建议

1. `中国区 key 用中国区 endpoint`
否则会直接 401。

2. `给足 max_tokens`
MiniMax 的 thinking 很容易吃掉输出预算。

3. `把完整 assistant response 回填 history`
尤其是 tool-use 场景。

4. `技能要更硬，不要只写风格`
要写 Goal / Inputs / Output / Stop Condition。

5. `窗口宁可小一点`
优先多窗口或阶段化，不要默认堆长上下文。

6. `workflow 场景必须接 verifier`
因为模型语义上常常“差不多对”，但格式/顺序/收尾不稳。

## 7. 这份报告的边界

这份报告仍然只是 `initial live canary report`，不是 production-grade benchmark 结论。

它的价值在于：

- 已经不是纯离线猜测
- 已经跑了真实 API
- 已经暴露出 MiniMax 在真实 harness 里的几个关键工程特征

它还不能代表：

- 企业级最终能力上限
- coding / office / browser / multi-agent 全面能力
- 生产环境中的长期可靠性

## 8. 下一步最值得做什么

如果要继续推进，我建议下一轮不是盲目加题，而是做三件事：

1. `做 v2 canary`
加入 semantic validators，而不只依赖 JSON 和字符串。

2. `做 perturbation layer`
对同一任务加 prompt、tool、environment 扰动。

3. `做真实 workflow benchmark`
选 3 到 5 个真实场景：
chatbot、tool workflow、coding/CLI、multi-agent coordination，各做可执行 validator。
