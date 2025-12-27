"""Vector similarity search service for RAG."""

from typing import List, Dict, Any, Optional
from sqlalchemy import text

from app import db
from app.models.dialogue import Dialogue
from app.services.embedding_service import EmbeddingService
from app.config import Config


class VectorSearchService:
    """
    Service for semantic search using pgvector.

    Implements RAG (Retrieval Augmented Generation) by finding
    dialogues similar to a query and using them as context for LLM.
    """

    def __init__(self):
        """Initialize vector search service."""
        self.embedding_service = EmbeddingService()
        self.top_k = Config.SIMILARITY_TOP_K
        self.threshold = Config.SIMILARITY_THRESHOLD

    def search_similar_dialogues(
        self,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None,
        comedian: Optional[str] = None,
        emotion: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for dialogues similar to the query using vector similarity.

        Args:
            query: User's query text
            top_k: Number of results to return (defaults to Config.SIMILARITY_TOP_K)
            threshold: Minimum similarity score (defaults to Config.SIMILARITY_THRESHOLD)
            comedian: Filter by specific comedian
            emotion: Filter by specific emotion

        Returns:
            List of dictionaries containing dialogue and similarity score
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        # Use defaults if not provided
        if top_k is None:
            top_k = self.top_k
        if threshold is None:
            threshold = self.threshold

        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)

        # Format embedding as PostgreSQL array literal
        embedding_str = '[' + ','.join(str(x) for x in query_embedding) + ']'

        # Build SQL query with pgvector
        # Note: Using f-string for embedding since it's safe (just numbers)
        # and :param for other parameters to avoid SQLAlchemy escaping issues
        sql_query = f"""
        SELECT
            id,
            comedian,
            dialogue_english,
            dialogue_tanglish,
            context,
            emotion,
            1 - (embedding <=> '{embedding_str}'::vector) as similarity
        FROM dialogues
        WHERE
            embedding IS NOT NULL
            AND 1 - (embedding <=> '{embedding_str}'::vector) > :threshold
        """

        # Add optional filters
        params = {
            'threshold': threshold,
            'top_k': top_k
        }

        if comedian:
            sql_query += " AND comedian = :comedian"
            params['comedian'] = comedian

        if emotion:
            sql_query += " AND emotion = :emotion"
            params['emotion'] = emotion

        # Order by similarity and limit
        sql_query += f"""
        ORDER BY embedding <=> '{embedding_str}'::vector
        LIMIT :top_k
        """

        # Execute query
        result = db.session.execute(text(sql_query), params)

        # Format results
        dialogues = []
        for row in result:
            dialogues.append({
                'id': row.id,
                'comedian': row.comedian,
                'dialogue_english': row.dialogue_english,
                'dialogue_tanglish': row.dialogue_tanglish,
                'context': row.context,
                'emotion': row.emotion,
                'similarity': float(row.similarity)
            })

        return dialogues

    def build_rag_context(
        self,
        retrieved_dialogues: List[Dict[str, Any]],
        include_metadata: bool = True
    ) -> str:
        """
        Build context from retrieved dialogues for RAG.

        Args:
            retrieved_dialogues: List of dialogue dictionaries from search
            include_metadata: Whether to include movie/comedian info

        Returns:
            Formatted context string for LLM prompt
        """
        if not retrieved_dialogues:
            return ""

        context_parts = [
            "Here are some relevant Tamil comedian dialogues for context:\n"
        ]

        for i, dialogue in enumerate(retrieved_dialogues, 1):
            parts = [f"\n{i}. "]

            if include_metadata:
                parts.append(f"{dialogue['comedian']}")

                if dialogue.get('emotion'):
                    parts.append(f" ({dialogue['emotion']})")

                parts.append(": ")

            # Add dialogue text - prioritize Tanglish for authentic Tamil comedy style
            if dialogue.get('dialogue_tanglish'):
                parts.append(f"\"{dialogue['dialogue_tanglish']}\"")
                # Include English as reference but de-emphasize it
                if dialogue.get('dialogue_english'):
                    parts.append(f" (English: {dialogue['dialogue_english']})")
            elif dialogue.get('dialogue_english'):
                parts.append(f"\"{dialogue['dialogue_english']}\"")

            # Add context if available
            if dialogue.get('context'):
                parts.append(f"\n   Context: {dialogue['context']}")

            context_parts.append("".join(parts))

        return "".join(context_parts)

    def get_educational_explanation(
        self,
        query: str,
        retrieved_dialogues: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate educational explanation of the RAG process.

        Args:
            query: User's original query
            retrieved_dialogues: Retrieved dialogues with similarity scores

        Returns:
            Dictionary with step-by-step explanation
        """
        return {
            "process": "RAG (Retrieval Augmented Generation)",
            "steps": [
                {
                    "step": 1,
                    "title": "Query Embedding",
                    "description": f"Converted your query into a {Config.EMBEDDING_DIMENSION}-dimensional vector",
                    "technical": "Used OpenAI's ada-002 embedding model via OpenRouter"
                },
                {
                    "step": 2,
                    "title": "Similarity Search",
                    "description": f"Searched {Dialogue.query.count()} dialogues using cosine similarity",
                    "technical": f"PostgreSQL pgvector extension: ORDER BY embedding <=> query_vector"
                },
                {
                    "step": 3,
                    "title": "Retrieved Context",
                    "description": f"Found {len(retrieved_dialogues)} relevant dialogues above threshold {self.threshold}",
                    "results": [
                        {
                            "dialogue": d['dialogue_tanglish'] or d['dialogue_english'],
                            "comedian": d['comedian'],
                            "emotion": d['emotion'],
                            "similarity": round(d['similarity'], 3)
                        }
                        for d in retrieved_dialogues
                    ]
                },
                {
                    "step": 4,
                    "title": "Context Augmentation",
                    "description": "Added retrieved dialogues to the LLM prompt as context",
                    "technical": "System message + retrieved context + user query"
                }
            ],
            "why_rag": (
                "RAG gives the AI access to specific information it wasn't trained on. "
                "Instead of relying solely on training data, it retrieves relevant context "
                "from our dialogue database to generate more accurate, grounded responses."
            )
        }
