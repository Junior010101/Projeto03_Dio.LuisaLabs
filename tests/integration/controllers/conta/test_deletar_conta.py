from fastapi import status
from httpx import AsyncClient
from pytest import fixture


@fixture
async def conta_cadastrada(client: AsyncClient, user_access_token):
    # cria cliente via API
    cliente = {
        "nome": "Maria",
        "cpf": "77777777777",
        "data_nascimento": "1992-02-02",
        "endereco": "Rua C",
    }

    await client.post("/clientes/", json=cliente)

    # cria conta vinculada com saldo zero (para permitir deletar)
    headers = {"Authorization": f"Bearer {user_access_token}"}
    conta = {"agencia": "0001", "saldo": 0}

    res_conta = await client.post(
        "/contas/",
        json=conta,
        headers=headers,
    )

    assert res_conta.status_code == status.HTTP_201_CREATED
    return res_conta.json()


async def test_deletar_conta_sucesso_admin(
    client: AsyncClient,
    adm_access_token: str,
    conta_cadastrada,
):
    conta_id = conta_cadastrada["id"]

    headers = {"Authorization": f"Bearer {adm_access_token}"}

    response = await client.delete(
        f"/contas/{conta_id}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_deletar_conta_nao_encontrada(
    client: AsyncClient,
    adm_access_token: str,
):
    headers = {"Authorization": f"Bearer {adm_access_token}"}

    response = await client.delete(
        "/contas/9999",
        headers=headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_deletar_conta_com_saldo_falha(
    client: AsyncClient,
    adm_access_token: str,
    user_access_token,
):
    # cria conta com saldo > 0
    cliente = {
        "nome": "João",
        "cpf": "88888888888",
        "data_nascimento": "1990-01-01",
        "endereco": "Rua D",
    }
    await client.post("/clientes/", json=cliente)

    headers_user = {"Authorization": f"Bearer {user_access_token}"}
    res_conta = await client.post(
        "/contas/",
        json={"agencia": "0001", "saldo": 100},
        headers=headers_user,
    )
    conta_id = res_conta.json()["id"]

    headers_admin = {"Authorization": f"Bearer {adm_access_token}"}
    response = await client.delete(
        f"/contas/{conta_id}",
        headers=headers_admin,
    )

    assert (
        response.status_code == status.HTTP_409_CONFLICT
    )  # ou 422 dependendo do seu raise
