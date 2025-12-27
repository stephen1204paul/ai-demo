"""Embedding generation service for vector search."""

from typing import List, Optional
from app.services.openrouter_client import OpenRouterClient
from app.config import Config


class EmbeddingService:
    """
    Service for generating text embeddings.

    Uses OpenRouter API to generate embeddings for semantic search
    and RAG (Retrieval Augmented Generation).
    """

    def __init__(self):
        """Initialize embedding service."""
        self.client = OpenRouterClient()
        self.model = Config.EMBEDDING_MODEL
        self.dimension = Config.EMBEDDING_DIMENSION

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text.

        Args:
            text: Text to generate embedding for

        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Clean text
        text = text.strip()

        # Generate embedding
        embedding = self.client.create_embedding(text, model=self.model)

        # Verify dimension
        if len(embedding) != self.dimension:
            raise ValueError(
                f"Expected embedding dimension {self.dimension}, "
                f"got {len(embedding)}"
            )

        return embedding

    def batch_generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of texts to generate embeddings for
            batch_size: Number of texts to process in each batch

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Clean texts
        texts = [t.strip() for t in texts if t and t.strip()]

        if not texts:
            raise ValueError("No valid texts provided")

        # Process in batches
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                batch_embeddings = self.client.batch_create_embeddings(
                    batch,
                    model=self.model
                )
                all_embeddings.extend(batch_embeddings)

            except Exception as e:
                raise Exception(
                    f"Error generating embeddings for batch {i//batch_size + 1}: {str(e)}"
                )

        return all_embeddings

    def prepare_text_for_embedding(
        self,
        dialogue_tamil: Optional[str],
        dialogue_english: Optional[str],
        context: Optional[str],
        emotion: Optional[str]
    ) -> str:
        """
        Prepare dialogue text for embedding generation.

        Combines multiple fields into a single text optimized for
        semantic search.

        Args:
            dialogue_tamil: Tamil dialogue text
            dialogue_english: English translation
            context: Scene context
            emotion: Emotional classification

        Returns:
            Combined text ready for embedding
        """
        parts = []

        if dialogue_english:
            parts.append(dialogue_english)

        if dialogue_tamil:
            parts.append(dialogue_tamil)

        if context:
            parts.append(f"Context: {context}")

        if emotion:
            parts.append(f"Emotion: {emotion}")

        if not parts:
            raise ValueError("At least one dialogue field must be provided")

        return " | ".join(parts)
