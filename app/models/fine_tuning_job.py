"""Fine-tuning job model - tracks fine-tuning experiments."""

from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

from app import db


class FineTuningJob(db.Model):
    """
    Fine-tuning job model for tracking model training experiments.

    Stores information about fine-tuning jobs including status,
    hyperparameters, and resulting model identifiers.
    """

    __tablename__ = 'fine_tuning_jobs'

    id = db.Column(db.Integer, primary_key=True)

    # Job identification
    job_id = db.Column(db.String(200), unique=True, nullable=False)

    # Model information
    model_name = db.Column(db.String(100))
    base_model = db.Column(db.String(100))
    fine_tuned_model = db.Column(db.String(200))  # Resulting model ID

    # Training configuration
    training_file_path = db.Column(db.Text)
    training_samples = db.Column(db.Integer)
    hyperparameters = db.Column(JSONB)

    # Status tracking
    status = db.Column(
        db.String(50),
        default='pending'
    )  # 'pending', 'running', 'completed', 'failed'

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<FineTuningJob {self.job_id}: {self.status}>'

    def to_dict(self):
        """Convert fine-tuning job to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'model_name': self.model_name,
            'base_model': self.base_model,
            'fine_tuned_model': self.fine_tuned_model,
            'training_file_path': self.training_file_path,
            'training_samples': self.training_samples,
            'hyperparameters': self.hyperparameters,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }

    @classmethod
    def get_by_status(cls, status):
        """Get all jobs with a specific status."""
        return cls.query.filter_by(status=status).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_latest(cls, limit=10):
        """Get the most recent fine-tuning jobs."""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()

    def mark_completed(self, fine_tuned_model_id):
        """Mark job as completed with resulting model ID."""
        self.status = 'completed'
        self.fine_tuned_model = fine_tuned_model_id
        self.completed_at = datetime.utcnow()
        db.session.commit()

    def mark_failed(self):
        """Mark job as failed."""
        self.status = 'failed'
        self.completed_at = datetime.utcnow()
        db.session.commit()
