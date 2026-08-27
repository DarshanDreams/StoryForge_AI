from src.retrieval.retriever import (
    InMemoryRetriever,
)


def create_retriever():
    """
    Create the application's retriever.

    Keeping construction behind a factory makes
    it possible to replace the in-memory retriever
    with Qdrant later without changing the services.
    """

    return InMemoryRetriever()