# Kapp - Development Guidelines

## Security Rules

### SECRET_KEY (CRITICAL)
- Never provide default SECRET_KEY
- Validate key strength at startup (min 32 chars)
- Reject known weak values (`changeme`, `secret`, empty)
- Generate with: `python -c 'import secrets; print(secrets.token_hex(32))'`

### Prompt Injection
- Limit input length (500 chars max)
- Detect injection patterns ("ignore previous instructions")
- Validate conversation history structure
- Log suspicious patterns, don't expose details to user

### Input Validation
- Type check (string/int/list)
- Length limits (prevent DoS)
- Format validation (regex)
- Sanitization (strip dangerous content)

## Database

### SQLite Paths
- Convert relative paths to absolute at startup
- Use `pathlib` for cross-platform compatibility

### Migrations
- Always backup before migration
- Export data to JSON as secondary backup
- Test migration on copy first

## Frontend

### API URLs
- Use environment variables: `import.meta.env.VITE_API_URL`
- Never hardcode `localhost:5001`

### CSS Positioning (Critical)
- `overflow: hidden` does NOT clip `position: absolute` children unless parent has `position: relative/absolute/fixed`
- Always add `position: relative` to containers with `overflow: hidden` that have absolutely-positioned children

### React State Patterns
**Exercise State Pollution Fix:**
When one state change should trigger another, use `useEffect` with dependencies:
```typescript
useEffect(() => {
  setLastResult(null);
}, [currentExerciseIndex]);
```
Don't call multiple state setters sequentially for dependent state.

**Duplicate Rendering:**
- Never render feedback in both parent (LessonView) and child (ExerciseRenderer)
- Choose ONE location for result feedback

### Performance
- Use `React.memo` for expensive components
- Memoize callbacks with `useCallback`
- Use `key` prop strategically to control remounts

## Git Workflow

### Branch Rule
NEVER make changes directly on main. Always create feature branch first.

### .gitignore Essentials
```
.env
.env.local
*.db
__pycache__/
node_modules/
```

## Debugging

### CORS Issues
Check `CORS_ORIGINS` in config includes frontend URL.

### Database Locked (SQLite)
- Use connection pooling with short timeouts
- Wrap writes in transactions
- Consider PostgreSQL for production

### Audio Playback Fails
1. Audio file exists in `data/audio_cache/`
2. File permissions allow read
3. CORS allows audio endpoint
4. File is valid MP3 format

## AI Code Review Checklist

### Security
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] SQL injection protection (use ORM)
- [ ] XSS protection (escape output)

### Error Handling
- [ ] Exceptions caught and handled
- [ ] Error messages don't expose internals
- [ ] Rollback on database errors

### Performance
- [ ] N+1 query prevention
- [ ] Appropriate pagination
- [ ] Caching where beneficial

### Maintainability
- [ ] Clear variable names
- [ ] Functions do one thing
- [ ] Comments explain "why" not "what"
