from fastapi import status
from httpx import AsyncClient
from pytest import fixture


@fixture
async def conta_cadastrada(client: AsyncClient, user_access_token):
    cliente = {
        "nome": "Maria",
        "cpf": "66666666666",
        "data_nascimento": "1992-02-02",
        "endereco": "Rua B",
    }

    await client.post("/clientes/", json=cliente)

    # cria conta vinculada
    headers = {"Authorization": f"Bearer {user_access_token}"}
    conta = {"agencia": "0001", "saldo": 100}

    res_conta = await client.post(
        "/contas/",
        json=conta,
        headers=headers,
    )

    assert res_conta.status_code == status.HTTP_201_CREATED
    return res_conta.json()


async def test_atualizar_conta_sucesso_admin(
    client: AsyncClient,
    adm_access_token: str,
    conta_cadastrada,
):
    conta_id = conta_cadastrada["id"]

    payload = {
        "limite": 5000,
        "limite_saques": 10,
    }

    headers = {"Authorization": f"Bearer {adm_access_token}"}

    response = await client.patch(
        f"/contas/{conta_id}",
        json=payload,
        headers=headers,
    )

    content = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert content["id"] == conta_id
    assert content["limite"] == 5000
    assert content["limite_saques"] == 10


async def test_atualizar_conta_sem_dados_falha(
    client: AsyncClient,
    adm_access_token: str,
    conta_cadastrada,
):
    conta_id = conta_cadastrada["id"]

    headers = {"Authorization": f"Bearer {adm_access_token}"}

    response = await client.patch(
        f"/contas/{conta_id}",
        json={},
        headers=headers,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_atualizar_conta_nao_encontrada(
    client: AsyncClient,
    adm_access_token: str,
):
    headers = {"Authorization": f"Bearer {adm_access_token}"}

    response = await client.patch(
        "/contas/9999",
        json={"limite": 1000},
        headers=headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_atualizar_conta_usuario_nao_admin(
    client: AsyncClient,
    user_access_token: str,
    conta_cadastrada,
):
    conta_id = conta_cadastrada["id"]

    headers = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.patch(
        f"/contas/{conta_id}",
        json={"limite": 9999},
        headers=headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
