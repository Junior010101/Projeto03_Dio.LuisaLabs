from fastapi import status
from httpx import AsyncClient


async def test_cadastrar_cliente_sucesso(client: AsyncClient):
    data = {
        "nome": "Marcelo",
        "cpf": "81637949090",
        "data_nascimento": "1995-12-31",
        "endereco": "Rua José Quirino, 34A - São João - Itajaí/SC",
    }

    response = await client.post("/clientes/", json=data)
    content = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert content["id"] is not None


async def test_cadastrar_cliente_invalid_payload_fall(client: AsyncClient):
    data = {
        "cpf": "81637949090",
        "data_nascimento": "1995-12-31",
        "endereco": "Rua José Quirino, 34A - São João - Itajaí/SC",
    }

    response = await client.post("/clientes/", json=data)
    content = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert content["detail"][0]["loc"] == ["body", "nome"]


async def test_cadastrar_cliente_cpf_duplicado(
    client: AsyncClient,
    adm_access_token,
):
    headers_adm = {"Authorization": f"Bearer {adm_access_token}"}

    data = {
        "nome": "Marcelo",
        "cpf": "81637949090",
        "data_nascimento": "1995-12-31",
        "endereco": "Rua X",
    }

    await client.post("/clientes/", json=data)
    response = await client.post("/clientes/", json=data)
    await client.delete("/clientes/1", headers=headers_adm)

    assert response.status_code == status.HTTP_409_CONFLICT
