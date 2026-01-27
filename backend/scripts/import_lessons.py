#!/usr/bin/env python3
"""
Import script for lesson content

This script:
1. Reads korean_lessons.json
2. Creates Course/Unit/Lesson/Exercise records
3. Creates VocabularyItem records

Usage:
    cd backend
    python scripts/import_lessons.py
"""
import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import db
from app import create_app
from models_v2 import Course, Unit, Lesson, Exercise, VocabularyItem, ExerciseType


def load_lessons_json():
    """Load the korean_lessons.json file"""
    data_dir = Path(__file__).parent.parent / "data"
    lessons_file = data_dir / "korean_lessons.json"

    if not lessons_file.exists():
        print(f"Error: {lessons_file} not found!")
        return None

    with open(lessons_file, "r", encoding="utf-8") as f:
        return json.load(f)


def import_courses(data):
    """Import courses, units, lessons, and exercises"""
    courses_data = data.get("courses", [])

    for course_order, course_data in enumerate(courses_data):
        print(f"\nImporting course: {course_data['title']}")

        # Create course
        course = Course(
            title=course_data["title"],
            description=course_data.get("description"),
            language=course_data.get("language", "Korean"),
            level=course_data.get("level", "Beginner"),
            display_order=course_order,
        )
        db.session.add(course)
        db.session.flush()  # Get course.id

        # Import units
        for unit_order, unit_data in enumerate(course_data.get("units", [])):
            print(f"  - Unit: {unit_data['title']}")

            unit = Unit(
                course_id=course.id,
                title=unit_data["title"],
                description=unit_data.get("description"),
                display_order=unit_order,
            )
            db.session.add(unit)
            db.session.flush()  # Get unit.id

            # Import lessons
            for lesson_order, lesson_data in enumerate(unit_data.get("lessons", [])):
                print(f"    - Lesson: {lesson_data['title']}")

                lesson = Lesson(
                    unit_id=unit.id,
                    title=lesson_data["title"],
                    description=lesson_data.get("description"),
                    grammar_explanation=lesson_data.get("grammar_explanation"),
                    grammar_tip=lesson_data.get("grammar_tip"),
                    estimated_minutes=lesson_data.get("estimated_minutes", 5),
                    display_order=lesson_order,
                )
                db.session.add(lesson)
                db.session.flush()  # Get lesson.id

                # Import exercises
                for ex_order, ex_data in enumerate(lesson_data.get("exercises", [])):
                    exercise_type_str = ex_data.get("exercise_type", "vocabulary")
                    try:
                        exercise_type = ExerciseType(exercise_type_str)
                    except ValueError:
                        exercise_type = ExerciseType.VOCABULARY

                    exercise = Exercise(
                        lesson_id=lesson.id,
                        exercise_type=exercise_type,
                        question=ex_data["question"],
                        instruction=ex_data.get("instruction"),
                        korean_text=ex_data.get("korean_text"),
                        romanization=ex_data.get("romanization"),
                        english_text=ex_data.get("english_text"),
                        content_text=ex_data.get("content_text"),
                        audio_url=ex_data.get("audio_url"),
                        options=json.dumps(ex_data.get("options", []))
                        if ex_data.get("options")
                        else None,
                        correct_answer=ex_data["correct_answer"],
                        explanation=ex_data.get("explanation"),
                        display_order=ex_order,
                    )
                    db.session.add(exercise)

    db.session.commit()
    print(f"\nImported {len(courses_data)} course(s)")


def import_vocabulary(data):
    """Import vocabulary items"""
    vocab_data = data.get("vocabulary", [])

    for item_data in vocab_data:
        vocab_item = VocabularyItem(
            korean=item_data["korean"],
            romanization=item_data.get("romanization"),
            english=item_data["english"],
            category=item_data.get("category"),
            difficulty_level=item_data.get("difficulty_level", 1),
        )
        db.session.add(vocab_item)

    db.session.commit()
    print(f"Imported {len(vocab_data)} vocabulary item(s)")


def check_existing_data():
    """Check if data already exists"""
    course_count = db.session.query(Course).count()
    if course_count > 0:
        return True
    return False


def clear_existing_data():
    """Clear all existing lesson data"""
    print("Clearing existing data...")
    db.session.query(Exercise).delete()
    db.session.query(Lesson).delete()
    db.session.query(Unit).delete()
    db.session.query(Course).delete()
    db.session.query(VocabularyItem).delete()
    db.session.commit()
    print("Cleared existing data")


def run_import():
    """Run the full import process"""
    print("=" * 60)
    print("LESSON CONTENT IMPORT")
    print("=" * 60)

    # Load JSON data
    data = load_lessons_json()
    if not data:
        return False

    # Create app context
    app = create_app("development")

    with app.app_context():
        # Check for existing data
        if check_existing_data():
            print("\nExisting lesson data found!")
            response = (
                input("Clear existing data and reimport? (yes/no): ").strip().lower()
            )
            if response == "yes":
                clear_existing_data()
            else:
                print("Import cancelled.")
                return False

        # Import courses and lessons
        print("\nImporting courses and lessons...")
        import_courses(data)

        # Import vocabulary
        print("\nImporting vocabulary...")
        import_vocabulary(data)

        print("\n" + "=" * 60)
        print("IMPORT COMPLETE!")
        print("=" * 60)

        # Print summary
        course_count = db.session.query(Course).count()
        unit_count = db.session.query(Unit).count()
        lesson_count = db.session.query(Lesson).count()
        exercise_count = db.session.query(Exercise).count()
        vocab_count = db.session.query(VocabularyItem).count()

        print(f"\nSummary:")
        print(f"  - Courses: {course_count}")
        print(f"  - Units: {unit_count}")
        print(f"  - Lessons: {lesson_count}")
        print(f"  - Exercises: {exercise_count}")
        print(f"  - Vocabulary items: {vocab_count}")

    return True


if __name__ == "__main__":
    success = run_import()
    sys.exit(0 if success else 1)
