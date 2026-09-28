"""
Structured logging configuration for the application.

Configures Python's standard logging module with a consistent format
suitable for both local development (human-readable) and production
(JSON-parsable when needed).

Usage:
    from app.core.logging import configure_logging
    configure_logging()   # call once at application startup

    import logging
    logger = logging.getLogger(__name__)
    logger.info("Something happened", extra={"key": "value"})
"""

from __future__ import annotations

import logging
import sys

from app.core.config import settings

# Log format used in development — structured but human-readable.
_DEV_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging() -> None:
    """
    Apply the application-wide logging configuration.

    - In development (DEBUG=True), the log level is DEBUG and output goes to stdout.
    - In staging/production (DEBUG=False), the log level is INFO.
    - Third-party library loggers are quieted to WARNING to reduce noise.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        level=log_level,
        format=_DEV_FORMAT,
        datefmt=_DATE_FORMAT,
        stream=sys.stdout,
    )

    # Reduce noise from chatty third-party libraries.
    for noisy_logger in ("uvicorn.access", "sqlalchemy.engine", "httpx"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    logging.getLogger(__name__).debug(
        "Logging configured | env=%s | level=%s",
        settings.APP_ENV,
        logging.getLevelName(log_level),
    )
