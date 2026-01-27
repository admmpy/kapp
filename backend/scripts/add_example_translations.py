"""
Add English translations to example sentences in the database
This script updates all cards to have example sentences in format:
"Korean sentence - English translation"
"""

import json
from pathlib import Path

# Simple translations for common examples
example_translations = {
    "안녕하세요, 만나서 반갑습니다.": "Hello, nice to meet you.",
    "안녕히 가세요, 내일 봐요.": "Goodbye, see you tomorrow.",
    "도와주셔서 감사합니다.": "Thank you for your help.",
    "늦어서 죄송합니다.": "I'm sorry for being late.",
    "네, 맞아요.": "Yes, that's right.",
    "아니요, 괜찮아요.": "No, it's okay.",
    "잠깐만요, 지금 갈게요.": "Wait a moment, I'll go now.",
    "괜찮아요, 걱정하지 마세요.": "It's okay, don't worry.",
    "사과 하나 주세요.": "Please give me one apple.",
    "둘 중에 하나를 선택하세요.": "Choose one of the two.",
    "셋 중에서 골라보세요.": "Try choosing from the three.",
    "아빠 (appa) - Dad": "아빠 (appa) - Dad",
    "어머니 (eomeoni) - Mother": "어머니 (eomeoni) - Mother",
    "오다 (oda) - To come": "오다 (oda) - To come",
}


def update_vocab_file():
    """Update the korean_vocab.json file with English translations"""
    vocab_path = Path(__file__).parent.parent / "data" / "korean_vocab.json"

    with open(vocab_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated_count = 0

    for deck in data["decks"]:
        for card in deck["cards"]:
            if "example_sentence" in card and card["example_sentence"]:
                example = card["example_sentence"]

                # Skip if already has translation (contains " - ")
                if (
                    " - " in example
                    and not example.startswith("아빠")
                    and not example.startswith("어머니")
                ):
                    continue

                # Try to find translation
                if example in example_translations:
                    if " - " not in example:
                        card[
                            "example_sentence"
                        ] = f"{example} - {example_translations[example]}"
                        updated_count += 1
                else:
                    # For cards without manual translation, add a placeholder
                    # This will be handled by LLM or manual addition later
                    if " - " not in example:
                        # Simple heuristic translations based on common patterns
                        if "주세요" in example:
                            eng = "Please give/do (polite request)"
                        elif "감사합니다" in example:
                            eng = "Thank you"
                        elif "죄송합니다" in example:
                            eng = "I'm sorry"
                        elif "안녕하세요" in example:
                            eng = "Hello"
                        elif "안녕히" in example:
                            eng = "Goodbye"
                        elif "괜찮아요" in example:
                            eng = "It's okay"
                        else:
                            eng = "[Translation needed]"

                        card["example_sentence"] = f"{example} - {eng}"
                        updated_count += 1

    # Save updated data
    with open(vocab_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Updated {updated_count} example sentences with English translations")
    print(f"📁 File: {vocab_path}")
    return updated_count


if __name__ == "__main__":
    count = update_vocab_file()
    print(f"\n🎉 Complete! {count} examples now have both Korean and English.")
    print(
        "\nNote: Some examples have '[Translation needed]' - these can be updated manually"
    )
    print("or via LLM explanation feature.")
