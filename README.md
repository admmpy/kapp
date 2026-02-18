# Kapp - Korean Language Learning Platform

Lesson-based Korean learning app with structured curriculum, spaced repetition, AI conversation practice, and offline PWA support.

---

## Thoughts

This project initially started in Cursor but later shifted into Claude Code, and later also used Codex both in CLI. The exposure I've gained through using both CC and Codex has definetely shown me the how strong 'vibe-coding' has become as this isn't my first rodeo using AI to code but it is my first time using CLI tools (mixture of Ghostty and Cursor Terminal). The project is essentially finished with a functioning web app available on to use on iOS as well as desktop. I believe going forward this will be easier, both because the tools and models will become better but also beacuse I was very dillegent with my use of these tools learning good practices from trial and error in other projects as well as reading articles and posts on X, Medium and Substack.

In the future, I think I would use local LLMs again (to completion) assuming I have the hardware to support better models (Potentially a Mac Studios with sizeable RAM). Also, investing and setting up a home server as a side project to keep certain projects up and running at all times (in generally I really think this is a good idea with the current state of everything being subscription and cloud based).

---

## Features

**Core Learning**
- Structured curriculum: Course → Unit → Lesson → Exercises
- Exercise types: vocabulary, grammar, reading, listening, sentence arrangement
- Progress tracking with completion status, scores, and activity history
- Audio (TTS) for Korean pronunciation with cached MP3 generation

**Spaced Repetition (SRS)**
- SM-2 algorithm for vocabulary review scheduling
- Sentence-level SRS for exercise review (opt-in)

**AI Features** (OpenAI API)
- Conversation practice with a Korean tutor (multi-turn)
- Inline translation of AI messages (Korean → English)
- Audio generation for conversation responses
- Grammar and vocabulary explanations
- Example sentence generation

**Training Enhancements** (opt-in via feature flags)
- Speaking-first mode: reorder exercises to prioritize audio (enabled by default)
- Weakness review: targeted practice for weak grammar/vocabulary
- Grammar mastery tracking
- Controlled immersion: hide romanization and English translations
- Pronunciation self-check after audio exercises

**Platform**
- Offline PWA with service worker + IndexedDB caching
- iOS home screen support with safe area handling
- Dark mode with system preference detection
- Rate limiting and input validation

---

## Tech Stack

| Component | Tech |
|-----------|------|
| **Backend** | Flask 3.0, Python 3.9+, SQLAlchemy, SQLite |
| **Frontend** | React 19, TypeScript, Vite 7 |
| **Audio** | gTTS with MD5-based file caching |
| **AI** | OpenRouter (deepseek/deepseek-v3.2, OpenAI-compatible API) |

---

## Quick Start

### Prerequisites
- Python 3.9+, Node.js 18+, Git

### Installation

**1. Backend**
```bash
git clone https://github.com/admmpy/kapp.git && cd kapp/backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))" >> .env
```

**2. Frontend**
```bash
cd ../
npm install
```

**3. Run**
```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && python app.py

# Terminal 2 - Frontend
npm run web
```

Open http://localhost:5173.

---

## Feature Flags

Feature flags are set via environment variables in `packages/web/.env.local`:

| Flag | Default | Description |
|------|---------|-------------|
| `VITE_SPEAKING_FIRST_ENABLED` | `true` | Reorder exercises, audio first |
| `VITE_WEAKNESS_REVIEW_ENABLED` | `true` | Weakness-driven review sessions |
| `VITE_SENTENCE_SRS_ENABLED` | `true` | Sentence-level spaced repetition |
| `VITE_IMMERSION_MODE_ENABLED` | `true` | Hide romanization/English |
| `VITE_GRAMMAR_MASTERY_ENABLED` | `true` | Grammar mastery tracking UI |
| `VITE_PRONUNCIATION_SELF_CHECK_ENABLED` | `true` | Self-rating after audio exercises |

Backend flags with matching names must also be enabled for features that require server support.

---

## Project Structure

```
kapp/
├── backend/
│   ├── app.py, config.py, models_v2.py
│   ├── routes/ (courses, lessons, progress, vocabulary,
│   │            exercise_review, weakness, audio, llm,
│   │            settings, debug)
│   ├── srs_utils.py (shared SM-2 algorithm)
│   ├── llm_service.py, tts_service.py
│   ├── data/ (korean_lessons.json, korean_vocab.json, audio_cache/)
│   └── scripts/
├── packages/
│   ├── core/ (shared API client + types)
│   └── web/ (React + Vite PWA)
└── scripts/ (iOS tunnel + proxy helpers)
```

---

## iOS PWA

iOS requires HTTPS and same-origin `/api` routing:

```bash
# Prerequisites: brew install caddy ngrok/ngrok/ngrok
scripts/run-ios-tunnel.sh
```

---

## Contributing

1. `git checkout -b feat/your-feature`
2. `git commit -m "feat: add your feature"`
3. `git push origin feat/your-feature`
4. Create PR docs:
   - `docs/prs/<topic>-pr.md`
   - `docs/reviews/<topic>-architecture-review.md`
5. Open a Pull Request with verification evidence

---

## License

MIT License - see `LICENSE`
