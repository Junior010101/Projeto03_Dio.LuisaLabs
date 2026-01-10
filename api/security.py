from time import time
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from jwt import decode, encode, exceptions
from pydantic import BaseModel

from api.config import settings

SECRET = "my-secret"
ALGORITHM = "HS256"


class TokenAcesso(BaseModel):
    iss: str
    sub: int
    aud: str
    exp: float
    iat: float
    nbf: float
    jti: str


class JWTToken(BaseModel):
    token_acesso: TokenAcesso


def sign_jwt(id_usuario: int):
    agora = time()

    payload = {
        "iss": "curso-fastapi.com.br",
        "sub": str(id_usuario),
        "aud": "curso-fastapi",
        "exp": agora + (60 * 30),
        "iat": agora,
        "nbf": agora,
        "jti": uuid4().hex,
    }

    token = encode(payload, SECRET, algorithm=ALGORITHM)
    return {"token_acesso": token}


async def decode_jwt(token: str):
    try:
        return decode(
            token,
            SECRET,
            algorithms=[ALGORITHM],
            audience="curso-fastapi",
        )
    except exceptions.ExpiredSignatureError:
        return None
    except exceptions.InvalidTokenError as e:
        print("JWT error:", e)
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, *, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        autorizacao = request.headers.get("Authorization", "")
        scheme, _, credenciais = autorizacao.partition(" ")

        if credenciais:
            if not scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Forma de autenticação invalida.",
                )

            payload = await decode_jwt(credenciais)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalido ou expirado.",
                )

            return payload
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Codigo de autenticação invalido.",
            )


def get_current_user(token: dict = Depends(JWTBearer())):
    return {"id_usuario": token["sub"]}


def login_required(
    current_user: Annotated[dict[str, str], Depends(get_current_user)],
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Acesso Negado"
        )
    return current_user


def is_admin(
    token: dict = Depends(JWTBearer(auto_error=False)),
) -> bool:
    if not token:
        return False

    return str(token.get("sub")) == str(settings.adm_password)


def adm_access_required(
    admin: bool = Depends(is_admin),
):
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não possui privilégios de administrador.",
        )
