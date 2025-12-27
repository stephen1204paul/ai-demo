"""Flask application factory for AI Comedy Lab."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

from app.config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='development'):
    """
    Create and configure the Flask application.

    Args:
        config_name: Configuration to use ('development', 'production', 'testing')

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Register shell context
    @app.shell_context_processor
    def make_shell_context():
        """Make database and models available in flask shell."""
        from app.models import dialogue, conversation, fine_tuning_job
        return {
            'db': db,
            'Dialogue': dialogue.Dialogue,
            'Conversation': conversation.Conversation,
            'FineTuningJob': fine_tuning_job.FineTuningJob,
        }

    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    # Import blueprints
    from app.blueprints.dashboard import routes as dashboard
    from app.blueprints.rag import routes as rag
    from app.blueprints.system_prompts import routes as system_prompts
    from app.blueprints.fine_tuning import routes as fine_tuning
    from app.blueprints.agents import routes as agents

    # Register blueprints
    app.register_blueprint(dashboard.bp, url_prefix='/')
    app.register_blueprint(rag.bp, url_prefix='/rag')
    app.register_blueprint(system_prompts.bp, url_prefix='/system-prompts')
    app.register_blueprint(fine_tuning.bp, url_prefix='/fine-tuning')
    app.register_blueprint(agents.bp, url_prefix='/agents')


def register_error_handlers(app):
    """Register error handlers."""

    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle uncaught exceptions."""
        app.logger.error(f'Unhandled exception: {str(error)}')
        return {'error': 'An unexpected error occurred'}, 500
