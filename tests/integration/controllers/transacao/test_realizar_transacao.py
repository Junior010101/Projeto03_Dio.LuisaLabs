from fastapi import status
from httpx import AsyncClient
from pytest import fixture


@fixture
async def conta_cadastrada(client: AsyncClient, user_access_token):
    # cria cliente via API
    cliente = {
        "nome": "Lucas",
        "cpf": "99999999999",
        "data_nascimento": "1993-03-03",
        "endereco": "Rua X",
    }

    await client.post("/clientes/", json=cliente)

    # cria conta com saldo inicial
    headers = {"Authorization": f"Bearer {user_access_token}"}
    conta = {"agencia": "0001", "saldo": 500}

    res_conta = await client.post("/contas/", json=conta, headers=headers)
    assert res_conta.status_code == status.HTTP_201_CREATED
    return res_conta.json()


async def test_deposito_sucesso(
    client: AsyncClient, user_access_token, conta_cadastrada
):
    conta_id = conta_cadastrada["id"]
    headers = {"Authorization": f"Bearer {user_access_token}"}

    payload = {"conta_id": conta_id, "acao": "DEPOSITO", "valor": 200}

    response = await client.post("/transacoes/", json=payload, headers=headers)
    content = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert content["conta_id"] == conta_id
    assert content["acao"] == "DEPOSITO"
    assert content["valor"] == 200
    assert content["status"] is True


async def test_saque_sucesso(
    client: AsyncClient,
    user_access_token,
    conta_cadastrada,
):
    conta_id = conta_cadastrada["id"]
    headers = {"Authorization": f"Bearer {user_access_token}"}

    payload = {"conta_id": conta_id, "acao": "SAQUE", "valor": 100}

    response = await client.post("/transacoes/", json=payload, headers=headers)
    content = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert content["conta_id"] == conta_id
    assert content["acao"] == "SAQUE"
    assert content["valor"] == 100
    assert content["status"] is True


async def test_saque_saldo_insuficiente(
    client: AsyncClient, user_access_token, conta_cadastrada
):
    conta_id = conta_cadastrada["id"]
    headers = {"Authorization": f"Bearer {user_access_token}"}

    payload = {"conta_id": conta_id, "acao": "SAQUE", "valor": 9999}

    response = await client.post("/transacoes/", json=payload, headers=headers)
    assert (
        response.status_code == status.HTTP_400_BAD_REQUEST
    )  # TransacaoSaldoInsuficiente
    content = response.json()
    assert "SALDO_INSUFICIENTE" in content["code"]


async def test_conta_inexistente(client: AsyncClient, user_access_token):
    headers = {"Authorization": f"Bearer {user_access_token}"}

    payload = {"conta_id": 9999, "acao": "DEPOSITO", "valor": 100}

    response = await client.post("/transacoes/", json=payload, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
