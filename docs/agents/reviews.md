# Kapp Review Checklists

Consolidated review guide for PRs, architecture, security, code quality, and testing.

---

## PR Review Checklist

### Pre-Review
- [ ] Branch follows convention: `feature/*`, `fix/*`, `refactor/*`
- [ ] Conventional commit messages: `feat:`, `fix:`, `refactor:`
- [ ] No merge conflicts, rebased on base branch
- [ ] Only relevant files modified

### Backend (Python)
- [ ] Type hints on all function parameters and return types
- [ ] Uses `app.logger` not `print()`
- [ ] No bare `except:` clauses
- [ ] SQLAlchemy 2.0 syntax (`Mapped[]`, `mapped_column()`)
- [ ] HTTP endpoints return proper status codes (400, 404, 500)
- [ ] No hardcoded secrets or file paths

### Frontend (TypeScript)
- [ ] No `any` types (use `unknown` if needed)
- [ ] Component props typed with Interface
- [ ] Function return types specified
- [ ] No `console.log` in production code
- [ ] CSS Modules used (not inline styles)
- [ ] useEffect has correct dependencies

### Tests
- [ ] Unit tests for new functions
- [ ] Integration tests for API endpoints
- [ ] Tests pass locally

---

## Architecture Checklist

### Single Responsibility
- [ ] Each module has ONE clear purpose
- [ ] Routes handle HTTP, services handle business logic
- [ ] Components don't mix data fetching with display

### Database
- [ ] Primary keys on all tables
- [ ] Foreign keys with cascade rules
- [ ] Indexes on frequently queried columns
- [ ] No N+1 queries (use eager loading)

### API Design
- [ ] RESTful: `GET /api/cards`, not `GET /api/getCards`
- [ ] Consistent response format: `{"cards": [...]}` or `{"error": "..."}`
- [ ] Proper status codes: 200, 201, 400, 404, 500

### Frontend
- [ ] Props for reusable components, hooks for app-specific state
- [ ] No component key that changes on hash change
- [ ] Component-level state (no global store unless needed)

---

## Security Checklist

### Critical (Must Fix)
- [ ] CORS configured with specific origins (not `*`)
- [ ] SECRET_KEY validated (strong, not default, min 32 chars)
- [ ] Rate limiting on expensive operations (LLM, TTS)
- [ ] Port bound to `127.0.0.1` in development (not `0.0.0.0`)

### Input Validation
- [ ] Type validation (is it string/int/list?)
- [ ] Range validation (rating 0-5, positive IDs)
- [ ] SQL injection prevented (use ORM, no string concatenation)
- [ ] Path traversal prevented (`..` and `/` blocked in filenames)

### Error Messages
- [ ] Don't leak system details (DB schema, file paths)
- [ ] Stack traces logged, not returned to user
- [ ] Generic messages to user: "Failed to process request"

### XSS Prevention
- [ ] No `dangerouslySetInnerHTML` without sanitization
- [ ] User data escaped in templates (React does this by default)

### Dependencies
- [ ] Run `pip-audit` for Python vulnerabilities
- [ ] Run `npm audit` for JavaScript vulnerabilities
- [ ] Update vulnerable packages

---

## Code Quality Checklist

### Duplication
- [ ] Error responses use helper: `error_response(msg, code)`
- [ ] Card queries use helper: `get_card_or_error(id)`
- [ ] Audio validation centralized

### Complexity
- [ ] Functions under 50 lines
- [ ] Cyclomatic complexity under 10
- [ ] Early returns instead of deep nesting
- [ ] Magic numbers extracted to constants

### Type Safety
- [ ] Python: Type hints on all functions
- [ ] TypeScript: No `any`, use proper interfaces
- [ ] Error handling with typed exceptions

### Cleanup
- [ ] No unused functions/imports
- [ ] No commented-out code
- [ ] No TODO comments (create issues instead)
- [ ] No `print()` statements (use logging)

---

## Testing Checklist

### Coverage Targets
- [ ] Overall: 70%+
- [ ] Critical paths: 90%+ (input validation, core logic)
- [ ] API endpoints: 80%+

### Backend Tests (pytest)
- [ ] Unit tests for algorithms (e.g., SM-2 if used)
- [ ] Integration tests for API endpoints
- [ ] Edge cases: empty lists, None values, invalid IDs
- [ ] Error cases: 400, 404, 500 responses

### Frontend Tests (Vitest)
- [ ] Component renders correctly
- [ ] User interactions work (click, submit)
- [ ] Error states handled
- [ ] API calls mocked

### Test Quality
- [ ] Descriptive test names: `test_submit_review_invalid_rating`
- [ ] Use fixtures for test setup
- [ ] No test interdependencies
- [ ] No `sleep()` in tests (use `waitFor`)

---

## Common Issues

### Backend
| Issue | Fix |
|-------|-----|
| `print()` statements | Use `app.logger.debug/error()` |
| Missing type hints | Add `def foo(x: int) -> str:` |
| Bare `except:` | Catch specific exceptions |
| N+1 queries | Use `joinedload()` |
| String SQL | Use ORM with parameters |

### Frontend
| Issue | Fix |
|-------|-----|
| `any` types | Use proper interface |
| Missing useEffect deps | Add all dependencies |
| `key={index}` on lists | Use stable identifiers |
| `console.log` | Remove or wrap in `DEV` check |
| Inline styles | Use CSS Modules |

---

## Quick Verification Commands

```bash
# Backend
cd backend
pytest -v                    # Run tests
pytest --cov=. --cov-report=html  # Coverage report
black --check .              # Format check

# Frontend
cd packages/web
npm run lint                 # ESLint
npm run test                 # Run tests
npm run test -- --coverage   # Coverage report

# Security
pip-audit                    # Python vulnerabilities
npm audit                    # JS vulnerabilities
```
