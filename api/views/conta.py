from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class ContaOut(BaseModel):
    id: Annotated[
        int,
        Field(
            description="Identificador unico da conta no banco de dados",
            examples=[1, 2, 3],
        ),
    ]
    numero: Annotated[
        str | None,
        Field(
            description="Numero da conta bancaria",
            examples=["0001-a9f31-42", "003A-b8g21-45", "B202-c5h11-46"],
            default=None,
        ),
    ]
    agencia: Annotated[
        str | None,
        Field(
            description="Código da agência bancária",
            examples=["0001", "003A", "B202"],
            default=None,
        ),
    ]
    saldo: Annotated[
        float | None,
        Field(
            description="Saldo da conta bancária",
            examples=[0, 50.5, 33.2],
            default=None,
        ),
    ]
    limite: Annotated[
        float | None,
        Field(
            description="Limite de conta corrente",
            examples=[500, 600.5, 700.86],
            default=None,
        ),
    ]
    limite_saques: Annotated[
        int | None,
        Field(
            description="Limite diario de saques na conta",
            examples=[3, 7, 14],
            default=None,
        ),
    ]
    numero_saques: Annotated[
        int | None,
        Field(
            description="Numero de saques realizados hoje",
            examples=[0, 1, 2],
            default=None,
        ),
    ]
    criada_em: Annotated[
        datetime | None,
        Field(
            description="Data de criação definida pelo sistema",
            default=None,
        ),
    ]


class ContaError(BaseModel):
    code: Annotated[
        Literal["CONTA_NAO_ENCONTRADA", "ACESSO_NEGADO", "CONTA_COM_SALDO"],
        Field(
            description="Tipo de erro",
            examples=["CONTA_NAO_ENCONTRADA", "ACESSO_NEGADO"],
        ),
    ]
    message: Annotated[
        str,
        Field(
            description="Mensagem de erro",
            examples=[
                "Não existe conta cadastrada para o ID informado",
                "O campo agência não deve ficar vazio.",
                "O cliente cujo id é 0,"
                " não tem permissão de acesso sobre essa conta.",
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
