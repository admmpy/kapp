# Architecture Review: Korean Learning Speed Plan (Top 3)

## Context
- Goal: improve Korean learning speed by enabling adaptive loops, improving SRS signal quality, and increasing production-oriented practice.
- Constraints: no major infra/model changes; preserve backward compatibility for clients.

## Change Design
- Configuration defaults moved to opt-out model (`'false'` disables).
- Sentence-SRS signal collected on `submit` endpoint via optional quality signal.
- Review UI changed to require explicit quality selection after reveal.
- Vocabulary reveal path marked low-confidence using peek handling.
- Lesson flow guarantees early production task and includes attempt-first gate.

## Boundaries and Contracts
- API boundary updated at `POST /api/exercises/{id}/submit` with optional `quality` and `peeked`.
- Legacy review endpoint preserved (`POST /api/exercises/{id}/review`).
- Shared TypeScript client/types updated to reflect new submit contract.

## Failure Modes / Edge Cases
- Invalid quality values rejected (non-int or outside 0-5).
- Missing quality falls back to deterministic legacy behavior.
- Peeked path caps effective quality for confidence integrity.
- Review progression blocked until explicit quality choice.

## Security Review Notes
- No secrets introduced.
- Input validation added for new fields at backend boundary.
- Legacy endpoint retained to avoid breaking older clients.

## Testing Strategy
- Backend tests:
  - quality validation and fallback,
  - peek penalty application,
  - existing training enhancement regression.
- Frontend verification:
  - build + lint,
  - Playwright MCP interaction tests for changed user journeys.

## Residual Risk
- UX friction increase from added explicit rating step.
- Content rebalance may affect completion time in pilot lessons.
- Mitigation: monitor completion and retention metrics before expansion.

## Decision
- Approved with follow-up monitoring on pilot lesson performance metrics.
