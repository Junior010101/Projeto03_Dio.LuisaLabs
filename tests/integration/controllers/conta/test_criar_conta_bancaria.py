from httpx import AsyncClient
from pytest import fixture


@fixture
async def cliente_no_banco(client: AsyncClient):
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
        )
        assert resp.status_code == 201, resp.text


async def test_criar_conta_bancaria_sucesso(
    client: AsyncClient, user_access_token, cliente_no_banco
):
    headers_user = {"Authorization": f"Bearer {user_access_token}"}

    payload = {"agencia": "0001"}

    response = await client.post(
        "/contas/",
        json=payload,
        headers=headers_user,
    )

    data = response.json()

    assert response.status_code == 201

    assert data["agencia"] == "0001"
    assert data["saldo"] == 0
    assert data["numero"].startswith("0001-")


async def test_criar_conta_cliente_inexistente(client: AsyncClient):
    payload = {"agencia": "0001"}

    response = await client.post("/contas/", json=payload)

    assert response.status_code == 401
