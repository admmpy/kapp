# Testing Guide - Full App Functionality

## Quick Start

```bash
# From project root
./start-servers.sh
```

The script will:
1. Check and kill any process on port 5001
2. Start Flask backend on http://localhost:5001
3. Start React frontend on http://localhost:5173

---

## Test Scenarios

### Scenario 1: Dashboard Loading
**Steps:**
1. Open http://localhost:5173 in browser
2. Observe dashboard loading

**Expected Results:**
- ✅ Spinner appears briefly
- ✅ Stats display: cards due, reviewed today, accuracy, streak
- ✅ "Start Reviewing" button visible (if cards due)
- ✅ Deck cards show with due/total counts
- ✅ Deck cards have hover effect (border turns purple)

---

### Scenario 2: Start General Review
**Steps:**
1. From dashboard, click "Start Reviewing" button
2. Observe URL change

**Expected Results:**
- ✅ URL changes to `http://localhost:5173/#review`
- ✅ Review session loads
- ✅ First card displays with Korean text
- ✅ Progress bar shows "Card 1 of X"
- ✅ Audio button appears (if available)

---

### Scenario 3: Deck-Filtered Review
**Steps:**
1. From dashboard, click on any deck card
2. Observe URL and loaded cards

**Expected Results:**
- ✅ URL changes to `http://localhost:5173/#review?deck_id={N}`
- ✅ Review session loads only cards from that deck
- ✅ Card counter shows correct deck-specific count
- ✅ All cards belong to selected deck

**How to Verify Deck Filtering:**
- Note the deck name you clicked
- During review, mentally check if vocabulary matches that deck's topic
- After session, check console logs for API call: should include `deck_id` parameter

---

### Scenario 4: Review Submission
**Steps:**
1. In review session, click "Show Answer"
2. View Korean + English translations
3. Click any rating (0-5)
4. Observe card advancement

**Expected Results:**
- ✅ Answer reveals back of card
- ✅ Rating buttons appear (6 options)
- ✅ Clicking rating submits review
- ✅ Next card loads automatically
- ✅ Progress bar advances

---

### Scenario 5: Session Completion
**Steps:**
1. Complete all cards in session (submit rating for last card)
2. Observe completion screen

**Expected Results:**
- ✅ "🎉 Session Complete!" message
- ✅ Shows count: "You reviewed X cards"
- ✅ Two buttons: "Start New Session" and "View Dashboard"

---

### Scenario 6: Return to Dashboard
**Steps:**
1. From completion screen, click "View Dashboard"
2. Observe stats update

**Expected Results:**
- ✅ URL changes back to `http://localhost:5173/` or `#`
- ✅ Dashboard reloads
- ✅ "Cards Reviewed Today" count increased
- ✅ "Cards Due Today" count decreased (by cards you rated 4-5)

---

### Scenario 7: Browser Back/Forward Navigation
**Steps:**
1. Dashboard → Click "Start Reviewing" → Browser Back button
2. Dashboard → Click deck → Browser Back button
3. Review session → Browser Forward button

**Expected Results:**
- ✅ Back from review → returns to dashboard
- ✅ Forward → returns to review session
- ✅ No console errors
- ✅ Cards reload correctly when navigating to review

---

### Scenario 8: Audio Playback
**Steps:**
1. In review session, look for audio button (🔊)
2. Click audio button
3. Listen for Korean pronunciation

**Expected Results:**
- ✅ Audio button appears for Korean text
- ✅ Clicking plays audio (may take 1-2 seconds first time)
- ✅ Audio matches the Korean word on card
- ✅ Subsequent plays are instant (cached)

**Troubleshooting Audio:**
- If no audio button: Check backend logs for TTS errors
- If audio doesn't play: Check browser console for network errors
- First generation may be slow (gTTS API call)

---

### Scenario 9: Empty State (No Due Cards)
**Steps:**
1. Review all due cards until completion
2. Return to dashboard

**Expected Results:**
- ✅ Dashboard shows "🎉 All caught up!" message
- ✅ No "Start Reviewing" button
- ✅ Message: "Come back tomorrow to continue learning!"

---

### Scenario 10: Port Conflict Handling
**Steps:**
1. Start servers with `./start-servers.sh`
2. Stop frontend (Ctrl+C)
3. Start servers again with `./start-servers.sh`

**Expected Results:**
- ✅ Script detects existing backend on port 5001
- ✅ Terminates old process
- ✅ Starts new backend successfully
- ✅ No "Address already in use" errors

---

## Debugging Tips

### Check Backend Health
```bash
curl http://localhost:5001/api/health
# Expected: {"service":"kapp-backend","status":"healthy","version":"1.0"}
```

### Check Due Cards API
```bash
# All due cards
curl http://localhost:5001/api/cards/due?limit=5

# Deck-filtered
curl http://localhost:5001/api/cards/due?deck_id=1&limit=5
```

### Check Stats API
```bash
curl http://localhost:5001/api/stats
```

### Browser Console
Open DevTools (F12) → Console tab:
- Check for API errors (red)
- Watch for API calls when navigating
- Verify hash changes logged

### Backend Logs
Backend terminal shows:
- API requests (GET /api/cards/due, POST /api/reviews)
- TTS generation logs
- Any errors with stack traces

---

## Common Issues

### "No cards due" but I just started
- Database may not be initialized
- Run: `cd backend && python init_db.py`

### Audio doesn't play
- Check backend logs for TTS errors
- Verify `backend/data/audio_cache/` directory exists
- Check browser console for 404 on audio files

### Cards not updating after review
- Check backend logs for database errors
- Verify review submission in Network tab (should be 200 OK)
- Refresh dashboard to see updated stats

### Port 5001 in use
- Run: `lsof -ti:5001 | xargs kill -9`
- Or let the script handle it automatically

### Frontend can't reach backend
- Verify backend is running: `curl http://localhost:5001/api/health`
- Check CORS settings in backend/app.py
- Verify VITE_API_URL (should be http://localhost:5001 or unset)

---

## Success Checklist

After running through all scenarios, you should have:

- ✅ Dashboard displaying stats
- ✅ Navigation working (hash-based)
- ✅ Deck filtering functional
- ✅ Reviews persisting to database
- ✅ Stats updating after reviews
- ✅ Audio playing (Korean TTS)
- ✅ Back/forward navigation working
- ✅ No port conflicts on startup
- ✅ Clean browser console (no errors)
- ✅ Smooth user experience

---

## Next Steps (Future Work)

1. **Add unit tests** for navigation logic
2. **Add integration tests** for review flow
3. **Implement React Router** (replace hash routing)
4. **Add charts** for learning progress
5. **Background TTS** pre-generation
6. **Deck management UI** (CRUD operations)
7. **Card management UI** (CRUD operations)
8. **Mobile responsiveness** improvements

---

## Need Help?

- Backend issues: Check `backend/app.py` and route files
- Frontend issues: Check browser DevTools console
- Database issues: Use `sqlite3 backend/data/kapp.db` to inspect
- API issues: Use curl commands above to test endpoints

Happy testing! 🚀
