# How Duolingo Uses LLMs - Research Summary

## Overview

Duolingo is reportedly OpenAI's largest API customer, having integrated GPT-4 and GPT-5 extensively throughout their platform. Their implementation demonstrates how LLMs can transform a language learning app from static flashcards into an interactive, AI-powered tutor.

---

## Key Findings

### 1. Duolingo is More Than a Wrapper

Whilst Duolingo heavily uses OpenAI's API, they're not simply a "wrapper" - they've built sophisticated systems around the LLM:

- **Prompt Engineering Layer**: Carefully crafted system prompts for each feature
- **Context Management**: Inject user level, learning history, and performance data
- **Content Moderation**: Filter inappropriate AI responses
- **Caching System**: Cache common responses to reduce API costs
- **Hybrid Approach**: Combine LLM outputs with traditional rule-based systems
- **Quality Control**: Human review of AI-generated content for courses

### 2. Architecture Pattern

```
User Input
    ↓
Frontend Validation
    ↓
API Gateway (Rate Limiting, Auth)
    ↓
Backend Services (Python/Go)
    ├─ Feature Router
    ├─ Context Builder (user level, history, card difficulty)
    ├─ Prompt Template Manager
    └─ Response Cache Check
         ↓
    OpenAI API (GPT-4/5)
         ↓
    Response Post-Processing
    ├─ Format validation
    ├─ Safety checks
    └─ Logging/Analytics
         ↓
    Return to User
```

---

## LLM-Powered Features in Duolingo

### 🎯 1. Explain My Answer

**Purpose**: Help learners understand their mistakes

**User Flow**:
1. User makes mistake in exercise
2. Taps "Why is this wrong?" or "Explain"
3. Sees AI-generated explanation

**LLM Input**:
- User's incorrect answer
- Correct answer
- Exercise type (translation, fill-in-blank, etc.)
- User's CEFR level
- Recent exercise history

**LLM Output**:
- Explanation of the specific error
- Grammar rule explanation
- Example showing correct usage
- Encouragement/motivation

**Example**:
```
User Answer: "Je vais à le magasin"
Correct: "Je vais au magasin"

AI Explanation:
"You're close! When 'à' (to) is used with 'le' (the), they combine 
to form 'au'. This is called a contraction. So 'à le' becomes 'au'.

Think of it like English 'cannot' = 'can not', but mandatory in French!

✅ Je vais au magasin (I go to the store)
❌ Je vais à le magasin"
```

### 💬 2. Roleplay Conversations (Duolingo Max)

**Purpose**: Practice real conversations with AI characters

**User Flow**:
1. Start conversation scenario (e.g., "Order food at café")
2. AI plays character (waiter, friend, etc.)
3. User responds in target language
4. AI responds naturally and continues conversation
5. AI gently corrects mistakes in context

**LLM Input**:
- Scenario/scene setting
- Character description
- User's current message
- Conversation history
- User's proficiency level
- Target learning objectives

**LLM Output**:
- Natural character response
- Contextual corrections (embedded naturally)
- Difficulty adapted to user level

**Example**:
```
Scenario: Ordering coffee in Seoul

User: "저는 커피 마시고 싶어요" (I want to drink coffee)

AI Barista: "아, 커피 주문하시겠어요? 어떤 커피를 마시고 싶으세요?" 
             (Oh, would you like to order coffee? What kind of coffee 
             would you like to drink?)

[Note how AI maintains conversation whilst modeling correct 
politeness level and introducing new vocabulary naturally]
```

### 📹 3. Video Call Feature (Max Tier)

**Purpose**: Real-time conversation practice with AI tutor

**Technical Stack**:
- Speech-to-Text (Whisper API or similar)
- LLM processing (GPT-4)
- Text-to-Speech (ElevenLabs or similar)
- Video avatar rendering

**User Flow**:
1. Start video call with AI character
2. Speak in target language
3. AI responds with voice and animated character
4. Real-time conversation practice

**LLM Role**:
- Process transcribed speech
- Generate contextual responses
- Adapt difficulty in real-time
- Track conversation topics
- Provide session summary

### 🎮 4. Adaptive Exercise Generation

**Purpose**: Create personalised practice exercises

**User Flow**:
1. System analyses user's weak areas
2. Generates targeted exercises
3. Presents to user in practice session

**LLM Input**:
- User's mistake patterns
- Grammar topics user struggles with
- Vocabulary gaps
- Current course position

**LLM Output**:
- Custom exercises targeting weaknesses
- Progressive difficulty
- Varied exercise types

**Example**:
```
Analysis: User struggles with Korean particles 이/가 vs 은/는

Generated Exercise 1:
"Fill in the blank: 저___ 학생이에요" (I am a student)
Answer: 는

Generated Exercise 2:
"Which is correct?
A) 고양이가 귀여워요
B) 고양이는 귀여워요"
[Context: Seeing a specific cat for first time]
Answer: A
```

### 💡 5. Progressive Hint System

**Purpose**: Help without giving away answer

**User Flow**:
1. User stuck on exercise
2. Requests hint (can request multiple times)
3. Gets increasingly specific hints

**LLM Input**:
- Exercise question
- Correct answer
- Number of previous hints
- User's level

**LLM Output** (graduated):
```
Hint 1: "Think about which particle is used for subjects of actions"
Hint 2: "The particle 이/가 marks the subject performing the action"
Hint 3: "After '고양이' (cat), you need '가' because it's the subject"
```

### 🎯 6. Smart Review Queue

**Purpose**: Optimise spaced repetition with AI insights

**LLM Role**:
- Analyse which mistakes indicate deeper misunderstanding
- Recommend when to reintroduce concepts
- Generate review exercises that connect related concepts

**Traditional SRS**: Based purely on time intervals
**AI-Enhanced SRS**: Considers *why* user made mistake

### 🌍 7. Contextual Translation

**Purpose**: Explain why multiple translations are valid

**Example**:
```
Korean: "먹었어"
User translates: "ate"
Also correct: "have eaten", "had eaten", "I ate"

AI Explanation:
"Great! Korean doesn't always specify tense as precisely as English.
먹었어 uses past tense (-었-) but the exact English translation 
depends on context:

- 밥 먹었어? = 'Did you eat?' or 'Have you eaten?'
- 어제 먹었어 = 'I ate yesterday'
- 벌써 먹었어 = 'I've already eaten'

All your translations are correct depending on when it happened!"
```

---

## Technical Implementation Details

### Prompt Engineering Techniques

#### 1. System Prompts

Duolingo uses carefully crafted system prompts for each feature:

```python
EXPLAIN_ANSWER_SYSTEM_PROMPT = """
You are an expert language tutor helping a {language} learner at {level} level.

Your role:
- Explain mistakes clearly and concisely
- Use simple language appropriate for their level
- Be encouraging and supportive
- Focus on the specific error, not overwhelming detail
- Provide one concrete example
- Keep response under 150 words

Tone: Friendly, patient, encouraging
Format: Short paragraphs, use emojis sparingly
"""
```

#### 2. Context Injection

```python
def build_explain_context(user_answer, correct_answer, user_data):
    return f"""
    Exercise: Translate "{exercise.source_text}"
    User's answer: "{user_answer}"
    Correct answer: "{correct_answer}"
    
    User context:
    - CEFR Level: {user_data.level}
    - Recent mistakes: {user_data.recent_mistakes[:5]}
    - This error type: {user_data.error_type_count} times
    
    Explain why the user's answer is incorrect and how to fix it.
    """
```

#### 3. Response Formatting

```python
def parse_llm_response(raw_response):
    # Extract structured data from LLM output
    # Validate format
    # Check for inappropriate content
    # Add metadata
    return {
        'explanation': clean_text(raw_response),
        'source': 'gpt-4',
        'confidence': calculate_confidence(raw_response),
        'fallback_available': has_rule_based_explanation()
    }
```

### Cost Optimisation Strategies

#### 1. Aggressive Caching

```python
# Cache key includes user level, not individual user
# Allows cache sharing across users at same level
cache_key = hash(f"{exercise_id}|{error_type}|{user_level}")

# Common explanations cached for 30 days
# Reduces API calls by ~60-70%
```

#### 2. Tiered Model Usage

- **GPT-4**: Complex explanations, conversations
- **GPT-3.5**: Simple hints, routine translations
- **Fine-tuned models**: Common error explanations
- **Rule-based**: Grammar rules, verb conjugations

#### 3. Batch Processing

```python
# Generate explanations for common mistakes in batches
# Pre-generate conversation responses for typical scenarios
# Cache entire conversation trees for common topics
```

### Graceful Degradation

```python
async def get_explanation(exercise, user_answer, user_data):
    try:
        # Try LLM first
        return await llm_client.explain(exercise, user_answer, user_data)
    except LLMTimeoutError:
        # Fallback to cached template
        return template_explanation(exercise.error_type)
    except LLMUnavailableError:
        # Fallback to rule-based system
        return rule_based_explanation(exercise)
    except Exception:
        # Last resort: generic message
        return "Check the correct answer and try to spot the difference!"
```

---

## Cost Implications

### Estimated API Usage

Duolingo has **30+ million active users**. If even 10% use LLM features:

```
Daily LLM requests:
- 3M users × 5 exercises/day × 20% error rate = 3M explanations
- 500K conversation mode users × 10 messages = 5M chat completions
- 100K video calls × 15 messages = 1.5M chat completions

Total: ~10M API calls/day

At OpenAI pricing:
- GPT-4: $0.03/1K input + $0.06/1K output
- Average: ~500 input + ~300 output tokens per request
- Cost: ~$0.03 per request

Daily cost: $300,000
Monthly cost: $9,000,000
Annual cost: $108,000,000
```

**This is why they're OpenAI's largest customer!**

### How They Reduce Costs

1. **Caching**: 70% cache hit rate → save $75M/year
2. **Tiered models**: GPT-3.5 for simple tasks → save $40M/year
3. **Batching**: Pre-generate common scenarios → save $20M/year
4. **Fine-tuning**: Custom models for specific tasks → save $15M/year

**Estimated actual cost: ~$40-50M/year** (still substantial!)

---

## Key Takeaways for Kapp

### ✅ What to Adopt

1. **Prompt Engineering**: Invest time in crafting good system prompts
2. **Context Injection**: Include user level, history, card difficulty
3. **Caching Strategy**: Cache common explanations to improve speed
4. **Graceful Degradation**: Have fallbacks when LLM unavailable
5. **Progressive Features**: Start simple (explanations), add advanced later

### ❌ What Not to Copy

1. **Video calls**: Too complex for MVP
2. **Massive infrastructure**: Overkill for single-user app
3. **Multiple models**: Stick to one good local model
4. **Real-time translation**: Not needed for flashcards

### 🎯 Kapp's Advantages with Local LLM

| Aspect | Duolingo (OpenAI API) | Kapp (Local LLM) |
|--------|----------------------|------------------|
| **Cost** | $40M+/year | Free (after hardware) |
| **Privacy** | Data sent to OpenAI | 100% local |
| **Latency** | 1-2s (network) | 2-5s (processing) |
| **Customisation** | Limited by API | Full control |
| **Offline** | Requires internet | Works offline |
| **Scale** | 30M users | 1 user (you) |

**Conclusion**: Local LLM is perfect for Kapp because:
- Single-user app (don't need massive scale)
- Privacy-conscious Korean learners
- No ongoing costs
- Can fine-tune specifically for Korean learning
- Offline capability for study anywhere

---

## Recommended Implementation Priorities

### Phase 1: Core Features (Week 1-2)
1. ✅ Vocabulary explanations
2. ✅ Example sentence generation
3. ✅ Translation assistance

### Phase 2: Interactive (Week 3-4)
4. 💬 Conversation practice mode
5. 💡 Progressive hint system

### Phase 3: Advanced (Month 2+)
6. 🎯 Adaptive exercise generation
7. 📊 Learning path recommendations
8. 🌏 Cultural context enrichment

---

## References

- [Duolingo Max announcement](https://blog.duolingo.com/duolingo-max/) - Official blog post about GPT-4 features
- [OpenAI case study](https://openai.com/customers/duolingo) - Partnership details
- [Duolingo engineering blog](https://blog.duolingo.com/tag/engineering/) - Technical implementation insights

---

**Created**: November 6, 2025
**For**: Kapp Korean Learning App LLM Integration Research
**Next**: See `LLM_INTEGRATION_PLAN.md` for implementation details

