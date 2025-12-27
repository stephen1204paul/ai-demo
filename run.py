"""Application entry point for AI Comedy Lab."""

import os
from app import create_app

# Get configuration from environment
config_name = os.getenv('FLASK_ENV', 'development')

# Create Flask application
app = create_app(config_name)

if __name__ == '__main__':
    # Run development server
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=(config_name == 'development')
    )
