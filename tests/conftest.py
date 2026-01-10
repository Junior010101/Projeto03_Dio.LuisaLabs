from os import environ
from tempfile import NamedTemporaryFile

from httpx import ASGITransport, AsyncClient
from pytest_asyncio import fixture
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from alembic import command
from alembic.config import Config


@fixture(scope="session", autouse=True)
def test_database_url():
    with NamedTemporaryFile(suffix=".sqlite") as tmp:
        environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{tmp.name}"
        environ["ENVIRONMENT"] = "test"
        environ["ADM_PASSWORD"] = "123456"
        yield


@fixture(scope="session", autouse=True)
def apply_migrations(test_database_url):
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        environ["DATABASE_URL"],
    )

    command.upgrade(alembic_cfg, "head")
    yield
    command.downgrade(alembic_cfg, "base")


@fixture
async def db_session():
    from api.db import engine

    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@fixture
async def client(db_session):
    from api.main import api

    transport = ASGITransport(app=api)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    async with AsyncClient(
        base_url="http://test", transport=transport, headers=headers
    ) as client:
        yield client


@fixture
async def user_access_token(client: AsyncClient):
    response = await client.post("/auth/login", json={"id_usuario": 1})
    return response.json()["token_acesso"]


@fixture
async def adm_access_token(client: AsyncClient):
    from api.config import settings

    response = await client.post(
        "/auth/login", json={"id_usuario": settings.adm_password}
    )
    return response.json()["token_acesso"]


@fixture(scope="session", autouse=True)
async def close_engine():
    yield
    from api.db import engine

    await engine.dispose()
