# Security Policy

## Scope of this policy

ALCA is published as an **evaluation and portfolio artifact**, not a production service. It is designed to run against **synthetic instructor data only** — no real learner or employee recordings, transcripts, or PII are stored in or distributed with this repository.

That said, several classes of vulnerability are relevant to this project and we want to hear about them.

## In scope

We welcome reports about:

- **Authentication and authorization** — once Phase 2 RBAC lands: token handling, session management, privilege escalation, cross-user data access.
- **Data exposure paths** — any code path that could leak a video, transcript, evaluation, or report across user or organization boundaries.
- **Input handling** — injection (SQL, prompt injection that bypasses the analysis rubric, command injection), unsafe file handling on upload, SSRF.
- **File upload** — bypass of format/size validation, path traversal, or content that could compromise the host.
- **Dependency vulnerabilities** — CVEs in dependencies that affect this codebase as deployed.
- **CI / supply-chain** — workflow misconfigurations exploitable via PRs from forks.
- **LLM-specific issues** — prompt injection that leaks the system prompt, fabricates transcript citations, or causes the model to score around the rubric.

## Out of scope

- Anything requiring a real learner-data set (none exists in this repo).
- Theoretical issues without a demonstrated exploit path.
- Self-XSS or social-engineering scenarios that require user cooperation.
- Automated scanner output without manual verification.
- Issues in third-party services (Anthropic, AssemblyAI, hosting providers) — report those to the relevant vendor.

## How to report

**Email:** drdgreed@gmail.com

Please include:

1. A clear description of the vulnerability.
2. The minimum reproduction steps.
3. The impact you believe it has.
4. Any suggested mitigation.

If your finding involves a working exploit, include it as a private gist or attached file rather than a public link.

## Response commitment

- **Acknowledgment** within 5 business days of receipt.
- **Initial assessment** within 14 days.
- **Remediation timeline** communicated after assessment, prioritized by severity.

## Responsible disclosure

Please give a reasonable opportunity to address an issue before public disclosure. Reporters are credited in release notes unless they prefer to remain anonymous.

## Production deployment

This repository is not certified for processing real learner or employee data. Anyone deploying ALCA in a setting that handles real recordings is responsible for: a data-processing agreement with the LLM and transcription providers, a compliant hosting environment, authentication and role-based access control, retention and deletion policies, audit logging, and any regulatory obligations (FERPA, GDPR, or sector-specific rules) applicable to the deployment jurisdiction.
