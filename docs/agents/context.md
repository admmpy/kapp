# Kapp AI Agent Context

## Project Overview
**Kapp** - Korean language learning app with structured lessons (LingoDeer-style).
- **Target:** TOPIK I level learners
- **Features:** Lessons with exercises, OpenAI LLM explanations, TTS pronunciation

## Tech Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Backend | Flask 3.0 | Application factory pattern |
| ORM | SQLAlchemy 2.0 | Modern `Mapped[]` syntax |
| Database | SQLite | Single-user, file-based |
| Frontend | React 18 + TypeScript | Vite, CSS Modules |
| Routing | Hash-based | `/#lesson/42` not react-router |
| State | Component-level | No Redux/Zustand |
| LLM | OpenAI API (GPT-4o mini) | Server-side only |
| TTS | gTTS | Cached in `data/audio_cache/` |

## Architecture Constraints

### Single-User Design
- No authentication system
- SQLite sufficient for personal use
- Adding auth would be breaking change

### LLM Integration
- OpenAI API for LLM (requires API key)
- Keep API key server-side only

### Hash Routing
- Uses `window.location.hash` intentionally
- Simpler deployment, no server config needed

## DON'T Suggest

| Don't Suggest | Reason |
|---------------|--------|
| React Router | Hash routing is intentional |
| PostgreSQL | Requires auth system first |
| Exposing API keys to frontend | Security risk |
| Docker | Complicates local setup |
| WebSockets | REST is sufficient |
| Authentication | Breaking change, out of scope |
| Tailwind CSS | Using CSS Modules |
| Redux/Zustand | Component state is sufficient |

## Coding Conventions

### Python Backend
- Type hints required on all functions
- Use `app.logger` not `print()`
- SQLAlchemy 2.0 syntax: `Mapped[]`, `mapped_column()`
- No bare `except:` clauses

### TypeScript Frontend
- No `any` types (use `unknown` if needed)
- Interface for component props
- Explicit return types on functions
- No console.log in production

### Git
- Conventional commits: `feat:`, `fix:`, `refactor:`
- Branch naming: `feature/*`, `fix/*`, `refactor/*`
- Rebase before merging

## Environment Variables

### Backend (.env)
```bash
DATABASE_URL=sqlite:///./data/kapp.db
SECRET_KEY=<generate-strong-random-key>
CORS_ORIGINS=http://localhost:5173
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
LLM_ENABLED=true
GRAMMAR_MASTERY_ENABLED=false
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:5001
VITE_PRONUNCIATION_SELF_CHECK_ENABLED=false
VITE_SPEAKING_FIRST_ENABLED=false
VITE_GRAMMAR_MASTERY_ENABLED=false
```

### Feature Flags

| Flag | Layer | Default | Purpose |
|------|-------|---------|---------|
| `VITE_PRONUNCIATION_SELF_CHECK_ENABLED` | Frontend | `false` | Show self-rating after audio playback |
| `VITE_SPEAKING_FIRST_ENABLED` | Frontend | `false` | Reorder exercises: audio-based first |
| `VITE_GRAMMAR_MASTERY_ENABLED` | Frontend | `false` | Show mastery pill + weakest patterns UI |
| `GRAMMAR_MASTERY_ENABLED` | Backend | `false` | Track grammar pattern mastery in DB |

### Data Models (Grammar Mastery)

When `GRAMMAR_MASTERY_ENABLED=true`, two new tables are used:
- **`grammar_pattern`** — patterns linked to lessons (key, title, pattern, meaning, examples)
- **`grammar_mastery`** — per-user mastery tracking (attempts, correct, mastery_score)

Exercises can link to a grammar pattern via `grammar_pattern_id`. The import script resolves `grammar_pattern_key` from lesson JSON to the FK.

## Quick Reference

| Aspect | Decision |
|--------|----------|
| Backend | Flask 3.0, application factory |
| Frontend | React 18 + TypeScript |
| Database | SQLite (single-user) |
| Styling | CSS Modules |
| LLM | OpenAI API (GPT-4o mini) |
| TTS | gTTS (cached) |
| Auth | None (single-user) |
| State | Component-level |
