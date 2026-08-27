import uuid
from contextlib import contextmanager
from time import perf_counter

from src.observability.logger import (
    get_logger,
)


logger = get_logger(__name__)


def create_request_id() -> str:
    """
    Create a unique request ID.
    """

    return str(
        uuid.uuid4()
    )


@contextmanager
def trace(
    operation: str,
    request_id: str | None = None,
    metadata: dict | None = None,
):
    """
    Trace a single application operation.

    Logs:
    - operation start
    - operation completion
    - latency
    - errors
    - request ID
    """

    request_id = (
        request_id
        or create_request_id()
    )

    metadata = metadata or {}

    start_time = perf_counter()

    logger.info(
        f"{operation} started",
        extra={
            "event": "operation_started",
            "request_id": request_id,
            "metadata": metadata,
        },
    )

    try:

        yield request_id

        latency_ms = round(
            (
                perf_counter()
                - start_time
            )
            * 1000,
            2,
        )

        logger.info(
            f"{operation} completed",
            extra={
                "event": "operation_completed",
                "request_id": request_id,
                "latency_ms": latency_ms,
                "metadata": metadata,
            },
        )

    except Exception as exc:

        latency_ms = round(
            (
                perf_counter()
                - start_time
            )
            * 1000,
            2,
        )

        logger.exception(
            f"{operation} failed",
            extra={
                "event": "operation_failed",
                "request_id": request_id,
                "latency_ms": latency_ms,
                "metadata": {
                    **metadata,
                    "error": str(exc),
                },
            },
        )

        raise