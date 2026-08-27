from __future__ import annotations

import math
import re
from dataclasses import dataclass

from src.documents.models import (
    DocumentChunk,
)


@dataclass
class RetrievalResult:
    """
    A retrieved chunk together with its
    relevance score and source metadata.
    """

    chunk: DocumentChunk

    score: float

    source: str

    chunk_index: int

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk.chunk_id,
            "document_id": self.chunk.document_id,
            "text": self.chunk.text,
            "score": self.score,
            "source": self.source,
            "chunk_index": self.chunk_index,
        }


class InMemoryRetriever:
    """
    Lightweight retrieval implementation for
    the Streamlit demo.

    This intentionally keeps the demo easy to run
    without requiring an external vector database.

    The architecture allows this class to later be
    replaced with Qdrant/Pinecone/etc.
    """

    def __init__(self):

        self.chunks: list[
            DocumentChunk
        ] = []

    def add_chunks(
        self,
        chunks: list[DocumentChunk],
    ):

        self.chunks.extend(
            chunks
        )

    def clear(self):

        self.chunks = []

    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> list[RetrievalResult]:
        """
        Retrieve the most relevant chunks.

        Uses a lightweight lexical relevance
        calculation for the demo.
        """

        if not query.strip():
            return []

        if not self.chunks:
            return []

        query_tokens = self._tokenize(
            query
        )

        if not query_tokens:
            return []

        scored = []

        for chunk in self.chunks:

            score = self._score(
                query_tokens,
                chunk.text,
            )

            if score > 0:

                scored.append(
                    (
                        score,
                        chunk,
                    )
                )

        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        results = []

        for score, chunk in scored[:limit]:

            results.append(
                RetrievalResult(
                    chunk=chunk,
                    score=round(
                        score,
                        4,
                    ),
                    source=chunk.metadata.get(
                        "source",
                        "Unknown",
                    ),
                    chunk_index=chunk.chunk_index,
                )
            )

        return results

    def _score(
        self,
        query_tokens: set[str],
        text: str,
    ) -> float:

        text_tokens = self._tokenize(
            text
        )

        if not text_tokens:
            return 0.0

        intersection = (
            query_tokens
            & text_tokens
        )

        if not intersection:
            return 0.0

        # Query coverage
        query_coverage = (
            len(intersection)
            / len(query_tokens)
        )

        # Text relevance
        text_coverage = (
            len(intersection)
            / math.sqrt(
                len(text_tokens)
            )
        )

        # Weighted lexical score.
        score = (
            0.7 * query_coverage
            + 0.3 * text_coverage
        )

        return min(
            score,
            1.0,
        )

    def _tokenize(
        self,
        text: str,
    ) -> set[str]:

        tokens = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower(),
        )

        stop_words = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "to",
            "of",
            "in",
            "on",
            "for",
            "and",
            "or",
            "with",
            "what",
            "why",
            "how",
            "who",
            "does",
            "did",
            "this",
            "that",
            "from",
        }

        return {
            token
            for token in tokens
            if token not in stop_words
            and len(token) > 1
        }