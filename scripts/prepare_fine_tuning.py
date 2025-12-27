"""
Script to prepare fine-tuning dataset from dialogues.

This script creates a JSONL file in OpenAI fine-tuning format
from the dialogue database.

Usage:
    python scripts/prepare_fine_tuning.py
"""

import json
import jsonlines
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models.dialogue import Dialogue


def prepare_fine_tuning_dataset(output_file='data/processed/fine_tuning_dataset.jsonl'):
    """
    Prepare fine-tuning dataset from dialogues.

    Format:
    {"messages": [
        {"role": "system", "content": "You are Vadivelu..."},
        {"role": "user", "content": "Topic/situation"},
        {"role": "assistant", "content": "Dialogue response"}
    ]}
    """
    app = create_app('development')

    with app.app_context():
        print("Preparing fine-tuning dataset...")

        # Get all dialogues
        dialogues = Dialogue.query.all()

        if not dialogues:
            print("No dialogues found in database!")
            return

        print(f"Found {len(dialogues)} dialogues")

        # Prepare output directory
        output_path = Path(__file__).parent.parent / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # System prompts for each comedian (case-insensitive matching)
        system_prompts = {
            'vadivelu': "You are Vadivelu, the legendary Tamil comedian. Respond with exaggerated expressions, self-deprecating humor, and signature catchphrases. Use Tanglish (Tamil-English mix).",
            'santhanam': "You are Santhanam, the modern Tamil comedian. Respond with quick wit, contemporary references, and sharp sarcasm. Use Tanglish (Tamil-English mix).",
            'vivek': "You are Vivek, the intellectual Tamil comedian. Respond with social commentary, wordplay, and thoughtful messages. Use Tanglish (Tamil-English mix)."
        }

        training_examples = []

        for dialogue in dialogues:
            # Skip if no dialogue content
            if not dialogue.dialogue_english:
                continue

            # Create training example
            comedian_key = dialogue.comedian.lower()
            system_prompt = system_prompts.get(
                comedian_key,
                f"You are a Tamil comedian in the style of {dialogue.comedian}. Use Tanglish (Tamil-English mix)."
            )

            # Use context as user prompt (emotion as fallback)
            user_prompt = dialogue.context or f"Respond in the style of {dialogue.emotion or 'comedy'}"

            # Use Tanglish as primary response (more authentic), English as fallback
            assistant_response = dialogue.dialogue_tanglish or dialogue.dialogue_english

            example = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": assistant_response}
                ]
            }

            training_examples.append(example)

        # Write to JSONL file
        with jsonlines.open(output_path, 'w') as f:
            f.write_all(training_examples)

        print(f"\n{'='*60}")
        print(f"Fine-tuning dataset prepared!")
        print(f"Output file: {output_path}")
        print(f"Total training examples: {len(training_examples)}")
        print(f"{'='*60}")
        print(f"\nNote: For actual fine-tuning, you need:")
        print(f"  1. OpenRouter fine-tuning API access")
        print(f"  2. Minimum 50-100 examples (you have {len(training_examples)})")
        print(f"  3. To upload this file and create a fine-tuning job")


if __name__ == '__main__':
    prepare_fine_tuning_dataset()
