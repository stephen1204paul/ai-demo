"""Agents routes - autonomous AI agent demonstration."""

import json
import time
import uuid
from flask import Blueprint, request, jsonify, render_template

from app import db
from app.models.dialogue import Dialogue
from app.models.conversation import Conversation
from app.services.openrouter_client import OpenRouterClient
from app.config import Config

bp = Blueprint('agents', __name__)


@bp.route('/')
def index():
    """Render the Agents demo page."""
    return render_template('agents.html')

# Define tools the agent can use
AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_dialogues",
            "description": "Search the dialogue database for specific comedian, movie, or emotion",
            "parameters": {
                "type": "object",
                "properties": {
                    "comedian": {
                        "type": "string",
                        "enum": ["vadivelu", "santhanam", "vivek"],
                        "description": "Tamil comedian name"
                    },
                    "emotion": {
                        "type": "string",
                        "description": "Emotional tone (e.g., 'comedy', 'sarcasm', 'angry')"
                    },
                    "movie": {
                        "type": "string",
                        "description": "Movie name"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 5
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_comedian_stats",
            "description": "Get statistics about a comedian's dialogues in the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "comedian": {
                        "type": "string",
                        "enum": ["vadivelu", "santhanam", "vivek"],
                        "description": "Tamil comedian name"
                    }
                },
                "required": ["comedian"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_random_dialogue",
            "description": "Get a random funny dialogue from the database, optionally filtered by comedian",
            "parameters": {
                "type": "object",
                "properties": {
                    "comedian": {
                        "type": "string",
                        "enum": ["vadivelu", "santhanam", "vivek"],
                        "description": "Optional: specific comedian"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of random dialogues to return",
                        "default": 1
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_comedians",
            "description": "Compare statistics between two or more comedians",
            "parameters": {
                "type": "object",
                "properties": {
                    "comedians": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["vadivelu", "santhanam", "vivek"]
                        },
                        "description": "List of comedians to compare",
                        "minItems": 2
                    }
                },
                "required": ["comedians"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_emotion_patterns",
            "description": "Analyze emotion distribution across all comedians or a specific comedian",
            "parameters": {
                "type": "object",
                "properties": {
                    "comedian": {
                        "type": "string",
                        "enum": ["vadivelu", "santhanam", "vivek"],
                        "description": "Optional: analyze specific comedian only"
                    }
                }
            }
        }
    }
]


def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute agent tool and return result."""
    if tool_name == "search_dialogues":
        # Search dialogues based on criteria
        query = Dialogue.query

        if 'comedian' in arguments:
            query = query.filter_by(comedian=arguments['comedian'])

        if 'emotion' in arguments:
            query = query.filter_by(emotion=arguments['emotion'])

        if 'movie' in arguments:
            query = query.filter_by(movie_name=arguments['movie'])

        limit = arguments.get('limit', 5)
        dialogues = query.limit(limit).all()

        results = [
            {
                'comedian': d.comedian,
                'movie': d.movie_name,
                'dialogue': d.dialogue_tanglish or d.dialogue_english,
                'emotion': d.emotion
            }
            for d in dialogues
        ]

        return json.dumps({
            'found': len(results),
            'dialogues': results
        })

    elif tool_name == "get_comedian_stats":
        comedian = arguments['comedian']

        total_dialogues = Dialogue.query.filter_by(comedian=comedian).count()
        movies = db.session.query(Dialogue.movie_name).filter_by(
            comedian=comedian
        ).distinct().all()

        emotions = db.session.query(
            Dialogue.emotion,
            db.func.count(Dialogue.id)
        ).filter_by(
            comedian=comedian
        ).group_by(Dialogue.emotion).all()

        return json.dumps({
            'comedian': comedian,
            'total_dialogues': total_dialogues,
            'unique_movies': len(movies),
            'movies': [m[0] for m in movies if m[0]],
            'emotions': {e[0]: e[1] for e in emotions if e[0]}
        })

    elif tool_name == "get_random_dialogue":
        import random

        query = Dialogue.query

        if 'comedian' in arguments and arguments['comedian']:
            query = query.filter_by(comedian=arguments['comedian'])

        count = arguments.get('count', 1)
        all_dialogues = query.all()

        if not all_dialogues:
            return json.dumps({'error': 'No dialogues found', 'dialogues': []})

        random_dialogues = random.sample(all_dialogues, min(count, len(all_dialogues)))

        results = [
            {
                'comedian': d.comedian,
                'dialogue': d.dialogue_tanglish or d.dialogue_english,
                'emotion': d.emotion,
                'context': d.context
            }
            for d in random_dialogues
        ]

        return json.dumps({
            'count': len(results),
            'dialogues': results
        })

    elif tool_name == "compare_comedians":
        comedians = arguments['comedians']
        comparison = {}

        for comedian in comedians:
            total = Dialogue.query.filter_by(comedian=comedian).count()
            movies = db.session.query(Dialogue.movie_name).filter_by(
                comedian=comedian
            ).distinct().count()

            emotions = db.session.query(
                Dialogue.emotion,
                db.func.count(Dialogue.id)
            ).filter_by(
                comedian=comedian
            ).group_by(Dialogue.emotion).all()

            comparison[comedian] = {
                'total_dialogues': total,
                'unique_movies': movies,
                'top_emotions': [e[0] for e in sorted(emotions, key=lambda x: x[1], reverse=True)[:3] if e[0]]
            }

        return json.dumps({
            'comparison': comparison,
            'comedians_compared': len(comedians)
        })

    elif tool_name == "analyze_emotion_patterns":
        query = db.session.query(
            Dialogue.emotion,
            db.func.count(Dialogue.id)
        )

        if 'comedian' in arguments and arguments['comedian']:
            query = query.filter_by(comedian=arguments['comedian'])

        emotions = query.group_by(Dialogue.emotion).all()

        total = sum(e[1] for e in emotions if e[0])

        patterns = {
            e[0]: {
                'count': e[1],
                'percentage': round((e[1] / total * 100), 1) if total > 0 else 0
            }
            for e in emotions if e[0]
        }

        return json.dumps({
            'total_dialogues': total,
            'emotion_patterns': patterns,
            'most_common': max(patterns.keys(), key=lambda k: patterns[k]['count']) if patterns else None
        })

    return json.dumps({'error': 'Unknown tool'})


@bp.route('/chat', methods=['POST'])
def agent_chat():
    """
    Agent chat endpoint.

    Demonstrates autonomous AI agents that can decide which tools to use.
    """
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400

    user_message = data['message']
    session_id = data.get('session_id') or str(uuid.uuid4())

    try:
        start_time = time.time()

        # Log the model being used
        print(f"\n{'='*60}")
        print(f"AGENT MODEL: {Config.AGENT_MODEL}")
        print(f"{'='*60}\n")

        # System prompt for agent
        system_prompt = """You are an AI agent with access to Tamil comedian dialogue database. You respond in AUTHENTIC TANGLISH STYLE (Tamil-English mix) like a Tamil cinema fan.

CRITICAL INSTRUCTIONS:
- Respond in Tanglish style with phrases like "Aiyyo saar", "Enna koduma", "Super-u", "Comedy-ya irukku"
- Use tools proactively to demonstrate capabilities
- When greeting or simple questions: Still call tools to show what you can do
- Quote actual Tanglish dialogues from tool results when possible
- Keep it FUN and COMEDIC while being helpful
- NO pure English responses - always mix Tamil words

TOOL USAGE STRATEGY:
- For greetings: Call get_random_dialogue to welcome them with comedy
- For questions: Use appropriate search/stats tools
- Be PROACTIVE - demonstrate your autonomous capabilities

Example Tanglish style: "Aiyyo saar! Naan romba nalla irukken! Wait panna, I'll search some comedy dialogues for you-nu..."

Always use tools to make responses more interesting and demonstrate agent capabilities!"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        client = OpenRouterClient()
        agent_actions = []

        # Agent loop (max 3 iterations to prevent infinite loops)
        max_iterations = 3
        for iteration in range(max_iterations):
            # Get AI response with tools
            response = client.chat_completion(
                messages=messages,
                model=Config.AGENT_MODEL,
                tools=AGENT_TOOLS,
                tool_choice="auto"
            )

            # Check if AI wants to call tools
            if 'tool_calls' not in response or not response['tool_calls']:
                # No tool calls - agent has final answer
                final_response = response['response']
                break

            # Execute tool calls
            for tool_call in response['tool_calls']:
                tool_name = tool_call['function']['name']
                arguments = json.loads(tool_call['function']['arguments'])

                # Log action
                agent_actions.append({
                    'iteration': iteration + 1,
                    'action': 'tool_call',
                    'tool': tool_name,
                    'arguments': arguments,
                    'reasoning': 'Agent decided to use this tool'
                })

                # Execute tool
                tool_result = execute_tool(tool_name, arguments)

                # Log result
                agent_actions.append({
                    'iteration': iteration + 1,
                    'action': 'tool_result',
                    'tool': tool_name,
                    'result': json.loads(tool_result)
                })

                # Add tool result to conversation
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call['id'],
                    "content": tool_result
                })

            # Continue loop to get next response
        else:
            # Max iterations reached
            final_response = "I've reached my maximum number of tool calls. Let me know if you need anything else!"

        response_time = int((time.time() - start_time) * 1000)

        # Educational explanation
        educational_explanation = {
            "process": "AI Agent with Tool Use",
            "what_happened": agent_actions,
            "steps": [
                {
                    "step": 1,
                    "title": "Analyze Request",
                    "description": "Agent understood what you need and identified relevant tools"
                },
                {
                    "step": 2,
                    "title": "Decide on Tools",
                    "description": f"Agent autonomously chose to call {len([a for a in agent_actions if a['action'] == 'tool_call'])} tool(s)"
                },
                {
                    "step": 3,
                    "title": "Execute Tools",
                    "description": "Tools were executed and results returned to agent"
                },
                {
                    "step": 4,
                    "title": "Synthesize Response",
                    "description": "Agent used tool results to formulate final answer"
                }
            ],
            "why_agents": (
                "Agents can autonomously decide which actions to take based on the task. "
                "Unlike simple prompting, agents can chain multiple tools together and "
                "make decisions at each step. This enables complex, multi-step workflows."
            )
        }

        # Save conversation
        conversation = Conversation(
            session_id=session_id,
            ai_concept='agent',
            user_input=user_message,
            ai_response=final_response,
            model_used=Config.AGENT_MODEL,
            thinking_process=educational_explanation,
            agent_actions=agent_actions,
            response_time_ms=response_time
        )

        db.session.add(conversation)
        db.session.commit()

        return jsonify({
            'response': final_response,
            'session_id': session_id,
            'agent_actions': agent_actions,
            'educational_explanation': educational_explanation,
            'response_time_ms': response_time
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/tools', methods=['GET'])
def get_tools():
    """Get list of available agent tools."""
    return jsonify({
        'tools': [
            {
                'name': tool['function']['name'],
                'description': tool['function']['description'],
                'parameters': tool['function']['parameters']
            }
            for tool in AGENT_TOOLS
        ]
    })


@bp.route('/explain', methods=['GET'])
def explain_agents():
    """Get educational explanation of AI agents."""
    explanation = {
        'concept': 'AI Agents',
        'what_it_is': (
            'AI agents are autonomous systems that can decide which actions to take '
            'and which tools to use based on the task at hand. Unlike simple chatbots '
            'that just respond, agents can plan, execute tools, and adapt their strategy.'
        ),
        'how_it_works': [
            {
                'step': 1,
                'title': 'Define Tools',
                'description': 'Create functions the agent can call (search, calculate, etc.)'
            },
            {
                'step': 2,
                'title': 'Agent Decides',
                'description': 'AI decides which tool(s) to use based on user request'
            },
            {
                'step': 3,
                'title': 'Execute Tools',
                'description': 'Selected tools are executed with appropriate parameters'
            },
            {
                'step': 4,
                'title': 'Agent Synthesis',
                'description': 'Agent uses tool results to complete the task or make next decision'
            }
        ],
        'examples': [
            'Search database → Analyze results → Generate response',
            'Get stats → Compare comedians → Make recommendation',
            'Check availability → Search alternatives → Present options'
        ],
        'vs_alternatives': {
            'vs_rag': 'Agents decide what to retrieve, RAG retrieves similar content',
            'vs_system_prompts': 'Agents take actions, prompts shape personality',
            'vs_fine_tuning': 'Agents improve behavior, fine-tuning improves responses'
        }
    }

    return jsonify(explanation)
