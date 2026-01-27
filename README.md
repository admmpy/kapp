# 🇰🇷 Kapp v2.0 - Korean Language Learning Platform

A structured lesson-based Korean learning application inspired by LingoDeer, featuring grammar-focused lessons, reading & listening exercises, and progressive curriculum.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000.svg)](https://flask.palletsprojects.com/)

---

## 📖 Overview

Kapp v2.0 is a complete rebuild transitioning from flashcard-based learning to a structured lesson-based approach. Lessons include grammar explanations, vocabulary exercises, reading comprehension, and listening practice.

**v2.0 Major Changes:**
- Replaced flashcards with structured lessons
- Added grammar explanations in each lesson
- Multiple exercise types (vocabulary, grammar, reading, listening)
- Course → Unit → Lesson progression system
- Removed SM-2 spaced repetition (replaced with lesson-based progression)

---

## ✨ Key Features

### 📚 Structured Curriculum
- **Courses:** Organized learning paths (e.g., "Korean Fundamentals")
- **Units:** Thematic sections (e.g., "Greetings & Introductions")
- **Lessons:** Bite-sized learning with grammar and exercises
- **Progressive difficulty:** Start with basics, advance systematically

### 📖 Grammar-Focused Learning
- In-depth grammar explanations in each lesson
- Quick tips for practical usage
- Contextual examples
- Pattern-based learning

### 🎯 Multiple Exercise Types
- **Vocabulary:** Translation matching, word recognition
- **Grammar:** Fill-in-the-blank, pattern application
- **Reading:** Comprehension passages with questions
- **Listening:** Audio-based exercises with transcripts

### 📊 Progress Tracking
- Lesson completion tracking
- Score recording per lesson
- Learning streak counter
- Overall course progress

### 🔊 Native Audio Support
- Text-to-speech for Korean text
- Audio playback in listening exercises
- Pronunciation practice

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Flask 3.0 (Python)
- **Database:** SQLite with SQLAlchemy ORM
- **TTS:** gTTS (Google Text-to-Speech)
- **API:** RESTful JSON endpoints with Flask-CORS
- **Security:** Input sanitization, validated SECRET_KEY

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **Styling:** CSS with responsive design
- **Routing:** Hash-based navigation

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Node.js 18 or higher
- Git

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/admmpy/kapp.git
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
# IMPORTANT: Generate a secure SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
# Edit .env and add the generated key

# Run database migration (if upgrading from v1)
python migrations/migrate_to_lessons.py

# Import lesson content
python scripts/import_lessons.py
```

#### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install
```

#### 4. Run the Application

**Option A: Use the start script**
```bash
./start-servers.sh  # Unix/Mac
# or
.\start-servers.ps1  # Windows PowerShell
```

**Option B: Manual start**

Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate
python app.py
# Runs on http://localhost:5001
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

#### 5. Open Your Browser
Navigate to `http://localhost:5173` and start learning Korean! 🎉

---

## 📱 How to Use

### Course Navigation
1. **Course List:** See available courses and your progress
2. **Select Course:** Click to view units within the course
3. **Select Unit:** See lessons and their completion status
4. **Start Lesson:** Begin with grammar explanation

### Lesson Flow
1. **Grammar Section:** Read the grammar explanation
2. **Grammar Tip:** Quick practical tip
3. **Start Exercises:** Click to begin practice
4. **Exercise Types:**
   - Answer vocabulary questions
   - Complete grammar exercises
   - Read passages and answer questions
   - Listen to audio and respond
5. **Immediate Feedback:** See if you're correct
6. **Complete Lesson:** Get your score

### Tracking Progress
- View overall completion percentage
- Track lessons completed today
- Build a learning streak
- Review recent activity

---

## 📂 Project Structure

```
kapp/
├── backend/                    # Flask REST API
│   ├── app.py                  # Application factory
│   ├── config.py               # Environment configuration
│   ├── database.py             # SQLAlchemy setup
│   ├── models_v2.py            # Course, Lesson, Exercise models
│   ├── security.py             # Input validation & sanitization
│   ├── routes/
│   │   ├── courses.py          # Course/Unit endpoints
│   │   ├── lessons.py          # Lesson & Exercise endpoints
│   │   ├── progress.py         # Progress tracking
│   │   ├── vocabulary.py       # Vocabulary reference
│   │   ├── audio.py            # Audio serving
│   │   └── llm.py              # LLM integration
│   ├── data/
│   │   ├── korean_lessons.json # Lesson content
│   │   └── audio_cache/        # Generated TTS files
│   ├── migrations/
│   │   └── migrate_to_lessons.py
│   └── scripts/
│       └── import_lessons.py   # Content import script
│
├── frontend/                   # React SPA
│   ├── src/
│   │   ├── App.tsx             # Main app with routing
│   │   ├── components/
│   │   │   ├── CourseList.tsx  # Course selection
│   │   │   ├── UnitView.tsx    # Unit/Lesson navigation
│   │   │   ├── LessonView.tsx  # Lesson interface
│   │   │   ├── ExerciseRenderer.tsx # Exercise display
│   │   │   └── ProgressBar.tsx # Progress indicator
│   │   ├── api/
│   │   │   └── client.ts       # Backend API client
│   │   └── types/
│   │       └── index.ts        # TypeScript interfaces
│   └── package.json
│
├── claude.md                   # Development gotchas & lessons
└── README.md                   # This file
```

---

## 🧪 Testing

### Backend API Tests
```bash
# Health check
curl http://localhost:5001/api/health

# Get courses
curl http://localhost:5001/api/courses

# Get lesson details
curl http://localhost:5001/api/lessons/1

# Get progress
curl http://localhost:5001/api/progress
```

### Frontend
1. Navigate to `http://localhost:5173`
2. Select a course
3. Complete a lesson
4. Verify progress updates

---

## 🔒 Security

This version includes security improvements:
- **SECRET_KEY validation:** Rejects weak/default keys
- **Prompt injection protection:** Sanitizes LLM inputs
- **Input validation:** Length limits, type checking
- See `claude.md` for security lessons learned

---

## 🚧 Current Content

### Korean Fundamentals Course
- **Unit 1: Greetings & Introductions** (3 lessons)
  - Hello & Goodbye
  - Thank You & Sorry
  - Self Introduction

- **Unit 2: Numbers & Counting** (2 lessons)
  - Sino-Korean Numbers 1-10
  - Native Korean Numbers 1-10

- **Unit 3: Basic Phrases** (2 lessons)
  - Yes, No & Please
  - Excuse Me & Wait

**Total:** 7 lessons, 35+ exercises, 36 vocabulary items

---

## 🚧 Roadmap

### Next Steps
- [ ] Add more lessons (20+ planned)
- [ ] Improve exercise variety
- [ ] Add user authentication
- [ ] Mobile-responsive improvements

### Future Features
- [ ] Writing/speaking exercises
- [ ] Review mode for completed lessons
- [ ] Vocabulary flashcard mode
- [ ] Offline support (PWA)

---

## 📝 Migration from v1.0

If upgrading from the flashcard version:

1. **Backup your data:** The migration script does this automatically
2. **Run migration:** `python migrations/migrate_to_lessons.py`
3. **Import lessons:** `python scripts/import_lessons.py`

Note: Old flashcard/review data is exported to JSON but not used in v2.0.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Inspiration:** LingoDeer, Duolingo
- **TTS:** Google Text-to-Speech (gTTS library)
- **Vocabulary:** Curated from TOPIK I frequency lists

---

**Happy Learning! 화이팅! (Fighting!) 💪🇰🇷**
