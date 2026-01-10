from typing import Annotated

from pydantic import BaseModel, Field

from api.config import settings
from api.security import sign_jwt


class LoginOut(BaseModel):
    token_acesso: Annotated[
        str,
        Field(
            description="Token de acesso",
            examples=[
                sign_jwt(settings.adm_password)["token_acesso"],
            ],
        ),
    ]
