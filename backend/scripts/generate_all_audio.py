#!/usr/bin/env python3
"""Pre-generate audio files for all flashcards

This script generates TTS audio files for all cards in the database,
which improves user experience by eliminating first-load delays.

Usage:
    python scripts/generate_all_audio.py [--force]

Options:
    --force     Regenerate audio even if it already exists in cache
"""
import sys
import os
from pathlib import Path

# Add parent directory to path so we can import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from database import db
from models import Card
from tts_service import get_tts_service
import argparse
from datetime import datetime


def generate_all_audio(force=False):
    """Generate audio for all cards in the database

    Args:
        force: If True, regenerate audio even if it exists in cache
    """
    app = create_app("development")

    with app.app_context():
        # Get TTS service
        tts = get_tts_service(app.config["TTS_CACHE_DIR"])

        # Get all cards
        cards = db.session.query(Card).all()
        total_cards = len(cards)

        print(f"\n{'='*60}")
        print(f"Audio Pre-generation Script")
        print(f"{'='*60}")
        print(f"Total cards to process: {total_cards}")
        print(f"Cache directory: {tts.cache_dir}")
        print(f"Force regenerate: {force}")
        print(f"{'='*60}\n")

        # Track statistics
        stats = {
            "generated": 0,
            "cached": 0,
            "failed": 0,
            "slow_speed": 0,
            "normal_speed": 0,
        }

        start_time = datetime.now()

        for idx, card in enumerate(cards, 1):
            # Determine if we should use slow speed
            slow = card.level <= 1
            if slow:
                stats["slow_speed"] += 1
            else:
                stats["normal_speed"] += 1

            # Check if audio already exists
            cache_key = tts._generate_cache_key(card.front_korean, "ko", slow)
            cache_path = tts._get_cache_path(cache_key)

            if cache_path.exists() and not force:
                stats["cached"] += 1
                print(f"[{idx}/{total_cards}] ✓ Cached: {card.front_korean[:30]}")
                continue

            # Delete old file if force regeneration
            if force and cache_path.exists():
                cache_path.unlink()

            # Generate audio
            print(
                f"[{idx}/{total_cards}] ⚙️  Generating: {card.front_korean[:30]}... ",
                end="",
                flush=True,
            )

            audio_filename = tts.generate_audio(
                text=card.front_korean, lang="ko", slow=slow, max_retries=3
            )

            if audio_filename:
                stats["generated"] += 1
                print("✅")
            else:
                stats["failed"] += 1
                print("❌ FAILED")
                print(f"   └─ Card ID: {card.id}, Text: {card.front_korean}")

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Print summary
        print(f"\n{'='*60}")
        print(f"Generation Complete")
        print(f"{'='*60}")
        print(f"Total cards:        {total_cards}")
        print(f"Generated:          {stats['generated']}")
        print(f"Already cached:     {stats['cached']}")
        print(f"Failed:             {stats['failed']}")
        print(f"Slow speed (L0-1):  {stats['slow_speed']}")
        print(f"Normal speed (L2+): {stats['normal_speed']}")
        print(f"Duration:           {duration:.1f} seconds")

        # Get final cache stats
        cache_stats = tts.get_cache_size()
        print(f"\nCache Statistics:")
        print(f"Total files:        {cache_stats['file_count']}")
        print(f"Total size:         {cache_stats['total_size_mb']} MB")
        print(f"{'='*60}\n")

        if stats["failed"] > 0:
            print("⚠️  Warning: Some audio files failed to generate.")
            print("   Check the logs above for details.")
            return 1
        else:
            print("✅ All audio files generated successfully!")
            return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Pre-generate audio files for all flashcards"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate audio even if it already exists in cache",
    )

    args = parser.parse_args()

    try:
        exit_code = generate_all_audio(force=args.force)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting...")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
