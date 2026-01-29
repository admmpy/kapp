#!/usr/bin/env python3
"""Generate audio files for all lesson content

This script:
1. Reads korean_lessons.json
2. Extracts all Korean text from exercises and sentence_arrange tiles
3. Generates audio using TTSService
4. Updates the JSON with audio_url fields

Usage:
    cd backend
    python scripts/generate_lesson_audio.py          # Generate missing audio
    python scripts/generate_lesson_audio.py --force  # Regenerate all audio
"""
import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from tts_service import get_tts_service


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


def collect_korean_texts(data):
    """Collect all unique Korean texts that need audio

    Returns:
        set: Set of (korean_text, use_slow) tuples
    """
    texts = set()

    # Collect from exercises
    for course in data.get("courses", []):
        for unit in course.get("units", []):
            for lesson in unit.get("lessons", []):
                for exercise in lesson.get("exercises", []):
                    # Korean text from exercise (vocabulary, listening)
                    if exercise.get("korean_text"):
                        texts.add((exercise["korean_text"], True))

                    # Tiles from sentence_arrange exercises
                    if exercise.get("exercise_type") == "sentence_arrange":
                        for option in exercise.get("options", []):
                            if isinstance(option, dict) and option.get("korean"):
                                texts.add((option["korean"], True))

    # Collect from vocabulary section
    for vocab in data.get("vocabulary", []):
        if vocab.get("korean"):
            texts.add((vocab["korean"], True))

    return texts


def generate_audio_for_texts(tts, texts, force=False):
    """Generate audio files for all Korean texts

    Args:
        tts: TTSService instance
        texts: Set of (korean_text, slow) tuples
        force: Whether to regenerate existing audio

    Returns:
        dict: Mapping of korean_text -> audio_url
    """
    audio_map = {}
    total = len(texts)

    stats = {
        "generated": 0,
        "cached": 0,
        "failed": 0,
    }

    for idx, (korean_text, slow) in enumerate(sorted(texts), 1):
        # Check if audio already exists
        cache_key = tts._generate_cache_key(korean_text, "ko", slow)
        cache_path = tts._get_cache_path(cache_key)

        if cache_path.exists() and not force:
            stats["cached"] += 1
            audio_map[korean_text] = f"/api/audio/{cache_key}.mp3"
            print(f"[{idx}/{total}] ✓ Cached: {korean_text[:30]}")
            continue

        # Delete old file if force regeneration
        if force and cache_path.exists():
            cache_path.unlink()

        # Generate audio
        print(f"[{idx}/{total}] Generating: {korean_text[:30]}... ", end="", flush=True)

        audio_filename = tts.generate_audio(
            text=korean_text,
            lang="ko",
            slow=slow,
            max_retries=3
        )

        if audio_filename:
            stats["generated"] += 1
            audio_map[korean_text] = f"/api/audio/{audio_filename}"
            print("OK")
        else:
            stats["failed"] += 1
            print("FAILED")

    print(f"\nGeneration stats:")
    print(f"  Generated: {stats['generated']}")
    print(f"  Cached: {stats['cached']}")
    print(f"  Failed: {stats['failed']}")

    return audio_map


def update_json_with_audio_urls(data, audio_map):
    """Update the JSON data with audio_url fields

    Args:
        data: The lessons JSON data
        audio_map: Mapping of korean_text -> audio_url
    """
    updated_count = 0

    for course in data.get("courses", []):
        for unit in course.get("units", []):
            for lesson in unit.get("lessons", []):
                for exercise in lesson.get("exercises", []):
                    # Add audio_url to exercises with korean_text
                    korean_text = exercise.get("korean_text")
                    if korean_text and korean_text in audio_map:
                        exercise["audio_url"] = audio_map[korean_text]
                        updated_count += 1

                    # Add audio_url to sentence_arrange tiles
                    if exercise.get("exercise_type") == "sentence_arrange":
                        for option in exercise.get("options", []):
                            if isinstance(option, dict) and option.get("korean"):
                                korean = option["korean"]
                                if korean in audio_map:
                                    option["audio_url"] = audio_map[korean]
                                    updated_count += 1

    print(f"Updated {updated_count} audio_url fields in JSON")
    return data


def run_generation(force=False):
    """Run the full audio generation process"""
    print("=" * 60)
    print("LESSON AUDIO GENERATION")
    print("=" * 60)

    # Load JSON data
    data, filepath = load_lessons_json()
    if not data:
        return False

    # Create app context for TTS service
    app = create_app("development")

    with app.app_context():
        # Get TTS service
        tts = get_tts_service(app.config["TTS_CACHE_DIR"])

        print(f"\nCache directory: {tts.cache_dir}")
        print(f"Force regenerate: {force}")

        # Collect Korean texts
        print("\nCollecting Korean texts from lessons...")
        texts = collect_korean_texts(data)
        print(f"Found {len(texts)} unique Korean texts")

        if not texts:
            print("No texts to process!")
            return True

        # Generate audio
        print("\nGenerating audio files...")
        start_time = datetime.now()

        audio_map = generate_audio_for_texts(tts, texts, force=force)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"Duration: {duration:.1f} seconds")

        # Update JSON with audio URLs
        print("\nUpdating JSON with audio URLs...")
        updated_data = update_json_with_audio_urls(data, audio_map)

        # Save updated JSON
        save_lessons_json(updated_data, filepath)

        # Print final cache stats
        cache_stats = tts.get_cache_size()
        print(f"\nCache Statistics:")
        print(f"  Total files: {cache_stats['file_count']}")
        print(f"  Total size: {cache_stats['total_size_mb']} MB")

        print("\n" + "=" * 60)
        print("AUDIO GENERATION COMPLETE!")
        print("=" * 60)
        print("\nNext step: Run 'python scripts/import_lessons.py --force' to import updated lessons")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate audio files for lesson content"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Regenerate audio even if it exists in cache"
    )
    args = parser.parse_args()

    try:
        success = run_generation(force=args.force)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
