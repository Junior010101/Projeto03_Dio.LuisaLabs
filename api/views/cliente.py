from datetime import date, datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field


class ClienteOut(BaseModel):
    id: Annotated[
        int,
        Field(
            description="Identificador unico do cliente no banco de dados",
            examples=[1, 2, 3],
        ),
    ]
    nome: Annotated[
        str,
        Field(
            description="Nome do cliente",
            examples=["João", "Gustavo", "Marcelo"],
            max_length=69,
        ),
    ]
    cpf: Annotated[
        str,
        Field(
            description="CPF do cliente",
            examples=["51086862007", "28291831009", "81637949090"],
            max_length=11,
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
        ),
    ]
    criado_em: Annotated[
        datetime,
        Field(
            description="Data de criação definida pelo sistema",
        ),
    ]


class ClienteError(BaseModel):
    code: Annotated[
        Literal[
            "CLIENTE_NAO_ENCONTRADO",
            "SEM_DADOS_PARA_ATUALIZAR",
            "CLIENTE_POSSUI_CONTAS",
            "CPF_DUPLICADO",
        ],
        Field(
            description="Tipo de erro",
            examples=["CLIENTE_NAO_ENCONTRADO", "CONTEUDO_INVALIDO"],
        ),
    ]
    message: Annotated[
        str,
        Field(
            description="Mensagem de erro",
            examples=[
                "Não existe cliente cadastrado para o CPF informado",
                "Formato da data de nascimento inválido",
                "O campo nome não deve ficar vazio.",
            ],
        ),
    ]
    field: Annotated[
        Optional[str],
        Field(
            default_factory=None,
            description="Campo que gerou o erro",
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
