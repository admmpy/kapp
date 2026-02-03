#!/usr/bin/env python3
"""Add final 3 grammar lessons (65 exercises) to complete Grammar unit"""
import json
from pathlib import Path

lessons_file = Path(__file__).parent.parent / "data" / "korean_lessons.json"

with open(lessons_file, "r", encoding="utf-8") as f:
    data = json.load(f)

grammar_unit = data['courses'][0]['units'][-1]
print(f"Current lessons: {len(grammar_unit['lessons'])}")
print(f"Current exercises: {sum(len(l['exercises']) for l in grammar_unit['lessons'])}")

# Final 3 lessons
final_lessons = [
    {
        "title": "Negation: 안 and 못",
        "description": "Learn to make negative sentences",
        "estimated_minutes": 15,
        "grammar_explanation": "Two ways to negate in Korean:\n\n안 (an) - General negation:\n- Place before action verb\n- 안 가요 (don't go)\n\n못 (mot) - Cannot/inability:\n- Indicates can't do something\n- 못 가요 (can't go)\n\nFor 이다, 하다, use -지 않다/-지 못하다",
        "grammar_tip": "안 = don't want to/not doing, 못 = can't/unable to",
        "exercises": [
            {"exercise_type": "grammar", "question": "가다 (to go) → negative", "instruction": "Make it negative with 안", "options": ["안 가요", "가 안요", "안가요", "가요 안"], "correct_answer": "안 가요", "explanation": "Place 안 before the verb stem"},
            {"exercise_type": "grammar", "question": "먹다 (to eat) → negative", "instruction": "Make it negative with 안", "options": ["안 먹어요", "먹 안어요", "안먹어요", "먹어 안요"], "correct_answer": "안 먹어요", "explanation": "안 + verb"},
            {"exercise_type": "grammar", "question": "보다 (to see) → cannot", "instruction": "Express inability with 못", "options": ["못 봐요", "봐 못요", "못봐요", "봐요 못"], "correct_answer": "못 봐요", "explanation": "못 shows inability"},
            {"exercise_type": "grammar", "question": "자다 (to sleep) → cannot", "instruction": "Express inability with 못", "options": ["못 자요", "자 못요", "못자요", "자요 못"], "correct_answer": "못 자요", "explanation": "못 + verb"},
            {"exercise_type": "grammar", "question": "읽다 (to read) → negative", "instruction": "Make it negative with 안", "options": ["안 읽어요", "읽 안어요", "안읽어요", "읽어 안요"], "correct_answer": "안 읽어요", "explanation": "안 + verb"},
            {"exercise_type": "grammar", "question": "Which means 'I can't go'?", "instruction": "Choose the correct expression", "options": ["못 가요", "안 가요", "가못요", "가안요"], "correct_answer": "못 가요", "explanation": "못 expresses inability"},
            {"exercise_type": "grammar", "question": "Which means 'I don't eat'?", "instruction": "Choose the correct expression", "options": ["안 먹어요", "못 먹어요", "먹안어요", "먹못어요"], "correct_answer": "안 먹어요", "explanation": "안 for general negation"},
            {"exercise_type": "grammar", "question": "오다 (to come) → negative", "instruction": "Make it negative with 안", "options": ["안 와요", "와 안요", "안와요", "와요 안"], "correct_answer": "안 와요", "explanation": "안 + verb"},
            {"exercise_type": "grammar", "question": "듣다 (to listen) → cannot", "instruction": "Express inability with 못", "options": ["못 들어요", "들 못어요", "못들어요", "들어 못요"], "correct_answer": "못 들어요", "explanation": "못 + verb (ㄷ irregular)"},
            {"exercise_type": "grammar", "question": "쓰다 (to write) → negative", "instruction": "Make it negative with 안", "options": ["안 써요", "써 안요", "안써요", "써요 안"], "correct_answer": "안 써요", "explanation": "안 + verb"},
            {"exercise_type": "grammar", "question": "마시다 (to drink) → cannot", "instruction": "Express inability with 못", "options": ["못 마셔요", "마셔 못요", "못마셔요", "마셔요 못"], "correct_answer": "못 마셔요", "explanation": "못 + verb"},
            {"exercise_type": "grammar", "question": "공부하다 (to study) → negative", "instruction": "Make it negative with 안", "options": ["공부 안 해요", "안 공부해요", "공부안해요", "공부해 안요"], "correct_answer": "공부 안 해요", "explanation": "For 하다 verbs: noun + 안 + 해요"},
            {"exercise_type": "grammar", "question": "살다 (to live) → negative", "instruction": "Make it negative with 안", "options": ["안 살아요", "살 안아요", "안살아요", "살아 안요"], "correct_answer": "안 살아요", "explanation": "안 + verb"},
            {"exercise_type": "grammar", "question": "일하다 (to work) → cannot", "instruction": "Express inability with 못", "options": ["일 못 해요", "못 일해요", "일못해요", "일해 못요"], "correct_answer": "일 못 해요", "explanation": "For 하다 verbs: noun + 못 + 해요"},
            {"exercise_type": "grammar", "question": "앉다 (to sit) → negative", "instruction": "Make it negative with 안", "options": ["안 앉아요", "앉 안아요", "안앉아요", "앉아 안요"], "correct_answer": "안 앉아요", "explanation": "안 + verb"},
            {"exercise_type": "grammar", "question": "서다 (to stand) → cannot", "instruction": "Express inability with 못", "options": ["못 서요", "서 못요", "못서요", "서요 못"], "correct_answer": "못 서요", "explanation": "못 + verb"},
            {"exercise_type": "grammar", "question": "놀다 (to play) → negative", "instruction": "Make it negative with 안", "options": ["안 놀아요", "놀 안아요", "안놀아요", "놀아 안요"], "correct_answer": "안 놀아요", "explanation": "안 + verb"},
            {"exercise_type": "grammar", "question": "배우다 (to learn) → cannot", "instruction": "Express inability with 못", "options": ["못 배워요", "배워 못요", "못배워요", "배워요 못"], "correct_answer": "못 배워요", "explanation": "못 + verb"},
            {"exercise_type": "grammar", "question": "주다 (to give) → negative", "instruction": "Make it negative with 안", "options": ["안 줘요", "줘 안요", "안줘요", "줘요 안"], "correct_answer": "안 줘요", "explanation": "안 + verb"},
            {"exercise_type": "grammar", "question": "걷다 (to walk) → cannot", "instruction": "Express inability with 못", "options": ["못 걸어요", "걸 못어요", "못걸어요", "걸어 못요"], "correct_answer": "못 걸어요", "explanation": "못 + verb (ㄷ irregular)"}
        ]
    },
    {
        "title": "Question Formation",
        "description": "Learn to ask questions in Korean",
        "estimated_minutes": 15,
        "grammar_explanation": "Korean questions:\n\n1. Yes/No questions:\n- Add rising intonation to statements\n- 가요? (Are you going?)\n\n2. WH-questions:\n- 누구 (who), 무엇/뭐 (what)\n- 어디 (where), 언제 (when)\n- 왜 (why), 어떻게 (how)\n- 얼마나 (how much/many)",
        "grammar_tip": "Question words replace the information you're asking about in the sentence",
        "exercises": [
            {"exercise_type": "vocabulary", "question": "What does 누구 mean?", "instruction": "Select the correct translation", "korean_text": "누구", "romanization": "nugu", "options": ["Who", "What", "Where", "When"], "correct_answer": "Who", "explanation": "누구 = who"},
            {"exercise_type": "vocabulary", "question": "What does 뭐 mean?", "instruction": "Select the correct translation", "korean_text": "뭐", "romanization": "mwo", "options": ["Who", "What", "Where", "When"], "correct_answer": "What", "explanation": "뭐 = what (informal)"},
            {"exercise_type": "vocabulary", "question": "What does 어디 mean?", "instruction": "Select the correct translation", "korean_text": "어디", "romanization": "eodi", "options": ["Who", "What", "Where", "When"], "correct_answer": "Where", "explanation": "어디 = where"},
            {"exercise_type": "vocabulary", "question": "What does 언제 mean?", "instruction": "Select the correct translation", "korean_text": "언제", "romanization": "eonje", "options": ["Who", "What", "Where", "When"], "correct_answer": "When", "explanation": "언제 = when"},
            {"exercise_type": "vocabulary", "question": "What does 왜 mean?", "instruction": "Select the correct translation", "korean_text": "왜", "romanization": "wae", "options": ["Who", "What", "Why", "How"], "correct_answer": "Why", "explanation": "왜 = why"},
            {"exercise_type": "vocabulary", "question": "What does 어떻게 mean?", "instruction": "Select the correct translation", "korean_text": "어떻게", "romanization": "eotteoke", "options": ["Where", "When", "Why", "How"], "correct_answer": "How", "explanation": "어떻게 = how"},
            {"exercise_type": "grammar", "question": "Ask 'Who is it?'", "instruction": "Choose the correct question", "options": ["누구예요?", "뭐예요?", "어디예요?", "언제예요?"], "correct_answer": "누구예요?", "explanation": "누구 = who"},
            {"exercise_type": "grammar", "question": "Ask 'What is this?'", "instruction": "Choose the correct question", "options": ["이게 누구예요?", "이게 뭐예요?", "이게 어디예요?", "이게 언제예요?"], "correct_answer": "이게 뭐예요?", "explanation": "뭐 = what"},
            {"exercise_type": "grammar", "question": "Ask 'Where do you go?'", "instruction": "Choose the correct question", "options": ["누구 가요?", "뭐 가요?", "어디 가요?", "언제 가요?"], "correct_answer": "어디 가요?", "explanation": "어디 = where"},
            {"exercise_type": "grammar", "question": "Ask 'When do you study?'", "instruction": "Choose the correct question", "options": ["누구 공부해요?", "뭐 공부해요?", "어디 공부해요?", "언제 공부해요?"], "correct_answer": "언제 공부해요?", "explanation": "언제 = when"},
            {"exercise_type": "grammar", "question": "Ask 'Why are you sad?'", "instruction": "Choose the correct question", "options": ["왜 슬퍼요?", "어디 슬퍼요?", "언제 슬퍼요?", "누구 슬퍼요?"], "correct_answer": "왜 슬퍼요?", "explanation": "왜 = why"},
            {"exercise_type": "grammar", "question": "Ask 'How do you do it?'", "instruction": "Choose the correct question", "options": ["왜 해요?", "어떻게 해요?", "언제 해요?", "어디 해요?"], "correct_answer": "어떻게 해요?", "explanation": "어떻게 = how"},
            {"exercise_type": "grammar", "question": "Ask 'Who came?'", "instruction": "Choose the correct question", "options": ["누가 왔어요?", "뭐가 왔어요?", "어디가 왔어요?", "언제가 왔어요?"], "correct_answer": "누가 왔어요?", "explanation": "누구 + 가 = 누가 (who as subject)"},
            {"exercise_type": "grammar", "question": "Ask 'What happened?'", "instruction": "Choose the correct question", "options": ["누가 있었어요?", "뭐가 있었어요?", "어디가 있었어요?", "언제가 있었어요?"], "correct_answer": "뭐가 있었어요?", "explanation": "뭐 + 가 = 뭐가/무엇이 (what as subject)"},
            {"exercise_type": "grammar", "question": "Ask 'Where is school?'", "instruction": "Choose the correct question", "options": ["학교가 누구예요?", "학교가 뭐예요?", "학교가 어디예요?", "학교가 언제예요?"], "correct_answer": "학교가 어디예요?", "explanation": "어디 = where"},
            {"exercise_type": "grammar", "question": "Ask 'When is your birthday?'", "instruction": "Choose the correct question", "options": ["생일이 누구예요?", "생일이 뭐예요?", "생일이 어디예요?", "생일이 언제예요?"], "correct_answer": "생일이 언제예요?", "explanation": "언제 = when"},
            {"exercise_type": "grammar", "question": "Ask 'Why don't you eat?'", "instruction": "Choose the correct question", "options": ["왜 안 먹어요?", "어디 안 먹어요?", "언제 안 먹어요?", "누구 안 먹어요?"], "correct_answer": "왜 안 먹어요?", "explanation": "왜 = why"},
            {"exercise_type": "grammar", "question": "Ask 'How do you come?'", "instruction": "Choose the correct question", "options": ["왜 와요?", "어떻게 와요?", "언제 와요?", "어디 와요?"], "correct_answer": "어떻게 와요?", "explanation": "어떻게 = how"},
            {"exercise_type": "grammar", "question": "Ask 'Who do you meet?'", "instruction": "Choose the correct question", "options": ["누구를 만나요?", "뭐를 만나요?", "어디를 만나요?", "언제를 만나요?"], "correct_answer": "누구를 만나요?", "explanation": "누구 + 를 (who as object)"},
            {"exercise_type": "grammar", "question": "Ask 'What do you eat?'", "instruction": "Choose the correct question", "options": ["누구를 먹어요?", "뭐를 먹어요?", "어디를 먹어요?", "언제를 먹어요?"], "correct_answer": "뭐를 먹어요?", "explanation": "뭐 + 를 (what as object)"},
            {"exercise_type": "grammar", "question": "Ask 'Where do you live?'", "instruction": "Choose the correct question", "options": ["누구에서 살아요?", "뭐에서 살아요?", "어디에서 살아요?", "언제에서 살아요?"], "correct_answer": "어디에서 살아요?", "explanation": "어디 + 에서 = where (location of action)"},
            {"exercise_type": "grammar", "question": "Ask 'When do you sleep?'", "instruction": "Choose the correct question", "options": ["누구에 자요?", "뭐에 자요?", "어디에 자요?", "언제 자요?"], "correct_answer": "언제 자요?", "explanation": "언제 = when"},
            {"exercise_type": "grammar", "question": "Ask 'Why do you study Korean?'", "instruction": "Choose the correct question", "options": ["왜 한국어를 공부해요?", "어디 한국어를 공부해요?", "누구 한국어를 공부해요?", "뭐 한국어를 공부해요?"], "correct_answer": "왜 한국어를 공부해요?", "explanation": "왜 = why"},
            {"exercise_type": "grammar", "question": "Ask 'How do you know?'", "instruction": "Choose the correct question", "options": ["왜 알아요?", "어떻게 알아요?", "언제 알아요?", "어디 알아요?"], "correct_answer": "어떻게 알아요?", "explanation": "어떻게 = how"},
            {"exercise_type": "grammar", "question": "Ask 'Who are you?' (polite)", "instruction": "Choose the correct question", "options": ["누구세요?", "뭐세요?", "어디세요?", "언제세요?"], "correct_answer": "누구세요?", "explanation": "누구 + 세요 = who are you (polite)"}
        ]
    },
    {
        "title": "Connecting Sentences",
        "description": "Learn to connect ideas and clauses",
        "estimated_minutes": 15,
        "grammar_explanation": "Korean sentence connectors:\n\n-고 (go) - And (sequential actions):\n- 학교에 가고 공부해요 (go to school and study)\n\n-지만 (jiman) - But/Although:\n- 비가 오지만 가요 (It's raining but I'm going)\n\n-아/어서 (aseo/eoseo) - Because/So:\n- 피곤해서 자요 (I'm tired so I sleep)\n\n-(으)니까 (eunikka) - Because (strong reason):\n- 바쁘니까 못 가요 (I'm busy so I can't go)",
        "grammar_tip": "-고 links equal actions, -지만 shows contrast, -아/어서 and -(으)니까 show cause",
        "exercises": [
            {"exercise_type": "grammar", "question": "Connect: 'I eat rice ___ drink water'", "instruction": "Choose the connector for 'and'", "options": ["밥을 먹고 물을 마셔요", "밥을 먹지만 물을 마셔요", "밥을 먹어서 물을 마셔요", "밥을 먹으니까 물을 마셔요"], "correct_answer": "밥을 먹고 물을 마셔요", "explanation": "-고 connects sequential actions"},
            {"exercise_type": "grammar", "question": "Connect: 'It's cold ___ I go out'", "instruction": "Choose the connector for 'but'", "options": ["추워고 나가요", "춥지만 나가요", "추워서 나가요", "추우니까 나가요"], "correct_answer": "춥지만 나가요", "explanation": "-지만 shows contrast"},
            {"exercise_type": "grammar", "question": "Connect: 'I'm hungry ___ I eat'", "instruction": "Choose the connector for 'so'", "options": ["배고프고 먹어요", "배고프지만 먹어요", "배고파서 먹어요", "배고프니까 먹어요"], "correct_answer": "배고파서 먹어요", "explanation": "-아/어서 shows cause and effect"},
            {"exercise_type": "grammar", "question": "Connect: 'It's late ___ let's go'", "instruction": "Choose the connector for 'so' (strong reason)", "options": ["늦어고 가요", "늦지만 가요", "늦어서 가요", "늦으니까 가요"], "correct_answer": "늦으니까 가요", "explanation": "-(으)니까 for strong reason/suggestion"},
            {"exercise_type": "grammar", "question": "Connect: 'I study ___ play'", "instruction": "Choose the connector for 'and'", "options": ["공부하고 놀아요", "공부하지만 놀아요", "공부해서 놀아요", "공부하니까 놀아요"], "correct_answer": "공부하고 놀아요", "explanation": "-고 connects actions"},
            {"exercise_type": "grammar", "question": "Connect: 'It's expensive ___ I buy it'", "instruction": "Choose the connector for 'but'", "options": ["비싸고 사요", "비싸지만 사요", "비싸서 사요", "비싸니까 사요"], "correct_answer": "비싸지만 사요", "explanation": "-지만 shows contrast"},
            {"exercise_type": "grammar", "question": "Connect: 'I'm sick ___ I rest'", "instruction": "Choose the connector for 'so'", "options": ["아프고 쉬어요", "아프지만 쉬어요", "아파서 쉬어요", "아프니까 쉬어요"], "correct_answer": "아파서 쉬어요", "explanation": "-아/어서 for cause"},
            {"exercise_type": "grammar", "question": "Connect: 'It's raining ___ take an umbrella'", "instruction": "Choose the connector for 'so' (suggestion)", "options": ["비가 오고 우산을 가져가요", "비가 오지만 우산을 가져가요", "비가 와서 우산을 가져가요", "비가 오니까 우산을 가져가요"], "correct_answer": "비가 오니까 우산을 가져가요", "explanation": "-(으)니까 for suggestions"},
            {"exercise_type": "grammar", "question": "Connect: 'I wake up ___ wash my face'", "instruction": "Choose the connector for 'and'", "options": ["일어나고 얼굴을 씻어요", "일어나지만 얼굴을 씻어요", "일어나서 얼굴을 씻어요", "일어나니까 얼굴을 씻어요"], "correct_answer": "일어나고 얼굴을 씻어요", "explanation": "-고 for sequential actions"},
            {"exercise_type": "grammar", "question": "Connect: 'I'm tired ___ I work'", "instruction": "Choose the connector for 'but'", "options": ["피곤하고 일해요", "피곤하지만 일해요", "피곤해서 일해요", "피곤하니까 일해요"], "correct_answer": "피곤하지만 일해요", "explanation": "-지만 for contrast"},
            {"exercise_type": "grammar", "question": "Connect: 'It's hot ___ I turn on AC'", "instruction": "Choose the connector for 'so'", "options": ["더워고 에어컨을 켜요", "덥지만 에어컨을 켜요", "더워서 에어컨을 켜요", "더우니까 에어컨을 켜요"], "correct_answer": "더워서 에어컨을 켜요", "explanation": "-아/어서 for cause"},
            {"exercise_type": "grammar", "question": "Connect: 'It's delicious ___ try it'", "instruction": "Choose the connector for 'so' (recommendation)", "options": ["맛있어고 먹어 보세요", "맛있지만 먹어 보세요", "맛있어서 먹어 보세요", "맛있으니까 먹어 보세요"], "correct_answer": "맛있으니까 먹어 보세요", "explanation": "-(으)니까 for recommendations"},
            {"exercise_type": "grammar", "question": "Connect: 'I read a book ___ listen to music'", "instruction": "Choose the connector for 'and'", "options": ["책을 읽고 음악을 들어요", "책을 읽지만 음악을 들어요", "책을 읽어서 음악을 들어요", "책을 읽으니까 음악을 들어요"], "correct_answer": "책을 읽고 음악을 들어요", "explanation": "-고 connects actions"},
            {"exercise_type": "grammar", "question": "Connect: 'It's difficult ___ fun'", "instruction": "Choose the connector for 'but'", "options": ["어렵고 재미있어요", "어렵지만 재미있어요", "어려워서 재미있어요", "어려우니까 재미있어요"], "correct_answer": "어렵지만 재미있어요", "explanation": "-지만 for contrast"},
            {"exercise_type": "grammar", "question": "Connect: 'I have no money ___ I can't buy it'", "instruction": "Choose the connector for 'so'", "options": ["돈이 없어고 못 사요", "돈이 없지만 못 사요", "돈이 없어서 못 사요", "돈이 없으니까 못 사요"], "correct_answer": "돈이 없어서 못 사요", "explanation": "-아/어서 for cause"},
            {"exercise_type": "grammar", "question": "Connect: 'It's late ___ go home'", "instruction": "Choose the connector for 'so' (suggestion)", "options": ["늦어고 집에 가세요", "늦지만 집에 가세요", "늦어서 집에 가세요", "늦으니까 집에 가세요"], "correct_answer": "늦으니까 집에 가세요", "explanation": "-(으)니까 for suggestions"},
            {"exercise_type": "grammar", "question": "Connect: 'I shower ___ go to bed'", "instruction": "Choose the connector for 'and'", "options": ["샤워하고 자요", "샤워하지만 자요", "샤워해서 자요", "샤워하니까 자요"], "correct_answer": "샤워하고 자요", "explanation": "-고 for sequential actions"},
            {"exercise_type": "grammar", "question": "Connect: 'It's close ___ I walk'", "instruction": "Choose the connector for 'so'", "options": ["가까워고 걸어요", "가깝지만 걸어요", "가까워서 걸어요", "가까우니까 걸어요"], "correct_answer": "가까워서 걸어요", "explanation": "-아/어서 for cause"},
            {"exercise_type": "grammar", "question": "Connect: 'I don't like it ___ I eat it'", "instruction": "Choose the connector for 'but'", "options": ["싫어하고 먹어요", "싫어하지만 먹어요", "싫어해서 먹어요", "싫어하니까 먹어요"], "correct_answer": "싫어하지만 먹어요", "explanation": "-지만 for contrast"},
            {"exercise_type": "grammar", "question": "Connect: 'It's good weather ___ let's go out'", "instruction": "Choose the connector for 'so' (suggestion)", "options": ["날씨가 좋아고 나가요", "날씨가 좋지만 나가요", "날씨가 좋아서 나가요", "날씨가 좋으니까 나가요"], "correct_answer": "날씨가 좋으니까 나가요", "explanation": "-(으)니까 for suggestions"}
        ]
    }
]

grammar_unit['lessons'].extend(final_lessons)

with open(lessons_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Added {len(final_lessons)} final lessons")
print(f"Total lessons in Grammar unit: {len(grammar_unit['lessons'])}")
total_ex = sum(len(l['exercises']) for l in grammar_unit['lessons'])
print(f"Total exercises: {total_ex}")
print("\nGrammar unit complete!")
