# PR: Attempt-First Challenge Gate + English Attempt Check

## Summary
- Added `POST /api/exercises/{id}/attempt-check` for attempt-first evaluation with semantic (LLM) + deterministic fallback behavior.
- Implemented explicit right/wrong/unscored attempt feedback in the exercise UI.
- Enforced a 2-strikes scaffold:
  - first miss -> micro-hint + retry,
  - second miss -> force options path and mark assist usage.
- Expanded attempt-first gating to all option-based exercises with English attempt input.

## Scope
- In scope:
  - backend attempt-check endpoint and validation,
  - shared core API/types for attempt-check contract,
  - frontend attempt-first UX state machine and feedback visuals,
  - targeted tests and flow verification.
- Out of scope:
  - broad lesson content migration,
  - auth model changes,
  - replacing submit/scoring contracts.

## API / Contract Changes
- Added `POST /api/exercises/{id}/attempt-check`
  - required: `attempt` (string), `attempt_number` (1|2), `used_hint` (boolean)
  - returns:
    - `status`: `correct|wrong|unscored`
    - `method`: `llm_semantic|exact_fallback|unscored`
    - `micro_hint`
    - `feedback`
    - `challenge_state`: `attempts_used`, `can_retry`, `force_options`

## Risks and Tradeoffs
- Semantic check quality depends on LLM availability/quality when enabled.
- Fallback exact matching is deterministic but less flexible.
- UI state complexity increased to support challenge loop, offset by explicit guard states and tests.

## Rollback Plan
- Revert attempt-check endpoint and frontend attempt-first async state to prior unlock-only behavior.
- Keep existing `/submit` flow intact (unchanged) as stable fallback.

## Verification Evidence
- Commands run:
  - `cd backend && pytest -q tests/test_training_enhancements.py tests/test_settings.py`
  - `npm --workspace packages/web run lint`
  - `npm run web:build`
- Results:
  - backend targeted tests passing (`40 passed`),
  - web lint passing with one pre-existing warning in `SentenceArrangeExercise.tsx`,
  - web build passing.

## Playwright MCP Validation (if UI/API flow changed)
- Flows tested:
  - lesson attempt-first wrong attempt then retry,
  - second wrong attempt forces options,
  - correct attempt shows explicit positive feedback and unlocks options,
  - backend `attempt-check` network calls and console health.
- Outcomes:
  - correct/wrong feedback surfaced inline as expected,
  - micro-hint shown after first miss,
  - options forced after second miss,
  - no blocking console errors; changed-flow API calls returned 200.

## Screenshots / Artifacts
- Playwright MCP snapshots and network traces captured in session.

## Review Outcomes
- Security review: no new Critical or High findings for this delta.
- Architecture review: no Critical findings; medium residual risk documented around LLM availability variance.

## Template Note
- Repository `.github/pull_request_template.md` was not present in this checkout; this PR body follows `docs/prs/PR_TEMPLATE.md` sections.
