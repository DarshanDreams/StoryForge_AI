import time
from dataclasses import dataclass, field


@dataclass
class RequestMetrics:
    """
    Runtime metrics for one application operation.
    """

    start_time: float = field(
        default_factory=time.perf_counter
    )

    end_time: float | None = None

    success: bool = False

    error: str | None = None

    input_tokens: int | None = None

    output_tokens: int | None = None

    retrieval_count: int = 0

    llm_calls: int = 0

    tool_calls: int = 0

    @property
    def latency_ms(self) -> float:

        end_time = (
            self.end_time
            if self.end_time is not None
            else time.perf_counter()
        )

        return round(
            (
                end_time
                - self.start_time
            )
            * 1000,
            2,
        )

    def finish(
        self,
        success: bool = True,
        error: str | None = None,
    ):

        self.end_time = (
            time.perf_counter()
        )

        self.success = success

        self.error = error

    def to_dict(self) -> dict:

        return {
            "latency_ms": self.latency_ms,
            "success": self.success,
            "error": self.error,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "retrieval_count": self.retrieval_count,
            "llm_calls": self.llm_calls,
            "tool_calls": self.tool_calls,
        }