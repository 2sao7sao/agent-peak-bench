# Agent Peak Bench: MiniMax M2.7 High Initial Report

Date: `2026-05-06`

## Name

`Agent Peak Bench`

This name is intentionally model-agnostic. The first published case is MiniMax M2.7 High, but the benchmark is designed to expand to other agentic models.

## Published Assets

- Public report page: [docs/index.html](../docs/index.html)
- Public sanitized summary: [public/minimax-m27-high-summary.json](../public/minimax-m27-high-summary.json)
- Detailed local report: [report/minimax-initial-live-report-2026-05-06.md](./minimax-initial-live-report-2026-05-06.md)

## MiniMax M2.7 High Initial Scores

| Dimension | Score |
| --- | ---: |
| Short memory | 95 |
| Long history noise | 20 |
| Grounded workflow | 35 |
| Tool error honesty | 50 |
| Context window stability | 30 |
| Structured decomposition | 50 |
| Skill adherence | 35 |
| Harness fit | 42 |

Overall live canary:

- `pass@1 = 25%`
- `pass@3 = 50%`
- `8` scenarios
- `3` trials per scenario

## Security

The public report and sanitized JSON do not include API keys, bearer tokens, or raw request credentials.
