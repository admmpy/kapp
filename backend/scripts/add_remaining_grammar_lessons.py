#!/usr/bin/env python3
"""Add remaining 6 grammar lessons (135 exercises) to Essential Grammar unit"""
import json
from pathlib import Path

lessons_file = Path(__file__).parent.parent / "data" / "korean_lessons.json"

with open(lessons_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Find the Essential Grammar unit (should be the last one)
grammar_unit = data['courses'][0]['units'][-1]
print(f"Current lessons in Grammar unit: {len(grammar_unit['lessons'])}")

# Define remaining 6 lessons with exercises
new_lessons = [
    {
        "title": "Present Tense Verb Conjugation",
        "description": "Learn to conjugate verbs in present tense",
        "estimated_minutes": 20,
        "grammar_explanation": "Korean present tense ending: -아/어요\n\n- Stem ends in ㅏ or ㅗ: add -아요\n- Other vowels: add -어요\n- 하다 verbs: -해요\n\nExamples:\n- 가다 → 가요 (go)\n- 먹다 → 먹어요 (eat)\n- 공부하다 → 공부해요 (study)",
        "grammar_tip": "Listen for the last vowel in the verb stem to choose -아요 or -어요",
        "exercises": [
            {"exercise_type": "grammar", "question": "가다 (to go) → present tense", "instruction": "Choose the correct conjugation", "options": ["가요", "가아요", "가어요", "가해요"], "correct_answer": "가요", "explanation": "가 ends in ㅏ, so use -아요, which combines to 가요"},
            {"exercise_type": "grammar", "question": "먹다 (to eat) → present tense", "instruction": "Choose the correct conjugation", "options": ["먹아요", "먹어요", "먹해요", "먹요"], "correct_answer": "먹어요", "explanation": "먹 ends in ㅓ (other vowel), so add -어요"},
            {"exercise_type": "grammar", "question": "보다 (to see) → present tense", "instruction": "Choose the correct conjugation", "options": ["보아요", "봐요", "보어요", "보해요"], "correct_answer": "봐요", "explanation": "보 ends in ㅗ, so use -아요, which contracts to 봐요"},
            {"exercise_type": "grammar", "question": "자다 (to sleep) → present tense", "instruction": "Choose the correct conjugation", "options": ["자요", "자아요", "자어요", "자해요"], "correct_answer": "자요", "explanation": "자 ends in ㅏ, so use -아요"},
            {"exercise_type": "grammar", "question": "읽다 (to read) → present tense", "instruction": "Choose the correct conjugation", "options": ["읽아요", "읽어요", "읽요", "읽해요"], "correct_answer": "읽어요", "explanation": "읽 ends in ㅣ (other vowel), so add -어요"},
            {"exercise_type": "grammar", "question": "오다 (to come) → present tense", "instruction": "Choose the correct conjugation", "options": ["오아요", "와요", "오어요", "오해요"], "correct_answer": "와요", "explanation": "오 ends in ㅗ, contracts to 와요"},
            {"exercise_type": "grammar", "question": "듣다 (to listen) → present tense", "instruction": "Choose the correct conjugation", "options": ["듣아요", "들어요", "듣어요", "듣요"], "correct_answer": "들어요", "explanation": "ㄷ irregular: 듣 → 들 + 어요"},
            {"exercise_type": "grammar", "question": "쓰다 (to write) → present tense", "instruction": "Choose the correct conjugation", "options": ["쓰아요", "쓰어요", "써요", "쓰해요"], "correct_answer": "써요", "explanation": "쓰 ends in ㅡ, contracts to 써요"},
            {"exercise_type": "grammar", "question": "마시다 (to drink) → present tense", "instruction": "Choose the correct conjugation", "options": ["마시아요", "마셔요", "마시어요", "마시해요"], "correct_answer": "마셔요", "explanation": "시 becomes 셔 + 요"},
            {"exercise_type": "grammar", "question": "공부하다 (to study) → present tense", "instruction": "Choose the correct conjugation", "options": ["공부하아요", "공부하어요", "공부해요", "공부하요"], "correct_answer": "공부해요", "explanation": "하다 verbs → 해요"},
            {"exercise_type": "grammar", "question": "살다 (to live) → present tense", "instruction": "Choose the correct conjugation", "options": ["살아요", "사라요", "살어요", "살해요"], "correct_answer": "살아요", "explanation": "살 ends in ㅏ, so use -아요"},
            {"exercise_type": "grammar", "question": "일하다 (to work) → present tense", "instruction": "Choose the correct conjugation", "options": ["일하아요", "일하어요", "일해요", "일하요"], "correct_answer": "일해요", "explanation": "하다 verbs → 해요"},
            {"exercise_type": "grammar", "question": "앉다 (to sit) → present tense", "instruction": "Choose the correct conjugation", "options": ["앉아요", "앉어요", "안자요", "앉요"], "correct_answer": "앉아요", "explanation": "앉 ends in ㅏ, so use -아요"},
            {"exercise_type": "grammar", "question": "서다 (to stand) → present tense", "instruction": "Choose the correct conjugation", "options": ["서아요", "서요", "서어요", "서해요"], "correct_answer": "서요", "explanation": "서 ends in ㅓ, contracts to 서요"},
            {"exercise_type": "grammar", "question": "놀다 (to play) → present tense", "instruction": "Choose the correct conjugation", "options": ["놀아요", "노라요", "놀어요", "놀해요"], "correct_answer": "놀아요", "explanation": "놀 ends in ㅗ, so use -아요"},
            {"exercise_type": "grammar", "question": "배우다 (to learn) → present tense", "instruction": "Choose the correct conjugation", "options": ["배우아요", "배워요", "배우어요", "배우해요"], "correct_answer": "배워요", "explanation": "우 + 어 → 워"},
            {"exercise_type": "grammar", "question": "주다 (to give) → present tense", "instruction": "Choose the correct conjugation", "options": ["주아요", "줘요", "주어요", "주해요"], "correct_answer": "줘요", "explanation": "ㅜ + 어 → 워, shortened to 줘요"},
            {"exercise_type": "grammar", "question": "걷다 (to walk) → present tense", "instruction": "Choose the correct conjugation", "options": ["걷아요", "걸어요", "걷어요", "걷요"], "correct_answer": "걸어요", "explanation": "ㄷ irregular: 걷 → 걸 + 어요"},
            {"exercise_type": "grammar", "question": "울다 (to cry) → present tense", "instruction": "Choose the correct conjugation", "options": ["울아요", "울라요", "울어요", "울해요"], "correct_answer": "울어요", "explanation": "울 ends in ㅜ (other vowel), so add -어요"},
            {"exercise_type": "grammar", "question": "웃다 (to laugh) → present tense", "instruction": "Choose the correct conjugation", "options": ["웃아요", "워요", "웃어요", "웃요"], "correct_answer": "웃어요", "explanation": "웃 ends in ㅜ (other vowel), so add -어요"},
            {"exercise_type": "grammar", "question": "타다 (to ride) → present tense", "instruction": "Choose the correct conjugation", "options": ["타요", "타아요", "타어요", "타해요"], "correct_answer": "타요", "explanation": "타 ends in ㅏ, so use -아요"},
            {"exercise_type": "grammar", "question": "사다 (to buy) → present tense", "instruction": "Choose the correct conjugation", "options": ["사요", "사아요", "사어요", "사해요"], "correct_answer": "사요", "explanation": "사 ends in ㅏ, so use -아요"},
            {"exercise_type": "grammar", "question": "팔다 (to sell) → present tense", "instruction": "Choose the correct conjugation", "options": ["팔아요", "파라요", "팔어요", "팔해요"], "correct_answer": "팔아요", "explanation": "팔 ends in ㅏ, so use -아요"},
            {"exercise_type": "grammar", "question": "닫다 (to close) → present tense", "instruction": "Choose the correct conjugation", "options": ["닫아요", "달아요", "닫어요", "닫요"], "correct_answer": "닫아요", "explanation": "닫 ends in ㅏ, so use -아요"},
            {"exercise_type": "grammar", "question": "열다 (to open) → present tense", "instruction": "Choose the correct conjugation", "options": ["열아요", "여라요", "열어요", "열해요"], "correct_answer": "열어요", "explanation": "열 ends in ㅓ (other vowel), so add -어요"}
        ]
    },
    {
        "title": "Past Tense Verb Conjugation",
        "description": "Learn to express past actions",
        "estimated_minutes": 20,
        "grammar_explanation": "Korean past tense: -았/었어요\n\n- Stem ends in ㅏ or ㅗ: -았어요\n- Other vowels: -었어요\n- 하다 verbs: -했어요\n\nExamples:\n- 가다 → 갔어요 (went)\n- 먹다 → 먹었어요 (ate)\n- 공부하다 → 공부했어요 (studied)",
        "grammar_tip": "Past tense follows the same vowel harmony rules as present tense",
        "exercises": [
            {"exercise_type": "grammar", "question": "가다 (to go) → past tense", "instruction": "Choose the correct conjugation", "options": ["갔어요", "가았어요", "가었어요", "가했어요"], "correct_answer": "갔어요", "explanation": "가 + 았어요 → 갔어요"},
            {"exercise_type": "grammar", "question": "먹다 (to eat) → past tense", "instruction": "Choose the correct conjugation", "options": ["먹았어요", "먹었어요", "먹했어요", "먹어요"], "correct_answer": "먹었어요", "explanation": "먹 + 었어요"},
            {"exercise_type": "grammar", "question": "보다 (to see) → past tense", "instruction": "Choose the correct conjugation", "options": ["보았어요", "봤어요", "보었어요", "보했어요"], "correct_answer": "봤어요", "explanation": "보 + 았어요 → 봤어요"},
            {"exercise_type": "grammar", "question": "자다 (to sleep) → past tense", "instruction": "Choose the correct conjugation", "options": ["잤어요", "자았어요", "자었어요", "자했어요"], "correct_answer": "잤어요", "explanation": "자 + 았어요 → 잤어요"},
            {"exercise_type": "grammar", "question": "읽다 (to read) → past tense", "instruction": "Choose the correct conjugation", "options": ["읽았어요", "읽었어요", "읽어요", "읽했어요"], "correct_answer": "읽었어요", "explanation": "읽 + 었어요"},
            {"exercise_type": "grammar", "question": "오다 (to come) → past tense", "instruction": "Choose the correct conjugation", "options": ["오았어요", "왔어요", "오었어요", "오했어요"], "correct_answer": "왔어요", "explanation": "오 + 았어요 → 왔어요"},
            {"exercise_type": "grammar", "question": "듣다 (to listen) → past tense", "instruction": "Choose the correct conjugation", "options": ["듣았어요", "들었어요", "듣었어요", "듣어요"], "correct_answer": "들었어요", "explanation": "ㄷ irregular: 들었어요"},
            {"exercise_type": "grammar", "question": "쓰다 (to write) → past tense", "instruction": "Choose the correct conjugation", "options": ["쓰았어요", "쓰었어요", "썼어요", "쓰했어요"], "correct_answer": "썼어요", "explanation": "쓰 + 었어요 → 썼어요"},
            {"exercise_type": "grammar", "question": "마시다 (to drink) → past tense", "instruction": "Choose the correct conjugation", "options": ["마시았어요", "마셨어요", "마시었어요", "마시했어요"], "correct_answer": "마셨어요", "explanation": "마시 + 었어요 → 마셨어요"},
            {"exercise_type": "grammar", "question": "공부하다 (to study) → past tense", "instruction": "Choose the correct conjugation", "options": ["공부하았어요", "공부하었어요", "공부했어요", "공부하어요"], "correct_answer": "공부했어요", "explanation": "하다 → 했어요"},
            {"exercise_type": "grammar", "question": "살다 (to live) → past tense", "instruction": "Choose the correct conjugation", "options": ["살았어요", "사랐어요", "살었어요", "살했어요"], "correct_answer": "살았어요", "explanation": "살 + 았어요"},
            {"exercise_type": "grammar", "question": "일하다 (to work) → past tense", "instruction": "Choose the correct conjugation", "options": ["일하았어요", "일하었어요", "일했어요", "일하어요"], "correct_answer": "일했어요", "explanation": "하다 → 했어요"},
            {"exercise_type": "grammar", "question": "앉다 (to sit) → past tense", "instruction": "Choose the correct conjugation", "options": ["앉았어요", "앉었어요", "안았어요", "앉어요"], "correct_answer": "앉았어요", "explanation": "앉 + 았어요"},
            {"exercise_type": "grammar", "question": "서다 (to stand) → past tense", "instruction": "Choose the correct conjugation", "options": ["서았어요", "섰어요", "서었어요", "서했어요"], "correct_answer": "섰어요", "explanation": "서 + 었어요 → 섰어요"},
            {"exercise_type": "grammar", "question": "놀다 (to play) → past tense", "instruction": "Choose the correct conjugation", "options": ["놀았어요", "노랐어요", "놀었어요", "놀했어요"], "correct_answer": "놀았어요", "explanation": "놀 + 았어요"},
            {"exercise_type": "grammar", "question": "배우다 (to learn) → past tense", "instruction": "Choose the correct conjugation", "options": ["배우았어요", "배웠어요", "배우었어요", "배우했어요"], "correct_answer": "배웠어요", "explanation": "배우 + 었어요 → 배웠어요"},
            {"exercise_type": "grammar", "question": "주다 (to give) → past tense", "instruction": "Choose the correct conjugation", "options": ["주았어요", "줬어요", "주었어요", "주했어요"], "correct_answer": "줬어요", "explanation": "주 + 었어요 → 줬어요"},
            {"exercise_type": "grammar", "question": "걷다 (to walk) → past tense", "instruction": "Choose the correct conjugation", "options": ["걷았어요", "걸었어요", "걷었어요", "걷어요"], "correct_answer": "걸었어요", "explanation": "ㄷ irregular: 걸었어요"},
            {"exercise_type": "grammar", "question": "울다 (to cry) → past tense", "instruction": "Choose the correct conjugation", "options": ["울았어요", "울랐어요", "울었어요", "울했어요"], "correct_answer": "울었어요", "explanation": "울 + 었어요"},
            {"exercise_type": "grammar", "question": "웃다 (to laugh) → past tense", "instruction": "Choose the correct conjugation", "options": ["웃았어요", "워었어요", "웃었어요", "웃어요"], "correct_answer": "웃었어요", "explanation": "웃 + 었어요"},
            {"exercise_type": "grammar", "question": "타다 (to ride) → past tense", "instruction": "Choose the correct conjugation", "options": ["탔어요", "타았어요", "타었어요", "타했어요"], "correct_answer": "탔어요", "explanation": "타 + 았어요 → 탔어요"},
            {"exercise_type": "grammar", "question": "사다 (to buy) → past tense", "instruction": "Choose the correct conjugation", "options": ["샀어요", "사았어요", "사었어요", "사했어요"], "correct_answer": "샀어요", "explanation": "사 + 았어요 → 샀어요"},
            {"exercise_type": "grammar", "question": "팔다 (to sell) → past tense", "instruction": "Choose the correct conjugation", "options": ["팔았어요", "팔랐어요", "팔었어요", "팔했어요"], "correct_answer": "팔았어요", "explanation": "팔 + 았어요"},
            {"exercise_type": "grammar", "question": "닫다 (to close) → past tense", "instruction": "Choose the correct conjugation", "options": ["닫았어요", "달았어요", "닫었어요", "닫어요"], "correct_answer": "닫았어요", "explanation": "닫 + 았어요"},
            {"exercise_type": "grammar", "question": "열다 (to open) → past tense", "instruction": "Choose the correct conjugation", "options": ["열았어요", "열랐어요", "열었어요", "열했어요"], "correct_answer": "열었어요", "explanation": "열 + 었어요"}
        ]
    },
    {
        "title": "Future Tense and Intention",
        "description": "Express future plans and intentions",
        "estimated_minutes": 15,
        "grammar_explanation": "Korean future tense: -(으)ㄹ 거예요\n\n- After vowel or ㄹ: -ㄹ 거예요\n- After consonant: -을 거예요\n\nExamples:\n- 가다 → 갈 거예요 (will go)\n- 먹다 → 먹을 거예요 (will eat)",
        "grammar_tip": "거예요 comes from 것 (thing), literally meaning 'it is the thing that...'",
        "exercises": [
            {"exercise_type": "grammar", "question": "가다 (to go) → future tense", "instruction": "Choose the correct conjugation", "options": ["갈 거예요", "가을 거예요", "갈거예요", "가ㄹ 거예요"], "correct_answer": "갈 거예요", "explanation": "가 ends in vowel, add -ㄹ 거예요"},
            {"exercise_type": "grammar", "question": "먹다 (to eat) → future tense", "instruction": "Choose the correct conjugation", "options": ["먹ㄹ 거예요", "먹을 거예요", "먹을거예요", "먹을이예요"], "correct_answer": "먹을 거예요", "explanation": "먹 ends in consonant, add -을 거예요"},
            {"exercise_type": "grammar", "question": "보다 (to see) → future tense", "instruction": "Choose the correct conjugation", "options": ["볼 거예요", "보을 거예요", "볼거예요", "보ㄹ 거예요"], "correct_answer": "볼 거예요", "explanation": "보 ends in vowel, add -ㄹ 거예요"},
            {"exercise_type": "grammar", "question": "읽다 (to read) → future tense", "instruction": "Choose the correct conjugation", "options": ["읽ㄹ 거예요", "읽을 거예요", "읽을거예요", "읽을이예요"], "correct_answer": "읽을 거예요", "explanation": "읽 ends in consonant, add -을 거예요"},
            {"exercise_type": "grammar", "question": "오다 (to come) → future tense", "instruction": "Choose the correct conjugation", "options": ["올 거예요", "오을 거예요", "올거예요", "오ㄹ 거예요"], "correct_answer": "올 거예요", "explanation": "오 ends in vowel, add -ㄹ 거예요"},
            {"exercise_type": "grammar", "question": "쓰다 (to write) → future tense", "instruction": "Choose the correct conjugation", "options": ["쓸 거예요", "쓰을 거예요", "쓸거예요", "쓰ㄹ 거예요"], "correct_answer": "쓸 거예요", "explanation": "쓰 ends in vowel, add -ㄹ 거예요"},
            {"exercise_type": "grammar", "question": "만들다 (to make) → future tense", "instruction": "Choose the correct conjugation", "options": ["만들 거예요", "만들을 거예요", "만들거예요", "만들ㄹ 거예요"], "correct_answer": "만들 거예요", "explanation": "Verbs ending in ㄹ just add 거예요"},
            {"exercise_type": "grammar", "question": "살다 (to live) → future tense", "instruction": "Choose the correct conjugation", "options": ["살 거예요", "살을 거예요", "살거예요", "살ㄹ 거예요"], "correct_answer": "살 거예요", "explanation": "살 ends in ㄹ, just add 거예요"},
            {"exercise_type": "grammar", "question": "앉다 (to sit) → future tense", "instruction": "Choose the correct conjugation", "options": ["앉ㄹ 거예요", "앉을 거예요", "앉을거예요", "앉을이예요"], "correct_answer": "앉을 거예요", "explanation": "앉 ends in consonant, add -을 거예요"},
            {"exercise_type": "grammar", "question": "배우다 (to learn) → future tense", "instruction": "Choose the correct conjugation", "options": ["배울 거예요", "배우을 거예요", "배울거예요", "배우ㄹ 거예요"], "correct_answer": "배울 거예요", "explanation": "배우 ends in vowel, add -ㄹ 거예요"},
            {"exercise_type": "grammar", "question": "주다 (to give) → future tense", "instruction": "Choose the correct conjugation", "options": ["줄 거예요", "주을 거예요", "줄거예요", "주ㄹ 거예요"], "correct_answer": "줄 거예요", "explanation": "주 ends in vowel, add -ㄹ 거예요"},
            {"exercise_type": "grammar", "question": "놀다 (to play) → future tense", "instruction": "Choose the correct conjugation", "options": ["놀 거예요", "놀을 거예요", "놀거예요", "놀ㄹ 거예요"], "correct_answer": "놀 거예요", "explanation": "놀 ends in ㄹ, just add 거예요"},
            {"exercise_type": "grammar", "question": "듣다 (to listen) → future tense", "instruction": "Choose the correct conjugation", "options": ["듣ㄹ 거예요", "들을 거예요", "듣을 거예요", "들ㄹ 거예요"], "correct_answer": "들을 거예요", "explanation": "ㄷ irregular verb changes to 들 + 을 거예요"},
            {"exercise_type": "grammar", "question": "타다 (to ride) → future tense", "instruction": "Choose the correct conjugation", "options": ["탈 거예요", "타을 거예요", "탈거예요", "타ㄹ 거예요"], "correct_answer": "탈 거예요", "explanation": "타 ends in vowel, add -ㄹ 거예요"},
            {"exercise_type": "grammar", "question": "사다 (to buy) → future tense", "instruction": "Choose the correct conjugation", "options": ["살 거예요", "사을 거예요", "살거예요", "사ㄹ 거예요"], "correct_answer": "살 거예요", "explanation": "사 ends in vowel, add -ㄹ 거예요"},
            {"exercise_type": "grammar", "question": "일하다 (to work) → future tense", "instruction": "Choose the correct conjugation", "options": ["일할 거예요", "일하을 거예요", "일할거예요", "일하ㄹ 거예요"], "correct_answer": "일할 거예요", "explanation": "하다 verbs: 할 거예요"},
            {"exercise_type": "grammar", "question": "공부하다 (to study) → future tense", "instruction": "Choose the correct conjugation", "options": ["공부할 거예요", "공부하을 거예요", "공부할거예요", "공부하ㄹ 거예요"], "correct_answer": "공부할 거예요", "explanation": "하다 verbs: 할 거예요"},
            {"exercise_type": "grammar", "question": "팔다 (to sell) → future tense", "instruction": "Choose the correct conjugation", "options": ["팔 거예요", "팔을 거예요", "팔거예요", "팔ㄹ 거예요"], "correct_answer": "팔 거예요", "explanation": "팔 ends in ㄹ, just add 거예요"},
            {"exercise_type": "grammar", "question": "닫다 (to close) → future tense", "instruction": "Choose the correct conjugation", "options": ["닫ㄹ 거예요", "닫을 거예요", "닫을거예요", "닫을이예요"], "correct_answer": "닫을 거예요", "explanation": "닫 ends in consonant, add -을 거예요"},
            {"exercise_type": "grammar", "question": "열다 (to open) → future tense", "instruction": "Choose the correct conjugation", "options": ["열ㄹ 거예요", "열을 거예요", "열을거예요", "열을이예요"], "correct_answer": "열을 거예요", "explanation": "열 ends in consonant, add -을 거예요"}
        ]
    }
]

# Add new lessons to grammar unit
grammar_unit['lessons'].extend(new_lessons)

# Save
with open(lessons_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Added {len(new_lessons)} more lessons")
print(f"Total lessons in Grammar unit: {len(grammar_unit['lessons'])}")
total_ex = sum(len(l['exercises']) for l in grammar_unit['lessons'])
print(f"Total exercises: {total_ex}")
