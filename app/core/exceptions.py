from typing import Any, Dict

from starlette import status


class AppBaseException(Exception):
    """
    Base class for all application errors.
    Each subclass defines its own status code and default message.
    """
    status_code: int = 500
    default_message: str = "An internal server error occurred!"
    log_level: str = "error"

    def __init__(self, message: str = None, payload: Dict[str, Any] = None):
        """
        :param message: Override the default message if needed
        :param payload: Extra data to log (e.g., {"user_id": 123})
        """
        self.message = message or self.default_message
        self.payload = payload or {}
        super().__init__(self.message)


class URLNotFoundException(AppBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "The requested URL not found."
    log_level = "warning"


class InvalidShortCodeException(AppBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "The provided short code format is invalid."
    log_level = "info"

