#!/usr/bin/env python3
"""
Migration script: Flashcards → Lesson-based architecture

This script:
1. Backs up the current database
2. Exports review history to JSON
3. Drops old flashcard tables (deck, card, review)
4. Creates new lesson-based tables
5. Optionally imports lesson content

Usage:
    python migrations/migrate_to_lessons.py

WARNING: This is a one-way migration. Ensure backups before running!
"""
import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import db
from app import create_app


def backup_database(app):
    """Create a backup of the current database"""
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

    if not os.path.exists(db_path):
        print(f"No existing database at {db_path}, skipping backup")
        return None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path(app.root_path) / 'data' / 'backups'
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir / f'kapp_backup_flashcard_{timestamp}.db'
    shutil.copy2(db_path, backup_path)
    print(f"Database backed up to: {backup_path}")
    return backup_path


def export_review_history(app):
    """Export existing review history to JSON for reference"""
    try:
        from models import Card, Review, Deck

        export_dir = Path(app.root_path) / 'data' / 'exports'
        export_dir.mkdir(parents=True, exist_ok=True)

        with app.app_context():
            # Export decks
            decks = []
            for deck in db.session.query(Deck).all():
                decks.append({
                    'id': deck.id,
                    'name': deck.name,
                    'description': deck.description,
                    'level': deck.level
                })

            # Export cards with their review history
            cards = []
            for card in db.session.query(Card).all():
                card_data = {
                    'id': card.id,
                    'deck_id': card.deck_id,
                    'front_korean': card.front_korean,
                    'front_romanization': card.front_romanization,
                    'back_english': card.back_english,
                    'example_sentence': card.example_sentence,
                    'level': card.level,
                    'interval': card.interval,
                    'repetitions': card.repetitions,
                    'ease_factor': card.ease_factor,
                    'next_review_date': str(card.next_review_date) if card.next_review_date else None,
                    'created_at': card.created_at.isoformat() if card.created_at else None,
                    'reviews': []
                }

                for review in card.reviews:
                    card_data['reviews'].append({
                        'id': review.id,
                        'review_date': review.review_date.isoformat(),
                        'quality_rating': review.quality_rating,
                        'time_spent': review.time_spent
                    })

                cards.append(card_data)

            # Write exports
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            with open(export_dir / f'decks_{timestamp}.json', 'w', encoding='utf-8') as f:
                json.dump(decks, f, indent=2, ensure_ascii=False)

            with open(export_dir / f'cards_with_reviews_{timestamp}.json', 'w', encoding='utf-8') as f:
                json.dump(cards, f, indent=2, ensure_ascii=False)

            print(f"Exported {len(decks)} decks and {len(cards)} cards to {export_dir}")
            return True

    except Exception as e:
        print(f"Warning: Could not export review history: {e}")
        print("This may be expected if the database is empty or tables don't exist")
        return False


def drop_old_tables(app):
    """Drop the old flashcard tables"""
    with app.app_context():
        # Check if old tables exist and drop them
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()

        old_tables = ['review', 'card', 'deck']  # Order matters for foreign keys
        dropped = []

        for table in old_tables:
            if table in existing_tables:
                db.session.execute(db.text(f'DROP TABLE IF EXISTS {table}'))
                dropped.append(table)

        db.session.commit()

        if dropped:
            print(f"Dropped old tables: {', '.join(dropped)}")
        else:
            print("No old tables to drop")


def create_new_tables(app):
    """Create the new lesson-based tables"""
    # Import new models to register them with SQLAlchemy
    import models_v2  # noqa: F401

    with app.app_context():
        # Create all tables defined in models_v2
        db.create_all()

        # Verify tables were created
        inspector = db.inspect(db.engine)
        new_tables = inspector.get_table_names()

        expected_tables = ['course', 'unit', 'lesson', 'exercise', 'user_progress', 'vocabulary_item']
        created = [t for t in expected_tables if t in new_tables]

        print(f"Created new tables: {', '.join(created)}")

        if len(created) != len(expected_tables):
            missing = [t for t in expected_tables if t not in new_tables]
            print(f"Warning: Missing tables: {', '.join(missing)}")


def run_migration():
    """Run the full migration process"""
    print("=" * 60)
    print("MIGRATION: Flashcards → Lesson-based Architecture")
    print("=" * 60)
    print()

    # Confirm with user
    print("WARNING: This migration will:")
    print("  1. Backup the current database")
    print("  2. Export review history to JSON")
    print("  3. DROP old tables (deck, card, review)")
    print("  4. Create new lesson-based tables")
    print()
    print("This is a ONE-WAY migration. Make sure you have backups!")
    print()

    confirm = input("Type 'yes' to proceed: ").strip().lower()
    if confirm != 'yes':
        print("Migration cancelled.")
        return False

    print()

    # Create app context
    app = create_app('development')

    # Step 1: Backup database
    print("\n[1/4] Backing up database...")
    backup_path = backup_database(app)

    # Step 2: Export review history
    print("\n[2/4] Exporting review history...")
    export_review_history(app)

    # Step 3: Drop old tables
    print("\n[3/4] Dropping old tables...")
    drop_old_tables(app)

    # Step 4: Create new tables
    print("\n[4/4] Creating new tables...")
    create_new_tables(app)

    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Run: python scripts/import_lessons.py")
    print("  2. Verify the app works correctly")
    print()
    if backup_path:
        print(f"To restore old database: cp {backup_path} <original_path>")
    print()

    return True


if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
