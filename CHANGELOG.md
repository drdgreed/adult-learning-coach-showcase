# Changelog

All notable changes to ALCA are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added — Portfolio packaging
- Recruiter-first `README.md`: problem framing, rendered architecture diagram, provenance-labeled results table, demo scenarios, and an About-the-Author section.
- Rendered architecture diagram at [`docs/assets/architecture.svg`](docs/assets/architecture.svg), with Mermaid source embedded in the README.
- Repository hygiene files: `LICENSE` (MIT), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, this changelog, issue/PR templates, and a GitHub Actions CI workflow.

### Changed
- `README` license section changed from "Private repository, all rights reserved" to MIT.
- Corrected clone URL and stack details (React 19, not 18) in documentation.

---

## [2.0.0] — 2026-05 — Prompt refresh

### Changed
- **Coaching-analysis prompts reworked (v2).** The standalone reflection-worksheet content was merged into the main coaching report; the separate `worksheet/pdf` endpoint and frontend download were removed as redundant.

### Added
- **Multi-video comparison** — select 2–10 completed evaluations and run a cross-session analysis (`personal_performance`, `class_delivery`, `program_evaluation`). Comparisons analyze evaluation *reports*, not raw transcripts, to stay within token budget.
- Aggregated comparison metrics: averages, min/max ranges, and directional trend detection (5% threshold, first-to-last session).

---

## [1.0.0] — 2026-04 — MVP pipeline

### Added
- **End-to-end coaching pipeline** — video upload (MP4/MOV/WebM/AVI, ≤10 GB) → AssemblyAI transcription with speaker diarization and timestamps → Claude four-dimension analysis (Clarity & Pacing, Engagement, Explanation Quality, Time Management) → ReportLab PDF report.
- **Evidence standard** — every observation cites a transcript timestamp; every metric shows its calculation.
- **Instructor dashboard** — evaluation history and per-metric trend charts (React 19 + MUI + React Query).
- **Async FastAPI backend** on PostgreSQL (SQLAlchemy 2.0, JSONB metric payloads); local-filesystem storage with an optional S3 path.
- **61 integration tests** against real PostgreSQL fixtures.

### Notes
This codebase is a portfolio and evaluation artifact — not a production service, ships with synthetic data only. See [`SECURITY.md`](SECURITY.md) for production-deployment obligations.
