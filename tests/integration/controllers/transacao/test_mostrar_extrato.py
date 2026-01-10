from fastapi import status
from httpx import AsyncClient
from pytest import fixture


@fixture
async def conta_cadastrada(client: AsyncClient, user_access_token):
    # cria cliente via API
    cliente = {
        "nome": "Ana",
        "cpf": "55555555555",
        "data_nascimento": "1994-04-04",
        "endereco": "Rua Z",
    }

    await client.post("/clientes/", json=cliente)

    # cria conta vinculada
    headers = {"Authorization": f"Bearer {user_access_token}"}
    conta = {"agencia": "0001", "saldo": 500}

    res_conta = await client.post("/contas/", json=conta, headers=headers)
    assert res_conta.status_code == status.HTTP_201_CREATED
    return res_conta.json()


async def test_mostrar_extrato_sucesso(
    client: AsyncClient, user_access_token, conta_cadastrada
):
    conta_id = conta_cadastrada["id"]
    headers = {"Authorization": f"Bearer {user_access_token}"}

    # cria algumas transações
    await client.post(
        "/transacoes/",
        json={"conta_id": conta_id, "acao": "DEPOSITO", "valor": 200},
        headers=headers,
    )
    await client.post(
        "/transacoes/",
        json={"conta_id": conta_id, "acao": "SAQUE", "valor": 100},
        headers=headers,
    )

    # chama endpoint de extrato
    response = await client.get(f"/transacoes/{conta_id}", headers=headers)
    content = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(content, list)
    assert len(content) == 2
    assert content[0]["acao"] == "DEPOSITO"
    assert content[1]["acao"] == "SAQUE"


async def test_mostrar_extrato_conta_inexistente(
    client: AsyncClient, user_access_token
):
    headers = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.get("/transacoes/9999", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_mostrar_extrato_acesso_negado(
    client: AsyncClient, user_access_token, adm_access_token
):
    # cria conta de outro usuário
    outro_cliente = {
        "nome": "Bruno",
        "cpf": "44444444444",
        "data_nascimento": "1990-01-01",
        "endereco": "Rua Y",
    }
    await client.post("/clientes/", json=outro_cliente)

    headers_admin = {"Authorization": f"Bearer {adm_access_token}"}
    res_conta = await client.post(  # noqa
        "/contas/",
        json={"agencia": "0001", "saldo": 300},
        headers=headers_admin,
    )

    # tenta acessar extrato com user_access_token do outro usuário
    headers_user = {"Authorization": f"Bearer {user_access_token}"}
    response = await client.get(
        "/transacoes/2",
        headers=headers_user,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
