# Agent Peak Bench

<p align="center">
  <strong>面向 Agent 落地的 harness-first 模型评测：从真实任务、失败归因到工程设计和模型使用指南。</strong>
</p>

<p align="center">
  <a href="https://2sao7sao.github.io/agent-peak-bench/"><img alt="在线报告" src="https://img.shields.io/badge/report-live-0f766e?style=for-the-badge"></a>
  <a href="./report/agent-peak-bench-integrated-report.zh-CN.md"><img alt="综合报告" src="https://img.shields.io/badge/report-integrated-111827?style=for-the-badge"></a>
  <a href="./evals/benchmark_manifest_v2.json"><img alt="Benchmark Manifest" src="https://img.shields.io/badge/benchmark-v3.0-2563eb?style=for-the-badge"></a>
  <img alt="无密钥发布" src="https://img.shields.io/badge/secrets-not_published-b91c1c?style=for-the-badge">
</p>

<p align="center">
  <a href="./README.md">English</a>
  ·
  <a href="./report/agent-peak-bench-integrated-report.zh-CN.md">综合报告</a>
  ·
  <a href="./docs/evaluation-samples.zh-CN.md">评估样本</a>
  ·
  <a href="https://2sao7sao.github.io/agent-peak-bench/">在线页面</a>
</p>

## 项目定位

Agent Peak Bench 不做单一排行榜分数。它要回答的是：

> 一个模型在真实 Agent 场景里，什么时候能稳定完成任务，什么时候需要 harness、router、skills、MCP 分层、verifier 或人工审批才能安全落地？

本仓库的主入口是 [Agent Peak Bench 综合报告](./report/agent-peak-bench-integrated-report.zh-CN.md)。所有评估结论、方法论、OpenClaw 复杂任务方向、工具/skills/MCP 归因、MiniMax M2.7 High 使用指南，都统一收敛到这份报告中。

早期 smoke/canary 只用于验证评测 runner 和接口链路，不作为 README 的模型能力结论。

## 主评测集

| Suite | 目的 | 评估重点 |
| --- | --- | --- |
| [`enterprise_agent_landing_v3.json`](./evals/suites/enterprise_agent_landing_v3.json) | 企业级 Agent 端到端任务 | 潜台词理解、企业资料查询、多 MCP 工具调用、权限治理、复杂需求拆解、长任务恢复。 |
| [`tool_skill_mcp_ablation_v3.json`](./evals/suites/tool_skill_mcp_ablation_v3.json) | 工具/skills/MCP 工程归因 | 3 工具直连、14 工具平铺、router 分层、procedural skill 对稳定性的影响。 |
| [`openclaw_complex_agent_tasks_v1.json`](./evals/suites/openclaw_complex_agent_tasks_v1.json) | OpenClaw 风格复杂任务 | personal OS、语音生产修复、异步 GitHub、多 Agent 运营、插件治理、长期记忆安全。 |

## 评估闭环

```mermaid
flowchart LR
  A["真实任务设计"] --> B["子能力观测"]
  B --> C["端到端完成率"]
  C --> D["pass@k 稳定性"]
  D --> E["失败归因"]
  E --> F["Harness 设计"]
  F --> G["模型使用指南"]
```

## 关键问题

| 问题 | 对应评测 |
| --- | --- |
| 模型能否理解用户潜台词，而不是只按显式指令答题？ | 企业安全评审、续约风险、业务分析场景。 |
| 最多可以挂多少工具才稳定？ | 3 工具直连 vs 14 工具平铺 vs router 分层 ablation。 |
| MCP / skills 如何设计更稳？ | `tool_skill_mcp_ablation_v3`。 |
| 复杂系统该如何拆解？ | 企业知识 Agent 架构、multi-agent handoff、OpenClaw personal OS。 |
| 长期运行和 memory 是否安全？ | OpenClaw persistent workspace memory / prompt injection 场景。 |
| pass@1 低但 pass@7 高时怎么办？ | 引入 retry、verifier、repair loop、权限 gate，而不是直接 autonomous execution。 |

## 运行方式

```bash
export MINIMAX_API_KEY="your_key"
export MINIMAX_MODEL="MiniMax-M2.7-highspeed"
export MINIMAX_API_BASE="https://api.minimaxi.com/anthropic/v1/messages"
```

运行三组主评测：

```bash
python3 scripts/run_minimax_evals.py \
  --suite evals/suites/enterprise_agent_landing_v3.json \
  --pass-k 1,3,5,7 \
  --out results/minimax-enterprise-agent-v3.json

python3 scripts/run_minimax_evals.py \
  --suite evals/suites/tool_skill_mcp_ablation_v3.json \
  --pass-k 1,3,5,7 \
  --out results/minimax-tool-skill-mcp-ablation-v3.json

python3 scripts/run_minimax_evals.py \
  --suite evals/suites/openclaw_complex_agent_tasks_v1.json \
  --pass-k 1,3,5,7 \
  --out results/minimax-openclaw-complex-v1.json
```

检查任务分布：

```bash
python3 scripts/check_benchmark_distribution.py
```

## 仓库结构

| 路径 | 作用 |
| --- | --- |
| [`report/agent-peak-bench-integrated-report.zh-CN.md`](./report/agent-peak-bench-integrated-report.zh-CN.md) | 唯一主综合报告。 |
| [`docs/evaluation-samples.zh-CN.md`](./docs/evaluation-samples.zh-CN.md) | 真实样本与判分逻辑示例。 |
| [`evals/suites/`](./evals/suites) | 评测 suite。 |
| [`scripts/run_minimax_evals.py`](./scripts/run_minimax_evals.py) | MiniMax 评测执行器。 |
| [`scripts/summarize_eval_results.py`](./scripts/summarize_eval_results.py) | 结果摘要脚本。 |
| [`scripts/check_benchmark_distribution.py`](./scripts/check_benchmark_distribution.py) | 任务分布检查。 |

## 安全边界

- 不要把 API key 写入 README、suite、结果文件或命令历史。
- `results/` 是本地结果目录，已被 gitignore。
- 对外只发布脱敏 summary、聚合指标、failure taxonomy 和工程建议。
- 原始工具返回、私有 trace、凭证、token、cookie 不应发布。
