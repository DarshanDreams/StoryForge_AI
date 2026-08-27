from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)


class VectorStore:

    def __init__(
        self,
        url: str | None,
        api_key: str | None,
        collection_name: str,
        vector_size: int,
    ):

        self.collection_name = (
            collection_name
        )

        if url:

            self.client = QdrantClient(
                url=url,
                api_key=api_key,
            )

        else:

            self.client = QdrantClient(
                ":memory:"
            )

        self._ensure_collection(
            vector_size
        )

    def _ensure_collection(
        self,
        vector_size: int,
    ):

        collections = (
            self.client
            .get_collections()
            .collections
        )

        exists = any(
            collection.name
            == self.collection_name
            for collection in collections
        )

        if not exists:

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def upsert(
        self,
        texts: list[str],
        vectors: list[list[float]],
        metadata: list[dict],
    ):

        if not (
            len(texts)
            == len(vectors)
            == len(metadata)
        ):
            raise ValueError(
                "texts, vectors and metadata "
                "must have the same length."
            )

        points = []

        for text, vector, item_metadata in zip(
            texts,
            vectors,
            metadata,
        ):

            points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=vector,
                    payload={
                        "text": text,
                        **item_metadata,
                    },
                )
            )

        if points:

            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

    def search(
        self,
        vector: list[float],
        limit: int = 5,
    ):

        return self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=limit,
            with_payload=True,
        ).points