# PR: Korean Learning Speed Plan (Top 3)

## Summary
- Enabled adaptive learning loops by default with explicit `false` opt-out semantics.
- Upgraded sentence SRS quality capture through `/api/exercises/:id/submit` optional `quality` and `peeked` fields.
- Rebalanced production practice via lesson ordering, attempt-first exercise flow, and pilot content updates.
- Added local recommendations archive support and enforced ignore behavior.
- Added project workflow + PR/review documentation standards.

## Scope
- In scope:
  - feature flag default behavior,
  - submit contract and SRS quality logic,
  - review UX changes,
  - production-first exercise flow and pilot lessons,
  - docs workflow and PR/review artifacts.
- Out of scope:
  - new model providers,
  - major infra changes,
  - broad curriculum expansion outside pilot block.

## API / Contract Changes
- `POST /api/exercises/{id}/submit`
  - required: `answer`
  - optional: `quality` (0-5), `peeked` (boolean)
- `POST /api/exercises/{id}/review` retained for backward compatibility.

## Risks and Tradeoffs
- Review UI now depends on explicit quality action; improves signal but adds one step.
- Attempt-first flow may increase friction for beginners; mitigated by hint path.
- Pilot lesson conversion biases toward production; monitored via completion rate and retention.

## Rollback Plan
- Set adaptive-related env flags to `false`.
- Continue using legacy `/api/exercises/{id}/review` path if needed.
- Revert pilot lesson content files to previous revision.

## Verification Evidence
- Commands run:
  - `cd backend && pytest -q tests/test_training_enhancements.py tests/test_settings.py`
  - `npm --workspace packages/web run lint`
  - `npm run web:build`
- Results:
  - backend targeted tests passing,
  - web lint passing (existing non-blocking warning in `SentenceArrangeExercise.tsx`),
  - web build passing.

## Playwright MCP Validation
- Flows tested:
  - dashboard adaptive loops visibility,
  - lesson attempt-first gate behavior,
  - vocabulary review peek penalty behavior,
  - exercise review quality gating and submit flow.
- Outcomes:
  - quality selection gate verified (Next/Finish disabled until explicit selection),
  - attempt-first and hint assist paths verified,
  - vocabulary high-quality ratings blocked after reveal path,
  - review flow completes and posts submit path.

## Screenshots / Artifacts
- Playwright snapshots and network traces captured in MCP session.
