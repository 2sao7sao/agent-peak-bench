# Roadmap

Agent Peak Bench should become a business-to-benchmark system, not a generic
leaderboard.

## Phase 1: Credible OSS Kit

- Business-goal YAML profiles.
- Suite skeleton generator.
- CI for distribution checks and suite generation.
- Clear README, contribution guide, security policy, and issue templates.
- Pilot MiniMax case study with explicit confidence labels.

## Phase 2: Multi-Model Evidence

- Run at least three model providers on the same business profiles.
- Add r30 calibration cells for selected business goals.
- Publish model comparison cards with pass@k, CI95, tool metrics, latency, and failure clusters.
- Add dashboard-ready summary JSON.

## Phase 3: Business Cookbook Engine

- Generate deployment cookbooks from benchmark results.
- Recommend single-agent vs multi-agent topology.
- Recommend memory, RAG, MCP router, skills, verifier, and approval gates.
- Export model-vendor feedback packs with minimal reproducible failures.

## Phase 4: Production-Like Canaries

- Add sanitized live-adapter fixtures.
- Track tool latency, permission errors, context drift, and retry cost.
- Support periodic regression campaigns across model versions.

## Non-Goals

- Do not become a single-number leaderboard.
- Do not claim production readiness from smoke tests.
- Do not publish private traces or provider secrets.
