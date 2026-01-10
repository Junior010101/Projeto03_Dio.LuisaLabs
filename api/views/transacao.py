from datetime import datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field


class TransacaoOut(BaseModel):
    id: Annotated[
        int,
        Field(
            description="Identificador unico da transação",
            examples=[1, 10, 256],
        ),
    ]

    conta_id: Annotated[
        int,
        Field(
            description="Identificador da conta associada à transação",
            examples=[3, 7, 42],
        ),
    ]

    acao: Annotated[
        str,
        Field(
            description="Tipo de ação executada na transação",
            examples=["DEPOSITO", "SAQUE"],
        ),
    ]

    status: Annotated[
        bool,
        Field(
            description="Status final da transação",
            examples=[True, False],
        ),
    ]

    valor: Annotated[
        float,
        Field(
            description="Valor monetário da transação",
            examples=[50.0, 120.75],
        ),
    ]

    efetuada_em: Annotated[
        Optional[datetime],
        Field(
            description="Data e hora em que a transação foi efetuada",
            examples=["2026-01-08T15:32:10Z"],
        ),
    ]


class TransacaoError(BaseModel):
    code: Annotated[
        Literal["SALDO_INSUFICIENTE", "TIPO_INVALIDO"],
        Field(
            description="Tipo de erro",
            examples=["SALDO_INSUFICIENTE", "TIPO_INVALIDO"],
        ),
    ]
    message: Annotated[
        str,
        Field(
            description="Mensagem de erro",
            examples=[
                "Tipo de transação inválido",
                "Saldo insuficiente",
            ],
        ),
    ]
    field: Annotated[
        str | None,
        Field(
            default=None,
            description="Campo que gerou o erro",
        ),
    ]
    Parameter: Annotated[
        str | None,
        Field(
            default=None,
            description="Parametro que gerou o erro",
        ),
    ]
    origin: Annotated[
        str,
        Field(
            description="Origem da resposta de erro",
            examples=[
                "domain",
                "validation",
            ],
        ),
    ]
