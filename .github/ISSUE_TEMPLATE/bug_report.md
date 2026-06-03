---
name: Bug report
about: Report a defect in ALCA's behavior
title: "[BUG] "
labels: bug
assignees: ''
---

## What is wrong

A clear, one-paragraph description of the actual behavior and the expected behavior.

## Reproduction

Minimum steps to reproduce. If the bug is in analysis, include the (synthetic) transcript or the evaluation/comparison payload. If it is in the API or frontend, include the request/response or the browser action.

```
1. ...
2. ...
3. ...
```

## Component

Which part of the system is affected (check all that apply):

- [ ] Video upload / validation
- [ ] Transcription (AssemblyAI integration)
- [ ] Analysis (Claude, four-dimension rubric)
- [ ] Comparison (cross-session analysis)
- [ ] PDF generation (ReportLab)
- [ ] FastAPI backend / data layer
- [ ] React frontend / dashboard
- [ ] CI / build
- [ ] Documentation

## Environment

- ALCA commit SHA: `<git rev-parse --short HEAD>`
- Python version: `3.x.x`
- Node version: `x.x.x`
- OS: `<macOS / Linux / Windows>`
- Claude model in `.env`: `<claude-sonnet-4-… / etc.>`

## Logs / output

Paste relevant backend logs, browser console, or pytest output. Use synthetic data only — never paste a real recording, transcript, or name.

```
<paste here>
```

## Severity (your assessment)

- [ ] **P0** — data exposure across users/orgs, fabricated transcript citation, or upload that compromises the host
- [ ] **P1** — broken CI, broken Quick Start, or a major UX regression
- [ ] **P2** — visible but workaroundable defect
- [ ] **P3** — cosmetic / docs-only

## Suspected cause (optional)

If you've already traced this, name the file/line. Otherwise leave blank.
