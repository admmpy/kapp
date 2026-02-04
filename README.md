# Kapp - Korean Language Learning Platform

Lesson-based Korean learning app with grammar explanations, vocabulary exercises, reading/listening practice, and word-ordering exercises.

---

## Overview

Structured curriculum progression: **Course → Unit → Lesson → Exercises** with immediate feedback.

---

## Features

- Structured lessons with grammar explanations and examples
- 5 exercise types: Vocabulary, Grammar, Reading, Listening, Sentence Arrangement
- Progress tracking: completion status, scores, activity history
- Audio support (TTS) for Korean pronunciation
- Optional AI explanations via OpenAI
- Security: input validation, SECRET_KEY enforcement, prompt injection protection
- iOS PWA support with install prompt and offline caching

---

## Tech Stack

| Component | Tech |
|-----------|------|
| **Backend** | Flask 3.0 (Python 3.9+) with SQLAlchemy ORM, SQLite |
| **Web** | React 19 + TypeScript, Vite 7, Axios, CSS |
| **Audio** | gTTS |

---

## Quick Start

### Prerequisites
- Python 3.9+, Node.js 18+, Git

### Installation

**1. Clone & Backend Setup**
```bash
git clone https://github.com/admmpy/kapp.git && cd kapp/backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))" >> .env
```

**2. Web Setup**
```bash
cd ../
npm install
```

**3. Run**

*Option A - Start scripts:*
```bash
./start-servers.sh        # Unix/Mac
.\start-servers.ps1       # Windows
```

*Option B - Manual:*
```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && python app.py

# Terminal 2 - Web
npm --workspace packages/web run dev
```

Open http://localhost:5173.

---

## Usage

1. Select a course
2. Choose a unit
3. Start a lesson (grammar → exercises → score)
4. Track progress on the course page

---

## iOS PWA Testing (Recommended)

iOS requires HTTPS and same-origin `/api` routing. Use the ngrok tunnel script:

```bash
scripts/run-ios-tunnel.sh
```

**Prereqs**
```bash
brew install caddy
brew install ngrok/ngrok/ngrok
ngrok config add-authtoken YOUR_TOKEN
```

**Troubleshooting**
- `curl -i http://localhost:4173/api/courses` should return JSON (not HTML).

---

## Project Structure

```
kapp/
├── backend/
│   ├── app.py, config.py, models_v2.py, security.py
│   ├── routes/ (courses, lessons, progress, vocabulary, audio, llm, debug)
│   ├── data/ (korean_lessons.json, korean_vocab.json, audio_cache/)
│   └── migrations/, scripts/
├── packages/
│   └── web/ (React + Vite)
├── scripts/ (tunnel + proxy helpers)
├── claude.md
└── README.md
```

---

## Testing

**API**
```bash
curl http://localhost:5001/api/health
curl http://localhost:5001/api/courses
curl http://localhost:5001/api/courses/1
curl http://localhost:5001/api/progress
```

**Web:** open http://localhost:5173 and complete a lesson

---

## Security

- SECRET_KEY validation (min 32 chars)
- Input sanitization and rate limiting
- LLM prompt protections
- See `CLAUDE.md`

---

## Content

Korean Fundamentals:
- Unit 1: Greetings & Introductions
- Unit 2: Numbers & Counting
- Unit 3: Basic Phrases

---

## Contributing

1. `git checkout -b feature/your-feature`
2. `git commit -m "Add your feature"`
3. `git push origin feature/your-feature`
4. Open a Pull Request

---

## Working On

- Practice Speaking audio failure in PWA: `23:59:00.609 GMT GET /api/audio/안녕하세요! 어떻게 지내세요?.mp3 500 Internal Server Error`

---

## License

MIT License - see `LICENSE`
