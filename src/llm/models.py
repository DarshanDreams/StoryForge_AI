from typing import Any

from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    role: str
    content: str


class LLMRequest(BaseModel):
    messages: list[LLMMessage]

    model: str | None = None

    temperature: float = Field(
        0.2,
        ge=0,
        le=2,
    )

    max_tokens: int | None = Field(
        None,
        gt=0,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class LLMUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class LLMResponse(BaseModel):
    content: str
    model: str
    provider: str

    usage: LLMUsage = Field(
        default_factory=LLMUsage
    )

    latency_ms: float = 0.0
    estimated_cost: float = 0.0
    finish_reason: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )