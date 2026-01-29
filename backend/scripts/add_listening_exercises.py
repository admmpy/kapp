#!/usr/bin/env python3
"""Add full-sentence listening exercises to lessons

This script adds 2-3 listening exercises per lesson with natural sentences.

Usage:
    cd backend
    python scripts/add_listening_exercises.py
"""
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from tts_service import get_tts_service


# Listening exercises to add to each lesson
# Format: lesson_title -> list of exercises
LISTENING_EXERCISES = {
    "Hello & Goodbye": [
        {
            "exercise_type": "listening",
            "question": "Listen to the full sentence and select what you hear",
            "instruction": "Play the audio carefully",
            "korean_text": "안녕하세요. 만나서 반갑습니다.",
            "options": [
                "안녕하세요. 만나서 반갑습니다.",
                "안녕히 가세요. 감사합니다.",
                "안녕하세요. 죄송합니다.",
                "안녕히 계세요. 고마워요."
            ],
            "correct_answer": "안녕하세요. 만나서 반갑습니다.",
            "explanation": "The sentence means 'Hello. Nice to meet you.'"
        },
        {
            "exercise_type": "listening",
            "question": "Listen and select what you hear",
            "instruction": "This is a common greeting phrase",
            "korean_text": "오늘 날씨가 좋아요.",
            "options": [
                "오늘 날씨가 좋아요.",
                "오늘 뭐 해요?",
                "어제 날씨가 나빴어요.",
                "내일 날씨가 좋을까요?"
            ],
            "correct_answer": "오늘 날씨가 좋아요.",
            "explanation": "The sentence means 'The weather is nice today.'"
        }
    ],
    "Thank You & Sorry": [
        {
            "exercise_type": "listening",
            "question": "Listen to the sentence and select what you hear",
            "instruction": "Pay attention to the formality",
            "korean_text": "도와 주셔서 정말 감사합니다.",
            "options": [
                "도와 주셔서 정말 감사합니다.",
                "도와 주셔서 고마워요.",
                "죄송합니다. 도와 주세요.",
                "감사합니다. 잘 지내요."
            ],
            "correct_answer": "도와 주셔서 정말 감사합니다.",
            "explanation": "The sentence means 'Thank you very much for your help.'"
        },
        {
            "exercise_type": "listening",
            "question": "Listen and identify the apology phrase",
            "instruction": "Listen carefully to the full sentence",
            "korean_text": "죄송합니다. 잘 못 들었어요.",
            "options": [
                "죄송합니다. 잘 못 들었어요.",
                "감사합니다. 잘 들었어요.",
                "미안해요. 뭐라고요?",
                "죄송합니다. 다시 말해 주세요."
            ],
            "correct_answer": "죄송합니다. 잘 못 들었어요.",
            "explanation": "The sentence means 'I'm sorry. I didn't hear well.'"
        }
    ],
    "Self Introduction": [
        {
            "exercise_type": "listening",
            "question": "Listen to the introduction and select what you hear",
            "instruction": "This is a self-introduction",
            "korean_text": "저는 미국에서 왔습니다.",
            "options": [
                "저는 미국에서 왔습니다.",
                "저는 한국에서 왔어요.",
                "저는 일본에서 왔습니다.",
                "저는 중국에서 왔어요."
            ],
            "correct_answer": "저는 미국에서 왔습니다.",
            "explanation": "The sentence means 'I came from America.'"
        },
        {
            "exercise_type": "listening",
            "question": "Listen and select what you hear",
            "instruction": "Pay attention to the verb ending",
            "korean_text": "한국어를 배우고 싶어요.",
            "options": [
                "한국어를 배우고 싶어요.",
                "한국어를 잘 해요.",
                "한국어를 공부해요.",
                "한국어를 가르쳐요."
            ],
            "correct_answer": "한국어를 배우고 싶어요.",
            "explanation": "The sentence means 'I want to learn Korean.'"
        },
        {
            "exercise_type": "listening",
            "question": "Listen to the full introduction",
            "instruction": "A longer self-introduction phrase",
            "korean_text": "제 이름은 김민수입니다. 대학생이에요.",
            "options": [
                "제 이름은 김민수입니다. 대학생이에요.",
                "제 이름은 박지현입니다. 회사원이에요.",
                "제 이름은 김민수입니다. 선생님이에요.",
                "저는 김민수입니다. 학생이 아니에요."
            ],
            "correct_answer": "제 이름은 김민수입니다. 대학생이에요.",
            "explanation": "The sentence means 'My name is Kim Minsu. I'm a university student.'"
        }
    ],
    "Sino-Korean Numbers 1-10": [
        {
            "exercise_type": "listening",
            "question": "Listen and identify the price",
            "instruction": "This is about money",
            "korean_text": "이것은 삼천 원입니다.",
            "options": [
                "이것은 삼천 원입니다.",
                "이것은 오천 원입니다.",
                "이것은 만 원입니다.",
                "이것은 천 원입니다."
            ],
            "correct_answer": "이것은 삼천 원입니다.",
            "explanation": "The sentence means 'This is 3,000 won.' (삼천 = 3,000)"
        },
        {
            "exercise_type": "listening",
            "question": "Listen and select the date phrase",
            "instruction": "Pay attention to the numbers",
            "korean_text": "오늘은 삼월 십오일입니다.",
            "options": [
                "오늘은 삼월 십오일입니다.",
                "오늘은 사월 이십일입니다.",
                "오늘은 오월 십일입니다.",
                "오늘은 일월 오일입니다."
            ],
            "correct_answer": "오늘은 삼월 십오일입니다.",
            "explanation": "The sentence means 'Today is March 15th.' (삼월 십오일 = 3/15)"
        }
    ],
    "Native Korean Numbers 1-10": [
        {
            "exercise_type": "listening",
            "question": "Listen and select the counting phrase",
            "instruction": "Uses native Korean numbers with counters",
            "korean_text": "사과 세 개 주세요.",
            "options": [
                "사과 세 개 주세요.",
                "사과 두 개 주세요.",
                "사과 네 개 주세요.",
                "사과 다섯 개 주세요."
            ],
            "correct_answer": "사과 세 개 주세요.",
            "explanation": "The sentence means 'Please give me three apples.' (세 개 = 3 items)"
        },
        {
            "exercise_type": "listening",
            "question": "Listen and identify the age statement",
            "instruction": "Korean uses native numbers for age",
            "korean_text": "저는 스물다섯 살입니다.",
            "options": [
                "저는 스물다섯 살입니다.",
                "저는 서른 살입니다.",
                "저는 스무 살입니다.",
                "저는 열아홉 살입니다."
            ],
            "correct_answer": "저는 스물다섯 살입니다.",
            "explanation": "The sentence means 'I am 25 years old.' (스물다섯 = 25)"
        }
    ],
    "Yes, No & Please": [
        {
            "exercise_type": "listening",
            "question": "Listen and select the request phrase",
            "instruction": "A polite request",
            "korean_text": "물 한 잔 주세요.",
            "options": [
                "물 한 잔 주세요.",
                "커피 주세요.",
                "물 있어요?",
                "주스 두 잔 주세요."
            ],
            "correct_answer": "물 한 잔 주세요.",
            "explanation": "The sentence means 'Please give me a glass of water.'"
        },
        {
            "exercise_type": "listening",
            "question": "Listen and identify the response",
            "instruction": "Yes/No response in context",
            "korean_text": "네, 알겠습니다. 잠깐만 기다려 주세요.",
            "options": [
                "네, 알겠습니다. 잠깐만 기다려 주세요.",
                "아니요, 괜찮습니다.",
                "네, 감사합니다.",
                "아니요, 모르겠어요."
            ],
            "correct_answer": "네, 알겠습니다. 잠깐만 기다려 주세요.",
            "explanation": "The sentence means 'Yes, I understand. Please wait a moment.'"
        }
    ],
    "Excuse Me & Wait": [
        {
            "exercise_type": "listening",
            "question": "Listen and select the question",
            "instruction": "Asking for directions",
            "korean_text": "화장실이 어디에 있어요?",
            "options": [
                "화장실이 어디에 있어요?",
                "식당이 어디에 있어요?",
                "지하철역이 어디에 있어요?",
                "출구가 어디에 있어요?"
            ],
            "correct_answer": "화장실이 어디에 있어요?",
            "explanation": "The sentence means 'Where is the bathroom?'"
        },
        {
            "exercise_type": "listening",
            "question": "Listen and identify the polite request",
            "instruction": "Asking someone to wait",
            "korean_text": "잠깐만 기다려 주세요. 금방 돌아올게요.",
            "options": [
                "잠깐만 기다려 주세요. 금방 돌아올게요.",
                "여기서 기다리세요. 가지 마세요.",
                "저기요, 도와주세요.",
                "실례합니다. 지나갈게요."
            ],
            "correct_answer": "잠깐만 기다려 주세요. 금방 돌아올게요.",
            "explanation": "The sentence means 'Please wait a moment. I'll be right back.'"
        }
    ]
}


def load_lessons_json():
    """Load the korean_lessons.json file"""
    data_dir = Path(__file__).parent.parent / "data"
    lessons_file = data_dir / "korean_lessons.json"

    if not lessons_file.exists():
        print(f"Error: {lessons_file} not found!")
        return None, None

    with open(lessons_file, "r", encoding="utf-8") as f:
        return json.load(f), lessons_file


def save_lessons_json(data, filepath):
    """Save updated korean_lessons.json"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved updated JSON to {filepath}")


def generate_audio_for_exercises(tts, exercises):
    """Generate audio for listening exercises"""
    audio_map = {}

    for lesson_title, lesson_exercises in exercises.items():
        for ex in lesson_exercises:
            korean_text = ex.get("korean_text")
            if korean_text:
                # Generate audio
                cache_key = tts._generate_cache_key(korean_text, "ko", True)
                cache_path = tts._get_cache_path(cache_key)

                if cache_path.exists():
                    print(f"  Cached: {korean_text[:40]}...")
                else:
                    print(f"  Generating: {korean_text[:40]}... ", end="", flush=True)
                    audio_filename = tts.generate_audio(
                        text=korean_text,
                        lang="ko",
                        slow=True,
                        max_retries=3
                    )
                    if audio_filename:
                        print("OK")
                    else:
                        print("FAILED")
                        continue

                audio_map[korean_text] = f"/api/audio/{cache_key}.mp3"

    return audio_map


def add_exercises_to_lessons(data, audio_map):
    """Add listening exercises to lessons"""
    added_count = 0

    for course in data.get("courses", []):
        for unit in course.get("units", []):
            for lesson in unit.get("lessons", []):
                lesson_title = lesson.get("title")
                if lesson_title in LISTENING_EXERCISES:
                    new_exercises = LISTENING_EXERCISES[lesson_title]

                    for ex in new_exercises:
                        # Add audio_url if we have it
                        korean_text = ex.get("korean_text")
                        if korean_text in audio_map:
                            ex["audio_url"] = audio_map[korean_text]

                        # Remove korean_text from the exercise
                        # (we don't want to show it, only use it for audio)
                        # Actually, keep it for audio generation but the frontend won't display it

                        # Add exercise to lesson
                        if "exercises" not in lesson:
                            lesson["exercises"] = []

                        # Insert listening exercises after vocabulary exercises
                        # but before grammar and sentence_arrange
                        insert_idx = 0
                        for i, existing_ex in enumerate(lesson["exercises"]):
                            if existing_ex.get("exercise_type") in ["vocabulary", "listening"]:
                                insert_idx = i + 1

                        lesson["exercises"].insert(insert_idx, ex)
                        added_count += 1
                        print(f"  Added listening exercise to '{lesson_title}'")

    return data, added_count


def main():
    print("=" * 60)
    print("ADD LISTENING EXERCISES")
    print("=" * 60)

    # Load JSON data
    data, filepath = load_lessons_json()
    if not data:
        return 1

    # Create app context for TTS service
    app = create_app("development")

    with app.app_context():
        # Get TTS service
        tts = get_tts_service(app.config["TTS_CACHE_DIR"])

        # Generate audio for new exercises
        print("\nGenerating audio for new listening exercises...")
        audio_map = generate_audio_for_exercises(tts, LISTENING_EXERCISES)
        print(f"Generated/cached {len(audio_map)} audio files")

        # Add exercises to lessons
        print("\nAdding exercises to lessons...")
        updated_data, added_count = add_exercises_to_lessons(data, audio_map)
        print(f"Added {added_count} listening exercises")

        # Save updated JSON
        save_lessons_json(updated_data, filepath)

        print("\n" + "=" * 60)
        print("DONE!")
        print("=" * 60)
        print("\nNext step: Run 'python scripts/import_lessons.py --force' to import updated lessons")

    return 0


if __name__ == "__main__":
    sys.exit(main())
