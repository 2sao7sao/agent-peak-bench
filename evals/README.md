# Evals Layering

这个目录现在被明确分成两类资产：

## 1. `suites/`

这里的内容目前主要是：

- smoke tests
- prompt/workflow probes
- ablation experiments

它们的用途是：

- 找方向
- 验证接口
- 比较 prompt、skill、tool、window 配置

它们的用途不是：

- 充当真实 benchmark 分数
- 代表企业级任务完成能力
- 作为模型 leaderboard

## 2. `blueprints/`

这里用于存放未来的真实 benchmark 设计蓝图。

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

## v3: 企业级 Agent 主评测

当前更接近真实落地的主评测集是：

- [`suites/enterprise_agent_landing_v3.json`](./suites/enterprise_agent_landing_v3.json)
- [`suites/tool_skill_mcp_ablation_v3.json`](./suites/tool_skill_mcp_ablation_v3.json)

`enterprise_agent_landing_v3` 面向端到端企业任务：安全评审、续约风险、发布 gate、权限治理、业务分析、复杂系统设计、多 Agent handoff、长任务 resume。

`tool_skill_mcp_ablation_v3` 面向工程归因：比较 3 工具直连、14 工具平铺、router 分层、procedural skill + tools 的稳定性差异。

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
```

`minimax_canary_v1.json` 现在只应视为 smoke test，不应作为模型落地能力结论。
