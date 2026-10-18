from dataclasses import dataclass, field
from typing import Any



@dataclass
class LLMMessage:
    """A single message sent to an LLM."""

    role: str
    content: str


@dataclass
class LLMRequest:
    """Provider-independent LLM request."""

    messages: list[LLMMessage]

    model: str | None = None

    temperature: float = 0.7

    max_tokens: int | None = None

    response_format: type | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2.")
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("max_tokens must be greater than zero.")


@dataclass
class LLMUsage:
    """Token usage returned by the provider."""

    input_tokens: int = 0

    output_tokens: int = 0

    total_tokens: int = 0


@dataclass
class LLMResponse:
    """Normalized response returned by the LLM Gateway."""

    content: str

    model: str

    provider: str

    parsed_output: Any = None

    usage: LLMUsage = field(default_factory=LLMUsage)

    latency_ms: float = 0.0

    estimated_cost: float = 0.0

    metadata: dict[str, Any] = field(default_factory=dict)