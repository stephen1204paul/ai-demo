"""Configuration management for AI Comedy Lab application."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class."""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://localhost/ai_comedy_lab'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # OpenRouter API (for RAG, System Prompts, Agents)
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'
    OPENROUTER_SITE_URL = os.getenv('OPENROUTER_SITE_URL', 'http://localhost:5000')
    OPENROUTER_APP_NAME = os.getenv('OPENROUTER_APP_NAME', 'AI Comedy Lab')

    # OpenAI API (for Fine-Tuning)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_BASE_URL = 'https://api.openai.com/v1'

    # Model Configuration
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'openai/text-embedding-ada-002')
    EMBEDDING_DIMENSION = 1536  # OpenAI ada-002 dimension

    # OpenRouter models (use openai/ prefix for OpenRouter)
    RAG_MODEL = os.getenv('RAG_MODEL', 'openai/gpt-3.5-turbo')
    SYSTEM_PROMPT_MODEL = os.getenv('SYSTEM_PROMPT_MODEL', 'openai/gpt-3.5-turbo')
    AGENT_MODEL = os.getenv('AGENT_MODEL', 'openai/gpt-4-turbo-preview')

    # OpenAI model for fine-tuning (no prefix, direct OpenAI model name)
    FINE_TUNING_BASE_MODEL = os.getenv('FINE_TUNING_BASE_MODEL', 'gpt-4.1-mini-2025-04-14')

    # Vector Search Settings
    SIMILARITY_TOP_K = int(os.getenv('SIMILARITY_TOP_K', 5))
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', 0.7))

    # Fine-tuning
    FINE_TUNING_DATA_PATH = 'data/processed/fine_tuning_dataset.jsonl'

    # CORS
    CORS_HEADERS = 'Content-Type'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False

    # Additional production settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://localhost/ai_comedy_lab_test'
    )


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
