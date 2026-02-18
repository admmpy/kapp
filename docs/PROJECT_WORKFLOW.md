# Kapp Project Workflow

This workflow is mandatory for project implementation streams.

## Source of Truth
- `/Users/am/.codex/CODEX_ENGINEERING_STANDARDS.md`
- `/Users/am/.codex/CODEX_ENGINEERING_GUIDE.md`
- `/Users/am/.codex/CODEX_SECURITY_GUIDE.md`
- `/Users/am/.codex/CODEX_NEW_PROJECT_BOOTSTRAP.md`
- `AGENTS.md`
- `docs/agents/reviews.md`

## 1) Branch Rules
- Never implement on `main`.
- Start every stream from `main` on a short-lived branch:
  - `feat/*`, `fix/*`, `chore/*`, `docs/*`
- Use Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`.

## 2) Delivery Loop (Per Slice)
1. Implement a minimal, scoped change.
2. Run Tier A checks:
   - `cd backend && pytest`
   - `npm --workspace packages/web run lint`
   - `npm run web:build`
3. Run Playwright MCP smoke tests for changed user flows.
4. Update PR docs artifacts with verification evidence.
5. Commit and continue.

## 3) Required PR Docs
For non-trivial changes, both files are required:
- `docs/prs/<topic>-pr.md`
- `docs/reviews/<topic>-architecture-review.md`

PR docs must include:
- behavior summary,
- risks/tradeoffs,
- rollback approach,
- concrete verification evidence (commands + results),
- Playwright MCP validation notes for UI-affecting changes.

## 4) Playwright MCP Requirement
Run Playwright MCP when UI or API behavior changes affect user-facing workflows.
Minimum expected coverage:
- navigation to changed surface,
- primary success path,
- at least one guarded/edge interaction,
- no blocking console/network errors for changed flow.

## 5) Security Baseline
- No secrets in code or frontend bundles.
- Validate untrusted inputs at backend boundaries.
- Keep server-side authorization assumptions explicit.
- Record critical/high security findings before merge.

## 6) Merge Readiness
Before opening or updating PR:
- branch rebased or synced with `main`,
- Tier A checks pass,
- Playwright MCP pass noted,
- required docs in `docs/prs` and `docs/reviews` updated.
