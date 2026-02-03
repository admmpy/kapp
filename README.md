# 🇰🇷 Kapp - Korean Language Learning Platform

A structured lesson-based Korean learning app with grammar explanations, vocabulary exercises, reading/listening practice, and word-ordering exercises.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-19.0+-61DAFB.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000.svg)](https://flask.palletsprojects.com/)

---

## Overview

Kapp is a lesson-based learning platform with structured curriculum progression: **Course → Unit → Lesson → Exercises**. Each lesson includes grammar explanations and multiple exercise types with immediate feedback.

**Current Content:** 1 course, 3 units, 7 lessons, 48 exercises

---

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
| **Frontend** | React 19 + TypeScript, Vite 7, Axios, CSS |
| **Audio** | gTTS (Google Text-to-Speech) |

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

# Configure environment
cp .env.example .env
# Generate secure SECRET_KEY (required):
python -c "import secrets; print(secrets.token_hex(32))" >> .env

# Optional: Enable AI explanations (OpenAI)
# Add to backend/.env:
# OPENAI_API_KEY=your-openai-api-key-here
# OPENAI_MODEL=gpt-4o-mini
# LLM_ENABLED=true
```

**2. Frontend Setup**
```bash
cd ../frontend
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
# Runs on http://localhost:5001

# Terminal 2 - Frontend
cd frontend && npm run dev
# Runs on http://localhost:5173
```

Open http://localhost:5173 in your browser.

---

## Usage

1. **Select a course** from the home page
2. **Choose a unit** to see available lessons
3. **Start a lesson:**
   - Read grammar explanation
   - Complete 4-6 practice exercises
   - See immediate feedback
   - View final score
4. **Track progress** on the course page

---

## Project Structure

```
kapp/
├── backend/
│   ├── app.py, config.py, models_v2.py, security.py
│   ├── routes/ (courses, lessons, progress, vocabulary, audio, llm, debug)
│   ├── data/ (korean_lessons.json, korean_vocab.json, audio_cache/)
│   └── migrations/, scripts/
├── frontend/
│   └── src/ (App.tsx, components/, api/, types/)
├── claude.md (development notes & security lessons)
└── README.md
```

---

## Testing

**API Endpoints:**
```bash
curl http://localhost:5001/api/health        # Health check
curl http://localhost:5001/api/courses       # All courses
curl http://localhost:5001/api/courses/1    # Course with units/lessons
curl http://localhost:5001/api/progress     # User progress
```

**Frontend:** Navigate to http://localhost:5173 and complete a lesson

---

## Security

- **SECRET_KEY validation:** Rejects weak/missing keys (min 32 chars)
- **Input sanitization:** Length limits, type checking
- **Prompt injection protection:** Sanitizes LLM inputs
- See `CLAUDE.md` for security design decisions

---

## Content

**Korean Fundamentals Course:**
- Unit 1: Greetings & Introductions (3 lessons)
- Unit 2: Numbers & Counting (2 lessons)
- Unit 3: Basic Phrases (2 lessons)

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) file

---

**Happy Learning! 화이팅! 💪**
