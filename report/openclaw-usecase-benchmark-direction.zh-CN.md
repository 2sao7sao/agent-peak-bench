# OpenClaw 使用场景调研与复杂任务评测方向

本报告把公开 OpenClaw 使用方式转化为 Agent Peak Bench 的复杂任务评测方向。目标不是评测 OpenClaw 本身，而是利用 OpenClaw 暴露出的真实 agent 使用形态，反推模型在复杂 agent harness 中应被测试的能力。

## 1. 公开使用形态

公开资料显示，OpenClaw 被描述为一个通用 AI agent runtime：支持长期运行、通过自然语言操作多种工具、管理 workspace、skills、sessions、steering 和 hook 等机制。官方文档强调 workspace、bootstrap files、内置工具、skills、sessions、steering、hooks 等运行时能力；官方首页展示了与 Gmail、Calendar、Slack、GitHub、Linear、Notion、Figma、Discord 等工具协作的定位。

社区/生态文章中，OpenClaw 常被包装为“个人 Chief of Staff / personal OS / 多 Agent 团队 / 异步开发助手 / 自动化运营助手”。这些描述有营销成分，但它们很好地暴露了真实用户希望 agent 处理的复杂任务类型：跨 App、跨时间、跨权限、跨工具，以及从模糊意图到行动闭环。

参考来源：

- [OpenClaw Docs](https://docs.openclaw.dev)
- [OpenClaw runtime concepts: workspace, skills, sessions, steering, hooks](https://docs.openclaw.dev)
- [OpenClaw official site](https://openclaw.ai)
- [OpenClaw use cases list](https://openclaw.rocks/blog/openclaw-use-cases)
- [RemoteOpenClaw use-case analysis](https://www.remoteopenclaw.com/posts/openclaw-use-cases-analysis)
- [OpenClaw CIK safety analysis](https://arxiv.org/abs/2604.04759)
- [OpenClaw PRISM runtime security layer](https://arxiv.org/abs/2603.11853)

## 2. 可转化为复杂评测的方向

| OpenClaw 使用形态 | 复杂任务评测方向 | 核心能力 |
| --- | --- | --- |
| Personal Chief of Staff | 个人操作系统：邮件、日历、Slack、任务、CRM 综合决策 | 潜台词理解、跨 App 证据、优先级排序、行动闭环 |
| Voice / mobile-driven automation | 语音触发生产修复：模糊口语、时间压力、代码/CI/部署工具 | 口语意图恢复、工具调用、发布安全、状态汇报 |
| Async coding assistant | 异步 GitHub backlog：issue triage、代码搜索、测试、PR 计划 | repo 理解、风险分级、可执行验证、长任务规划 |
| Multi-agent teams | 多 Agent 电商运营：库存、客服、广告、物流、内容协作 | 角色分工、handoff、冲突解决、集成决策 |
| Skill / plugin ecosystem | skills 与插件治理：选择、安装、权限、安全、最小工具面 | skill 选择、供应链风险、权限分层、工具路由 |
| Always-on workspace memory | 长期记忆与安全：跨 session resume、prompt injection、敏感信息 | state reconstruction、context reset、policy gate、安全拒绝 |

## 3. 为什么适合作为复杂任务 benchmark

OpenClaw 风格任务比普通问答更适合测试 agent 落地，原因是：

| 特征 | 对模型的压力 |
| --- | --- |
| 用户输入更模糊 | 用户说“帮我搞定明早的客户会”，不是列 checklist。 |
| 工具面更大 | 同时出现 Gmail、Calendar、Slack、GitHub、Linear、Notion、Figma 等工具。 |
| 状态持续存在 | agent 需要从 workspace/memory/session 恢复上下文。 |
| 行动有副作用 | 发邮件、改代码、建 PR、改日历、创建任务都需要权限控制。 |
| 安全风险真实 | workspace agent 持有大量上下文和工具权限，容易受到 prompt injection 或过度授权影响。 |
| 结果必须可用 | 不是“解释一下”，而是输出可交付计划、草稿、PR 路线、审批动作或多 Agent handoff。 |

## 4. 新增评测集

新增 suite：

[`evals/suites/openclaw_complex_agent_tasks_v1.json`](../evals/suites/openclaw_complex_agent_tasks_v1.json)

该 suite 包含 6 个复杂任务：

| 场景 | 真实映射 | 主要检查 |
| --- | --- | --- |
| `openclaw-chief-of-staff-morning-brief` | 个人 Chief of Staff / personal OS | 邮件、日历、Slack、CRM、任务综合；输出 priorities/actions/risks。 |
| `openclaw-voice-prod-fix-commute` | 语音触发生产修复 | 口语需求恢复、CI/log/repo/deploy 工具链、禁止危险发布。 |
| `openclaw-async-github-backlog` | 异步 coding agent | issue triage、代码搜索、测试状态、PR 分解、风险控制。 |
| `openclaw-multi-agent-ecommerce-ops` | 多 Agent 电商运营 | 内容/客服/库存/广告/物流角色拆分和 handoff。 |
| `openclaw-skill-plugin-governance` | skills/插件生态治理 | 最小 skill 集、权限审批、供应链风险、拒绝不可信插件。 |
| `openclaw-memory-security-resume` | 持久记忆与安全 | session resume、敏感信息保护、prompt injection 识别。 |

## 5. 评估方式

每个样本默认 `repeat=7`，用于有效计算：

- `pass@1`
- `pass@3`
- `pass@5`
- `pass@7`
- exact output consistency
- tool precision / redundancy
- failure taxonomy

判分逻辑不是只看关键词，而是组合检查：

| 检查 | 用途 |
| --- | --- |
| `required_tool_names` | 必须使用关键系统。 |
| `required_tool_name_groups` | 允许等价工具，但必须覆盖某类证据。 |
| `forbidden_tool_names` | 防止危险副作用，例如直接 deploy、直接安装不可信插件。 |
| `max_tool_calls` | 检查工具面是否导致冗余调用。 |
| `json_key_contains` | 确认证据和决策进入指定结构字段。 |
| `must_not_contain` | 禁止危险或过度自信结论。 |

## 6. 可以回答的工程问题

这个方向可以帮助回答：

| 工程问题 | 通过什么测试 |
| --- | --- |
| 模型是否适合个人操作系统类 agent？ | morning brief 场景，看跨 App 综合与行动排序。 |
| 语音/移动端模糊命令是否会失控？ | prod fix 场景，看是否先验证而不是直接发布。 |
| coding agent 是否能异步推进 backlog？ | GitHub backlog 场景，看 issue triage、代码证据和测试计划。 |
| multi-agent 是否只是角色扮演？ | ecommerce ops 场景，看 handoff artifact 和冲突解决。 |
| skills/插件到底怎么挂更稳？ | governance 场景，看最小 skill 集、权限和供应链控制。 |
| 长期 memory 会不会带来安全问题？ | resume/security 场景，看 secret handling 和 injection 抵抗。 |

## 7. 运行方式

```bash
python3 scripts/run_minimax_evals.py \
  --suite evals/suites/openclaw_complex_agent_tasks_v1.json \
  --pass-k 1,3,5,7 \
  --out results/minimax-openclaw-complex-v1.json
```

## 8. 结论

把 OpenClaw 用作复杂任务来源是合理的，但要避免“复刻 OpenClaw 宣传样例”。正确做法是提取它背后的真实 agent 压力：跨 App、长时程、工具副作用、权限、memory、skills、multi-agent handoff。这样设计出来的评测更接近企业和个人生产环境，也更容易反推模型最佳使用方式。
