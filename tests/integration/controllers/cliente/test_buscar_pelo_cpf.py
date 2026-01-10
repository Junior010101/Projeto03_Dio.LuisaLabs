from fastapi import status
from httpx import AsyncClient
from pytest import fixture


@fixture(autouse=True)
async def populate_clientes(client: AsyncClient):
    await client.post(
        "/clientes/",
        json={
            "nome": "Marcelo",
            "cpf": "12345678912",
            "data_nascimento": "1995-12-31",
            "endereco": "Rua X",
        },
    )


async def test_buscar_cliente_pelo_cpf_sucesso(client: AsyncClient):
    cpf = "12345678912"

    response = await client.get(f"/clientes/{cpf}")
    content = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert content["cpf"] == cpf
    assert content["nome"] == "Marcelo"


async def test_buscar_cliente_pelo_cpf_nao_encontrado(client: AsyncClient):
    cpf = "00000000000"

    response = await client.get(f"/clientes/{cpf}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
