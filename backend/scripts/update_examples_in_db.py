"""
Update existing database cards with new example sentences from JSON
"""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from database import db
from models import Card, Deck


def update_examples():
    # Load vocab data
    vocab_path = Path(__file__).parent.parent / "data" / "korean_vocab.json"
    with open(vocab_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Create app context
    app = create_app()

    with app.app_context():
        updated = 0

        for deck_data in data["decks"]:
            # Find deck by name
            deck = Deck.query.filter_by(name=deck_data["name"]).first()
            if not deck:
                print(f"Warning: Deck '{deck_data['name']}' not found")
                continue

            for card_data in deck_data["cards"]:
                # Find card by Korean text and deck
                card = Card.query.filter_by(
                    deck_id=deck.id, front_korean=card_data["front_korean"]
                ).first()

                if card and "example_sentence" in card_data:
                    old_example = card.example_sentence
                    new_example = card_data["example_sentence"]

                    if old_example != new_example:
                        card.example_sentence = new_example
                        updated += 1
                        print(f"Updated: {card.front_korean}")
                        print(f"  Old: {old_example}")
                        print(f"  New: {new_example}\n")

        # Commit changes
        db.session.commit()
        print(f"\n✅ Updated {updated} cards with new example sentences")


if __name__ == "__main__":
    update_examples()
