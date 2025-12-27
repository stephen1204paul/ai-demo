"""RAG routes - Retrieval Augmented Generation demonstration."""

import time
import uuid
from flask import Blueprint, request, jsonify, render_template

from app import db
from app.models.conversation import Conversation
from app.services.openrouter_client import OpenRouterClient
from app.services.vector_search import VectorSearchService
from app.config import Config

bp = Blueprint('rag', __name__)


@bp.route('/')
def index():
    """Render the RAG demo page."""
    return render_template('rag_demo.html')


@bp.route('/chat', methods=['POST'])
def rag_chat():
    """
    RAG chat endpoint.

    Retrieves relevant dialogues and uses them as context for LLM response.
    """
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400

    user_message = data['message']
    session_id = data.get('session_id') or str(uuid.uuid4())

    # Optional filters
    comedian = data.get('comedian')
    emotion = data.get('emotion')

    try:
        start_time = time.time()

        # Step 1: Vector similarity search
        vector_search = VectorSearchService()
        retrieved_dialogues = vector_search.search_similar_dialogues(
            query=user_message,
            comedian=comedian,
            emotion=emotion
        )

        # Fallback: If no relevant dialogues found, use random famous dialogues
        retrieval_method = "vector_search"
        if len(retrieved_dialogues) < 3:
            retrieval_method = "fallback_random"
            # Query random dialogues from database
            from app.models.dialogue import Dialogue
            import random

            query = Dialogue.query.filter(Dialogue.embedding.isnot(None))

            # Apply filters if provided
            if comedian:
                query = query.filter_by(comedian=comedian)
            if emotion:
                query = query.filter_by(emotion=emotion)

            # Get random dialogues
            all_dialogues = query.limit(20).all()
            random_selection = random.sample(all_dialogues, min(5, len(all_dialogues)))

            # Convert to same format as vector search results
            retrieved_dialogues = [
                {
                    'id': d.id,
                    'comedian': d.comedian,
                    'dialogue_english': d.dialogue_english,
                    'dialogue_tanglish': d.dialogue_tanglish,
                    'context': d.context,
                    'emotion': d.emotion,
                    'similarity': 0.0  # No similarity score for random selection
                }
                for d in random_selection
            ]

        # Step 2: Build context from retrieved dialogues
        context = vector_search.build_rag_context(retrieved_dialogues)

        # Step 3: Create prompt with context
        system_message = """You are responding using authentic Tamil comedian dialogue style.

CRITICAL INSTRUCTIONS:
- Use the provided dialogue examples to answer the user's question
- Respond in the EXACT style of the retrieved dialogues: short, punchy, classic Tamil cinema comedy
- Quote or directly paraphrase the TANGLISH dialogues (Tamil words written in English) when possible
- ALWAYS use Tanglish format, NOT pure English translations
- Keep responses brief and to the point (2-4 sentences max)
- NO emojis, NO modern social media slang, NO internet references
- Use authentic Tanglish style like the examples (e.g., "Aaniye pudunga venam", "comedy geemady pannaliye", "Aiyyo saar", "nalla irukken")
- Match the comedian's personality and emotion from the context
- If English translations are provided in parentheses, IGNORE them - use only the Tanglish version

Pick the most relevant dialogue from the examples and deliver it in the comedian's authentic Tanglish style."""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"{context}\n\nUser question: {user_message}"}
        ]

        # Step 4: Get LLM response
        client = OpenRouterClient()
        response = client.chat_completion(
            messages=messages,
            model=Config.RAG_MODEL,
            temperature=0.7
        )

        # Step 5: Generate educational explanation
        educational_explanation = vector_search.get_educational_explanation(
            query=user_message,
            retrieved_dialogues=retrieved_dialogues
        )

        response_time = int((time.time() - start_time) * 1000)

        # Save conversation
        conversation = Conversation(
            session_id=session_id,
            ai_concept='rag',
            user_input=user_message,
            ai_response=response['response'],
            model_used=response['model'],
            thinking_process=educational_explanation,
            retrieved_dialogues=[
                {
                    'id': d['id'],
                    'dialogue': d['dialogue_english'] or d['dialogue_tanglish'],
                    'comedian': d['comedian'],
                    'emotion': d['emotion'],
                    'similarity': d['similarity']
                }
                for d in retrieved_dialogues
            ],
            response_time_ms=response_time
        )

        db.session.add(conversation)
        db.session.commit()

        # Return response with educational data
        return jsonify({
            'response': response['response'],
            'session_id': session_id,
            'retrieval_method': retrieval_method,
            'retrieved_dialogues': [
                {
                    'id': d['id'],
                    'comedian': d['comedian'],
                    'dialogue_english': d['dialogue_english'],
                    'dialogue_tanglish': d['dialogue_tanglish'],
                    'context': d['context'],
                    'emotion': d['emotion'],
                    'similarity': round(d['similarity'], 3) if d['similarity'] > 0 else None
                }
                for d in retrieved_dialogues
            ],
            'educational_explanation': educational_explanation,
            'context_used': context,
            'response_time_ms': response_time,
            'usage': response['usage']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/search', methods=['POST'])
def direct_search():
    """
    Direct similarity search endpoint for educational demonstration.

    Shows raw vector search results without LLM generation.
    """
    data = request.get_json()

    if not data or 'query' not in data:
        return jsonify({'error': 'Query is required'}), 400

    query = data['query']
    top_k = data.get('top_k', Config.SIMILARITY_TOP_K)
    threshold = data.get('threshold', Config.SIMILARITY_THRESHOLD)
    comedian = data.get('comedian')
    emotion = data.get('emotion')

    try:
        vector_search = VectorSearchService()
        results = vector_search.search_similar_dialogues(
            query=query,
            top_k=top_k,
            threshold=threshold,
            comedian=comedian,
            emotion=emotion
        )

        return jsonify({
            'query': query,
            'results_count': len(results),
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/explain', methods=['GET'])
def explain_rag():
    """
    Get educational explanation of RAG concept.
    """
    explanation = {
        'concept': 'RAG (Retrieval Augmented Generation)',
        'what_it_is': (
            'RAG combines information retrieval with AI text generation. '
            'Instead of relying only on what the AI learned during training, '
            'RAG retrieves relevant information from a database and includes it '
            'as context in the prompt.'
        ),
        'how_it_works': [
            {
                'step': 1,
                'title': 'Convert query to embedding',
                'description': 'Your question is converted into a vector (list of numbers) that captures its meaning'
            },
            {
                'step': 2,
                'title': 'Search similar content',
                'description': 'The database finds dialogues with similar meaning using vector math (cosine similarity)'
            },
            {
                'step': 3,
                'title': 'Build context',
                'description': 'Retrieved dialogues are formatted into context for the AI'
            },
            {
                'step': 4,
                'title': 'Generate response',
                'description': 'The AI uses both its training and the retrieved context to respond'
            }
        ],
        'benefits': [
            'Access to up-to-date information not in training data',
            'More accurate, grounded responses',
            'Can cite specific sources',
            'No need to retrain the model'
        ],
        'vs_alternatives': {
            'vs_fine_tuning': 'RAG retrieves information, fine-tuning modifies the model itself',
            'vs_system_prompts': 'RAG adds external knowledge, system prompts shape behavior',
            'vs_agents': 'RAG is passive retrieval, agents actively decide what to retrieve'
        }
    }

    return jsonify(explanation)
