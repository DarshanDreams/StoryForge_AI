from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=2)
def _load_model(
    model_name: str,
) -> SentenceTransformer:

    return SentenceTransformer(
        model_name
    )


class EmbeddingService:

    def __init__(
        self,
        model_name: str,
    ):
        self.model_name = model_name

        self.model = _load_model(
            model_name
        )

    @property
    def dimension(self) -> int:

        return self.model.get_sentence_embedding_dimension()

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return embeddings.tolist()