# Security Policy

Agent Peak Bench may run model APIs and tool simulations. Keep secrets and raw
private traces out of the repository.

## Do Not Commit

- API keys, tokens, cookies, SSH credentials, or provider config with secrets.
- Raw model traces containing private data.
- Real customer documents, tickets, emails, CRM exports, or logs.
- Live tool results that have not been sanitized.

## Safe Publishing Pattern

Publish aggregate metrics, sanitized failure clusters, synthetic fixtures, and
engineering guidance. Keep raw traces and provider credentials local.

## Reporting

Open a GitHub issue for non-sensitive security hardening suggestions. For
sensitive vulnerabilities, contact the repository owner privately instead of
posting exploit details publicly.
