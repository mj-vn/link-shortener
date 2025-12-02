from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppBaseException
from app.core.logging import logger


async def app_exception_handler(request: Request, exc: AppBaseException):
    """
    handler for handle AppBaseException subclasses.
    """

    log_method = getattr(logger, exc.log_level, logger.error)

    log_method(
        f"application_error.{exc.__class__.__name__}",
        path=request.url.path,
        message=exc.message,
        payload=exc.payload,
        status_code=exc.status_code
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "detail": exc.message
        }
    )

