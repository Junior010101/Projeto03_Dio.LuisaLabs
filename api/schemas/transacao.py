from typing import Annotated, Literal

from pydantic import BaseModel, Field


class TransacaoIn(BaseModel):
    conta_id: Annotated[
        int,
        Field(
            description="ID da conta associada à transação",
            examples=[1, 42, 1337],
        ),
    ]

    acao: Annotated[
        Literal["DEPOSITO", "SAQUE"],
        Field(
            description="Tipo de ação da transação (ex: DEPOSITO, SAQUE)",
            examples=["DEPOSITO", "SAQUE"],
            min_length=1,
        ),
    ]

    valor: Annotated[
        float,
        Field(
            description="Valor monetário da transação",
            examples=[50.0, 100.75, 20],
            gt=0,
        ),
    ]
