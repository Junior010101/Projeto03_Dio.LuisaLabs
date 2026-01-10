from fastapi import status
from httpx import AsyncClient
from pytest_asyncio import fixture
from sqlalchemy import text


@fixture
async def cliente_cadastrado(client: AsyncClient, db_session):
    await db_session.execute(text("DELETE FROM clientes"))
    await db_session.commit()

    payload = {
        "nome": "Carlos",
        "cpf": "99999999999",
        "data_nascimento": "1990-01-01",
        "endereco": "Rua A",
    }

    response = await client.post("/clientes/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    return response.json()


async def test_atualizar_cliente_sucesso_admin(
    client: AsyncClient,
    adm_access_token: str,
    cliente_cadastrado,
):
    cliente_id = cliente_cadastrado["id"]

    payload = {
        "nome": "Carlos Atualizado",
        "endereco": "Rua Nova",
    }

    headers = {"Authorization": f"Bearer {adm_access_token}"}

    response = await client.patch(
        f"/clientes/{cliente_id}",
        json=payload,
        headers=headers,
    )

    content = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert content["id"] == cliente_id
    assert content["nome"] == "Carlos Atualizado"
    assert content["endereco"] == "Rua Nova"
    assert content["cpf"] == cliente_cadastrado["cpf"]


async def test_atualizar_cliente_sem_dados_falha(
    client: AsyncClient,
    adm_access_token: str,
    cliente_cadastrado,
):
    cliente_id = cliente_cadastrado["id"]
    headers = {"Authorization": f"Bearer {adm_access_token}"}

    response = await client.patch(
        f"/clientes/{cliente_id}",
        json={},
        headers=headers,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_atualizar_cliente_nao_encontrado(
    client: AsyncClient,
    adm_access_token: str,
):
    headers = {"Authorization": f"Bearer {adm_access_token}"}

    response = await client.patch(
        "/clientes/9999",
        json={"nome": "Inexistente"},
        headers=headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_atualizar_cliente_usuario_nao_admin(
    client: AsyncClient,
    user_access_token: str,
    cliente_cadastrado,
):
    cliente_id = cliente_cadastrado["id"]
    headers = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.patch(
        f"/clientes/{cliente_id}",
        json={"nome": "Hackeado"},
        headers=headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
