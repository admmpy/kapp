# Kapp - Development Gotchas & Lessons Learned

This document captures common issues, security lessons, and development patterns discovered during the project.

## Security Issues

### SECRET_KEY Vulnerabilities (CRITICAL)

**Problem:** Hardcoded default SECRET_KEY in config.py was easily discoverable.

```python
# BAD - Don't do this!
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
```

**Solution:**
1. Never provide a default SECRET_KEY
2. Validate key strength at startup (min 32 chars)
3. Reject known weak/placeholder values
4. Provide `.env.example` with generation instructions

```python
# GOOD - Require proper key
SECRET_KEY = os.getenv('SECRET_KEY')
WEAK_SECRET_KEYS = {'changeme', 'secret', None, ''}

def init_app(app):
    if app.config['SECRET_KEY'] in WEAK_SECRET_KEYS:
        raise ValueError("SECRET_KEY is missing or weak!")
```

### Prompt Injection Vulnerabilities

**Problem:** User input directly inserted into LLM prompts without sanitization.

```python
# BAD - Direct user input to LLM
prompt = f"User says: {user_message}"
```

**Solution:** Create a security module with sanitization:

1. Limit input length (500 chars max)
2. Detect injection patterns ("ignore previous instructions")
3. Validate conversation history structure
4. Log suspicious patterns but don't expose details to user

```python
# GOOD - Sanitize before use
from security import sanitize_user_input
message, warnings = sanitize_user_input(raw_message)
```

## Database Issues

### SQLite Path Detection

**Problem:** Relative SQLite paths caused issues on Windows vs Unix.

```python
# BAD - Inconsistent path handling
db_url = 'sqlite:///data/kapp.db'  # Relative path varies by OS
```

**Solution:** Convert to absolute path at startup:

```python
# GOOD - Absolute path handling
if db_url.startswith('sqlite:///') and not is_absolute:
    db_path = basedir / db_url.replace('sqlite:///', '')
    DATABASE_URL = f"sqlite:///{db_path.as_posix()}"
```

### Migration Risks

**Problem:** Database migrations can lose data if not handled carefully.

**Solutions:**
1. Always backup before migration
2. Export data to JSON as secondary backup
3. Test migration on copy first
4. Provide clear rollback instructions

## Frontend Issues

### Hardcoded API URLs

**Problem:** API URLs hardcoded in components break when ports change.

```typescript
// BAD - Hardcoded URL
fetch('http://localhost:5001/api/cards')
```

**Solution:** Use environment variables and centralized client:

```typescript
// GOOD - Environment-based URL
const API_BASE_URL = import.meta.env.VITE_API_URL || '';
```

### Re-render Performance

**Problem:** Unnecessary re-renders when API data changes.

**Solutions:**
1. Use React.memo for expensive components
2. Memoize callbacks with useCallback
3. Use key prop strategically to control remounts

### Absolute Position Overflow

**Problem:** Progress bar gradient escapes container, covering large portion of screen.

**Symptom:** Large purple gradient appears on landing page (not just hover).

**Cause:** CSS cascade conflict - `.progress-fill` inherited `position: absolute` from ProgressBar.css while its parent `.progress-bar` in CourseList.css had `position: static`.

**Key CSS Rule:** `overflow: hidden` does NOT clip `position: absolute` children unless the parent has `position: relative/absolute/fixed`.

**Fix:** Always add `position: relative` to containers with `overflow: hidden` that have absolutely-positioned children.

## Content Structure

### Example Sentence Format

**Problem:** Inconsistent example sentence format in vocabulary.

**Solution:** Standardize format:
```json
{
  "korean": "안녕하세요",
  "romanization": "annyeonghaseyo",
  "english": "hello",
  "example_sentence_korean": "안녕하세요, 만나서 반갑습니다.",
  "example_sentence_english": "Hello, nice to meet you."
}
```

## Development Workflow

### Branch Workflow

**Rule:** NEVER make changes directly on main. Always create a new branch before starting work.

```bash
# Good - create feature branch first
git checkout main && git pull
git checkout -b feature/my-changes

# Bad - making changes on main
git checkout main
# ... making edits (DON'T DO THIS)
```

### .gitignore Essentials

Always include:
```
.env
.env.local
*.db
__pycache__/
node_modules/
```

### Virtual Environments

**Problem:** Package conflicts between projects.

**Solution:**
```bash
# Create isolated environment
python -m venv venv
source venv/bin/activate  # Unix
.\venv\Scripts\activate   # Windows
```

## Testing & Validation

### Input Validation Patterns

Always validate:
1. Type checking (is it a string/int/list?)
2. Length limits (prevent DoS)
3. Format validation (regex for patterns)
4. Sanitization (strip dangerous content)

```python
def validate_level(level, default=0) -> int:
    """Validate and clamp level to valid range"""
    if not isinstance(level, int):
        try:
            level = int(level)
        except (TypeError, ValueError):
            return default
    return max(0, min(5, level))
```

## AI Code Generation

### Review Checklist for AI-Generated Code

When reviewing AI-generated code, check:

1. **Security**
   - [ ] No hardcoded secrets
   - [ ] Input validation present
   - [ ] SQL injection protection (use ORM)
   - [ ] XSS protection (escape output)

2. **Error Handling**
   - [ ] Exceptions are caught and handled
   - [ ] Error messages don't expose internals
   - [ ] Rollback on database errors

3. **Performance**
   - [ ] N+1 query prevention
   - [ ] Appropriate pagination
   - [ ] Caching where beneficial

4. **Maintainability**
   - [ ] Clear variable names
   - [ ] Functions do one thing
   - [ ] Comments explain "why" not "what"

## Architecture Decisions

### v2.0 Migration: Flashcards → Lessons

**Why:** LingoDeer-style structured learning is more effective than flashcard drilling.

**Trade-offs:**
- Lost: Spaced repetition algorithm (SM-2)
- Gained: Grammar explanations, structured progression
- Data: Old reviews exported to JSON for reference

**Lesson learned:** Get clear requirements before building. The flashcard approach was over-engineered for the actual need.

## Common Debugging

### CORS Issues

**Symptom:** "Access-Control-Allow-Origin" errors in browser console.

**Fix:** Check `CORS_ORIGINS` in config includes frontend URL:
```python
CORS_ORIGINS = 'http://localhost:5173,http://localhost:5174'
```

### Database Locked (SQLite)

**Symptom:** "database is locked" errors under load.

**Fixes:**
1. Use connection pooling with short timeouts
2. Wrap writes in transactions
3. Consider PostgreSQL for production

### Audio Playback Fails

**Symptom:** Audio files don't play in exercises.

**Check:**
1. Audio file exists in `data/audio_cache/`
2. File permissions allow read
3. CORS allows audio endpoint
4. File is valid MP3 format
