import logging
import sys
import os
from typing import Any, Dict

import structlog
from asgi_correlation_id import correlation_id

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

try:
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
except OSError:
    pass


def add_correlation_id(
        logger: Any,
        method_name: str,
        event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Add request_id to the log event."""
    request_id = correlation_id.get()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def configure_logger():
    """
    Configures structlog.
    """

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        add_correlation_id,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    handlers = [logging.StreamHandler(sys.stdout)]

    try:
        file_handler = logging.FileHandler(LOG_FILE)
        handlers.append(file_handler)
    except (PermissionError, OSError) as e:
        print(f"WARNING: Could not write to log file '{LOG_FILE}'. Error: {e}", file=sys.stderr)
        print("Continuing with Console logging only.", file=sys.stderr)

    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
        handlers=handlers,
        force=True
    )


logger = structlog.get_logger()

