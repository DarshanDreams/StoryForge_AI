from __future__ import annotations

from dataclasses import dataclass, field

from src.retrieval.retriever import RetrievalResult


@dataclass
class AgentState:
    """
    State passed through the StoryForge agent pipeline.
    """

    query: str

    retrieved_context: list[
        RetrievalResult
    ] = field(
        default_factory=list
    )

    context_text: str = ""

    answer: str = ""

    sources: list[dict] = field(
        default_factory=list
    )

    confidence: float = 0.0

    blocked: bool = False

    error: str | None = None

    metadata: dict = field(
        default_factory=dict
    )