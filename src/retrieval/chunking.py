from __future__ import annotations

import re
import uuid
from dataclasses import dataclass

from src.documents.models import (
    Document,
    DocumentChunk,
)


@dataclass
class TextChunk:
    """Legacy text-only chunk returned by ``chunk_text``."""

    text: str
    index: int


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[TextChunk]:
    """Split raw text while preserving the original helper API."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size.")

    normalized = text.strip()
    if not normalized:
        return []

    step = chunk_size - overlap
    chunks = []
    for index, start in enumerate(range(0, len(normalized), step)):
        piece = normalized[start:start + chunk_size].strip()
        if piece:
            chunks.append(TextChunk(text=piece, index=index))
        if start + chunk_size >= len(normalized):
            break
    return chunks


class TextChunker:
    """
    Splits a document into overlapping chunks.

    The chunker keeps document metadata attached
    to every chunk so retrieval can later provide
    source attribution.
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ):

        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than 0."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller "
                "than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        document: Document,
    ) -> list[DocumentChunk]:
        """
        Convert a normalized Document into
        overlapping DocumentChunks.
        """

        if document.is_empty():
            return []

        text = self._normalize_text(
            document.content
        )

        paragraphs = self._split_paragraphs(
            text
        )

        chunks = []

        current_text = ""

        chunk_index = 0

        for paragraph in paragraphs:

            if not paragraph:
                continue

            candidate = (
                f"{current_text}\n\n{paragraph}"
                if current_text
                else paragraph
            )

            if (
                len(candidate)
                <= self.chunk_size
            ):

                current_text = candidate

                continue

            if current_text:

                chunk = self._create_chunk(
                    document=document,
                    text=current_text,
                    chunk_index=chunk_index,
                )

                chunks.append(
                    chunk
                )

                chunk_index += 1

            overlap = self._get_overlap(
                current_text
            )

            current_text = (
                f"{overlap}\n\n{paragraph}"
                if overlap
                else paragraph
            )

            # Extremely long paragraphs need
            # character-level splitting.
            if (
                len(current_text)
                > self.chunk_size
            ):

                oversized_chunks = (
                    self._split_long_text(
                        current_text
                    )
                )

                for piece in oversized_chunks[:-1]:

                    chunk = (
                        self._create_chunk(
                            document=document,
                            text=piece,
                            chunk_index=chunk_index,
                        )
                    )

                    chunks.append(
                        chunk
                    )

                    chunk_index += 1

                current_text = (
                    oversized_chunks[-1]
                )

        if current_text.strip():

            chunk = self._create_chunk(
                document=document,
                text=current_text,
                chunk_index=chunk_index,
            )

            chunks.append(
                chunk
            )

        return chunks

    def _create_chunk(
        self,
        document: Document,
        text: str,
        chunk_index: int,
    ) -> DocumentChunk:

        return DocumentChunk(
            chunk_id=str(
                uuid.uuid4()
            ),
            document_id=(
                document.document_id
            ),
            text=text.strip(),
            chunk_index=chunk_index,
            metadata={
                **document.metadata,
                "document_id": (
                    document.document_id
                ),
                "chunk_index": chunk_index,
                "source": document.filename,
            },
        )

    def _split_paragraphs(
        self,
        text: str,
    ) -> list[str]:

        return [
            paragraph.strip()
            for paragraph in re.split(
                r"\n\s*\n",
                text,
            )
            if paragraph.strip()
        ]

    def _split_long_text(
        self,
        text: str,
    ) -> list[str]:

        pieces = []

        start = 0

        step = (
            self.chunk_size
            - self.chunk_overlap
        )

        while start < len(text):

            end = min(
                start + self.chunk_size,
                len(text),
            )

            piece = text[
                start:end
            ].strip()

            if piece:
                pieces.append(
                    piece
                )

            if end >= len(text):
                break

            start += step

        return pieces

    def _get_overlap(
        self,
        text: str,
    ) -> str:

        if not text:
            return ""

        overlap_start = max(
            0,
            len(text)
            - self.chunk_overlap,
        )

        return text[
            overlap_start:
        ].strip()

    def _normalize_text(
        self,
        text: str,
    ) -> str:

        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()