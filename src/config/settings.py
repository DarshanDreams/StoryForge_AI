import os
from dataclasses import dataclass, field
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


def _config_value(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value:
        return value

    try:
        import streamlit as st

        secret_value = st.secrets.get(name)
    except Exception:
        secret_value = None

    if secret_value is None:
        return default
    return str(secret_value)


def _env_bool(name: str, default: bool) -> bool:
    value = _config_value(name)
    if not value:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean value.")


@dataclass
class Settings:
    """
    Central application configuration.

    Secrets are loaded from environment variables.
    Non-secret configuration has sensible defaults.
    """

    # --------------------------------------------------------
    # Application
    # --------------------------------------------------------

    app_name: str = field(
        default_factory=lambda: os.getenv("APP_NAME", "StoryForge AI")
    )

    environment: str = field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development")
    )

    debug: bool = field(default_factory=lambda: _env_bool("DEBUG", True))

    # --------------------------------------------------------
    # OpenRouter
    # --------------------------------------------------------

    openrouter_api_key: str = field(
        default_factory=lambda: _config_value("OPENROUTER_API_KEY")
    )

    openrouter_base_url: str = field(
        default_factory=lambda: _config_value(
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1/chat/completions",
        )
    )

    llm_model: str = field(
        default_factory=lambda: _config_value(
            "LLM_MODEL",
            _config_value(
                "OPENROUTER_MODEL",
                "google/gemma-4-26b-a4b-it:free",
            ),
        )
    )

    openrouter_fallback_models: str = field(
        default_factory=lambda: _config_value(
            "OPENROUTER_FALLBACK_MODELS",
            "liquid/lfm-2.5-2.6b:free,qwen/qwen3.8-27b:free,inclusionai/ling-3.1-flash",
        )
    )

    llm_timeout: float = field(
        default_factory=lambda: float(os.getenv("LLM_TIMEOUT", "60.0"))
    )

    llm_temperature: float = field(
        default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.2"))
    )

    local_llm_enabled: bool = field(
        default_factory=lambda: _env_bool("LOCAL_LLM_ENABLED", False)
    )

    local_llm_base_url: str = field(
        default_factory=lambda: _config_value(
            "LOCAL_LLM_BASE_URL",
            "http://localhost:1234/v1/chat/completions",
        )
    )

    local_llm_model: str = field(
        default_factory=lambda: _config_value(
            "LOCAL_LLM_MODEL",
            "lmstudio-community/Qwen2.5-1.5B-Instruct-GGUF",
        )
    )

    # --------------------------------------------------------
    # Qdrant
    # --------------------------------------------------------

    qdrant_url: str = field(default_factory=lambda: os.getenv("QDRANT_URL", ""))

    qdrant_api_key: str = field(
        default_factory=lambda: os.getenv("QDRANT_API_KEY", "")
    )

    qdrant_collection: str = field(
        default_factory=lambda: os.getenv("QDRANT_COLLECTION", "storyforge")
    )

    # --------------------------------------------------------
    # Embeddings
    # --------------------------------------------------------

    embedding_model: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    )

    embedding_dimension: int = field(
        default_factory=lambda: int(os.getenv("EMBEDDING_DIMENSION", "384"))
    )

    # --------------------------------------------------------
    # Retrieval
    # --------------------------------------------------------

    retrieval_top_k: int = field(
        default_factory=lambda: int(os.getenv("RETRIEVAL_TOP_K", "5"))
    )

    chunk_size: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_SIZE", "800"))
    )

    chunk_overlap: int = field(
        default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "120"))
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
            "For local development, add it to .env; on Streamlit Community "
            "Cloud, add it under App settings > Secrets."
        )

    return settings