"""Fine-tuning service for creating custom comedian models."""

import time
from typing import Optional, Dict, Any
from openai import OpenAI

from app import db
from app.models.fine_tuning_job import FineTuningJob
from app.config import Config


class FineTuneService:
    """
    Service for managing fine-tuning jobs using OpenAI's API.

    This service uses OpenAI directly (not OpenRouter) because fine-tuning
    is only supported by OpenAI's native API.
    """

    def __init__(self):
        """Initialize fine-tuning service with OpenAI client."""
        if not Config.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required for fine-tuning. "
                "Please add it to your .env file."
            )

        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_BASE_URL
        )
        self.base_model = Config.FINE_TUNING_BASE_MODEL

    def upload_training_file(self, file_path: str) -> str:
        """
        Upload training file to OpenAI.

        Args:
            file_path: Path to JSONL training file

        Returns:
            File ID from OpenAI
        """
        try:
            with open(file_path, 'rb') as f:
                response = self.client.files.create(
                    file=f,
                    purpose='fine-tune'
                )

            return response.id

        except Exception as e:
            raise Exception(f"Failed to upload training file: {str(e)}")

    def create_fine_tuning_job(
        self,
        training_file_id: str,
        model_name: str,
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> FineTuningJob:
        """
        Create a fine-tuning job.

        Args:
            training_file_id: ID of uploaded training file
            model_name: Name for the fine-tuned model
            hyperparameters: Optional training hyperparameters

        Returns:
            FineTuningJob database record
        """
        try:
            # Default hyperparameters
            if hyperparameters is None:
                hyperparameters = {
                    "n_epochs": 3,  # Number of training epochs
                    "batch_size": 4,
                    "learning_rate_multiplier": 0.1
                }

            # Create fine-tuning job via OpenAI
            response = self.client.fine_tuning.jobs.create(
                training_file=training_file_id,
                model=self.base_model,
                hyperparameters=hyperparameters
            )

            # Create database record
            job = FineTuningJob(
                job_id=response.id,
                model_name=model_name,
                base_model=self.base_model,
                training_file_path=f"file://{training_file_id}",
                hyperparameters=hyperparameters,
                status='pending'
            )

            db.session.add(job)
            db.session.commit()

            return job

        except Exception as e:
            raise Exception(f"Failed to create fine-tuning job: {str(e)}")

    def check_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check status of a fine-tuning job.

        Args:
            job_id: OpenAI job ID

        Returns:
            Job status information
        """
        try:
            # Get status from OpenAI
            response = self.client.fine_tuning.jobs.retrieve(job_id)

            # Update database
            job = FineTuningJob.query.filter_by(job_id=job_id).first()

            if job:
                job.status = response.status

                if response.status == 'succeeded':
                    job.fine_tuned_model = response.fine_tuned_model
                    job.mark_completed(response.fine_tuned_model)
                elif response.status == 'failed':
                    job.mark_failed()

                db.session.commit()

            return {
                'job_id': response.id,
                'status': response.status,
                'model': response.model,
                'fine_tuned_model': getattr(response, 'fine_tuned_model', None),
                'created_at': response.created_at,
                'finished_at': getattr(response, 'finished_at', None),
                'trained_tokens': getattr(response, 'trained_tokens', None),
            }

        except Exception as e:
            raise Exception(f"Failed to check job status: {str(e)}")

    def list_jobs(self, limit: int = 10) -> list:
        """
        List recent fine-tuning jobs.

        Args:
            limit: Number of jobs to return

        Returns:
            List of job information dictionaries
        """
        try:
            response = self.client.fine_tuning.jobs.list(limit=limit)

            return [
                {
                    'job_id': job.id,
                    'status': job.status,
                    'model': job.model,
                    'created_at': job.created_at,
                }
                for job in response.data
            ]

        except Exception as e:
            raise Exception(f"Failed to list jobs: {str(e)}")

    def use_fine_tuned_model(
        self,
        model_id: str,
        messages: list,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Use a fine-tuned model for chat completion.

        Args:
            model_id: Fine-tuned model ID
            messages: Chat messages
            temperature: Sampling temperature

        Returns:
            Response from fine-tuned model
        """
        try:
            response = self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=temperature
            )

            return {
                "response": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            }

        except Exception as e:
            raise Exception(f"Failed to use fine-tuned model: {str(e)}")

    def compare_base_vs_finetuned(
        self,
        base_model: str,
        finetuned_model: str,
        prompt: str
    ) -> Dict[str, Any]:
        """
        Compare responses from base model vs fine-tuned model.

        Args:
            base_model: Base model ID
            finetuned_model: Fine-tuned model ID
            prompt: User prompt

        Returns:
            Comparison of both responses
        """
        messages = [{"role": "user", "content": prompt}]

        # Get base model response
        base_response = self.client.chat.completions.create(
            model=base_model,
            messages=messages,
            temperature=0.7
        )

        # Get fine-tuned model response
        ft_response = self.client.chat.completions.create(
            model=finetuned_model,
            messages=messages,
            temperature=0.7
        )

        return {
            "prompt": prompt,
            "base_model": {
                "model": base_model,
                "response": base_response.choices[0].message.content,
                "tokens": base_response.usage.total_tokens
            },
            "fine_tuned": {
                "model": finetuned_model,
                "response": ft_response.choices[0].message.content,
                "tokens": ft_response.usage.total_tokens
            }
        }
