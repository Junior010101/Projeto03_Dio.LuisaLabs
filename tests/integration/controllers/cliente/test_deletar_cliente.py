from fastapi import status
from pytest_asyncio import fixture
from sqlalchemy import text


@fixture
async def cliente_sem_conta(client, db_session):
    await db_session.execute(text("DELETE FROM contas"))
    await db_session.execute(text("DELETE FROM clientes"))
    await db_session.commit()

    payload = {
        "nome": "João",
        "cpf": "55555555555",
        "data_nascimento": "1990-01-01",
        "endereco": "Rua A",
    }

    response = await client.post("/clientes/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    return response.json()


@fixture
async def cliente_com_conta(client, user_access_token):
    headers = {"Authorization": f"Bearer {user_access_token}"}

    cliente = {
        "nome": "Maria",
        "cpf": "66666666666",
        "data_nascimento": "1992-02-02",
        "endereco": "Rua B",
    }

    res_cliente = await client.post("/clientes/", json=cliente)
    cliente_id = res_cliente.json()["id"]

    conta = {"agencia": "0001"}

    await client.post(
        "/contas/",
        json=conta,
        headers=headers,
    )

    return cliente_id


async def test_deletar_cliente_sucesso_admin(
    client,
    adm_access_token,
    cliente_sem_conta,
):
    cliente_id = cliente_sem_conta["id"]
    headers = {"Authorization": f"Bearer {adm_access_token}"}

    response = await client.delete(f"/clientes/{cliente_id}", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # garante que foi deletado de verdade
    get_response = await client.get(f"/clientes/{cliente_sem_conta['cpf']}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


async def test_deletar_cliente_nao_encontrado(
    client,
    adm_access_token,
):
    headers = {"Authorization": f"Bearer {adm_access_token}"}

    response = await client.delete("/clientes/9999", headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_deletar_cliente_com_conta_falha(
    client,
    adm_access_token,
    cliente_com_conta,
):
    headers = {"Authorization": f"Bearer {adm_access_token}"}

    response = await client.delete(
        f"/clientes/{cliente_com_conta}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT


async def test_deletar_cliente_usuario_nao_admin(
    client,
    user_access_token,
    cliente_sem_conta,
):
    headers = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.delete(
        f"/clientes/{cliente_sem_conta['id']}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
