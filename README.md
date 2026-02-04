# Kapp - Korean Language Learning Platform

Lesson-based Korean learning app with grammar explanations, vocabulary exercises, reading/listening practice, and word-ordering exercises.

---

## Overview

Structured curriculum progression: **Course → Unit → Lesson → Exercises** with immediate feedback.

---

## Thoughts

This project initially started in Cursor but later shifted into Claude Code, and later also used Codex both in CLI. The exposure I've gained through using both CC and Codex has definetely shown me the how strong 'vibe-coding' has become as this isn't my first rodeo using AI to code but it is my first time using CLI tools (mixture of Ghostty and Cursor Terminal). The project is essentially finished with a functioning web app available on to use on iOS as well as desktop. I believe going forward this will be easier, both because the tools and models will become better but also beacuse I was very dillegent with my use of these tools learning good practices from trial and error in other projects as well as reading articles and posts on X, Medium and Substack. 

In the future, I think I would use local LLMs again (to completion) assuming I have the hardware to support better models (Potentially a Mac Studios with sizeable RAM). Also, investing and setting up a home server as a side project to keep certain projects up and running at all times (in generally I really think this is a good idea with the current state of everything being subscription and cloud based).

## Features

- **Structured Lessons:** Grammar explanations + contextual examples
- **5 Exercise Types:** Vocabulary, Grammar, Reading, Listening, Sentence Arrangement
- **Progress Tracking:** Completion status, scores per lesson, activity history
- **Audio Support:** Text-to-speech for Korean pronunciation
- **AI Explanations (Optional):** GPT-4o mini via OpenAI API
- **Security:** Input validation, SECRET_KEY enforcement, prompt injection protection
- **Offline PWA:** Service worker + IndexedDB caching for mobile use

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
