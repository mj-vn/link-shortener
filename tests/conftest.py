import asyncio

import pytest
import pytest_asyncio
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

from app.api.deps import get_db
from app.main import app as fastapi_app
from app.core import decorators
from app.models.base_class import Base

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/url_shortener_test"

engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool
)

TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# Fixture to explicitly define the event loop
@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Fixture to init DB
@pytest_asyncio.fixture
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Fixture to override Dependency Injection
@pytest_asyncio.fixture
async def db_session(init_db):
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db

    original_factory = decorators.AsyncSessionLocal
    decorators.AsyncSessionLocal = TestingSessionLocal

    async with AsyncClient(transport=ASGITransport(app=fastapi_app),
                           base_url="http://test") as ac:
        yield ac

    fastapi_app.dependency_overrides.clear()
    decorators.AsyncSessionLocal = original_factory

