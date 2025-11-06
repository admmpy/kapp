#!/bin/bash
# LLM Integration Readiness Check
# Tests if Ollama is installed and ready for Kapp integration

set -e

RESET='\033[0m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BLUE}🧠 Kapp LLM Integration Readiness Check${RESET}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

# Check 1: Ollama installed
echo -n "1️⃣  Checking if Ollama is installed... "
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✅ Installed${RESET}"
    OLLAMA_VERSION=$(ollama --version 2>&1 | head -n1)
    echo "   Version: $OLLAMA_VERSION"
else
    echo -e "${RED}❌ Not installed${RESET}"
    echo ""
    echo -e "${YELLOW}Install Ollama:${RESET}"
    echo "   macOS:   brew install ollama"
    echo "   Linux:   curl -fsSL https://ollama.com/install.sh | sh"
    echo "   Windows: Download from https://ollama.com"
    exit 1
fi

echo ""

# Check 2: Ollama service running
echo -n "2️⃣  Checking if Ollama service is running... "
if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Running${RESET}"
else
    echo -e "${RED}❌ Not running${RESET}"
    echo ""
    echo -e "${YELLOW}Start Ollama service:${RESET}"
    echo "   ollama serve"
    echo ""
    echo "   (Leave it running in a terminal)"
    exit 1
fi

echo ""

# Check 3: Check for recommended models
echo "3️⃣  Checking for recommended models..."

MODELS_RESPONSE=$(curl -s http://localhost:11434/api/tags)
FOUND_QWEN=false
FOUND_LLAMA=false
FOUND_ANY=false

if echo "$MODELS_RESPONSE" | grep -q "qwen2.5:7b"; then
    echo -e "   ${GREEN}✅ qwen2.5:7b (Recommended - best Korean support)${RESET}"
    FOUND_QWEN=true
    FOUND_ANY=true
fi

if echo "$MODELS_RESPONSE" | grep -q "llama3.1:8b"; then
    echo -e "   ${GREEN}✅ llama3.1:8b (Alternative - good all-rounder)${RESET}"
    FOUND_LLAMA=true
    FOUND_ANY=true
fi

if echo "$MODELS_RESPONSE" | grep -q "llama3.2:3b"; then
    echo -e "   ${GREEN}✅ llama3.2:3b (Fast option)${RESET}"
    FOUND_ANY=true
fi

if [ "$FOUND_ANY" = false ]; then
    echo -e "   ${RED}❌ No recommended models found${RESET}"
    echo ""
    echo -e "${YELLOW}Download a model (choose one):${RESET}"
    echo "   ollama pull qwen2.5:7b      # Recommended (4GB)"
    echo "   ollama pull llama3.1:8b     # Alternative (4.7GB)"
    echo "   ollama pull llama3.2:3b     # Faster, smaller (2GB)"
    exit 1
fi

echo ""

# Check 4: Test model inference
echo -n "4️⃣  Testing model inference... "

if [ "$FOUND_QWEN" = true ]; then
    TEST_MODEL="qwen2.5:7b"
elif [ "$FOUND_LLAMA" = true ]; then
    TEST_MODEL="llama3.1:8b"
else
    TEST_MODEL=$(echo "$MODELS_RESPONSE" | grep -o '"name":"[^"]*"' | head -n1 | cut -d'"' -f4)
fi

# Test with a simple Korean prompt
TEST_PROMPT="Translate to English: 안녕하세요"
TEST_RESPONSE=$(curl -s -X POST http://localhost:11434/api/generate \
    -d "{\"model\": \"$TEST_MODEL\", \"prompt\": \"$TEST_PROMPT\", \"stream\": false}" \
    2>&1)

if echo "$TEST_RESPONSE" | grep -q "response"; then
    echo -e "${GREEN}✅ Working${RESET}"
    echo "   Model: $TEST_MODEL"
else
    echo -e "${RED}❌ Failed${RESET}"
    echo "   Error: $TEST_RESPONSE"
    exit 1
fi

echo ""

# Check 5: System resources
echo "5️⃣  Checking system resources..."

# Available memory
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    TOTAL_MEM_GB=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
    echo "   RAM: ${TOTAL_MEM_GB}GB total"
    
    if [ "$TOTAL_MEM_GB" -ge 16 ]; then
        echo -e "   ${GREEN}✅ Excellent (16GB+)${RESET}"
    elif [ "$TOTAL_MEM_GB" -ge 8 ]; then
        echo -e "   ${YELLOW}⚠️  Adequate (8GB+) - use 3B or 7B models${RESET}"
    else
        echo -e "   ${RED}❌ Insufficient (<8GB) - may struggle with LLMs${RESET}"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    TOTAL_MEM_GB=$(free -g | awk '/^Mem:/{print $2}')
    echo "   RAM: ${TOTAL_MEM_GB}GB total"
    
    if [ "$TOTAL_MEM_GB" -ge 16 ]; then
        echo -e "   ${GREEN}✅ Excellent (16GB+)${RESET}"
    elif [ "$TOTAL_MEM_GB" -ge 8 ]; then
        echo -e "   ${YELLOW}⚠️  Adequate (8GB+) - use 3B or 7B models${RESET}"
    else
        echo -e "   ${RED}❌ Insufficient (<8GB) - may struggle with LLMs${RESET}"
    fi
fi

# GPU availability
echo ""
echo -n "   GPU: "
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - check for Apple Silicon
    ARCH=$(uname -m)
    if [[ "$ARCH" == "arm64" ]]; then
        echo -e "${GREEN}Apple Silicon detected (Metal acceleration available)${RESET}"
    else
        echo -e "${YELLOW}Intel Mac (CPU only)${RESET}"
    fi
elif command -v nvidia-smi &> /dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n1)
    echo -e "${GREEN}NVIDIA GPU detected: $GPU_NAME${RESET}"
elif command -v rocm-smi &> /dev/null; then
    echo -e "${GREEN}AMD GPU detected (ROCm available)${RESET}"
else
    echo -e "${YELLOW}No GPU detected (CPU-only mode)${RESET}"
fi

echo ""

# Check 6: Backend status (optional)
echo -n "6️⃣  Checking Flask backend (optional)... "
if curl -sf http://localhost:5001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Running${RESET}"
    
    # Check if LLM routes are available
    if curl -sf http://localhost:5001/api/llm/health > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ LLM routes already integrated${RESET}"
    else
        echo -e "   ${YELLOW}⚠️  LLM routes not yet implemented${RESET}"
    fi
else
    echo -e "${YELLOW}⚠️  Not running (will be needed after backend implementation)${RESET}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${GREEN}✅ Ollama is ready for Kapp LLM integration!${RESET}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo -e "${BLUE}Next Steps:${RESET}"
echo "  1. Create feature branch: git checkout -b feature/local-llm-integration"
echo "  2. Follow implementation guide in LLM_INTEGRATION_PLAN.md"
echo "  3. Start with Phase 1: Backend implementation"
echo ""
echo -e "${BLUE}Quick Start:${RESET}"
echo "  See LLM_QUICKSTART.md for step-by-step guide"
echo ""

