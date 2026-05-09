# Benchmark Source Cache

This directory stores lightweight source artifacts used to design Agent Peak Bench.

The raw files under `raw/` are downloaded public README or evaluation-guide files from
benchmark repositories. Large PDFs, Docker images, Hugging Face datasets, and private
benchmark examples are intentionally not committed here. The goal is traceability for
methodology design, not redistributing third-party datasets.

## Source Groups

| Source | Local artifact | What we reuse |
| --- | --- | --- |
| AgentBench | `raw/agentbench_readme.md` | Multi-environment agent evaluation and failure taxonomy framing. |
| WebArena | `raw/webarena_readme.md` | Realistic web environments and functional task success checks. |
| SWE-bench | `raw/swebench_readme.md` | Repository issue tasks and executable test-patch validation. |
| tau-bench | `raw/tau_bench_readme.md` | Tool-agent-user interaction, policy constraints, and pass^k reliability. |
| OSWorld | `raw/osworld_readme.md` | Real computer-use tasks and execution-based graders. |
| WorkArena | `raw/workarena_readme.md` | Enterprise web tasks and knowledge-worker workflows. |
| TheAgentCompany | `raw/the_agent_company_readme.md` | Simulated company tasks, multi-application work, and subcheckpoint grading. |
| Terminal-Bench | `raw/terminal_bench_readme.md` | Sandbox terminal tasks with verification scripts. |
| PaperBench | `raw/paperbench_readme.md` | Hierarchical rubrics and judge calibration for long-horizon work. |
| BrowseComp / simple-evals | `raw/simple_evals_readme.md` | Browsing-agent evaluation pattern; do not expose dataset examples. |
| BFCL | `raw/bfcl_readme.md` | Function/tool calling categories and AST/API-style validation. |

## Use Policy

- Use downloaded files to learn benchmark structure, not to copy hidden test cases.
- Do not publish BrowseComp examples or ground-truth answers.
- Do not commit large benchmark datasets or third-party binary artifacts.
- For business-goal suites, create new synthetic-but-realistic scenarios with explicit mock tools, expected outputs, failure taxonomy, and harness hypotheses.
