from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    """
    Normalized document representation used by
    the rest of StoryForge.
    """

    document_id: str

    filename: str

    content: str

    content_type: str

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def is_empty(self) -> bool:
        return not bool(
            self.content.strip()
        )


@dataclass
class DocumentChunk:
    """
    A chunk created from a normalized document.
    """

    chunk_id: str

    document_id: str

    text: str

    chunk_index: int

    metadata: dict[str, Any] = field(
        default_factory=dict
    )