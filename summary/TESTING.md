# 🧪 Kapp Testing Guide

This guide walks you through testing the complete Korean language learning application end-to-end.

## Prerequisites

Before testing, ensure you have completed the initial setup:

- ✅ Python 3.9+ installed
- ✅ Node.js 18+ installed
- ✅ Backend dependencies installed (`pip install -r backend/requirements.txt`)
- ✅ Frontend dependencies installed (`npm install` in `frontend/`)
- ✅ Environment variables configured (`.env` files copied from `.env.example`)

## 🚀 Testing Procedure

### Step 1: Initialize Database with Vocabulary

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python init_db.py
```

**Expected Output:**
```
Initializing database...
Database initialized successfully.
Importing vocabulary from korean_vocab.json...
Imported 100 cards across 9 decks
✓ Database initialized successfully!

Summary:
- Total Decks: 9
- Total Cards: 100+
- Decks:
  * Hangul Basics (5 cards)
  * Greetings & Basic Phrases (8 cards)
  * Numbers 1-10 (10 cards)
  * Family Members (8 cards)
  * Common Food & Drinks (8 cards)
  * Essential Verbs (12 cards)
  * Places & Locations (8 cards)
  * Time & Days (11 cards)
  * Common Adjectives (10 cards)
```

**Verify:**
- ✅ Database file created at `backend/data/kapp.db`
- ✅ No error messages
- ✅ All 9 decks imported successfully

---

### Step 2: Start Backend Server

**In the same terminal (with venv activated):**

```bash
python app.py
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

**Verify:**
- ✅ Server starts without errors
- ✅ Running on port 5000
- ✅ No database connection errors

**Test Health Check:**
```bash
# In a new terminal window:
curl http://localhost:5000/api/health
```

**Expected Response:**
```json
{"status": "healthy"}
```

---

### Step 3: Start Frontend Development Server

**Open a NEW terminal window:**

```bash
cd frontend
npm run dev
```

**Expected Output:**
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Verify:**
- ✅ Server starts on port 5173
- ✅ No compilation errors
- ✅ No module not found errors

---

### Step 4: Test Frontend in Browser

**Open your browser to:** `http://localhost:5173`

#### 4.1 Dashboard Component Test

**Expected Display:**
- ✅ Page title: "Korean Learning Dashboard"
- ✅ Three stat cards:
  - Cards Due Today (should show 100+ initially)
  - Accuracy Rate (should show 0% or N/A initially)
  - Current Streak (should show 0 days)
- ✅ Nine deck cards with:
  - Deck name
  - Description
  - Card count
  - TOPIK level badge
- ✅ "Start Reviewing" button (should be enabled if cards are due)

**Test Actions:**
1. Verify all stats load without errors
2. Check browser console for errors (F12 → Console tab)
3. Verify all 9 decks are visible
4. Hover over deck cards (should show hover effect)

**Console Check:**
- ✅ No 404 errors
- ✅ No CORS errors
- ✅ API calls successful (`GET /api/stats` returns 200)

---

#### 4.2 Review Session Component Test

**Click "Start Reviewing" button**

**Expected Display:**
- ✅ Progress bar showing "1 / 20" (or total cards loaded)
- ✅ Flashcard with:
  - Korean text (Hangul) in large font
  - Romanization below in smaller font
  - Audio icon button (🔊)
- ✅ "Show Answer" button
- ✅ Six quality rating buttons (0-5) visible but disabled

**Test Card Front:**
1. Verify Korean text displays correctly (not garbled)
2. Verify romanization is present
3. Click audio button (🔊)
   - ✅ Audio plays (Korean pronunciation)
   - ✅ Button shows loading state during playback
   - ✅ No audio errors in console
4. Click "Show Answer" button

**Test Card Back:**
1. Card should flip with animation
2. **Expected Display:**
   - ✅ English translation
   - ✅ Example sentence (if available)
   - ✅ Audio button still functional
3. Six quality rating buttons now enabled:
   - **5** - Perfect response
   - **4** - Correct after hesitation
   - **3** - Correct with difficulty
   - **2** - Incorrect, but remembered when shown
   - **1** - Incorrect, seemed familiar
   - **0** - Complete blackout

**Test Rating Submission:**
1. Click any rating button (e.g., "4 - Correct after hesitation")
2. **Expected Behavior:**
   - ✅ Card advances to next card
   - ✅ Progress bar updates (e.g., "2 / 20")
   - ✅ New card displays
   - ✅ No errors in console
3. Check browser Network tab (F12 → Network):
   - ✅ `POST /api/reviews` returns 200
   - ✅ Response includes updated card scheduling

**Complete Multiple Reviews:**
- Review at least 5-10 cards with different quality ratings
- Mix ratings: try 5, 4, 3, 2, 1, and 0
- Test audio on multiple cards

---

#### 4.3 Session Completion Test

**Complete all 20 cards (or loaded batch)**

**Expected Display:**
- ✅ Completion screen with:
  - "🎉 Review Session Complete!"
  - Cards reviewed count
  - Average quality score
  - Time spent
- ✅ "Return to Dashboard" button

**Click "Return to Dashboard"**

**Expected Behavior:**
- ✅ Returns to Dashboard (URL changes to `#/`)
- ✅ Stats updated:
  - Cards Due Today decreased
  - Accuracy Rate updated (if applicable)
  - Streak may update if first review of day

---

### Step 5: Backend API Testing (Optional)

**Test each endpoint directly using curl:**

#### Get Due Cards
```bash
curl http://localhost:5000/api/cards/due?limit=5
```

**Expected:** JSON array with 5 cards

#### Get Specific Card
```bash
curl http://localhost:5000/api/cards/1
```

**Expected:** JSON object with card ID 1 details

#### Submit Review
```bash
curl -X POST http://localhost:5000/api/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "card_id": 1,
    "quality_rating": 4,
    "time_spent": 10
  }'
```

**Expected:** JSON response with updated card scheduling

#### Get Statistics
```bash
curl http://localhost:5000/api/stats
```

**Expected:** JSON with cards_due_today, accuracy_rate, streak_days, deck_stats

#### Get Audio File
```bash
curl -I http://localhost:5000/api/audio/test.mp3
```

**Expected:** 404 (unless you have a test.mp3 file) or 200 with audio file

---

### Step 6: Spaced Repetition Algorithm Test

**Test SM-2 scheduling logic:**

1. **Review a card with quality 5 (Perfect):**
   - Note the `next_review_date` in Network response
   - Should be scheduled for tomorrow or later

2. **Review a card with quality 0 (Blackout):**
   - Should be rescheduled for very soon (minutes or hours)
   - Interval resets to 1 day

3. **Review same card multiple times:**
   - Each successful review (4-5) should increase interval exponentially
   - Failed reviews (0-2) should reset progress

4. **Check stats after varied reviews:**
   - Accuracy rate should reflect quality ratings
   - Cards due should decrease as you review

---

### Step 7: Audio Caching Test

**Verify TTS caching works:**

1. Open browser DevTools → Network tab
2. Play audio for a card (first time)
   - Should show network request to `/api/audio/{hash}.mp3`
   - Check backend terminal - should see TTS generation logs
3. Navigate away and come back to same card
4. Play audio again (second time)
   - Should still request `/api/audio/{hash}.mp3`
   - But backend should serve from cache (no new TTS generation logs)
   - Response should be faster

**Check audio cache directory:**
```bash
ls -lh backend/data/audio_cache/
```

**Expected:**
- ✅ Multiple `.mp3` files with MD5 hash names
- ✅ File sizes vary (different text lengths)

---

### Step 8: Error Handling Tests

#### Test Network Errors

1. **Stop backend server** (Ctrl+C in backend terminal)
2. In browser, try to load dashboard or start review
3. **Expected:**
   - ✅ User-friendly error message (not raw error)
   - ✅ Console shows network error (expected)
   - ✅ App doesn't crash

4. **Restart backend server**
5. Refresh browser
6. **Expected:**
   - ✅ App works normally again

#### Test Invalid Ratings

1. Open browser console
2. Try to submit invalid quality rating (if possible via console):
   ```javascript
   // This should be blocked by frontend, but backend should handle
   fetch('http://localhost:5000/api/reviews', {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({card_id: 1, quality_rating: 10, time_spent: 5})
   })
   ```
3. **Expected:**
   - ✅ Backend returns 400 error
   - ✅ Error message: "Quality rating must be between 0 and 5"

---

## ✅ Test Checklist Summary

### Backend Tests
- [ ] Database initializes with 100+ cards across 9 decks
- [ ] Flask server starts without errors
- [ ] Health check endpoint returns healthy status
- [ ] All API endpoints respond correctly
- [ ] TTS generates audio files and caches them
- [ ] SM-2 algorithm calculates correct intervals
- [ ] Error responses return proper JSON with status codes

### Frontend Tests
- [ ] Dashboard loads and displays stats correctly
- [ ] All 9 decks visible with correct information
- [ ] Review session loads 20 cards
- [ ] Flashcard displays Korean text correctly
- [ ] Audio playback works on all cards
- [ ] Card flip animation works smoothly
- [ ] Quality rating buttons submit correctly
- [ ] Progress bar updates accurately
- [ ] Session completion screen appears after all reviews
- [ ] Navigation between Dashboard and Review works
- [ ] No console errors during normal operation

### Integration Tests
- [ ] Stats update after review submissions
- [ ] Cards due count decreases after reviews
- [ ] Accuracy rate calculates correctly
- [ ] Audio caching prevents duplicate TTS generation
- [ ] Network errors handled gracefully
- [ ] Invalid input rejected with helpful errors

---

## 🐛 Common Issues & Solutions

### Issue: Database not found
**Solution:** Run `python init_db.py` from backend directory with venv activated

### Issue: CORS errors in browser
**Solution:** Ensure Flask-CORS is installed and backend is running on port 5000

### Issue: Audio not playing
**Solution:** Check browser console for errors. Verify audio files in `backend/data/audio_cache/`

### Issue: Frontend can't connect to backend
**Solution:** Verify `VITE_API_URL=http://localhost:5000` in `frontend/.env`

### Issue: Port already in use
**Solution:** 
- Backend: Change port in `backend/config.py`
- Frontend: Vite will auto-increment (5173 → 5174)

### Issue: Korean text appears as boxes/garbage
**Solution:** Ensure UTF-8 encoding. Check database file encoding.

---

## 📊 Expected Performance Metrics

- **Initial page load:** < 2 seconds
- **Card flip animation:** Smooth 60fps
- **Audio generation (first time):** 1-3 seconds
- **Audio playback (cached):** < 500ms
- **Review submission:** < 200ms
- **Stats update:** < 500ms

---

## 🎉 Success Criteria

Your application is working correctly if:

1. ✅ All cards load and display properly
2. ✅ Audio plays for every card
3. ✅ Reviews submit and update scheduling
4. ✅ Stats reflect actual progress
5. ✅ Navigation works between all pages
6. ✅ No console errors during normal use
7. ✅ App handles errors gracefully

---

## 📝 Next Steps After Testing

Once testing is complete and successful:

1. ✅ Merge `development` branch to `main`
2. Consider adding more vocabulary decks
3. Implement user authentication (optional)
4. Deploy to production (Heroku + Vercel)
5. Add unit tests for critical functions
6. Optimize database queries for larger datasets

---

**Happy Testing! 화이팅! (Fighting!) 💪**
