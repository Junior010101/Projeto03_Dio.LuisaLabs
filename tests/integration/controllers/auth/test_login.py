from fastapi import status
from httpx import AsyncClient


async def test_login_success(client: AsyncClient):
    data = {"id_usuario": 1}

    response = await client.post("/auth/login", json=data)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["token_acesso"] is not None
