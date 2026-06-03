# Contributing to ALCA

Thanks for your interest. This document covers local setup, branching, and the pull-request workflow.

## Local setup

```bash
git clone https://github.com/drdgreed/adult-learning-coach-showcase.git
cd adult-learning-coach-showcase

# Backend
cd backend
python -m venv venv
source venv/bin/activate                   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                        # add DATABASE_URL, API keys, SECRET_KEY

# Frontend
cd ../frontend && npm install && cd ..
```

You need a local PostgreSQL 15+, an [AssemblyAI](https://www.assemblyai.com/) key, and an [Anthropic](https://console.anthropic.com/) key. Never commit `.env` or any real key — see [SECURITY.md](SECURITY.md).

## Running the system

```bash
# Backend (terminal 1)
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend (terminal 2)
cd frontend && npm start
```

Backend + interactive Swagger docs at `http://localhost:8000/docs`; frontend at `http://localhost:3000`.

## Tests

```bash
# Backend integration suite (61 tests against a real PostgreSQL instance)
cd backend && python -m pytest

# Frontend
cd frontend && npm test
```

A change must keep the backend suite green and the frontend type-checking (`npm run build` must succeed). The backend tests use real PostgreSQL fixtures, so a local database is required to run them.

## Branching

- Branch from `main`.
- Use a descriptive prefix: `feat/`, `fix/`, `docs/`, `refactor/`, `test/`, `chore/`.
- Example: `feat/instructor-trend-export`, `fix/upload-mime-validation`.

## Commits

- Imperative mood, present tense: "Add comparison PDF export" not "Added".
- One logical change per commit when feasible.
- Reference issues with `Refs #123` or `Closes #123`.

## Pull requests

Before opening a PR:

1. Rebase on the latest `main`.
2. Run the backend tests and confirm the frontend builds.
3. Update the README or relevant docs if behavior changed.

Then open the PR using the template. Reviewers look for a clear *what* and *why*, evidence the change was tested, and a note on any user-visible behavior change.

## Code style

- **Python:** type hints on public functions; keep services pure and routers thin. Format with Ruff/Black conventions if configured.
- **TypeScript / React:** functional components with hooks, no class components; data fetching through React Query; API calls go through `src/api/client.ts`, not inline in components.
- **Naming:** modules in `snake_case`, classes in `PascalCase`, constants `UPPER_SNAKE_CASE`.

## Reporting issues

Use the templates under `.github/ISSUE_TEMPLATE/`. For security issues, follow [SECURITY.md](SECURITY.md) — do not open a public issue.

## Code of Conduct

By contributing, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).
