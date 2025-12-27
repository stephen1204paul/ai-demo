"""System Prompts routes - personality shaping demonstration."""

import time
import uuid
from flask import Blueprint, request, jsonify, render_template

from app import db
from app.models.conversation import Conversation
from app.services.openrouter_client import OpenRouterClient
from app.config import Config

bp = Blueprint('system_prompts', __name__)

@bp.route('/')
def index():
    """Render the System Prompts demo page."""
    return render_template('system_prompts.html')


# Pre-defined comedian personalities
COMEDIAN_PROMPTS = {
    'vadivelu': """You are Vadivelu, the legendary Tamil comedian known for:
- Exaggerated expressions and physical comedy references in your speech
- Self-deprecating humor and innocent confusion
- Famous catchphrases like "Enna koduma sir idhu" (What atrocity is this, sir)
- Getting into absurd situations with comedic timing
- Mixing Tamil and English naturally in conversation

Respond in Vadivelu's comedic style, incorporating his signature mannerisms and catchphrases when appropriate.""",

    'santhanam': """You are Santhanam, the modern Tamil comedian known for:
- Quick-witted one-liners and perfect timing
- Contemporary references and wordplay
- Self-aware, meta-humor about cinema and life
- Confident, slightly sarcastic personality
- Sharp observations delivered with casual cool

Respond in Santhanam's style with modern, relatable comedy and clever wordplay.""",

    'vivek': """You are Vivek, the intellectual Tamil comedian known for:
- Social commentary woven seamlessly into comedy
- Thoughtful humor with educational messages
- Literary and cultural references
- Wordplay in both Tamil and English
- Making people laugh while making them think

Respond in Vivek's style with intelligent, message-oriented humor that entertains and enlightens."""
}


@bp.route('/chat', methods=['POST'])
def system_prompt_chat():
    """
    System prompt chat endpoint.

    Demonstrates how system prompts shape AI personality.
    """
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400

    if 'comedian' not in data:
        return jsonify({'error': 'Comedian personality is required'}), 400

    user_message = data['message']
    comedian = data['comedian'].lower()
    session_id = data.get('session_id') or str(uuid.uuid4())

    if comedian not in COMEDIAN_PROMPTS:
        return jsonify({'error': f'Invalid comedian. Choose from: {list(COMEDIAN_PROMPTS.keys())}'}), 400

    try:
        start_time = time.time()

        # Get system prompt for comedian
        system_prompt = COMEDIAN_PROMPTS[comedian]

        # Create messages with system prompt
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        # Get LLM response
        client = OpenRouterClient()
        response = client.chat_completion(
            messages=messages,
            model=Config.SYSTEM_PROMPT_MODEL,
            temperature=0.8  # Higher temperature for more creative comedy
        )

        response_time = int((time.time() - start_time) * 1000)

        # Educational explanation
        educational_explanation = {
            "process": "System Prompt Personality Shaping",
            "steps": [
                {
                    "step": 1,
                    "title": "Load Personality Prompt",
                    "description": f"Selected {comedian.title()}'s personality prompt with specific traits and style"
                },
                {
                    "step": 2,
                    "title": "Set System Message",
                    "description": "System message sets the AI's role and behavior for the entire conversation"
                },
                {
                    "step": 3,
                    "title": "Generate Response",
                    "description": "AI responds in character, following the personality guidelines"
                }
            ],
            "why_system_prompts": (
                "System prompts tell the AI 'who' it should be without changing the underlying model. "
                "The same AI can act as different comedians just by changing the system message. "
                "This is the simplest way to customize AI behavior."
            )
        }

        # Save conversation
        conversation = Conversation(
            session_id=session_id,
            ai_concept='system_prompt',
            user_input=user_message,
            ai_response=response['response'],
            model_used=response['model'],
            system_prompt=system_prompt,
            thinking_process=educational_explanation,
            response_time_ms=response_time
        )

        db.session.add(conversation)
        db.session.commit()

        return jsonify({
            'response': response['response'],
            'session_id': session_id,
            'comedian': comedian,
            'system_prompt': system_prompt,
            'educational_explanation': educational_explanation,
            'response_time_ms': response_time,
            'usage': response['usage']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/compare', methods=['POST'])
def compare_personalities():
    """
    Compare responses from all three comedian personalities.

    Educational demonstration showing how system prompts change behavior.
    """
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400

    user_message = data['message']

    try:
        client = OpenRouterClient()
        comparisons = []

        # Get response from each comedian
        for comedian, system_prompt in COMEDIAN_PROMPTS.items():
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            response = client.chat_completion(
                messages=messages,
                model=Config.SYSTEM_PROMPT_MODEL,
                temperature=0.8
            )

            comparisons.append({
                'comedian': comedian,
                'response': response['response'],
                'system_prompt': system_prompt
            })

        return jsonify({
            'message': user_message,
            'comparisons': comparisons,
            'explanation': (
                'Notice how the same AI model produces completely different responses '
                'based only on the system prompt. This demonstrates the power of '
                'prompt engineering to customize AI behavior without retraining.'
            )
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/templates', methods=['GET'])
def get_templates():
    """Get all available system prompt templates."""
    return jsonify({
        'templates': [
            {
                'comedian': comedian,
                'prompt': prompt,
                'description': prompt.split('\n')[0].replace('You are ', '')
            }
            for comedian, prompt in COMEDIAN_PROMPTS.items()
        ]
    })
