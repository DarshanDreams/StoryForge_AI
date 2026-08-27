from typing import Any, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T", bound=BaseModel)


class LLMMessage(BaseModel):
    """A single message sent to an LLM."""

    role: str
    content: str


class LLMRequest(BaseModel):
    """Provider-independent LLM request."""

    messages: list[LLMMessage]

    model: str | None = None

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
    )

    max_tokens: int | None = Field(
        default=None,
        gt=0,
    )

    response_format: type[BaseModel] | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class LLMUsage(BaseModel):
    """Token usage returned by the provider."""

    input_tokens: int = 0

    output_tokens: int = 0

    total_tokens: int = 0


class LLMResponse(BaseModel):
    """Normalized response returned by the LLM Gateway."""

    content: str

    parsed_output: Any = None

    model: str

    provider: str

    usage: LLMUsage = Field(
        default_factory=LLMUsage,
    )

    latency_ms: float = 0.0

    estimated_cost: float = 0.0

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )