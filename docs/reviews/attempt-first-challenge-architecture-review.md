# Architecture Review: Attempt-First Challenge Loop

## Context
- Goal: strengthen learning pressure and scaffold quality in attempt-first flow.
- Scope: new attempt-check boundary, frontend challenge state machine, and fallback behavior under LLM-unavailable conditions.

## Severity-Ranked Findings
1) **No Critical findings**
   - **Severity:** Critical
   - **Status:** None identified.

2) **AR-MED-001: New runtime dependency edge on LLM availability**
   - **Severity:** Medium
   - **Location:** `backend/routes/lessons.py:138`, `backend/routes/lessons.py:160`, `backend/routes/lessons.py:603`
   - **Issue:** Semantic grading behavior varies with `LLM_ENABLED` and model/network availability.
   - **Mitigation:** Deterministic exact fallback + `unscored` outcome keeps flow non-blocking.
   - **Tradeoff:** Better semantic flexibility when available vs. deterministic but narrower grading when unavailable.

3) **AR-LOW-002: Frontend challenge state is now multi-step and async**
   - **Severity:** Low
   - **Location:** `packages/web/src/components/ExerciseRenderer.tsx:32`, `packages/web/src/components/ExerciseRenderer.tsx:86`
   - **Issue:** Additional async states (`checkingAttempt`, `attemptLocked`, `attemptNumber`) increase UI complexity.
   - **Mitigation:** Explicit state transitions and disabled-action guards prevent double submits/races.
   - **Tradeoff:** Higher implementation complexity for materially improved pedagogy and feedback clarity.

## Boundaries and Contracts
- Added API boundary:
  - `POST /api/exercises/{id}/attempt-check`
  - Request: `attempt`, `attempt_number`, `used_hint`
  - Response: `status`, `method`, `micro_hint`, `feedback`, `challenge_state`
- Existing `POST /api/exercises/{id}/submit` contract unchanged.

## Data/State Ownership
- Backend owns attempt evaluation and scaffold progression flags.
- Frontend owns local interaction state and rendering decisions.
- SRS confidence penalty continues to flow through existing `peeked`/assist path at submit time.

## Failure Modes
- LLM timeout/error: fallback exact compare or `unscored` path.
- Missing English target: explicit `unscored` response, no hard failure.
- Client retries/race-clicks: guarded by `checkingAttempt` and button disable logic.

## Verification
- `cd backend && pytest -q tests/test_training_enhancements.py tests/test_settings.py` -> pass
- `npm --workspace packages/web run lint` -> pass with one pre-existing warning
- `npm run web:build` -> pass
- Playwright MCP:
  - wrong attempt -> feedback + micro-hint + retry
  - second miss -> force options
  - correct attempt -> explicit positive feedback before options confirm
  - no blocking console/network errors on changed flow

## Decision
- Approved for merge with no critical blockers.
