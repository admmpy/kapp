# Kapp Architecture

## Overview
Korean language learning app with monorepo structure enabling 95% code reuse between web and mobile.

**Stats:** 67KB lessons JSON + 185 MP3s (2.3MB) + SQLite progress DB

## Monorepo Structure
```
kapp/
├── packages/
│   ├── core/           # Shared types, API client, config
│   ├── web/            # React app (Vite)
│   └── content/        # Lesson data (JSON + audio)
├── backend/            # Flask API
└── package.json        # npm workspaces
```

## @kapp/core API Client

| Method | Description |
|--------|-------------|
| `getCourses()` | List all courses |
| `getCourse(id)` | Get course with units |
| `getLesson(id)` | Get lesson with exercises |
| `submitExercise(id, answer)` | Submit answer |
| `completeLesson(id, data)` | Mark lesson complete |
| `getProgress()` | Get overall progress |
| `sendConversationMessage(text, context)` | LLM chat |

## Component Routing (Hash-based)

| Route | Component |
|-------|-----------|
| `#` | CourseList |
| `#course/1` | UnitView |
| `#lesson/42` | LessonView |
| `#conversation` | ConversationView |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/courses` | List courses |
| GET | `/api/courses/{id}` | Course with units |
| GET | `/api/lessons/{id}` | Lesson with exercises |
| POST | `/api/lessons/{id}/start` | Start lesson |
| POST | `/api/lessons/{id}/complete` | Complete lesson |
| POST | `/api/exercises/{id}/submit` | Submit answer |
| GET | `/api/progress` | Overall progress |
| GET | `/api/llm/health` | LLM available? |
| POST | `/api/llm/conversation` | Chat with AI |

## Environment Config

### Frontend (.env)
| Variable | Example |
|----------|---------|
| `VITE_API_URL` | `http://localhost:5001` |

### Backend (.env)
| Variable | Example |
|----------|---------|
| `FLASK_ENV` | `development` |
| `DATABASE_URL` | `sqlite:///data/kapp.db` |
| `CORS_ORIGINS` | `http://localhost:5173` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` |

## Quick Start

**Terminal 1 (Backend):**
```bash
cd backend && source venv/bin/activate && python app.py
```

**Terminal 2 (Frontend):**
```bash
npm run web
```

## npm Commands

| Command | Description |
|---------|-------------|
| `npm install` | Install all packages |
| `npm run web` | Dev server on :5173 |
| `npm run web:build` | Production build |

## Adding New Features

**New API endpoint:**
1. Create route in `backend/routes/`
2. Add method to `packages/core/src/api/client.ts`
3. Export from `packages/core/src/index.ts`

**New component:**
1. Create in `packages/web/src/components/`
2. Import types from `@kapp/core`
