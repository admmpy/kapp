"""Database initialization script

This script initializes the database and imports starter Korean vocabulary.

Usage:
    python init_db.py [--generate-audio]

Options:
    --generate-audio    Pre-generate TTS audio for all cards after import
"""
import json
import sys
import argparse
from pathlib import Path
from app import create_app
from database import db
from models import Deck, Card


def init_database():
    """Initialize database tables"""
    app = create_app()

    with app.app_context():
        # Drop all tables and recreate (fresh start)
        print("Creating database tables...")
        db.drop_all()
        db.create_all()
        print("✓ Database tables created")

    return app


def load_vocabulary_data():
    """Load vocabulary data from JSON file

    Returns:
        Dictionary with decks and cards data
    """
    vocab_file = Path(__file__).parent / "data" / "korean_vocab.json"

    print(f"Loading vocabulary from {vocab_file}...")

    with open(vocab_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"✓ Loaded {len(data['decks'])} decks")
    return data


def import_vocabulary(app, vocab_data):
    """Import vocabulary into database

    Args:
        app: Flask application instance
        vocab_data: Dictionary with decks and cards
    """
    with app.app_context():
        total_cards = 0

        for deck_data in vocab_data["decks"]:
            # Create deck
            deck = Deck(
                name=deck_data["name"],
                description=deck_data["description"],
                level=deck_data["level"],
            )
            db.session.add(deck)
            db.session.flush()  # Get deck ID

            print(f"\nImporting deck: {deck.name}")

            # Add cards to deck
            card_count = 0
            for card_data in deck_data["cards"]:
                card = Card(
                    deck_id=deck.id,
                    front_korean=card_data["front_korean"],
                    front_romanization=card_data.get("front_romanization"),
                    back_english=card_data["back_english"],
                    example_sentence=card_data.get("example_sentence"),
                    level=card_data["level"],
                )
                db.session.add(card)
                card_count += 1

            print(f"  ✓ Added {card_count} cards")
            total_cards += card_count

        # Commit all changes
        db.session.commit()
        print(
            f"\n✓ Successfully imported {total_cards} cards across {len(vocab_data['decks'])} decks"
        )


def pregenerate_audio(app):
    """Pre-generate audio for all cards

    Args:
        app: Flask application instance
    """
    from tts_service import get_tts_service

    with app.app_context():
        tts = get_tts_service(app.config["TTS_CACHE_DIR"])
        cards = Card.query.all()

        print("\n" + "=" * 50)
        print("PRE-GENERATING AUDIO FILES")
        print("=" * 50)
        print(f"Total cards: {len(cards)}")
        print()

        stats = {"generated": 0, "cached": 0, "failed": 0}

        for idx, card in enumerate(cards, 1):
            slow = card.level <= 1
            cache_key = tts._generate_cache_key(card.front_korean, "ko", slow)
            cache_path = tts._get_cache_path(cache_key)

            if cache_path.exists():
                stats["cached"] += 1
                print(f"[{idx}/{len(cards)}] ✓ Cached: {card.front_korean[:30]}")
                continue

            print(
                f"[{idx}/{len(cards)}] ⚙️  Generating: {card.front_korean[:30]}... ",
                end="",
                flush=True,
            )
            audio_filename = tts.generate_audio(card.front_korean, "ko", slow)

            if audio_filename:
                stats["generated"] += 1
                print("✅")
            else:
                stats["failed"] += 1
                print("❌")

        print(f"\n✓ Audio generation complete:")
        print(f"  Generated: {stats['generated']}")
        print(f"  Cached: {stats['cached']}")
        print(f"  Failed: {stats['failed']}")


def print_summary(app, audio_generated=False):
    """Print database summary

    Args:
        app: Flask application instance
        audio_generated: Whether audio was pre-generated
    """
    with app.app_context():
        decks = Deck.query.all()
        total_cards = Card.query.count()

        print("\n" + "=" * 50)
        print("DATABASE SUMMARY")
        print("=" * 50)
        print(f"Total Decks: {len(decks)}")
        print(f"Total Cards: {total_cards}")
        print("\nDecks:")

        for deck in decks:
            deck_cards = Card.query.filter_by(deck_id=deck.id).count()
            print(f"  - {deck.name}: {deck_cards} cards (Level {deck.level})")

        if audio_generated:
            from tts_service import get_tts_service

            tts = get_tts_service(app.config["TTS_CACHE_DIR"])
            cache_stats = tts.get_cache_size()
            print(f"\nAudio Cache:")
            print(f"  - Files: {cache_stats['file_count']}")
            print(f"  - Size: {cache_stats['total_size_mb']} MB")

        print("=" * 50)
        print("\n✓ Database initialization complete!")
        print("\nYou can now start the backend server:")
        print("  python app.py")
        print("\nOr test the API:")
        print("  curl http://localhost:5001/api/health")
        print("  curl http://localhost:5001/api/cards/due")


def main():
    """Main initialization function"""
    parser = argparse.ArgumentParser(
        description="Initialize database and import Korean vocabulary"
    )
    parser.add_argument(
        "--generate-audio",
        action="store_true",
        help="Pre-generate TTS audio for all cards after import",
    )

    args = parser.parse_args()

    print("=" * 50)
    print("KAPP DATABASE INITIALIZATION")
    print("=" * 50)
    print()

    # Initialize database
    app = init_database()

    # Load vocabulary data
    vocab_data = load_vocabulary_data()

    # Import vocabulary
    import_vocabulary(app, vocab_data)

    # Pre-generate audio if requested
    if args.generate_audio:
        pregenerate_audio(app)

    # Print summary
    print_summary(app, audio_generated=args.generate_audio)


if __name__ == "__main__":
    main()
