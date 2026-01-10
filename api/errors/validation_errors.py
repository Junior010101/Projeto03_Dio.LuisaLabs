from typing import Optional

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ValidationErrorHandler:
    """
    Classe base para qualquer handler específico.

    Cada handler:
    - declara QUAL campo quer tratar (field)
    - declara QUAL tipo de erro do Pydantic (error_type)
    - decide se lida com o erro (match)
    - constrói a resposta HTTP (response)
    """

    # Nome do campo no schema (ex: "data_nascimento")
    field: str | None = None

    # Tipo do erro retornado pelo Pydantic
    # Ex: "date_from_datetime_parsing"
    error_type: str | None = None

    def match(self, error: dict) -> bool:

        if self.field and error["loc"][-1] != self.field:
            return False

        if self.error_type and error["type"] != self.error_type:
            return False

        return True

    def response(self) -> JSONResponse:
        raise NotImplementedError("Handler precisa implementar response()")


class DataNascimentoInvalidaHandler(ValidationErrorHandler):

    field = "data_nascimento"
    error_type = "date_from_datetime_parsing"

    def response(self) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "code": "CONTEUDO_INVALIDO",
                "message": "Formato da data de nascimento inválido",
                "field": f"{self.field}",
                "origin": "validation",
            },
        )


class CPFInvalidoHandler(ValidationErrorHandler):

    field = "cpf"
    error_type = "string_too_short"

    def response(self) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "code": "CONTEUDO_INVALIDO",
                "message": "A string do CPF,"
                + " deve ter exatamente "
                + "11 caracteres.",
                "field": f"{self.field}",
                "origin": "validation",
            },
        )


class NomeInvalidoHandler(ValidationErrorHandler):

    field = "nome"

    def match(self, error: dict) -> bool:
        if not super().match(error):
            return False

        self._error_type = error["type"]
        return self._error_type in {
            "string_too_long",
            "string_too_short",
        }

    def response(self) -> JSONResponse:
        if self._error_type == "string_too_long":
            detail = "O nome deve ter no máximo 69 caracteres."
        elif self._error_type == "string_too_short":
            detail = "O campo nome não deve ficar vazio."
        else:
            detail = "Nome inválido."

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "code": "CONTEUDO_INVALIDO",
                "message": f"{detail}",
                "field": f"{self.field}",
                "origin": "validation",
            },
        )


class EnderecoInvalidoHandler(ValidationErrorHandler):

    field = "endereco"
    error_type = "string_too_short"

    def response(self) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "code": "CONTEUDO_INVALIDO",
                "message": "O campo endereço não deve ficar vazio.",
                "field": f"{self.field}",
                "origin": "validation",
            },
        )


class AgenciaInvalidaHandler(ValidationErrorHandler):

    field = "agencia"

    def match(self, error: dict) -> bool:
        if not super().match(error):
            return False

        self._error_type = error["type"]
        return self._error_type in {
            "missing",
            "string_too_short",
        }

    def response(self) -> JSONResponse:
        if self._error_type == "missing":
            detail = "Há um campo obrigatório faltando no corpo do json."
        elif self._error_type == "string_too_short":
            detail = "O campo agência não deve ficar vazio."
        else:
            detail = "Agência inválida."

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "code": "CONTEUDO_INVALIDO",
                "message": f"{detail}",
                "field": f"{self.field}",
                "origin": "validation",
            },
        )


class CamposAbertosNoJsonHandler(ValidationErrorHandler):

    error_type = "json_invalid"

    def match(self, error: dict) -> bool:
        if not super().match(error):
            return False

        self._field = error["loc"][0]
        return self._field in {
            "body",
        }

    def response(self) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "code": "CONTEUDO_INVALIDO",
                "message": "Há um campo em aberto no corpo do json.",
                "field": f"{self._field}",
                "origin": "validation",
            },
        )


class ValidationErrorDispatcher:
    def __init__(self):
        self.handlers: list[ValidationErrorHandler] = []

    def register(self, handler: ValidationErrorHandler):
        self.handlers.append(handler)

    def dispatch(self, exc: RequestValidationError) -> Optional[JSONResponse]:
        for error in exc.errors():
            for handler in self.handlers:
                if handler.match(error):
                    return handler.response()

        return None


def register_validation_handler(app):

    dispatcher = ValidationErrorDispatcher()

    dispatcher.register(DataNascimentoInvalidaHandler())
    dispatcher.register(CPFInvalidoHandler())
    dispatcher.register(NomeInvalidoHandler())
    dispatcher.register(EnderecoInvalidoHandler())
    dispatcher.register(AgenciaInvalidaHandler())
    dispatcher.register(CamposAbertosNoJsonHandler())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        response = dispatcher.dispatch(exc)
        if response:
            return response

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exc.errors()},
        )
