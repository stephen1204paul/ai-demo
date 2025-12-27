"""Conversation model - stores user interactions and AI responses."""

from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

from app import db


class Conversation(db.Model):
    """
    Conversation model for tracking user interactions with different AI concepts.

    Stores conversation history along with educational metadata showing
    how each AI concept (RAG, system prompts, fine-tuning, agents) works.
    """

    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)

    # Session tracking
    session_id = db.Column(db.String(100), nullable=False, index=True)

    # AI concept used
    ai_concept = db.Column(
        db.String(50),
        nullable=False,
        index=True
    )  # 'rag', 'system_prompt', 'fine_tuned', 'agent'

    # Conversation content
    user_input = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)

    # Model information
    model_used = db.Column(db.String(100))

    # Educational metadata (varies by AI concept)
    thinking_process = db.Column(JSONB)  # Step-by-step explanation
    retrieved_dialogues = db.Column(JSONB)  # For RAG: what was retrieved
    system_prompt = db.Column(db.Text)  # For system prompts: the prompt used
    agent_actions = db.Column(JSONB)  # For agents: decision trail

    # Performance metrics
    response_time_ms = db.Column(db.Integer)

    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Conversation {self.id}: {self.ai_concept} - {self.session_id}>'

    def to_dict(self):
        """Convert conversation to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'ai_concept': self.ai_concept,
            'user_input': self.user_input,
            'ai_response': self.ai_response,
            'model_used': self.model_used,
            'thinking_process': self.thinking_process,
            'retrieved_dialogues': self.retrieved_dialogues,
            'system_prompt': self.system_prompt,
            'agent_actions': self.agent_actions,
            'response_time_ms': self.response_time_ms,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def get_session_history(cls, session_id):
        """Get all conversations for a specific session."""
        return cls.query.filter_by(session_id=session_id).order_by(cls.created_at).all()

    @classmethod
    def get_by_concept(cls, ai_concept):
        """Get all conversations for a specific AI concept."""
        return cls.query.filter_by(ai_concept=ai_concept).order_by(cls.created_at.desc()).all()
