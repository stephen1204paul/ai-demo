"""
Script to populate the database with dialogue data from JSON files.

Usage:
    python scripts/populate_data.py
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models.dialogue import Dialogue


def load_dialogues_from_json(file_path):
    """Load dialogues from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Handle both formats: {"dialogues": [...]} and direct array [...]
        if isinstance(data, list):
            return data
        return data.get('dialogues', [])


def populate_database():
    """Populate database with dialogues from all JSON files."""
    app = create_app('development')

    with app.app_context():
        print("Starting database population...")

        # Get data directory
        data_dir = Path(__file__).parent.parent / 'data' / 'raw'

        # List of dialogue files
        dialogue_files = [
            'combined_dialogues.json'
        ]

        total_added = 0
        total_skipped = 0

        for filename in dialogue_files:
            file_path = data_dir / filename

            if not file_path.exists():
                print(f"Warning: {filename} not found. Skipping...")
                continue

            print(f"\nProcessing {filename}...")

            try:
                dialogues = load_dialogues_from_json(file_path)
                print(f"Found {len(dialogues)} dialogues in {filename}")

                for dialogue_data in dialogues:
                    # Check if dialogue already exists (by comedian + english text)
                    existing = Dialogue.query.filter_by(
                        comedian=dialogue_data['comedian'],
                        dialogue_english=dialogue_data.get('dialogue_english')
                    ).first()

                    if existing:
                        print(f"  - Skipping duplicate: {dialogue_data.get('dialogue_english', '')[:50]}...")
                        total_skipped += 1
                        continue

                    # Create dialogue entry (simplified schema - without embedding for now)
                    dialogue = Dialogue(
                        comedian=dialogue_data['comedian'],
                        dialogue_english=dialogue_data.get('dialogue_english'),
                        dialogue_tanglish=dialogue_data.get('dialogue_tanglish'),
                        context=dialogue_data.get('context'),
                        emotion=dialogue_data.get('emotion')
                    )

                    db.session.add(dialogue)
                    total_added += 1
                    print(f"  + Added: {dialogue_data['comedian']} - {dialogue_data.get('emotion', 'N/A')}")

                # Commit after each file
                db.session.commit()
                print(f"Committed {len(dialogues)} dialogues from {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                db.session.rollback()
                continue

        print(f"\n{'='*60}")
        print(f"Database population complete!")
        print(f"Total dialogues added: {total_added}")
        print(f"Total dialogues skipped (duplicates): {total_skipped}")
        print(f"{'='*60}")
        print(f"\nNext step: Run 'python scripts/generate_embeddings.py' to generate vector embeddings")


if __name__ == '__main__':
    populate_database()
