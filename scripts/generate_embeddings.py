"""
Script to generate vector embeddings for all dialogues in the database.

This script:
1. Fetches dialogues without embeddings
2. Generates embeddings using OpenRouter API
3. Updates the database with the embeddings

Usage:
    python scripts/generate_embeddings.py
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models.dialogue import Dialogue
from app.services.embedding_service import EmbeddingService


def generate_embeddings(batch_size=10):
    """Generate embeddings for all dialogues without embeddings."""
    app = create_app('development')

    with app.app_context():
        print("Starting embedding generation...")

        # Get dialogues without embeddings
        dialogues = Dialogue.query.filter(
            Dialogue.embedding.is_(None)
        ).all()

        if not dialogues:
            print("No dialogues found without embeddings!")
            return

        print(f"Found {len(dialogues)} dialogues without embeddings")

        embedding_service = EmbeddingService()
        total_generated = 0
        total_errors = 0

        # Process in batches
        for i in range(0, len(dialogues), batch_size):
            batch = dialogues[i:i + batch_size]
            print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} dialogues)...")

            try:
                # Prepare texts for embedding
                texts = []
                for dialogue in batch:
                    text = embedding_service.prepare_text_for_embedding(
                        dialogue_tamil=dialogue.dialogue_tanglish,
                        dialogue_english=dialogue.dialogue_english,
                        context=dialogue.context,
                        emotion=dialogue.emotion
                    )
                    texts.append(text)

                # Generate embeddings in batch
                print("  Generating embeddings...")
                embeddings = embedding_service.batch_generate_embeddings(texts)

                # Update database
                for dialogue, embedding in zip(batch, embeddings):
                    dialogue.embedding = embedding
                    print(f"  + {dialogue.comedian} - {dialogue.emotion}")
                    total_generated += 1

                # Commit batch
                db.session.commit()
                print(f"  Batch {i//batch_size + 1} committed successfully")

            except Exception as e:
                print(f"  Error in batch {i//batch_size + 1}: {str(e)}")
                db.session.rollback()
                total_errors += len(batch)
                continue

        print(f"\n{'='*60}")
        print(f"Embedding generation complete!")
        print(f"Total embeddings generated: {total_generated}")
        print(f"Total errors: {total_errors}")
        print(f"{'='*60}")

        if total_generated > 0:
            print(f"\nSuccess! Your dialogues now have vector embeddings.")
            print(f"You can now use the RAG feature in the application!")


if __name__ == '__main__':
    generate_embeddings()
