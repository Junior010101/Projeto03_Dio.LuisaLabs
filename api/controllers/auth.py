from fastapi import APIRouter, status

from api.schemas import LoginIn
from api.security import sign_jwt
from api.views import LoginOut

router = APIRouter(prefix="/auth")


@router.post(
    "/login",
    description="Informe a variável ADM_PASSWORD,"
    " definida no arquivo .env, para habilitar operações"
    " com privilégios de superusuário.",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=LoginOut,
)
async def fazer_login(data: LoginIn):
    return sign_jwt(data.id_usuario)
