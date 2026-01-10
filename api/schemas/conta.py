from typing import Annotated

from pydantic import BaseModel, Field


class ContaIn(BaseModel):
    agencia: Annotated[
        str,
        Field(
            description="Código da agência bancária",
            examples=["0001", "003A", "B202"],
            min_length=1,
        ),
    ]
    saldo: Annotated[
        float,
        Field(
            description="Saldo inicial da conta",
            examples=[0, 50.5, 33.2],
            default=0,
        ),
    ]
    limite: Annotated[
        float,
        Field(
            description="Limite de conta corrente",
            examples=[500, 600.5, 700.86],
            default=500,
        ),
    ]
    limite_saques: Annotated[
        int,
        Field(
            description="Limite diario de saques na conta",
            examples=[3, 7, 14],
            default=3,
        ),
    ]
    numero_saques: Annotated[
        int,
        Field(
            description="Numero de saques realizados hoje",
            examples=[0, 1, 2],
            default=0,
        ),
    ]


class ContaUpdate(BaseModel):
    limite: Annotated[
        float | None,
        Field(
            description="Atualizar limite de conta corrente",
            examples=[500, 600.5, 700.86],
            default=None,
        ),
    ]
    limite_saques: Annotated[
        int | None,
        Field(
            description="Atualizar limite diario de saques na conta",
            examples=[3, 7, 14],
            default=None,
        ),
    ]
