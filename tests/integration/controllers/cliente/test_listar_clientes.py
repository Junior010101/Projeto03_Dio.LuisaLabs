from fastapi import status
from httpx import AsyncClient
from pytest_asyncio import fixture
from sqlalchemy import text


@fixture(autouse=True)
async def populate_clientes(
    client: AsyncClient,
    db_session,
):
    await db_session.execute(text("DELETE FROM clientes"))
    await db_session.commit()

    clientes = [
        {
            "nome": "Carlos",
            "cpf": "11111111111",
            "data_nascimento": "1990-01-01",
            "endereco": "Rua A",
        },
        {
            "nome": "Ana",
            "cpf": "22222222222",
            "data_nascimento": "1992-02-02",
            "endereco": "Rua B",
        },
        {
            "nome": "Bruno",
            "cpf": "33333333333",
            "data_nascimento": "1991-03-03",
            "endereco": "Rua C",
        },
    ]

    for cliente in clientes:
        await client.post("/clientes/", json=cliente)


async def test_listar_clientes_sucesso_admin(
    client: AsyncClient,
    adm_access_token: str,
):
    headers = {"Authorization": f"Bearer {adm_access_token}"}

    response = await client.get("/clientes/", headers=headers)
    content = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(content, list)
    assert len(content) == 3

    nomes = [c["nome"] for c in content]
    assert nomes == sorted(nomes)


async def test_listar_clientes_usuario_nao_admin(
    client: AsyncClient,
    user_access_token: str,
):
    headers = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.get("/clientes/", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_listar_clientes_sem_registros(
    client: AsyncClient,
    adm_access_token: str,
    db_session,
):
    await db_session.execute(text("DELETE FROM clientes"))
    await db_session.commit()

    headers = {"Authorization": f"Bearer {adm_access_token}"}

    response = await client.get("/clientes/", headers=headers)
    content = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert content == []
