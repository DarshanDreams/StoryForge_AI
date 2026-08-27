import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """
    Structured JSON logger.

    Works well with production log platforms such as
    CloudWatch, Datadog, Grafana Loki, ELK, etc.
    """

    def format(self, record: logging.LogRecord) -> str:

        payload = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "event"):
            payload["event"] = record.event

        if hasattr(record, "request_id"):
            payload["request_id"] = record.request_id

        if hasattr(record, "latency_ms"):
            payload["latency_ms"] = record.latency_ms

        if hasattr(record, "metadata"):
            payload["metadata"] = record.metadata

        if record.exc_info:
            payload["exception"] = (
                self.formatException(record.exc_info)
            )

        return json.dumps(
            payload,
            ensure_ascii=False,
        )


def configure_logging(
    level: str = "INFO",
):
    """
    Configure application-wide structured logging.
    """

    root_logger = logging.getLogger()

    if root_logger.handlers:
        return root_logger

    handler = logging.StreamHandler(
        sys.stdout
    )

    handler.setFormatter(
        JsonFormatter()
    )

    root_logger.setLevel(
        getattr(
            logging,
            level.upper(),
            logging.INFO,
        )
    )

    root_logger.addHandler(
        handler
    )

    return root_logger


def get_logger(name: str):
    """
    Return a configured logger.
    """

    configure_logging()

    return logging.getLogger(name)