#!/usr/bin/env python3
"""Update sentence arrange exercises with natural questions and statements

This script updates existing sentence_arrange exercises to use more
natural conversational questions and statements.

Mix: 50% questions, 50% statements

Usage:
    cd backend
    python scripts/update_sentence_arrange.py
"""
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from tts_service import get_tts_service


# Replacements for sentence_arrange exercises
# Format: (lesson_title, old_question) -> new_exercise_data
EXERCISE_REPLACEMENTS = {
    # Lesson 1: Hello & Goodbye - Keep first, update second
    ("Hello & Goodbye", "Hello, nice to meet you. I am Minsu."): {
        "question": "When did you arrive in Korea?",
        "instruction": "Arrange the Korean words to form the question",
        "options": [
            {"korean": "언제", "romanization": "eonje", "id": 0},
            {"korean": "한국에", "romanization": "hanguge", "id": 1},
            {"korean": "도착했어요", "romanization": "dochakhaesseoyo", "id": 2}
        ],
        "correct_answer": "[0, 1, 2]",
        "explanation": "언제 (when) + 한국에 (to Korea) + 도착했어요 (did you arrive) = When did you arrive in Korea?"
    },

    # Lesson 2: Thank You & Sorry - Update first to question
    ("Thank You & Sorry", "Thank you very much for your help."): {
        "question": "How can I help you today?",
        "instruction": "Arrange the Korean words to form the question",
        "options": [
            {"korean": "오늘", "romanization": "oneul", "id": 0},
            {"korean": "어떻게", "romanization": "eotteoke", "id": 1},
            {"korean": "도와", "romanization": "dowa", "id": 2},
            {"korean": "드릴까요", "romanization": "deurilkkayo", "id": 3}
        ],
        "correct_answer": "[0, 1, 2, 3]",
        "explanation": "오늘 (today) + 어떻게 (how) + 도와 드릴까요 (can I help you) = How can I help you today?"
    },

    # Lesson 3: Self Introduction - Update to a natural question
    ("Self Introduction", "Hello, I am Kim Minsu from Korea."): {
        "question": "Where are you from originally?",
        "instruction": "Arrange the Korean words to form the question",
        "options": [
            {"korean": "원래", "romanization": "wollae", "id": 0},
            {"korean": "어디", "romanization": "eodi", "id": 1},
            {"korean": "출신이에요", "romanization": "chulsinieyo", "id": 2}
        ],
        "correct_answer": "[0, 1, 2]",
        "explanation": "원래 (originally) + 어디 (where) + 출신이에요 (are you from) = Where are you from originally?"
    },

    # Lesson 4: Sino-Korean Numbers - Make into a real-world question
    ("Sino-Korean Numbers 1-10", "This coffee is 5,000 won. Is that okay?"): {
        "question": "How much is this altogether?",
        "instruction": "Arrange the Korean words to form the question",
        "options": [
            {"korean": "이거", "romanization": "igeo", "id": 0},
            {"korean": "전부", "romanization": "jeonbu", "id": 1},
            {"korean": "얼마예요", "romanization": "eolmayeyo", "id": 2}
        ],
        "correct_answer": "[0, 1, 2]",
        "explanation": "이거 (this) + 전부 (altogether) + 얼마예요 (how much is it) = How much is this altogether?"
    },

    # Lesson 5: Native Numbers - Make into statement
    ("Native Korean Numbers 1-10", "Two apples, please."): {
        "question": "Actually, I need three more.",
        "instruction": "Arrange the Korean words to form the statement",
        "options": [
            {"korean": "사실", "romanization": "sasil", "id": 0},
            {"korean": "세", "romanization": "se", "id": 1},
            {"korean": "개", "romanization": "gae", "id": 2},
            {"korean": "더", "romanization": "deo", "id": 3},
            {"korean": "필요해요", "romanization": "piryohaeyo", "id": 4}
        ],
        "correct_answer": "[0, 1, 2, 3, 4]",
        "explanation": "사실 (actually) + 세 개 (three items) + 더 (more) + 필요해요 (I need) = Actually, I need three more."
    },

    # Lesson 6: Yes, No & Please - Make into question
    ("Yes, No & Please", "Excuse me, could I have some cold water please?"): {
        "question": "Of course! Would you like ice with that?",
        "instruction": "Arrange the Korean words to form the response",
        "options": [
            {"korean": "물론이죠", "romanization": "mullonijyo", "id": 0},
            {"korean": "얼음도", "romanization": "eoreumdo", "id": 1},
            {"korean": "드릴까요", "romanization": "deurilkkayo", "id": 2}
        ],
        "correct_answer": "[0, 1, 2]",
        "explanation": "물론이죠 (of course) + 얼음도 (ice too) + 드릴까요 (shall I give you) = Of course! Would you like ice with that?"
    },

    # Lesson 7: Excuse Me & Wait - Make into natural question
    ("Excuse Me & Wait", "Excuse me, where is the bathroom?"): {
        "question": "Could you tell me where the exit is?",
        "instruction": "Arrange the Korean words to form the question",
        "options": [
            {"korean": "출구가", "romanization": "chulguga", "id": 0},
            {"korean": "어디인지", "romanization": "eodinji", "id": 1},
            {"korean": "알려", "romanization": "allyeo", "id": 2},
            {"korean": "주시겠어요", "romanization": "jusigesseoyo", "id": 3}
        ],
        "correct_answer": "[0, 1, 2, 3]",
        "explanation": "출구가 (the exit) + 어디인지 (where it is) + 알려 주시겠어요 (could you tell me) = Could you tell me where the exit is?"
    }
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


def generate_audio_for_tiles(tts, replacements):
    """Generate audio for new tile words"""
    audio_map = {}

    for key, new_ex in replacements.items():
        for tile in new_ex.get("options", []):
            korean = tile.get("korean")
            if korean:
                cache_key = tts._generate_cache_key(korean, "ko", True)
                cache_path = tts._get_cache_path(cache_key)

                if cache_path.exists():
                    print(f"  Cached: {korean}")
                else:
                    print(f"  Generating: {korean}... ", end="", flush=True)
                    audio_filename = tts.generate_audio(
                        text=korean,
                        lang="ko",
                        slow=True,
                        max_retries=3
                    )
                    if audio_filename:
                        print("OK")
                    else:
                        print("FAILED")
                        continue

                audio_map[korean] = f"/api/audio/{cache_key}.mp3"

    return audio_map


def update_exercises(data, audio_map):
    """Update sentence arrange exercises with new content"""
    updated_count = 0

    for course in data.get("courses", []):
        for unit in course.get("units", []):
            for lesson in unit.get("lessons", []):
                lesson_title = lesson.get("title")

                for i, exercise in enumerate(lesson.get("exercises", [])):
                    if exercise.get("exercise_type") != "sentence_arrange":
                        continue

                    old_question = exercise.get("question")
                    key = (lesson_title, old_question)

                    if key in EXERCISE_REPLACEMENTS:
                        new_ex = EXERCISE_REPLACEMENTS[key].copy()

                        # Add audio URLs to tiles
                        for tile in new_ex.get("options", []):
                            korean = tile.get("korean")
                            if korean in audio_map:
                                tile["audio_url"] = audio_map[korean]

                        # Replace exercise
                        new_ex["exercise_type"] = "sentence_arrange"
                        lesson["exercises"][i] = new_ex
                        updated_count += 1
                        print(f"  Updated: '{old_question[:40]}...' -> '{new_ex['question'][:40]}...'")

    return data, updated_count


def main():
    print("=" * 60)
    print("UPDATE SENTENCE ARRANGE EXERCISES")
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

        # Generate audio for new tiles
        print("\nGenerating audio for new tile words...")
        audio_map = generate_audio_for_tiles(tts, EXERCISE_REPLACEMENTS)
        print(f"Generated/cached {len(audio_map)} audio files")

        # Update exercises
        print("\nUpdating sentence arrange exercises...")
        updated_data, updated_count = update_exercises(data, audio_map)
        print(f"Updated {updated_count} exercises")

        # Save updated JSON
        save_lessons_json(updated_data, filepath)

        print("\n" + "=" * 60)
        print("DONE!")
        print("=" * 60)
        print("\nNext step: Run 'python scripts/import_lessons.py --force' to import updated lessons")

    return 0


if __name__ == "__main__":
    sys.exit(main())
