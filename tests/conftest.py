import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

from app.api.deps import get_db
from app.main import app
from app.db.session import Base

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/url_shortener_test"

engine = create_async_engine(
    TEST_DATABASE_URL,
    # connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


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
    # Override the get_db dependency to use our test session
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

