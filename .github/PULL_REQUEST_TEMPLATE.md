<!--
ALCA PR template. Keep it short and concrete. The reviewer wants a clear
what/why, evidence it was tested, and an honest note on risk.
-->

## Summary

One paragraph on what this PR does and why.

## What changed

- File-level bullet list. Be specific.

## Verification

What you ran and what passed:

- [ ] `python -m pytest` (backend) passes
- [ ] `npm run build` (frontend) succeeds
- [ ] Manual smoke test at `http://localhost:3000` (if frontend touched)
- [ ] OpenAPI docs at `http://localhost:8000/docs` reflect any endpoint change

## Risk

What could break? Cross-user/-org data exposure, upload validation, prompt/rubric behavior change, dependency footprint, migration impact. If "none," say so explicitly.

## Rollback plan

If this lands and something is wrong, what's the revert path? `git revert <sha>` is fine for most PRs; DB migrations or data backfills need a real plan.
