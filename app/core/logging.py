import logging
import structlog
import sys


def configure_logger():
    """
    Configures structlog to output JSON for production
    """

    processors = [
        structlog.contextvars.merge_contextvars,  # Bind values (like Request ID)
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Decide Output format based on environment
    if sys.stdout.isatty():
        # Local Dev: human readable
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # Production: JSON for Datadog/ELK
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)


logger = structlog.get_logger()

