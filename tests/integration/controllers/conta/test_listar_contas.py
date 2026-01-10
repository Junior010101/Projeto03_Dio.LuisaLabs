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


async def test_listar_contas_usuario_comum_sucesso(
    client,
    user_access_token,
    contas_no_banco,
):
    headers = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.get("/contas/", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert all("agencia" in conta for conta in data)
    assert all("saldo" in conta for conta in data)


async def test_listar_contas_admin_sucesso(
    client,
    adm_access_token,
):
    headers = {"Authorization": f"Bearer {adm_access_token}"}

    response = await client.get("/contas/", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


async def test_listar_contas_usuario_sem_cliente_falha(
    client,
    user_access_token,
    db_session,
):
    await db_session.execute(text("DELETE FROM contas"))
    await db_session.execute(text("DELETE FROM clientes"))
    await db_session.commit()

    headers = {"Authorization": f"Bearer {user_access_token}"}

    response = await client.get("/contas/", headers=headers)

    assert response.status_code == 404
