from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from asgi_correlation_id import CorrelationIdMiddleware

from app.api.endpoints.url import url_manager_router
from app.api.endpoints.url_statistics import stats_router
from app.core.config import settings
from app.core.errors import app_exception_handler
from app.core.exceptions import AppBaseException
from app.core.logging import configure_logger, logger
from app.db.session import async_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logger()
    logger.info("startup.initiated", env=settings.ENVIRONMENT)
    yield
    await async_engine.dispose()
    logger.info("shutdown.complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handler
app.add_exception_handler(AppBaseException, app_exception_handler)

# To add unique UUID to every request log
app.add_middleware(CorrelationIdMiddleware)

# Endpoints
app.include_router(url_manager_router)
app.include_router(stats_router)


# For k8s
# (I had to use this not standard endpoint because
# of assessment doc it has reserved for /{short_code})
@app.get("/health/system_health", tags=["Health"])  # fixme: enhance url
async def health_check():
    return {"status": "ok", "version": settings.VERSION}

