import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    """Configure structured, consistent logging for the application.

    Uses a single stream handler with a structured text format so logs
    remain easily searchable, per SPEC.md section 30 (Logging).
    """
    log_format = (
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Quiet noisy third-party loggers down to the configured level only.
    logging.getLogger("uvicorn.access").setLevel(settings.LOG_LEVEL)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
