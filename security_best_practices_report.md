# Security Best Practices Report

## Executive Summary
This project is explicitly **local-only and single-user**, so most web‑app security risks are not applicable unless the app is exposed to a network or deployed publicly. The only critical issue is **lack of authentication** if the app ever becomes network‑accessible. Development/debug exposure, security headers/CSP, and service‑worker caching are acceptable for local use but should be revisited before any deployment.

---

## Critical Findings

### 1) APP-AUTH-001: No authentication or per-user authorization (all requests map to user_id=1)
- **Severity:** Critical *if exposed* (Accepted for local-only)
- **Location:** `backend/routes/helpers.py:10-12`, `backend/routes/lessons.py:168-335`, `backend/routes/progress.py:137-182`, `backend/routes/vocabulary.py:230-275`, `backend/routes/vocabulary.py:395-443`
- **Evidence:** `get_current_user_id()` returns a constant (`return 1`) and is used by state‑changing routes without auth checks.
- **Impact:** Acceptable for local‑only; if exposed, any caller can read/mutate shared progress data.
- **Fix (if exposed):** Add real authentication and per‑user authorization across all progress/vocabulary routes.
- **Mitigation (if exposed):** Temporarily gate write endpoints with an API key.

---

## High Findings

### 2) FLASK-DEPLOY-002 / FLASK-DEPLOY-001: Development server + debug flag enabled in `__main__`
- **Severity:** High *if exposed* (Acceptable for local-only)
- **Location:** `backend/app.py:196-199`
- **Evidence:** `app.run(debug=True, host="127.0.0.1", port=port)` in `backend/app.py:196-199`.
- **Impact:** Acceptable for local‑only; if exposed, debugger can enable remote code execution.
- **Fix (if exposed):** Use a WSGI server and disable debug in production configs.

---

## Medium Findings

### 3) FLASK-HEADERS-001 / REACT-HEADERS-001 / REACT-CSP-001: Security headers/CSP not visible in repo
- **Severity:** Medium *if exposed* (Not applicable for local-only)
- **Location:** `packages/web/index.html:1-18` (no CSP meta); no server/edge header config in repo
- **Evidence:** `packages/web/index.html` contains no CSP `<meta http-equiv>` and there is no server/edge config in repo.
- **Impact:** Not applicable for local‑only; if exposed, reduced defense‑in‑depth against XSS/clickjacking.
- **Fix (if exposed):** Configure CSP and security headers at the edge.

### 4) FLASK-DEPLOY-002 (Debug endpoints risk if DEBUG is ever enabled in production)
- **Severity:** Medium *if exposed* (Acceptable for local-only)
- **Location:** `backend/app.py:113-118`, `backend/routes/debug.py:24-215`
- **Evidence:** Debug blueprint is registered when `DEBUG` or `TESTING` is true in `backend/app.py:113-118`, exposing diagnostic and cache-manipulation endpoints in `backend/routes/debug.py`.
- **Impact:** Acceptable for local‑only; if exposed, leaks internal cache details and allows cache modification.
- **Fix (if exposed):** Explicitly gate debug endpoints or require auth.

---

## Low Findings

### 5) REACT-SW-001: Service worker caches `/api/*` responses
- **Severity:** Low (can become Medium/High if user-specific data is added or device is shared)
- **Location:** `packages/web/vite.config.js:44-74`
- **Evidence:** Workbox runtime caching uses `NetworkFirst` for `/api/` with a 24-hour cache (`api-cache`) in `packages/web/vite.config.js:62-73`.
- **Impact:** Low for local‑only; if exposed/shared, cached user data could persist on shared devices.
- **Fix (if exposed/shared):** Restrict caching to non‑user data or use `NetworkOnly` for sensitive endpoints.

---

## Notes / Positive Observations
- `SECRET_KEY` is required and validated for length and weak values in `backend/config.py`, which is a strong baseline.
- CORS is restricted to configured origins by default.

---

## Next Steps (Local‑Only)
- No immediate changes required for local‑only usage.
- If you later expose the app, implement authentication and per‑user scoping first.
- Revisit debug gating and CSP/headers prior to any deployment.
