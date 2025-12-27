"""Dialogue model - stores comedian dialogues with vector embeddings."""

from datetime import datetime
from pgvector.sqlalchemy import Vector

from app import db


class Dialogue(db.Model):
    """
    Simplified dialogue model for storing comedian dialogues with embeddings.

    This model stores Tamil comedian dialogues in a minimal schema focused on
    core AI functionality (RAG, system prompts, fine-tuning, agents).
    """

    __tablename__ = 'dialogues'

    id = db.Column(db.Integer, primary_key=True)

    # Comedian identification
    comedian = db.Column(db.String(50), nullable=False, index=True)

    # Dialogue content (two versions)
    dialogue_english = db.Column(db.Text, nullable=False)  # Clean English translation
    dialogue_tanglish = db.Column(db.Text)  # Tamil-English mix (how it's actually spoken)

    # Context and classification
    context = db.Column(db.Text)  # When/why this dialogue is used
    emotion = db.Column(db.String(50), index=True)  # Comedy type: sarcasm, wisdom, etc.

    # Vector embedding for RAG
    embedding = db.Column(Vector(1536))  # OpenAI ada-002 dimension

    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Dialogue {self.id}: {self.comedian} - {self.emotion}>'

    def to_dict(self):
        """Convert dialogue to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'comedian': self.comedian,
            'dialogue_english': self.dialogue_english,
            'dialogue_tanglish': self.dialogue_tanglish,
            'context': self.context,
            'emotion': self.emotion,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def search_by_comedian(cls, comedian_name):
        """Get all dialogues for a specific comedian."""
        return cls.query.filter_by(comedian=comedian_name).all()

    @classmethod
    def search_by_emotion(cls, emotion):
        """Get all dialogues with a specific emotion."""
        return cls.query.filter_by(emotion=emotion).all()
