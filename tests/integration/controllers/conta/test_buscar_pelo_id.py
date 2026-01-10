from fastapi import status
from httpx import AsyncClient
from pytest import fixture
from sqlalchemy import text


@fixture
async def contas_no_banco(
    client: AsyncClient, db_session, adm_access_token, user_access_token
):
    await db_session.execute(text("DELETE FROM clientes"))
    await db_session.commit()

    headers_adm = {"Authorization": f"Bearer {adm_access_token}"}

    clientes = [
        {
            "nome": "Maria",
            "cpf": "89878876818",
            "data_nascimento": "1990-01-01",
            "endereco": "Rua A",
        },
        {
            "nome": "João",
            "cpf": "67868676786",
            "data_nascimento": "1991-01-01",
            "endereco": "Rua B",
        },
    ]

    for cliente in clientes:
        resp = await client.post(
            "/clientes/",
            json=cliente,
            headers=headers_adm,
        )
        assert resp.status_code == 201, resp.text

    headers_user = {"Authorization": f"Bearer {user_access_token}"}

    contas = [
        {
            "agencia": "0001",
            "saldo": 100,
            "limite": 1000,
            "limite_saques": 3,
        },
        {
            "agencia": "0001",
            "saldo": 200,
            "limite": 1000,
            "limite_saques": 3,
        },
    ]

    for conta in contas:
        resp = await client.post("/contas/", json=conta, headers=headers_user)
        assert resp.status_code == 201, resp.text

    yield


async def test_buscar_conta_pelo_id_sucesso(
    client,
    user_access_token,
    contas_no_banco,
):
    headers = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.get("/contas/1", headers=headers)

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body["id"] == 1


async def test_buscar_conta_pelo_id_nao_encontrada(
    client, user_access_token, contas_no_banco
):
    headers = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.get("/contas/999", headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_buscar_conta_pelo_id_acesso_negado(
    client: AsyncClient,
    adm_access_token,
):
    headers = {"Authorization": f"Bearer {adm_access_token}"}

    response = await client.get("/contas/1", headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_buscar_conta_cliente_inexistente(
    client,
    db_session,
    user_access_token,
):
    await db_session.execute(text("DELETE FROM clientes"))
    await db_session.commit()

    headers = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.get("/contas/1", headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_buscar_conta_sem_token(client):
    response = await client.get("/contas/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
