import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


load_dotenv()


class Settings(BaseSettings):
    """
    Central application configuration.

    Secrets are loaded from environment variables.
    Non-secret configuration has sensible defaults.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --------------------------------------------------------
    # Application
    # --------------------------------------------------------

    app_name: str = Field(
        default="StoryForge AI",
        alias="APP_NAME",
    )

    environment: str = Field(
        default="development",
        alias="ENVIRONMENT",
    )

    debug: bool = Field(
        default=True,
        alias="DEBUG",
    )

    # --------------------------------------------------------
    # OpenRouter
    # --------------------------------------------------------

    openrouter_api_key: str = Field(
        default="",
        alias="OPENROUTER_API_KEY",
    )

    llm_model: str = Field(
        default=(
            "nvidia/"
            "nemotron-3-nano-omni-30b-a3b-reasoning:free"
        ),
        alias="LLM_MODEL",
    )

    llm_timeout: float = Field(
        default=60.0,
        alias="LLM_TIMEOUT",
    )

    llm_temperature: float = Field(
        default=0.2,
        alias="LLM_TEMPERATURE",
    )

    # --------------------------------------------------------
    # Qdrant
    # --------------------------------------------------------

    qdrant_url: str = Field(
        default="",
        alias="QDRANT_URL",
    )

    qdrant_api_key: str = Field(
        default="",
        alias="QDRANT_API_KEY",
    )

    qdrant_collection: str = Field(
        default="storyforge",
        alias="QDRANT_COLLECTION",
    )

    # --------------------------------------------------------
    # Embeddings
    # --------------------------------------------------------

    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL",
    )

    embedding_dimension: int = Field(
        default=384,
        alias="EMBEDDING_DIMENSION",
    )

    # --------------------------------------------------------
    # Retrieval
    # --------------------------------------------------------

    retrieval_top_k: int = Field(
        default=5,
        alias="RETRIEVAL_TOP_K",
    )

    chunk_size: int = Field(
        default=800,
        alias="CHUNK_SIZE",
    )

    chunk_overlap: int = Field(
        default=120,
        alias="CHUNK_OVERLAP",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached singleton settings object.
    """

    settings = Settings()

    if not settings.openrouter_api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is not configured. "
            "Add it to your .env file."
        )

    return settings