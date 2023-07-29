import asyncio
from typing import AsyncGenerator
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session, engine, async_session_maker
from src.main import app
from src.restaurant.models import metadata
from httpx import AsyncClient

# DATABASE
metadata.bind = engine


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session


# SETUP
@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# Тестовая БД
# @pytest.fixture(autouse=True, scope='session')
# async def prepare_database():
#     async with engine.begin() as conn:
#         await conn.run_sync(metadata.create_all)
#     yield
#     async with engine.begin() as conn:
#         await conn.run_sync(metadata.drop_all)

# синхронный тест
# client = TestClient(app)









