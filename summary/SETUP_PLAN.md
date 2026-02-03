# Kapp Setup & Git Initialization Plan

**Date:** October 29, 2025  
**Repository:** https://github.com/RealistRBN/kapp.git

---

## Overview

This document outlines the complete setup plan for the Korean Learning App (Kapp) project, including:
- Git repository initialization
- Directory structure creation
- GitHub remote configuration
- Branch strategy (main + development)

---

## Git Strategy

### Files Excluded from Repository
- All `.md` documentation files
- `.github/` directory (Copilot instructions)
- `.vscode/` directory (VSCode settings)
- `.cursor/` directory (Cursor IDE rules)

**Rationale:** Keep repository focused on code only; manage documentation and IDE configurations locally.

---

## Execution Steps

### Step 1: Create .gitignore

Create `.gitignore` with exclusions for:
- Python cache and compiled files
- Flask database and instance files
- Environment variables
- TTS audio cache
- Frontend build artifacts
- IDE settings
- All markdown files
- GitHub configurations

### Step 2: Initialize Git Repository

```bash
cd /Users/am/Sync/Cursor/Kapp_1
git init
git branch -M main
git remote add origin https://github.com/RealistRBN/kapp.git
```

### Step 3: Commit 1 - Add .gitignore

```bash
git add .gitignore
git commit -m "chore: initialize project with .gitignore configuration

- Exclude Python cache and compiled files
- Exclude Flask instance and database files
- Exclude environment variables and secrets
- Exclude TTS audio cache (keep .gitkeep)
- Exclude frontend build artifacts and node_modules
- Exclude IDE settings (.vscode, .cursor, .idea)
- Exclude all markdown documentation
- Exclude GitHub workflow configurations"
```

### Step 4: Create Backend Structure

```bash
# Create directories
mkdir -p backend/routes
mkdir -p backend/data/audio_cache
touch backend/data/audio_cache/.gitkeep

# Create Python files
touch backend/__init__.py
touch backend/app.py
touch backend/config.py
touch backend/database.py
touch backend/models.py
touch backend/srs.py
touch backend/tts_service.py
touch backend/routes/__init__.py
touch backend/routes/cards.py
touch backend/routes/reviews.py
touch backend/routes/stats.py
touch backend/routes/audio.py
```

### Step 5: Commit 2 - Backend Structure

```bash
git add backend/
git commit -m "feat: scaffold backend directory structure

- Add Flask app factory placeholder (app.py)
- Define configuration module (config.py)
- Add SQLAlchemy setup placeholder (database.py, models.py)
- Create SM-2 algorithm module (srs.py)
- Add TTS service placeholder (tts_service.py)
- Organize routes by feature (cards, reviews, stats, audio)
- Create data directories for database and audio cache"
```

### Step 6: Create requirements.txt and .env.example

**backend/requirements.txt:**
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-CORS==4.0.0
python-dotenv==1.0.0
gTTS==2.5.0
requests==2.31.0

# Development dependencies
pytest==7.4.3
black==23.12.1
flake8==7.0.0
```

**backend/.env.example:**
```
DATABASE_URL=sqlite:///data/korean_learning.db
TTS_CACHE_DIR=data/audio_cache
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
CORS_ORIGINS=http://localhost:5173
```

### Step 7: Commit 3 - Dependencies

```bash
git add backend/requirements.txt backend/.env.example
git commit -m "chore: add Python dependencies and environment configuration

- Pin Flask 3.0.0 with SQLAlchemy and CORS extensions
- Add gTTS 2.5.0 for text-to-speech service
- Include development dependencies (pytest, black, flake8)
- Provide .env.example template for local development
- Configure database URL, TTS cache directory, and CORS origins"
```

### Step 8: Create Development Branch

```bash
git checkout -b development
```

### Step 9: Push to GitHub

```bash
# Push main branch
git checkout main
git push -u origin main

# Push development branch
git checkout development
git push -u origin development
```

---

## Verification Commands

```bash
# Check current branch and commits
git log --oneline --graph --all

# Verify files tracked by git
git ls-files

# Check remote configuration
git remote -v

# Verify .gitignore is working
git status --ignored
```

---

## Expected Repository Structure

```
kapp/ (main branch)
├── .gitignore
└── backend/
    ├── __init__.py
    ├── app.py
    ├── config.py
    ├── database.py
    ├── models.py
    ├── srs.py
    ├── tts_service.py
    ├── routes/
    │   ├── __init__.py
    │   ├── cards.py
    │   ├── reviews.py
    │   ├── stats.py
    │   └── audio.py
    ├── data/
    │   └── audio_cache/
    │       └── .gitkeep
    ├── requirements.txt
    └── .env.example
```

---

## Local Files (Not in Repository)

```
.github/copilot-instructions.md
.vscode/settings.json
.vscode/extensions.json
.vscode/AI_GUIDELINES.md
.cursor/rules/*.mdc
README.md
docs/SETUP.md
docs/API.md
docs/ARCHITECTURE.md
SETUP_PLAN.md (this file)
```

---

## Post-Setup Next Steps

1. **Backend Implementation** (on development branch)
   - Implement SQLAlchemy models
   - Build SM-2 algorithm
   - Create TTS service with caching
   - Build REST API endpoints

2. **Frontend Scaffolding**
   - Initialize Vite + React + TypeScript
   - Set up component structure
   - Implement API client

3. **Integration Testing**
   - Test full review workflow
   - Verify TTS audio generation
   - Test SM-2 scheduling

---

## Notes

- All commits use detailed commit messages following conventional commits format
- Main branch contains stable code only
- Development branch for active feature development
- Feature branches follow pattern: `feature/feature-name`
- Documentation managed locally, not in Git repository

---

## Status

- [x] Step 1: Create .gitignore ✅
- [x] Step 2: Initialize Git ✅
- [x] Step 3: Commit 1 - .gitignore ✅ (commit: 0df3997)
- [x] Step 4: Create backend structure ✅
- [x] Step 5: Commit 2 - Backend structure ✅ (commit: 059c2ba)
- [x] Step 6: Create requirements.txt and .env.example ✅
- [x] Step 7: Commit 3 - Dependencies ✅ (commit: aab85a5)
- [x] Step 8: Create development branch ✅
- [x] Step 9: Push to GitHub ✅
- [x] Verification: Check repository structure ✅

---

## Setup Complete! ✅

**Repository URL:** https://github.com/RealistRBN/kapp.git

### Final Repository State

**Branches:**
- `main` - 3 commits, pushed to origin
- `development` - 3 commits, pushed to origin

**Commits:**
1. `0df3997` - chore: initialize project with .gitignore configuration
2. `059c2ba` - feat: scaffold backend directory structure
3. `aab85a5` - chore: add Python dependencies and environment configuration

**Files in Repository:**
- `.gitignore`
- `backend/__init__.py`
- `backend/app.py`
- `backend/config.py`
- `backend/database.py`
- `backend/models.py`
- `backend/srs.py`
- `backend/tts_service.py`
- `backend/routes/__init__.py`
- `backend/routes/cards.py`
- `backend/routes/reviews.py`
- `backend/routes/stats.py`
- `backend/routes/audio.py`
- `backend/data/audio_cache/.gitkeep`
- `backend/requirements.txt`
- `backend/.env.example`

**Files Excluded (Local Only):**
- `.github/copilot-instructions.md`
- `.vscode/settings.json`
- `.vscode/extensions.json`
- `.vscode/AI_GUIDELINES.md`
- `.cursor/rules/*.mdc`
- All `.md` files (including this SETUP_PLAN.md)
- `docs/` directory

### Next Development Steps

You're now ready to start implementing features on the `development` branch:

1. **Create feature branches** from `development`:
   ```bash
   git checkout development
   git checkout -b feature/database-models
   ```

2. **Implement features** following the AI assistant rules in:
   - `.github/copilot-instructions.md` (for Copilot)
   - `.vscode/AI_GUIDELINES.md` (quick reference)

3. **First implementation priorities:**
   - Database models (Card, Review, Deck)
   - SM-2 algorithm
   - Basic Flask app factory
   - Health check endpoint

4. **Test as you go:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

**Setup completed:** October 29, 2025
