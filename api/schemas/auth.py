from typing import Annotated

from pydantic import BaseModel, Field

from api.config import settings


class LoginIn(BaseModel):
    id_usuario: Annotated[
        int | str,
        Field(
            description="Id do usuario ou senha do administrador",
            examples=[settings.adm_password, 1],
        ),
    ]
