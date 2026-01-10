from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field


class ClienteIn(BaseModel):
    nome: Annotated[
        str,
        Field(
            description="Nome do cliente",
            examples=["João", "Gustavo", "Marcelo"],
            max_length=69,
            min_length=1,
        ),
    ]
    cpf: Annotated[
        str,
        Field(
            description="CPF do cliente",
            examples=["51086862007", "28291831009", "81637949090"],
            max_length=11,
            min_length=11,
        ),
    ]
    data_nascimento: Annotated[
        date,
        Field(
            description="Data de nascimento do cliente",
            examples=["2000-09-22", "1988-05-13", "1995-12-31"],
        ),
    ]
    endereco: Annotated[
        str,
        Field(
            description="Endereço do cliente",
            examples=[
                "Avenida Duque de Caxias, 23 - Amambaí - Campo Grande/MS",
                "Rua Sara Schuster, C127 - Jardins - Aracaju/SE",
                "Rua José Quirino, 34A - São João - Itajaí/SC",
            ],
            min_length=1,
        ),
    ]


class ClienteUpdate(BaseModel):
    nome: Annotated[
        str | None,
        Field(
            description="Novo nome para o cliente",
            examples=["Gustavo", "João", "Marcelo"],
            max_length=69,
            default=None,
        ),
    ]
    data_nascimento: Annotated[
        date | None,
        Field(
            description="Nova data de nascimento para o cliente",
            examples=["1988-05-13", "2000-09-22", "1995-12-31"],
            default=None,
        ),
    ]
    endereco: Annotated[
        str | None,
        Field(
            description="Novo endereço para o cliente",
            examples=[
                "Rua Sara Schuster, C127 - Jardins - Aracaju/SE",
                "Avenida Duque de Caxias, 23 - Amambaí - Campo Grande/MS",
                "Rua José Quirino, 34A - São João - Itajaí/SC",
            ],
            default=None,
        ),
    ]
