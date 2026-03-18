from datetime import datetime as date
from functools import wraps

from python.servicos import ContaCorrente, Deposito, PessoaFisica, Saque
from python.utils import (
    buscar_log,
    buscar_usuario,
    salvar_log,
    validar_cpf,
    validar_data_nascimento,
)
from src.client import request_get, request_post


def registrar_log():
    def criar_log(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            registro_log = buscar_log()
            log_id = max(registro_log.keys(), default=0) + 1

            kwargs_filtrados = {k: v for k, v in kwargs.items() if k != "log"}

            def safe(valor):
                if isinstance(valor, (int, float, str, bool, type(None))):
                    return valor
                return str(valor)

            registro_log[log_id] = {
                "horario": date.now().strftime("%d-%m-%Y %H:%M:%S"),
                "evento": func.__name__,
                "args": [safe(a) for a in args],
                "kwargs": {k: safe(v) for k, v in kwargs_filtrados.items()},
                "status": False,
            }

            resultado = func(*args, **kwargs)

            if isinstance(resultado, tuple) and len(resultado) > 0:
                registro_log[log_id]["status"] = bool(resultado[0])

            salvar_log(registro_log)

            return resultado

        return wrapper

    return criar_log


def saque(*, valor, status):
    id_conta = status[1]["id"]
    id_usuario = status[0]["id"]

    resultado, resposta = Saque(valor).registrar(
        id_conta=id_conta,
        id_usuario=id_usuario,
    )
    if not resultado:
        return None, resposta

    res, erro = request_get(
        endpoint="contas",
        param=id_conta,
        headers=resultado,
    )

    if not res:
        return None, erro

    if resultado:
        return res, resposta

    return None, resposta


def deposito(valor, status, /):
    id_conta = status[1]["id"]
    id_usuario = status[0]["id"]

    resultado, resposta = Deposito(valor).registrar(
        id_conta=id_conta,
        id_usuario=id_usuario,
    )

    if not resultado:
        return None, resposta

    res, erro = request_get(
        endpoint="contas",
        param=id_conta,
        headers=resultado,
    )

    if not res:
        return None, erro

    if resultado:
        return res, resposta

    return None, resposta


def mostrar_extrato(*, status):
    id_conta = status[1]["id"]
    id_usuario = status[0]["id"]

    auth_re, auth_e = request_post(
        endpoint="auth/login",
        payload={"id_usuario": id_usuario},
    )

    if not auth_re:
        return auth_e

    headers_user = {"Authorization": f"Bearer {auth_re['token_acesso']}"}

    conta, erro = request_get(
        endpoint="contas",
        param=id_conta,
        headers=headers_user,
    )

    if not conta:
        return erro

    def extrato_para_texto(conta):
        linhas = []
        saldo = conta["saldo"]

        extrato, erro = request_get(
            endpoint="transacoes",
            param=id_conta,
            headers=headers_user,
        )

        if erro:
            return erro

        linhas.append("EXTRATO")
        linhas.append("")

        encontrou = False

        for item in extrato:
            encontrou = True
            data = item["efetuada_em"]
            acao = item["acao"].title()
            status = "OK" if item["status"] else "Falhou"
            valor = float(item["valor"])

            linhas.append(f"{data} | {acao} - R$ {valor:.2f} - {status}")

        if not encontrou:
            linhas.append("Não foram realizadas movimentações.")

        linhas.append("")
        linhas.append(f"Saldo atual: R$ {saldo:.2f}")

        return "\n".join(linhas)

    return extrato_para_texto(conta)


@registrar_log()
def criar_usuario(
    *,
    nome,
    data_nascimento,
    cpf,
    rua,
    numero,
    bairro,
    cidade,
    estado,
):
    rua = rua.strip() or "Não informado"
    endereco = f"{rua}, {numero} - {bairro} - {cidade}/{estado}"

    data_validada, data_err = validar_data_nascimento(data_nascimento)
    if data_validada is None:
        return None, data_err

    cpf_do_usuario, cpf_err = validar_cpf(cpf)

    if cpf_do_usuario is None:
        return None, cpf_err

    id_usuario, _ = buscar_usuario(cpf_tratado=cpf_do_usuario)

    if id_usuario is not None:
        return None, f"O CPF {cpf} já está cadastrado."

    usuario = PessoaFisica(
        nome=nome,
        cpf=cpf_do_usuario,
        data_nascimento=data_validada,
        endereco=endereco,
    )

    resposta, erro = request_post(
        endpoint="clientes/",
        payload=usuario.__dict__,
    )

    if not resposta:
        return None, erro

    return resposta, "Usuario cadastrado com sucesso!"


@registrar_log()
def criar_conta(*, cpf):
    cpf_do_usuario, cpf_err = validar_cpf(cpf)

    if cpf_do_usuario is None:
        return None, cpf_err

    id_usuario, erro = buscar_usuario(cpf_tratado=cpf_do_usuario)

    if id_usuario is None:
        return None, erro

    resposta, erro = request_post(
        endpoint="auth/login", payload={"id_usuario": id_usuario}
    )

    if not resposta:
        return None, erro

    conta = ContaCorrente(agencia="0001", saldo=0, limite=500, limite_saques=5)

    headers_user = {"Authorization": f"Bearer {resposta['token_acesso']}"}

    res, erro = request_post(
        endpoint="contas/", payload=conta.__dict__, headers=headers_user
    )

    if not res:
        return None, erro

    return res, "Conta corrente criada com sucesso!"


def gerar_relatorio(*, logs, id_usuario, id_conta, filtro=None):
    def buscar_log():
        for log in logs:
            mesmo_usuario = log.get("id_usuario") == id_usuario
            mesma_conta = log.get("conta") == id_conta

            if mesmo_usuario and mesma_conta:
                yield log

    def filtrar_relatorio(filtro):
        for log in buscar_log():
            if log.get("evento") in filtro:
                yield log

    if filtro:
        return filtrar_relatorio(filtro)

    return buscar_log()


class ContaIterador:
    def __init__(self, id_usuario):
        self.erro = None
        self.index = 0
        self.contas_usuario = []

        auth_re, auth_e = request_post(
            endpoint="auth/login",
            payload={"id_usuario": id_usuario},
        )

        if not auth_re:
            self.erro = auth_e
            return

        headers_user = {"Authorization": f"Bearer {auth_re['token_acesso']}"}

        contas, erro = request_get(endpoint="contas", headers=headers_user)

        if erro:
            self.erro = erro
            return

        self.contas_usuario = contas

    def __iter__(self):
        return self

    def __next__(self):
        if self.erro:
            raise StopIteration

        if self.index >= len(self.contas_usuario):
            raise StopIteration

        conta = self.contas_usuario[self.index]
        self.index += 1

        return {
            "agencia": conta["agencia"],
            "cc": conta["numero"],
            "saldo": conta["saldo"],
            "limite": conta["limite"],
            "limite_saques": conta["limite_saques"],
            "numero_saques": conta["numero_saques"],
        }
