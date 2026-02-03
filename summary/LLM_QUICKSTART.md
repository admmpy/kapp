# LLM Integration Quick Start

## TL;DR - What You're Building

Add AI-powered features to your Korean learning app using a **local LLM** (running on your computer) instead of expensive OpenAI API:

- 💡 **Explain This**: Get instant explanations for vocabulary cards
- 📝 **Example Sentences**: Auto-generate contextual examples
- 💬 **Conversation Practice**: Chat with AI tutor in Korean (Phase 2)
- 🎯 **Smart Hints**: Progressive hints during reviews (Phase 2)

**Privacy**: All AI runs locally - no data sent to external servers
**Cost**: Free after initial setup (no per-request charges)
**Performance**: 2-3 second responses on decent hardware

---

## Installation Checklist

### 1. Install Ollama (5 minutes)

**macOS:**
```bash
brew install ollama
```

**Windows:**
Download installer from [ollama.com](https://ollama.com)

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Start Ollama Service

```bash
ollama serve
```

Leave this running in a terminal. It's your local AI server.

### 3. Download AI Model (one-time, ~4GB download)

```bash
# Recommended: Qwen 2.5 7B (best Korean support)
ollama pull qwen2.5:7b

# Alternative: Llama 3.1 8B (good all-rounder)
ollama pull llama3.1:8b

# Faster option: Llama 3.2 3B (lower quality but faster)
ollama pull llama3.2:3b
```

### 4. Test It Works

```bash
ollama run qwen2.5:7b "Explain the Korean word 안녕하세요 to a beginner"
```

You should see a response explaining the word!

### 5. Verify API is Ready

```bash
curl http://localhost:11434/api/tags
```

Should return JSON with your installed models.

---

## Development Setup

### Create Feature Branch

```bash
cd /Users/am/Sync/Cursor/Kapp_1
git checkout development
git pull origin development
git checkout -b feature/local-llm-integration
```

### Update Backend Dependencies

No new dependencies needed! (requests is already in requirements.txt)

### Set Environment Variables

Add to `backend/.env`:

```bash
# LLM Configuration
LLM_ENABLED=true
LLM_MODEL=qwen2.5:7b
LLM_BASE_URL=http://localhost:11434
```

---

## Implementation Phases

### ✅ Phase 1: Backend Foundation (Do First)

**Files to create:**
1. `backend/llm_service.py` - LLM client and prompt templates
2. `backend/routes/llm.py` - API endpoints for LLM features

**Files to modify:**
1. `backend/app.py` - Register LLM blueprint
2. `backend/config.py` - Add LLM configuration

**Test with:**
```bash
# Start backend
cd backend
source venv/bin/activate
python app.py

# In another terminal, test endpoint
curl -X POST http://localhost:5001/api/llm/health
```

### ✅ Phase 2: Frontend Integration (Do Second)

**Files to create:**
1. `frontend/src/api/llm.ts` - TypeScript LLM client
2. `frontend/src/components/ExplanationModal.tsx` - Explanation popup
3. `frontend/src/components/ExplanationModal.css` - Modal styles

**Files to modify:**
1. `frontend/src/components/FlashCard.tsx` - Add "Explain" button
2. `frontend/src/components/FlashCard.css` - Style button
3. `frontend/src/components/ReviewSession.tsx` - Integrate modal

**Test with:**
```bash
# Start frontend (in new terminal)
cd frontend
npm run dev

# Navigate to review session
# Click "Explain This" button on flashcard back
```

### 🔄 Phase 3: Testing & Polish (Do Third)

- Test explanation generation speed
- Verify caching works (second request is instant)
- Check mobile responsiveness
- Add error handling edge cases
- Performance testing with multiple requests

### 🚀 Phase 4: Advanced Features (Optional)

- Conversation mode
- Smart hints system
- Example sentence generation
- Learning analytics

---

## Quick Test Script

Save as `test_llm.sh`:

```bash
#!/bin/bash

echo "🔍 Testing LLM Integration..."

# Check Ollama is running
echo -n "1. Checking Ollama service... "
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Not running"
    echo "   Start with: ollama serve"
    exit 1
fi

# Check model is loaded
echo -n "2. Checking for qwen2.5:7b model... "
if curl -s http://localhost:11434/api/tags | grep -q "qwen2.5:7b"; then
    echo "✅ Loaded"
else
    echo "⚠️  Not found"
    echo "   Install with: ollama pull qwen2.5:7b"
fi

# Check backend is running
echo -n "3. Checking Flask backend... "
if curl -s http://localhost:5001/api/health > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Not running"
    echo "   Start with: cd backend && python app.py"
    exit 1
fi

# Test LLM endpoint
echo -n "4. Testing LLM health endpoint... "
response=$(curl -s http://localhost:5001/api/llm/health)
if echo "$response" | grep -q '"available": true'; then
    echo "✅ Available"
else
    echo "❌ Unavailable"
    echo "   Response: $response"
    exit 1
fi

echo ""
echo "✅ All systems ready! LLM integration is working."
```

Make executable and run:
```bash
chmod +x test_llm.sh
./test_llm.sh
```

---

## Troubleshooting

### "Connection refused" errors
**Problem:** Ollama isn't running
**Solution:** Run `ollama serve` in a terminal

### "Model not found" errors
**Problem:** Model not downloaded
**Solution:** Run `ollama pull qwen2.5:7b`

### Very slow responses (>10s)
**Problem:** Model too large for your hardware
**Solution:** Use smaller model: `ollama pull llama3.2:3b`

### Out of memory errors
**Problem:** Not enough RAM
**Solution:** 
- Close other applications
- Use 3B model instead of 7B
- Reduce `max_tokens` in prompts

---

## Performance Expectations

### With GPU (Apple Silicon M1/M2/M3, NVIDIA, AMD)
- First request: ~2 seconds
- Cached requests: <100ms
- Concurrent requests: Handles 3-5 simultaneously

### CPU Only (Intel i5/i7, AMD Ryzen 5/7)
- First request: ~5 seconds
- Cached requests: <100ms
- Concurrent requests: Handles 1-2 simultaneously

### Caching
- Identical explanations: cached 24 hours
- Cache hit rate: ~60-70% in normal use
- Saves ~2-4 seconds per cached request

---

## What Makes This Different from Duolingo?

| Feature | Duolingo (OpenAI API) | Kapp (Local LLM) |
|---------|----------------------|------------------|
| **Privacy** | Sends data to OpenAI | All local, no external calls |
| **Cost** | Pay per API call | Free after setup |
| **Offline** | Requires internet | Works offline |
| **Speed** | 1-2s (network latency) | 2-5s (local processing) |
| **Quality** | GPT-4 level | Good (7B model level) |
| **Customisation** | Limited | Full prompt control |

---

## Next Steps

1. ✅ Install Ollama and download model (~10 minutes)
2. ✅ Create backend LLM service (~30 minutes)
3. ✅ Create API endpoints (~20 minutes)
4. ✅ Build explanation modal UI (~40 minutes)
5. ✅ Integration testing (~20 minutes)
6. ✅ Polish and error handling (~30 minutes)

**Total time: ~2.5 hours for MVP**

---

## Resources

- **Full Plan**: See `LLM_INTEGRATION_PLAN.md` for detailed implementation
- **Ollama Docs**: [ollama.com/docs](https://ollama.com/docs)
- **Qwen Model**: [ollama.com/library/qwen2.5](https://ollama.com/library/qwen2.5)
- **Llama Models**: [ollama.com/library/llama3.1](https://ollama.com/library/llama3.1)

Ready to start? Follow the implementation phases in order! 🚀

