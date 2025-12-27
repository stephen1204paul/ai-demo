# AI Comedy Lab

An educational Flask application demonstrating AI concepts (RAG, System Prompts, Fine-Tuning, and AI Agents) using Tamil comedian dialogues from Vadivelu, Santhanam, and Vivek.

## Features

- **RAG (Retrieval Augmented Generation)**: Vector similarity search with pgvector to retrieve relevant dialogues
- **System Prompts**: Personality shaping using different comedian personas
- **Fine-Tuning**: Prepare and train custom models (demonstration)
- **AI Agents**: Autonomous agents with tool-calling capabilities
- **Educational Dashboard**: Visual explanations of how each AI concept works

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL with pgvector extension
- **LLM**: OpenRouter API (access to multiple models)
- **Vector Embeddings**: OpenAI ada-002 via OpenRouter
- **Frontend**: HTML, Tailwind CSS, Alpine.js

## Prerequisites

- Python 3.9+
- PostgreSQL 13+ with pgvector extension
- OpenRouter API key ([Get one here](https://openrouter.ai/))

## Installation

### 1. Clone and Setup Virtual Environment

```bash
cd /Users/stephenpaulsamynathan/Code/web/group-project

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL with pgvector

#### Option A: Using Homebrew (macOS)

```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL
brew services start postgresql@15

# Create database
createdb ai_comedy_lab

# Enable pgvector extension
psql ai_comedy_lab -c "CREATE EXTENSION vector;"
```

#### Option B: Using Docker

```bash
docker run -d \
  --name ai-comedy-db \
  -e POSTGRES_DB=ai_comedy_lab \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  ankane/pgvector
```

### 3. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenRouter API key
# DATABASE_URL=postgresql://localhost/ai_comedy_lab
# OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
```

### 4. Initialize Database

```bash
# Initialize Flask-Migrate
flask db init

# Create initial migration
flask db migrate -m "Initial schema with pgvector"

# Apply migrations
flask db upgrade
```

### 5. Populate Database with Dialogues

```bash
# Import dialogues from JSON files
python scripts/populate_data.py

# Generate vector embeddings (requires OpenRouter API key)
python scripts/generate_embeddings.py
```

### 6. Run the Application

```bash
# Development server
python run.py

# Or using Flask CLI
flask run --debug
```

Visit `http://localhost:5000` in your browser!

## Project Structure

```
group-project/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration
│   ├── models/                  # Database models
│   │   ├── dialogue.py
│   │   ├── conversation.py
│   │   └── fine_tuning_job.py
│   ├── blueprints/              # Feature modules
│   │   ├── dashboard/           # Main UI
│   │   ├── rag/                 # RAG implementation
│   │   ├── system_prompts/      # System prompt demos
│   │   ├── fine_tuning/         # Fine-tuning workflows
│   │   └── agents/              # AI agents
│   ├── services/                # Business logic
│   │   ├── openrouter_client.py
│   │   ├── embedding_service.py
│   │   └── vector_search.py
│   ├── static/                  # CSS, JS, images
│   └── templates/               # HTML templates
├── data/
│   ├── raw/                     # JSON dialogue files
│   └── processed/               # Fine-tuning datasets
├── scripts/                     # Utility scripts
│   ├── populate_data.py
│   ├── generate_embeddings.py
│   └── prepare_fine_tuning.py
├── tests/                       # Test suite
├── requirements.txt
├── .env                         # Environment variables
└── run.py                       # Entry point
```

## API Endpoints

### RAG (Retrieval Augmented Generation)

```bash
# Chat with RAG
POST /rag/chat
{
  "message": "Tell me a joke about traffic",
  "comedian": "vadivelu"  # optional
}

# Direct similarity search
POST /rag/search
{
  "query": "traffic jokes",
  "top_k": 5
}

# Explain RAG concept
GET /rag/explain
```

### System Prompts

```bash
# Chat with specific personality
POST /system-prompts/chat
{
  "message": "Tell me about marriage",
  "comedian": "vadivelu"
}

# Compare all personalities
POST /system-prompts/compare
{
  "message": "What do you think about traffic?"
}

# Get available templates
GET /system-prompts/templates
```

### AI Agents

```bash
# Chat with agent
POST /agents/chat
{
  "message": "Find me funny dialogues about traffic from Santhanam"
}

# Get available tools
GET /agents/tools

# Explain agents concept
GET /agents/explain
```

### Dashboard

```bash
# Main dashboard
GET /

# Application statistics
GET /api/stats

# Individual concept page
GET /concept/rag
GET /concept/system-prompts
GET /concept/fine-tuning
GET /concept/agents
```

## Adding More Dialogues

1. Edit the JSON files in `data/raw/`:
   - `vadivelu_dialogues.json`
   - `santhanam_dialogues.json`
   - `vivek_dialogues.json`

2. Add dialogue in this format:
```json
{
  "comedian": "vadivelu",
  "movie_name": "Movie Name",
  "year": 2024,
  "character_name": "Character",
  "scene_description": "Scene description",
  "dialogue_tamil": "Tamil dialogue",
  "dialogue_english": "English translation",
  "context": "Context of the dialogue",
  "emotion": "comedy_type",
  "metadata": {
    "tags": ["tag1", "tag2"]
  }
}
```

3. Re-run the import scripts:
```bash
python scripts/populate_data.py
python scripts/generate_embeddings.py
```

## Development

### Running Tests

```bash
pytest
pytest tests/test_rag.py -v
pytest --cov=app tests/
```

### Code Formatting

```bash
# Format code
black app/

# Lint code
flake8 app/
```

### Database Migrations

```bash
# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

### Flask Shell

```bash
flask shell

>>> from app.models import Dialogue
>>> Dialogue.query.count()
>>> Dialogue.query.filter_by(comedian='vadivelu').all()
```

## Educational Use

This application is designed for teaching AI concepts:

1. **RAG**: Shows how vector similarity search works
   - Demonstrates embedding generation
   - Visualizes similarity scores
   - Explains how context is added to prompts

2. **System Prompts**: Shows prompt engineering
   - Same model, different personalities
   - Side-by-side comparisons
   - Explains role of system messages

3. **Fine-Tuning**: Explains model training
   - Shows training data preparation
   - Compares base vs fine-tuned models
   - Discusses when to use fine-tuning

4. **Agents**: Demonstrates autonomous AI
   - Shows tool selection process
   - Visualizes decision-making
   - Explains agent reasoning

## Troubleshooting

### pgvector Extension Not Found

```bash
# Install pgvector
# macOS: brew install pgvector
# Ubuntu: apt-get install postgresql-15-pgvector

# Enable in database
psql ai_comedy_lab -c "CREATE EXTENSION vector;"
```

### OpenRouter API Errors

- Verify your API key in `.env`
- Check your OpenRouter account balance
- Ensure you're using the correct model identifiers

### Database Connection Errors

- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in `.env`
- Ensure database exists: `createdb ai_comedy_lab`

### Import Errors

- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

## Next Steps

1. **Expand Dataset**: Add more dialogues (target: 100+ per comedian)
2. **Improve UI**: Add visualizations and animations
3. **Add Features**:
   - User authentication
   - Conversation history
   - Dialogue voting/rating
   - Search by movie/year
4. **Deploy**: Deploy to Render, Railway, or Heroku

## License

MIT

## Credits

- Tamil comedian dialogues used for educational purposes
- OpenRouter for LLM API access
- pgvector for vector similarity search

## Contributing

This is an educational project for students. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Add dialogues or features
4. Submit a pull request

---

Built with ❤️ for learning AI concepts through humor!
