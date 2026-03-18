from abc import ABC, abstractmethod
from datetime import datetime as date

from python.utils import buscar_log, salvar_log
from src.client import request_get, request_post


class Cliente:
    def __init__(self, endereco):
        self._endereco = endereco

    def realisar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, endereco, nome, data_nascimento, cpf):
        super().__init__(endereco)

        self.nome = nome
        self.data_nascimento = (
            f"{data_nascimento[2]}-"
            f"{data_nascimento[1]:02d}-"
            f"{data_nascimento[0]:02d}"
        )
        self.cpf = cpf
        self.endereco = endereco

    def __str__(self):
        return {
            "nome": self.nome,
            "cpf": self.cpf,
            "data_nascimento": self.data_nascimento,
        }


class Conta:
    def __init__(self, agencia="0001", saldo=0):
        self.agencia = agencia
        self.saldo = saldo

    def __str__(self):
        return (
            f"Agência: {self.agencia} | "
            f"Conta: {self.numero} | "
            f"Saldo: {self.saldo}"
        )

    def sacar(self, *, valor, id_conta, id_usuario):
        auth_re, auth_e = request_post(
            endpoint="auth/login",
            payload={"id_usuario": id_usuario},
        )

        if not auth_re:
            return False, auth_e

        headers_user = {"Authorization": f"Bearer {auth_re['token_acesso']}"}

        resp, error = request_get(
            endpoint="contas",
            param=id_conta,
            headers=headers_user,
        )

        if not resp:
            return False, error

        if valor <= 0:
            return False, "Operação falhou! O valor informado é inválido."

        data = {"conta_id": id_conta, "acao": "SAQUE", "valor": valor}

        res, erro = request_post(
            endpoint="transacoes/", payload=data, headers=headers_user
        )

        excedeu_saques = resp["numero_saques"] >= resp["limite_saques"]
        if excedeu_saques:
            return False, "Operação falhou! Número máximo de saques excedido."

        excedeu_limite = valor > resp["limite"]
        if excedeu_limite:
            return False, "Operação falhou! O valor do saque excede o limite."

        excedeu_saldo = valor > resp["saldo"]
        if excedeu_saldo:
            return False, "Operação falhou! Você não tem saldo suficiente."

        if not res:
            return False, erro

        return headers_user, f"Saque de: R$ {valor:.2f}, feito com sucesso!"

    def depositar(self, *, valor, id_conta, id_usuario):
        if valor <= 0:
            return False, "Operação falhou! O valor informado é inválido."

        auth_re, auth_e = request_post(
            endpoint="auth/login",
            payload={"id_usuario": id_usuario},
        )

        if not auth_re:
            return False, auth_e

        headers_user = {"Authorization": f"Bearer {auth_re['token_acesso']}"}
        data = {"conta_id": id_conta, "acao": "DEPOSITO", "valor": valor}

        res, erro = request_post(
            endpoint="transacoes/", payload=data, headers=headers_user
        )

        if not res:
            return False, erro

        return headers_user, f"Depósito de: R$ {valor:.2f}, feito com sucesso!"


class ContaCorrente(Conta):
    def __init__(self, agencia, saldo, limite=500, limite_saques=3):
        super().__init__(agencia, saldo)

        self.limite = limite
        self.limite_saques = limite_saques
        self.numero_saques = 0


class Historico:
    def __init__(self, conta):
        self._conta = conta

    @property
    def transacoes(self):
        registros = buscar_log()
        transacoes = []

        for data in registros.values():
            mesma_conta = data.get("conta") == self._conta

            if mesma_conta:
                transacoes.append(data)

        return transacoes

    def adicionar_transacao(self, *, evento, valor, status, cliente):
        registros = buscar_log()

        novo_id = max(registros.keys(), default=0) + 1

        registros[novo_id] = {
            "horario": date.now().strftime("%d-%m-%Y %H:%M:%S"),
            "evento": evento,
            "id_usuario": cliente,
            "conta": self._conta,
            "valor": valor,
            "status": status,
        }

        salvar_log(registros)


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @classmethod
    @abstractmethod
    def registrar(self, conta, id_usuario):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, *, id_conta, id_usuario):
        conta = Conta()

        resultado, resposta = conta.sacar(
            valor=self.valor,
            id_conta=id_conta,
            id_usuario=id_usuario,
        )

        if not resultado:
            historico = Historico(conta=id_conta)
            historico.adicionar_transacao(
                evento="saque",
                valor=self.valor,
                status=False,
                cliente=id_usuario,
            )
            return None, resposta

        historico = Historico(conta=id_conta)
        historico.adicionar_transacao(
            evento="saque",
            valor=self.valor,
            status=True,
            cliente=id_usuario,
        )

        return resultado, resposta


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, *, id_conta, id_usuario):
        conta = Conta()

        resultado, resposta = conta.depositar(
            valor=self.valor,
            id_conta=id_conta,
            id_usuario=id_usuario,
        )

        if not resultado:
            historico = Historico(conta=id_conta)
            historico.adicionar_transacao(
                evento="saque",
                valor=self.valor,
                status=False,
                cliente=id_usuario,
            )
            return None, resposta

        historico = Historico(conta=id_conta)
        historico.adicionar_transacao(
            evento=self.__class__.__name__.lower(),
            valor=self.valor,
            status=True,
            cliente=id_usuario,
        )

        if resultado:
            return resultado, resposta

        return None, resposta
