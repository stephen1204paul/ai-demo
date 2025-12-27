"""Dashboard routes - main educational interface."""

from flask import Blueprint, render_template, jsonify

from app.models.dialogue import Dialogue
from app.models.conversation import Conversation

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')


@bp.route('/api/stats')
def get_stats():
    """Get application statistics for dashboard."""
    stats = {
        'total_dialogues': Dialogue.query.count(),
        'total_conversations': Conversation.query.count(),
        'dialogues_by_comedian': {
            'vadivelu': Dialogue.query.filter_by(comedian='vadivelu').count(),
            'santhanam': Dialogue.query.filter_by(comedian='santhanam').count(),
            'vivek': Dialogue.query.filter_by(comedian='vivek').count(),
        },
        'conversations_by_concept': {
            'rag': Conversation.query.filter_by(ai_concept='rag').count(),
            'system_prompt': Conversation.query.filter_by(ai_concept='system_prompt').count(),
            'fine_tuned': Conversation.query.filter_by(ai_concept='fine_tuned').count(),
            'agent': Conversation.query.filter_by(ai_concept='agent').count(),
        }
    }

    return jsonify(stats)


@bp.route('/concept/<concept_name>')
def concept_page(concept_name):
    """Individual AI concept explanation page."""
    valid_concepts = ['rag', 'system-prompts', 'fine-tuning', 'agents']

    if concept_name not in valid_concepts:
        return {'error': 'Invalid concept'}, 404

    return render_template(f'{concept_name.replace("-", "_")}_demo.html')
