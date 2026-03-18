from json import load

import httpx

with open("api/openapi_config.json", "r", encoding="utf-8") as arquivo:
    data = load(arquivo)

API_URL = data["servers"][0]["url"]


def request_post(endpoint: str, payload: dict, headers: dict = {}):
    """POST genérico para a API."""
    url = f"{API_URL}{endpoint}"
    with httpx.Client() as client:
        try:
            res = client.post(url, json=payload, timeout=10.0, headers=headers)
        except httpx.RequestError as e:
            return None, f"Falha de conexão: {e}"

        if res.status_code in (200, 201, 202):
            return res.json(), None
        return None, f"Erro {res.status_code}: {res.text}"


def request_get(endpoint: str, param: str = "", headers: dict = {}):
    """GET genérico para a API."""
    url = f"{API_URL}{endpoint.lstrip('/')}/{param}"
    with httpx.Client() as client:
        try:
            res = client.get(url, timeout=10.0, headers=headers)
        except httpx.RequestError as e:
            return None, f"Falha de conexão: {e}"

        if res.status_code == 200:
            return res.json(), None
        return None, f"Erro {res.status_code}: {res.text}"
