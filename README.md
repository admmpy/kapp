# 🇰🇷 Kapp - Korean Language Learning App

A modern, intelligent flashcard application designed for Korean language learners (A0-A1 TOPIK I level) featuring spaced repetition, native audio pronunciation, and progress tracking.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000.svg)](https://flask.palletsprojects.com/)

---

## 📖 Overview

Kapp is a full-stack web application that helps beginners learn Korean through scientifically-proven spaced repetition. The app focuses on TOPIK I vocabulary (A0-A1 level) with native audio pronunciation, making it perfect for absolute beginners starting their Korean learning journey.

---

## ✨ Key Features

### 🧠 Smart Spaced Repetition (SM-2 Algorithm)
- Automatically schedules card reviews based on your performance
- Proven algorithm used by Anki and SuperMemo
- Optimizes long-term retention with minimal study time
- Cards you struggle with appear more frequently

### 🔊 Native Korean Pronunciation
- Text-to-speech for every flashcard using Google TTS
- Hear authentic Korean pronunciation
- Slower playback for beginner cards (level 0-1)
- Audio caching for instant playback

### 📚 Comprehensive Beginner Content
**100+ flashcards across 9 themed decks:**
- 🔤 **Hangul Basics** - Master Korean alphabet with pronunciation
- 👋 **Greetings & Phrases** - Essential daily expressions
- 🔢 **Numbers** - Count from 1-100 in Korean
- 👨‍👩‍👧‍👦 **Family Members** - Family vocabulary
- 🍜 **Food & Drinks** - Common items and restaurant words
- 🏃 **Essential Verbs** - Core action words (to be, to go, to eat)
- 🏢 **Places & Locations** - Navigate the city
- ⏰ **Time & Days** - Tell time and days of the week
- 😊 **Common Adjectives** - Express feelings and descriptions

### 📊 Progress Tracking
- **Dashboard with live statistics:**
  - Cards due today
  - Overall accuracy rate
  - Learning streak (consecutive days)
- **Per-deck analytics:**
  - Total cards in deck
  - Cards mastered
  - TOPIK level indicator

### 🎯 Beginner-Friendly Design
- **Clear flashcard format:**
  - Korean text (Hangul) prominently displayed
  - Romanization for pronunciation help
  - English translation
  - Example sentences in context
- **Progressive difficulty:** Start with alphabet, advance to phrases
- **Quality ratings (0-5):** Self-assess your recall accurately

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Flask 3.0 (Python)
- **Database:** SQLite with SQLAlchemy ORM
- **TTS:** gTTS (Google Text-to-Speech)
- **API:** RESTful JSON endpoints with Flask-CORS

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite (fast dev server + HMR)
- **Styling:** CSS Modules with responsive design
- **State Management:** React Hooks (useState, useEffect)

### Algorithm
- **Spaced Repetition:** Custom SM-2 implementation
- **Scheduling:** Interval-based with ease factor adjustment
- **Performance Tracking:** Quality ratings (0-5 scale)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Node.js 18 or higher
- Git

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/RealistRBN/kapp.git
cd kapp
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env if needed (defaults work for local development)

# Initialize database with vocabulary
python init_db.py
```

**Expected output:** 100+ cards imported across 9 decks

#### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Ensure VITE_API_URL=http://localhost:5000
```

#### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
# Runs on http://localhost:5000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

#### 5. Open Your Browser
Navigate to `http://localhost:5173` and start learning Korean! 🎉

---

## 📱 How to Use

### Starting a Review Session
1. **Dashboard:** View your stats and available decks
2. Click **"Start Reviewing"** button
3. System loads 20 due cards (or all available)

### Reviewing Cards
1. **Card Front:** See Korean text + romanization
2. Click **🔊 audio icon** to hear pronunciation
3. Try to recall the meaning
4. Click **"Show Answer"** to reveal English translation
5. **Rate your recall (0-5):**
   - **5** - Perfect (instant recall)
   - **4** - Correct after brief hesitation
   - **3** - Correct but required effort
   - **2** - Incorrect but recognized when shown
   - **1** - Incorrect but seemed familiar
   - **0** - Complete blackout (no recognition)

### Card Scheduling
- **Good ratings (4-5):** Card interval increases (1 day → 3 days → 7 days → 15 days...)
- **Medium ratings (3):** Interval increases slightly
- **Poor ratings (0-2):** Card resets to review again soon

### Tracking Progress
- Check dashboard stats daily
- Watch your accuracy improve over time
- Build a learning streak by reviewing daily

---

## 📂 Project Structure

```
kapp/
├── backend/                    # Flask REST API
│   ├── app.py                  # Application factory
│   ├── config.py               # Environment configuration
│   ├── database.py             # SQLAlchemy setup
│   ├── models.py               # Card, Review, Deck models
│   ├── srs.py                  # SM-2 algorithm implementation
│   ├── tts_service.py          # TTS generation & caching
│   ├── init_db.py              # Database initialization script
│   ├── routes/                 # API endpoints
│   │   ├── cards.py            # Card retrieval
│   │   ├── reviews.py          # Review submission
│   │   ├── stats.py            # Statistics
│   │   └── audio.py            # Audio serving
│   ├── data/
│   │   ├── korean_vocab.json   # Vocabulary dataset
│   │   └── audio_cache/        # Generated TTS files
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # React SPA
│   ├── src/
│   │   ├── App.tsx             # Main app component
│   │   ├── components/
│   │   │   ├── Dashboard.tsx   # Stats & deck overview
│   │   │   ├── ReviewSession.tsx # Review workflow
│   │   │   └── FlashCard.tsx   # Card display
│   │   ├── services/
│   │   │   └── api.ts          # Backend API client
│   │   ├── types/
│   │   │   └── index.ts        # TypeScript interfaces
│   │   └── styles/             # CSS modules
│   ├── package.json            # Node dependencies
│   └── vite.config.ts          # Vite configuration
│
├── .github/                    # GitHub Copilot instructions
├── .vscode/                    # VSCode settings (local)
├── .cursor/                    # Cursor IDE rules (local)
├── TESTING.md                  # Comprehensive testing guide
└── README.md                   # This file
```

---

## 🧪 Testing

See [`TESTING.md`](TESTING.md) for a comprehensive testing guide including:
- Step-by-step testing procedures
- Expected outputs and behaviors
- API endpoint testing with curl
- Error handling verification
- Performance benchmarks

**Quick Test:**
```bash
# Backend health check
curl http://localhost:5000/api/health

# Get due cards
curl http://localhost:5000/api/cards/due?limit=5

# Get statistics
curl http://localhost:5000/api/stats
```

---

## 🎓 Learning Methodology

### Why Spaced Repetition Works
Spaced repetition is a learning technique that involves reviewing information at increasing intervals. Research shows this method:
- Improves long-term retention by up to 200%
- Reduces study time compared to cramming
- Strengthens memory through optimal review timing
- Prevents forgetting through timely reinforcement

### SM-2 Algorithm Explained
The SM-2 (SuperMemo 2) algorithm calculates optimal review intervals:

```
For quality rating Q (0-5):
- If Q >= 3 (Correct):
  - Interval multiplies by ease factor (starts at 2.5)
  - Ease factor adjusts based on performance
  - Next review: 1 day → 3 days → 7 days → 15 days...

- If Q < 3 (Incorrect):
  - Interval resets to 1 day
  - Ease factor decreases slightly
  - Card needs more practice
```

This ensures difficult cards appear more frequently while mastered cards space out naturally.

---

## 🚧 Roadmap & Future Enhancements

### Version 1.1 (Planned)
- [ ] User authentication and multi-user support
- [ ] Cloud sync across devices
- [ ] Custom deck creation
- [ ] Import/export vocabulary (CSV, Anki format)

### Version 2.0 (Vision)
- [ ] ASR pronunciation feedback (Whisper/Vosk)
- [ ] Sentence construction practice
- [ ] Grammar pattern templates
- [ ] Mobile app (React Native)
- [ ] Offline mode (PWA)

### Long-term Goals
- [ ] TOPIK II vocabulary (intermediate)
- [ ] Conversation practice mode
- [ ] Gamification (achievements, leaderboards)
- [ ] Community-contributed decks
- [ ] AI-powered personalized learning paths

---

## 🤝 Contributing

This is currently a personal learning project, but suggestions and feedback are welcome!

**How to contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Areas for contribution:**
- Additional vocabulary decks
- UI/UX improvements
- Bug fixes
- Performance optimizations
- Documentation improvements

---

## 🐛 Known Issues

- Audio generation requires internet connection (gTTS is cloud-based)
- SQLite has concurrency limitations (single-user only)
- No offline support yet (requires backend connection)
- Browser must support Web Audio API for audio playback

See [Issues](https://github.com/RealistRBN/kapp/issues) for full list and report bugs.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Inspiration:** Anki, Duolingo, and the spaced repetition research community
- **Algorithm:** SM-2 algorithm by Piotr Woźniak (SuperMemo)
- **TTS:** Google Text-to-Speech (gTTS library)
- **Korean Fonts:** System fonts with Hangul support
- **Vocabulary:** Curated from TOPIK I frequency lists

---

**Happy Learning! 화이팅! (Fighting!) 💪🇰🇷**
