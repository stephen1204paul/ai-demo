"""OpenRouter API client for LLM interactions."""

import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
import tiktoken

from app.config import Config


class OpenRouterClient:
    """
    Wrapper for OpenRouter API using OpenAI SDK format.

    OpenRouter provides access to multiple LLMs through a unified API
    that follows the OpenAI format.
    """

    def __init__(self):
        """Initialize OpenRouter client."""
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = Config.OPENROUTER_BASE_URL

        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found. "
                "Please set it in your .env file."
            )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            default_headers={
                "HTTP-Referer": Config.OPENROUTER_SITE_URL,
                "X-Title": Config.OPENROUTER_APP_NAME,
            }
        )

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a chat completion using OpenRouter.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model identifier (e.g., 'openai/gpt-3.5-turbo')
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            tools: List of tool/function definitions for agents
            tool_choice: Tool choice strategy ('auto', 'none', or specific tool)

        Returns:
            Response dictionary containing:
                - response: The AI's response text
                - usage: Token usage statistics
                - model: Model used
                - tool_calls: If agent made tool calls
        """
        try:
            # Prepare API call parameters
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }

            if max_tokens:
                params["max_tokens"] = max_tokens

            if tools:
                params["tools"] = tools
                if tool_choice:
                    params["tool_choice"] = tool_choice

            # Log the request
            print(f"\n{'='*60}")
            print(f"OpenRouter Request:")
            print(f"Model: {model}")
            print(f"Tools: {len(tools) if tools else 0}")
            print(f"Tool Choice: {tool_choice}")
            print(f"{'='*60}\n")

            # Make API call
            response = self.client.chat.completions.create(**params)

            # Extract response
            message = response.choices[0].message

            result = {
                "response": message.content if message.content else "",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
            }

            # Add tool calls if present (for agents)
            if hasattr(message, 'tool_calls') and message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in message.tool_calls
                ]

            return result

        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")

    def create_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """
        Generate embedding vector for text.

        Args:
            text: Text to embed
            model: Embedding model (defaults to Config.EMBEDDING_MODEL)

        Returns:
            List of floats representing the embedding vector
        """
        if not model:
            model = Config.EMBEDDING_MODEL

        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )

            return response.data[0].embedding

        except Exception as e:
            raise Exception(f"Embedding generation error: {str(e)}")

    def batch_create_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.

        Args:
            texts: List of texts to embed
            model: Embedding model (defaults to Config.EMBEDDING_MODEL)

        Returns:
            List of embedding vectors
        """
        if not model:
            model = Config.EMBEDDING_MODEL

        try:
            response = self.client.embeddings.create(
                model=model,
                input=texts
            )

            # Sort by index to ensure correct order
            embeddings = sorted(response.data, key=lambda x: x.index)
            return [e.embedding for e in embeddings]

        except Exception as e:
            raise Exception(f"Batch embedding generation error: {str(e)}")

    @staticmethod
    def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
        """
        Count tokens in text for cost estimation.

        Args:
            text: Text to count tokens for
            model: Model name for tokenizer

        Returns:
            Number of tokens
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception:
            # Fallback: rough estimation (1 token ≈ 4 characters)
            return len(text) // 4

    @staticmethod
    def estimate_cost(
        prompt_tokens: int,
        completion_tokens: int,
        model: str
    ) -> float:
        """
        Estimate cost of API call.

        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            model: Model identifier

        Returns:
            Estimated cost in USD
        """
        # Pricing per 1K tokens (as of 2024)
        pricing = {
            'openai/gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
            'openai/gpt-4-turbo': {'input': 0.01, 'output': 0.03},
            'openai/gpt-4': {'input': 0.03, 'output': 0.06},
            'openai/text-embedding-ada-002': {'input': 0.0001, 'output': 0},
        }

        if model not in pricing:
            return 0.0

        price = pricing[model]
        cost = (
            (prompt_tokens / 1000 * price['input']) +
            (completion_tokens / 1000 * price['output'])
        )

        return round(cost, 6)
