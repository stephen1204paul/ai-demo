"""Fine-tuning routes - model training demonstration."""

import time
import uuid
from pathlib import Path
from flask import Blueprint, request, jsonify, render_template

from app import db
from app.models.fine_tuning_job import FineTuningJob
from app.models.conversation import Conversation
from app.services.fine_tune_service import FineTuneService
from app.config import Config

bp = Blueprint('fine_tuning', __name__)


@bp.route('/')
def index():
    """Render the Fine-tuning demo page."""
    return render_template('fine_tuning.html')


@bp.route('/start', methods=['POST'])
def start_fine_tuning():
    """
    Start a fine-tuning job.

    Request body:
    {
        "model_name": "vadivelu_comedian_v1",
        "hyperparameters": {
            "n_epochs": 3,
            "batch_size": 4
        }
    }
    """
    data = request.get_json()

    if not data or 'model_name' not in data:
        return jsonify({'error': 'Model name is required'}), 400

    model_name = data['model_name']
    hyperparameters = data.get('hyperparameters')

    # Check if training file exists
    from flask import current_app
    project_root = Path(current_app.root_path).parent
    training_file = project_root / Config.FINE_TUNING_DATA_PATH

    if not training_file.exists():
        return jsonify({
            'error': 'Training file not found',
            'message': 'Please run: python scripts/prepare_fine_tuning.py first',
            'expected_path': str(training_file)
        }), 400

    try:
        service = FineTuneService()

        # Step 1: Upload training file
        print(f"Uploading training file: {training_file}")
        file_id = service.upload_training_file(str(training_file))

        # Step 2: Create fine-tuning job
        print(f"Creating fine-tuning job for model: {model_name}")
        job = service.create_fine_tuning_job(
            training_file_id=file_id,
            model_name=model_name,
            hyperparameters=hyperparameters
        )

        return jsonify({
            'success': True,
            'job_id': job.job_id,
            'model_name': job.model_name,
            'status': job.status,
            'message': 'Fine-tuning job started successfully',
            'next_steps': [
                f'Monitor status: GET /fine-tuning/status/{job.job_id}',
                'Fine-tuning typically takes 10-60 minutes depending on dataset size',
                'You will receive an email when training completes'
            ]
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'troubleshooting': [
                'Verify your OPENAI_API_KEY is set in .env file',
                'Check that you have an active OpenAI account with billing enabled',
                'Ensure the training file is valid JSONL format',
                'Verify you have at least 10 training examples',
                'Check OpenAI fine-tuning documentation for model support'
            ]
        }), 500


@bp.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get fine-tuning job status."""
    try:
        service = FineTuneService()
        status = service.check_job_status(job_id)

        # Get database record for additional info
        job = FineTuningJob.query.filter_by(job_id=job_id).first()

        if not job:
            return jsonify({'error': 'Job not found in database'}), 404

        return jsonify({
            'job_id': status['job_id'],
            'status': status['status'],
            'model_name': job.model_name,
            'base_model': status['model'],
            'fine_tuned_model': status['fine_tuned_model'],
            'created_at': status['created_at'],
            'finished_at': status['finished_at'],
            'trained_tokens': status['trained_tokens'],
            'hyperparameters': job.hyperparameters,
            'training_samples': job.training_samples,
            'status_explanation': get_status_explanation(status['status'])
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/jobs', methods=['GET'])
def list_jobs():
    """List all fine-tuning jobs."""
    # Get from database
    jobs = FineTuningJob.get_latest(limit=20)

    return jsonify({
        'jobs': [job.to_dict() for job in jobs],
        'total': len(jobs)
    })


@bp.route('/chat', methods=['POST'])
def chat_with_finetuned():
    """
    Chat using a fine-tuned model.

    Request body:
    {
        "model_id": "ft:gpt-3.5-turbo:...",
        "message": "Tell me a joke about traffic"
    }
    """
    data = request.get_json()

    if not data or 'model_id' not in data or 'message' not in data:
        return jsonify({'error': 'model_id and message are required'}), 400

    model_id = data['model_id']
    user_message = data['message']
    session_id = data.get('session_id') or str(uuid.uuid4())
    comedian = data.get('comedian', 'vadivelu').lower()  # Default to Vadivelu

    try:
        start_time = time.time()

        service = FineTuneService()

        # System prompts for each comedian (matching training data)
        system_prompts = {
            'vadivelu': "You are Vadivelu, the legendary Tamil comedian. Respond with exaggerated expressions, self-deprecating humor, and signature catchphrases. Use Tanglish (Tamil-English mix).",
            'santhanam': "You are Santhanam, the modern Tamil comedian. Respond with quick wit, contemporary references, and sharp sarcasm. Use Tanglish (Tamil-English mix).",
            'vivek': "You are Vivek, the intellectual Tamil comedian. Respond with social commentary, wordplay, and thoughtful messages. Use Tanglish (Tamil-English mix)."
        }

        system_prompt = system_prompts.get(comedian, system_prompts['vadivelu'])

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = service.use_fine_tuned_model(
            model_id=model_id,
            messages=messages,
            temperature=0.7
        )

        response_time = int((time.time() - start_time) * 1000)

        # Save conversation
        conversation = Conversation(
            session_id=session_id,
            ai_concept='fine_tuned',
            user_input=user_message,
            ai_response=response['response'],
            model_used=model_id,
            thinking_process={
                "process": "Fine-Tuned Model",
                "explanation": (
                    "This response came from a model that was trained on our "
                    "comedian dialogue dataset. The model's weights were updated "
                    "to specialize in Tamil comedy style."
                )
            },
            response_time_ms=response_time
        )

        db.session.add(conversation)
        db.session.commit()

        return jsonify({
            'response': response['response'],
            'session_id': session_id,
            'model': response['model'],
            'usage': response['usage'],
            'response_time_ms': response_time
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/compare', methods=['POST'])
def compare_models():
    """
    Compare base model vs fine-tuned model.

    Request body:
    {
        "fine_tuned_model": "ft:gpt-3.5-turbo:...",
        "prompt": "Tell me about traffic"
    }
    """
    data = request.get_json()

    if not data or 'fine_tuned_model' not in data or 'prompt' not in data:
        return jsonify({'error': 'fine_tuned_model and prompt are required'}), 400

    finetuned_model = data['fine_tuned_model']
    prompt = data['prompt']
    base_model = data.get('base_model', Config.FINE_TUNING_BASE_MODEL)

    try:
        service = FineTuneService()

        comparison = service.compare_base_vs_finetuned(
            base_model=base_model,
            finetuned_model=finetuned_model,
            prompt=prompt
        )

        return jsonify({
            'comparison': comparison,
            'analysis': {
                'base_model_note': 'Generic response from base model without comedian training',
                'fine_tuned_note': 'Specialized response from model trained on comedian dialogues',
                'key_differences': [
                    'Fine-tuned model should use comedian-specific style',
                    'Fine-tuned model may reference movie dialogues naturally',
                    'Fine-tuned model understands Tamil comedy context better'
                ]
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/explain', methods=['GET'])
def explain_fine_tuning():
    """Get educational explanation of fine-tuning."""
    explanation = {
        'concept': 'Fine-Tuning',
        'what_it_is': (
            'Fine-tuning updates the AI model\'s weights using your custom dataset. '
            'Unlike RAG (retrieval) or system prompts (instructions), fine-tuning '
            'actually modifies how the model generates text by training it on your data.'
        ),
        'how_it_works': [
            {
                'step': 1,
                'title': 'Prepare Training Data',
                'description': 'Create JSONL file with input-output examples in chat format',
                'example': '{"messages":[{"role":"system","content":"You are Vadivelu"},{"role":"user","content":"traffic"},{"role":"assistant","content":"Enna koduma sir idhu!"}]}'
            },
            {
                'step': 2,
                'title': 'Upload Dataset',
                'description': 'Send training data to OpenRouter/OpenAI',
                'technical': 'POST /v1/files with purpose="fine-tune"'
            },
            {
                'step': 3,
                'title': 'Train Model',
                'description': 'Model learns patterns from your data (takes 10-60 minutes)',
                'technical': 'Backpropagation updates model weights over multiple epochs'
            },
            {
                'step': 4,
                'title': 'Use Fine-Tuned Model',
                'description': 'Call the custom model ID for specialized responses',
                'technical': 'model="ft:gpt-3.5-turbo:org:model_name:id"'
            }
        ],
        'benefits': [
            'Model learns your specific style/domain deeply',
            'Better than prompting for consistent behavior',
            'Can handle complex patterns in your data',
            'Reduced need for long prompts',
            'Faster inference (no retrieval needed)'
        ],
        'drawbacks': [
            'Expensive (requires training compute + API costs)',
            'Time-consuming (10-60 minutes minimum)',
            'Needs quality training data (50-100+ examples minimum)',
            'Less flexible than RAG for new information',
            'Cannot easily update knowledge (need to retrain)'
        ],
        'vs_alternatives': {
            'vs_rag': 'Fine-tuning changes the model permanently, RAG adds temporary context',
            'vs_system_prompts': 'Fine-tuning is deep learning, prompts are instructions',
            'vs_agents': 'Fine-tuning improves responses, agents improve decision-making'
        },
        'when_to_use': (
            'Use fine-tuning when you need consistent behavior across many interactions '
            'and have sufficient quality training data (100+ examples). For most use cases, '
            'start with RAG and system prompts first - they are faster and more flexible.'
        ),
        'cost_estimate': {
            'training': 'GPT-3.5-turbo: ~$0.008 per 1K tokens (one-time)',
            'usage': 'Fine-tuned models cost same or slightly more than base model',
            'example': '100 dialogues (~10K tokens) = ~$0.08 training cost'
        },
        'requirements': {
            'minimum_examples': 10,
            'recommended_examples': 100,
            'ideal_examples': 200,
            'file_format': 'JSONL with chat completion format',
            'validation': 'Optionally split 10% for validation set'
        }
    }

    return jsonify(explanation)


@bp.route('/dataset-stats', methods=['GET'])
def get_dataset_stats():
    """Get statistics about the fine-tuning dataset."""
    # Use absolute path from project root
    from flask import current_app
    project_root = Path(current_app.root_path).parent
    training_file = project_root / Config.FINE_TUNING_DATA_PATH

    if not training_file.exists():
        return jsonify({
            'exists': False,
            'path': str(training_file),
            'message': 'Dataset not prepared yet',
            'action': 'Run: python scripts/prepare_fine_tuning.py'
        })

    # Count lines in JSONL file
    with open(training_file, 'r') as f:
        line_count = sum(1 for _ in f)

    # Get file size
    file_size = training_file.stat().st_size

    return jsonify({
        'exists': True,
        'path': str(training_file),
        'training_examples': line_count,
        'file_size_bytes': file_size,
        'file_size_kb': round(file_size / 1024, 2),
        'ready_for_training': line_count >= 10,
        'recommendation': get_dataset_recommendation(line_count)
    })


def get_status_explanation(status: str) -> str:
    """Get human-readable explanation of job status."""
    explanations = {
        'validating_files': 'Validating your training data format and content',
        'queued': 'Job is in queue, waiting for training resources',
        'running': 'Model is currently training on your data',
        'succeeded': 'Training completed successfully! You can now use your fine-tuned model',
        'failed': 'Training failed. Check the error message and your training data',
        'cancelled': 'Training was cancelled'
    }

    return explanations.get(status, f'Status: {status}')


def get_dataset_recommendation(example_count: int) -> str:
    """Get recommendation based on dataset size."""
    if example_count < 10:
        return 'Too few examples. Add more dialogues (minimum 10, recommended 50+)'
    elif example_count < 50:
        return 'Minimum met, but more data recommended for better results (target: 100+)'
    elif example_count < 100:
        return 'Good dataset size. Training should produce decent results'
    else:
        return 'Excellent dataset size! Should produce high-quality fine-tuned model'
