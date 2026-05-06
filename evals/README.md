# Evals Layering

这个目录现在被明确分成三类资产。主评测结论统一进入 [`report/agent-peak-bench-integrated-report.zh-CN.md`](../report/agent-peak-bench-integrated-report.zh-CN.md)，不要分散写多个互相割裂的结论文件。

## 1. 主评测 suites

主评测集：

- [`suites/enterprise_agent_landing_v3.json`](./suites/enterprise_agent_landing_v3.json)
- [`suites/tool_skill_mcp_ablation_v3.json`](./suites/tool_skill_mcp_ablation_v3.json)
- [`suites/openclaw_complex_agent_tasks_v1.json`](./suites/openclaw_complex_agent_tasks_v1.json)

这些 suite 用于形成模型落地结论：端到端能力、工具稳定性、OpenClaw 风格复杂任务、失败归因和工程设计建议。

## 2. 辅助 probes / ablations

其他 suite 主要用于局部归因或机制验证，例如 prompt、skill、tool、window、context、multi-agent handoff 的局部对比。它们可以支持主报告，但不应单独作为模型能力结论。

## 3. Smoke tests

`minimax_canary_v1.json` 只应视为 smoke test，用于验证 API、基础格式、工具调用、JSON 解析和 pass@k 聚合链路。它不应作为 README 或综合报告中的模型落地能力结论。

## 4. `blueprints/`

这里用于存放 benchmark 设计蓝图。

一个 blueprint 至少应定义：

- task family
- environment shape
- validator type
- perturbation protocol
- pass@k setup
- latency/cost collection
- failure taxonomy

## 建议的评测层级

1. `Smoke`
测试接口、基础格式、最小稳定性。

2. `Ablation`
比较 skill 写法、工具数量、窗口大小、任务拆解方式。

3. `Benchmark`
在真实环境、真实 validator 下测任务完成率与可靠性。

4. `Deployment Canaries`
用真实 API、真实工具、真实 traces 做小规模线上回归。

## v3: 主评测说明

`enterprise_agent_landing_v3` 面向端到端企业任务：安全评审、续约风险、发布 gate、权限治理、业务分析、复杂系统设计、多 Agent handoff、长任务 resume。

`tool_skill_mcp_ablation_v3` 面向工程归因：比较 3 工具直连、14 工具平铺、router 分层、procedural skill + tools 的稳定性差异。

`openclaw_complex_agent_tasks_v1` 面向 OpenClaw 风格复杂任务：personal OS、语音触发生产修复、异步 GitHub backlog、多 Agent 电商运营、skills/插件治理、持久 workspace memory 与安全。

推荐运行：

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

运行结果应先用 `scripts/summarize_eval_results.py` 汇总，再统一写入综合报告，不要拆成多个独立结论文档。

## 模型无关配置

优先使用通用环境变量：

```bash
export MODEL_API_KEY="your_key"
export MODEL_NAME="target-model-name"
export MODEL_API_BASE="https://provider.example.com/anthropic/v1/messages"
```

`MINIMAX_*` 变量仍可作为兼容别名，但不应作为新文档的主配置方式。
