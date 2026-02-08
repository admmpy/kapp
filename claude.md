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

### Grammar Pattern Data
- `korean_lessons.json` may contain `grammar_patterns` arrays on lessons and `grammar_pattern_key` on exercises
- Import script (`scripts/import_lessons.py`) resolves keys to FK IDs
- New tables: `grammar_pattern`, `grammar_mastery` (behind `GRAMMAR_MASTERY_ENABLED` flag)

## Frontend

### Feature Flags
All training-enhancement features are behind env-var flags:
- `VITE_PRONUNCIATION_SELF_CHECK_ENABLED` — pronunciation self-rating after audio (default: disabled)
- `VITE_SPEAKING_FIRST_ENABLED` — reorder exercises, audio first (default: **enabled**; set `false` to disable)
- `VITE_GRAMMAR_MASTERY_ENABLED` — mastery pill + weakest patterns UI (default: disabled; requires backend `GRAMMAR_MASTERY_ENABLED`)
- `VITE_WEAKNESS_REVIEW_ENABLED` — weakness-driven review for grammar & vocabulary (default: disabled; requires backend `WEAKNESS_REVIEW_ENABLED`)
- `VITE_SENTENCE_SRS_ENABLED` — sentence-level spaced repetition for exercises (default: disabled; requires backend `SENTENCE_SRS_ENABLED`)
- `VITE_IMMERSION_MODE_ENABLED` — controlled immersion: hide romanization/English (default: disabled; requires backend `IMMERSION_MODE_ENABLED`)

### API URLs
- Use environment variables: `import.meta.env.VITE_API_URL`
- Never hardcode `localhost:5001`

### CSS Positioning (Critical)
- `overflow: hidden` does NOT clip `position: absolute` children unless parent has `position: relative/absolute/fixed`
- Always add `position: relative` to containers with `overflow: hidden` that have absolutely-positioned children

### Bottom Nav & Safe Areas
- Z-index layering: bottom nav `1000` < offline banner `9999` < iOS install prompt `10000`
- `.app.has-bottom-nav` sets `--bottom-nav-height: calc(56px + env(safe-area-inset-bottom, 0px))`
- Full-viewport components (e.g. ConversationView) must use `height: calc(100vh - var(--bottom-nav-height, 0px))` to avoid content hidden behind the nav
- Use `env(safe-area-inset-top)` / `env(safe-area-inset-bottom)` with `viewport-fit=cover` for iPhone notch/home indicator

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

### Lint Hygiene (Recent Fixes)
- Avoid `any` in TSX; use a targeted type extension instead:
  - Example: `const nav = navigator as Navigator & { standalone?: boolean };`
- For hooks, keep dependency arrays correct:
  - Wrap async functions in `useCallback` and include them in `useEffect` deps.
  - For memoized values, include only true inputs (avoid unnecessary deps).

### Theme / Dark Mode
**Initializing from localStorage — avoid FOUC:**
Always read persisted preferences synchronously via a lazy initializer, never in a `useEffect` (which runs after paint):
```typescript
// GOOD — no flash
const [theme, setTheme] = useState<Theme>(() => {
  const stored = localStorage.getItem('theme');
  if (stored === 'light' || stored === 'dark') return stored;
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
});

// BAD — causes flash of wrong theme
const [theme, setTheme] = useState<Theme>('light');
useEffect(() => { setTheme(readFromStorage()); }, []);
```

### useCallback with Object Props
**Never put object/array props directly in `useCallback`/`useMemo` dependency arrays** — they are new references every render, defeating memoization. Use a ref instead:
```typescript
const ctxRef = useRef(userContext);
ctxRef.current = userContext;

const doFetch = useCallback(async () => {
  await api.call(id, ctxRef.current); // stable callback, fresh value at call-time
}, [id]);
```

### useMemo Dependency Stability
**For `useMemo` that should only recompute on identity changes (e.g., shuffling tiles), use a stable primitive key like `entity.id`, not the array/object itself:**
```typescript
// GOOD — reshuffles only when exercise changes
useMemo(() => shuffle(tiles), [exercise.id]);

// BAD — reshuffles on every parent re-render (new array reference)
useMemo(() => shuffle(tiles), [tiles]);
```

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

## Parallel Subagent Coordination

### Merge Order Strategy
When multiple agents work in parallel on feature branches, merge in this order:
1. **Infrastructure changes first** (PWA, build configs, dependencies)
2. **Core data/content second** (lessons, vocabulary JSON)
3. **Feature-dependent changes third** (components using new data)
4. **Polish/enhancement last** (dashboard, analytics)

### Common Conflict Files
| File | Conflict Type | Resolution |
|------|---------------|------------|
| `korean_lessons.json` | Multiple agents add lessons | Combine all units/lessons, verify unique IDs |
| `korean_vocab.json` | Multiple vocabulary additions | Merge all entries, dedupe by korean text |
| `types.ts` | Type additions | Combine all new types |
| `client.ts` | API method additions | Combine all methods, add missing imports |
| `vite.config.*` | `.ts` vs `.js` conflicts | Keep ONE format, update tsconfig references |

### TypeScript Build Issues After Merge

**vite.config.ts vs .js conflict:**
```bash
# If both exist, keep .js and update references:
rm packages/web/vite.config.ts
# Edit tsconfig.json to remove tsconfig.node.json reference
```

**Missing type imports:**
```typescript
// Add missing imports to client.ts:
import type { VocabularyDueResponse, VocabularyReviewResponse } from '../types';
```

**Unused variable errors:**
```typescript
// Either use the variable or prefix with underscore:
const [_stats, setStats] = useState({});  // Prefix if intentionally unused
// OR use it in JSX:
{stats.newItems > 0 && <span>New: {stats.newItems}</span>}
```

### Sync Conflict Files
If using file sync (Syncthing, Dropbox), clean up before building:
```bash
find . -name "*sync-conflict*" -type f -delete
```

### Post-Merge Verification
```bash
# 1. Reset to origin
git fetch origin && git reset --hard origin/main

# 2. Clean sync conflicts
find . -name "*sync-conflict*" -delete

# 3. Verify build
npm run web:build

# 4. Verify backend
cd backend && python -c "from models_v2 import *; print('OK')"
```
