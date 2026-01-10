from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from api.views import ClienteError, ContaError, TransacaoError


class ClienteNaoEncontradoPeloCPF(Exception):
    def __init__(self, cpf: str):
        self.cpf = cpf


class ClienteNaoEncontradoPeloID(Exception):
    def __init__(self, cliente_id: int):
        self.cliente_id = cliente_id


class ClienteSemDadosNoUpdate(Exception):
    def __init__(self, dados: str):
        self.dados = dados


class ContaNaoEncontradaPeloID(Exception):
    def __init__(self, conta_id: int):
        self.conta_id = conta_id


class ContaAcessoNegado(Exception):
    def __init__(
        self,
        cliente_id: int,
        conta_id: int | None = None,
        conta_id_field: int | None = None,
    ):
        self.cliente_id = cliente_id
        self.conta_id_param = conta_id
        self.conta_id_field = conta_id_field


class ContaComSaldoNaoPodeSerDeletada(Exception):
    def __init__(self, saldo: float):
        self.saldo = saldo


class ClientePossuiContasNaoPodeSerDeletado(Exception):
    def __init__(self, cliente_id: int):
        self.cliente_id = cliente_id


class TransacaoSaldoInsuficiente(Exception):
    def __init__(self, saldo: int):
        self.saldo = saldo


class TransacaoTipoInvalido(Exception):
    def __init__(self, tipo: int):
        self.tipo = tipo


class TransacaoLimiteSaquesExcedido(Exception):
    pass


class TransacaoLimiteExcedido(Exception):
    pass


def register_domain_handlers(app: FastAPI):
    @app.exception_handler(ClienteNaoEncontradoPeloCPF)
    async def cliente_nao_encontrado_cpf_handler(
        request, exc: ClienteNaoEncontradoPeloCPF
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ClienteError(
                code="CLIENTE_NAO_ENCONTRADO",
                message="Não existe cliente cadastrado para o CPF informado",
                field=f"cpf:{exc.cpf}",
                origin="domain",
            ).model_dump(),
        )

    @app.exception_handler(ClienteNaoEncontradoPeloID)
    async def cliente_nao_encontrado_id_handler(
        request, exc: ClienteNaoEncontradoPeloID
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ClienteError(
                code="CLIENTE_NAO_ENCONTRADO",
                message="Não existe cliente cadastrado para o ID informado",
                field=f"id:{exc.cliente_id}",
                origin="domain",
            ).model_dump(),
        )

    @app.exception_handler(ClienteSemDadosNoUpdate)
    async def cliente_sem_dados_update_handler(
        request,
        exc: ClienteSemDadosNoUpdate,
    ):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=ClienteError(
                code="SEM_DADOS_PARA_ATUALIZAR",
                message="PATCH requer ao menos um campo",
                field=f"{exc.dados}",
                origin="domain",
            ).model_dump(),
        )

    @app.exception_handler(ContaNaoEncontradaPeloID)
    async def conta_nao_encontrada_id_handler(
        request,
        exc: ContaNaoEncontradaPeloID,
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ContaError(
                code="CONTA_NAO_ENCONTRADA",
                message="Não existe conta cadastrada para o ID informado",
                field=f"id:{exc.conta_id}",
                origin="domain",
            ).model_dump(),
        )

    @app.exception_handler(ContaAcessoNegado)
    async def conta_acesso_negado_handler(
        request,
        exc: ContaAcessoNegado,
    ):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ContaError(
                code="ACESSO_NEGADO",
                message=f"O cliente cujo id é {exc.cliente_id}, não tem"
                " permissão de acesso sobre essa conta.",
                field=(
                    f"id:{exc.conta_id_field}"
                    if exc.conta_id_field is not None
                    else None
                ),
                Parameter=(
                    f"id:{exc.conta_id_param}"
                    if exc.conta_id_param is not None
                    else None
                ),
                origin="domain",
            ).model_dump(),
        )

    @app.exception_handler(ContaComSaldoNaoPodeSerDeletada)
    async def conta_com_saldo_handler(
        request,
        exc: ContaComSaldoNaoPodeSerDeletada,
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ContaError(
                code="CONTA_COM_SALDO",
                message="A conta não pode ser deletada"
                " enquanto o saldo for diferente de zero",
                field=f"saldo:{exc.saldo}",
                origin="domain",
            ).model_dump(),
        )

    @app.exception_handler(ClientePossuiContasNaoPodeSerDeletado)
    async def cliente_possui_contas_handler(
        request,
        exc: ClientePossuiContasNaoPodeSerDeletado,
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ClienteError(
                code="CLIENTE_POSSUI_CONTAS",
                message="O cliente não pode ser deletado"
                " enquanto possuir contas associadas",
                field=f"id:{exc.cliente_id}",
                origin="domain",
            ).model_dump(),
        )

    @app.exception_handler(TransacaoSaldoInsuficiente)
    async def transacao_saldo_insuficiente_handler(
        request,
        exc: TransacaoSaldoInsuficiente,
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=TransacaoError(
                code="SALDO_INSUFICIENTE",
                message="Saldo insuficiente",
                field=f"saldo:{exc.saldo}",
                origin="domain",
            ).model_dump(),
        )

    @app.exception_handler(TransacaoTipoInvalido)
    async def transacao_tipo_invalido_handler(
        request,
        exc: TransacaoTipoInvalido,
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=TransacaoError(
                code="TIPO_INVALIDO",
                message="Tipo de transação inválido",
                field=f"tipo:{exc.tipo}",
                origin="domain",
            ).model_dump(),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request,
        exc: IntegrityError,
    ):
        message = str(exc.orig).lower()

        if "clientes.cpf" in message or "cpf" in message:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=ClienteError(
                    code="CPF_DUPLICADO",
                    message="Já existe um cliente cadastrado com este CPF.",
                    field="cpf",
                    origin="database",
                ).model_dump(),
            )

    @app.exception_handler(TransacaoLimiteSaquesExcedido)
    async def transacao_limite_saques_handler(
        request,
        exc: TransacaoLimiteSaquesExcedido,
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=TransacaoError(
                code="LIMITE_SAQUES_EXCEDIDO",
                message="Limite diário de saques excedido",
                field="numero_saques",
                origin="domain",
            ).model_dump(),
        )

    @app.exception_handler(TransacaoLimiteExcedido)
    async def transacao_limite_handler(
        request,
        exc: TransacaoLimiteExcedido,
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=TransacaoError(
                code="LIMITE_EXCEDIDO",
                message="Valor da transação excede o limite da conta",
                field="limite",
                origin="domain",
            ).model_dump(),
        )
