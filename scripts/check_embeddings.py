"""
Quick script to check embedding status in the database.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models.dialogue import Dialogue


def check_embeddings():
    """Check embedding status in database."""
    app = create_app('development')

    with app.app_context():
        # Count total dialogues
        total = Dialogue.query.count()

        # Count dialogues with embeddings
        with_embeddings = Dialogue.query.filter(
            Dialogue.embedding.isnot(None)
        ).count()

        # Count dialogues without embeddings
        without_embeddings = Dialogue.query.filter(
            Dialogue.embedding.is_(None)
        ).count()

        print("=" * 60)
        print("EMBEDDING STATUS CHECK")
        print("=" * 60)
        print(f"Total dialogues in database: {total}")
        print(f"Dialogues WITH embeddings:   {with_embeddings}")
        print(f"Dialogues WITHOUT embeddings: {without_embeddings}")
        print("=" * 60)

        if with_embeddings > 0:
            print("\n✓ Embeddings found in database!")

            # Show sample
            sample = Dialogue.query.filter(
                Dialogue.embedding.isnot(None)
            ).first()

            if sample:
                print(f"\nSample dialogue with embedding:")
                print(f"  ID: {sample.id}")
                print(f"  Comedian: {sample.comedian}")
                print(f"  Emotion: {sample.emotion}")
                embedding_dim = len(sample.embedding) if sample.embedding is not None else 0
                print(f"  Embedding dimension: {embedding_dim}")
        else:
            print("\n✗ No embeddings found in database.")
            print("Run: python scripts/generate_embeddings.py")


if __name__ == '__main__':
    check_embeddings()
