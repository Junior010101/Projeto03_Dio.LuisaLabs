import os
from calendar import monthrange
from json import dumps, loads
from pathlib import Path

from api_client import request_get, request_post


def mostrar_menu(
    status,
    /,
    mensagem="",
    menu_opcoes=None,
    trava=True,
    info_extra=None,
):
    def header():
        print(f"\033[32m╔{'═' * 77}╗")
        print(f"║{'Sistema bancário'.center(77)}║")
        (print(f"╚{'═' * 77}╝\033[0m") if not info_extra else None)

    def formatar_mensagem(msg, largura=48):
        linhas = []
        while msg:
            linhas.append(msg[:largura].ljust(largura))
            msg = msg[largura:]
        while len(linhas) < 7:
            linhas.append(" " * largura)
        return linhas[:7]

    def container(
        usuario_atual,
        conta_atual,
        logado,
        mensagem="",
        menu_opcoes=None,
    ):
        linhas_msg = formatar_mensagem(mensagem)

        if menu_opcoes is None:
            menu_opcoes = [
                " [c] Cadastro",
                " [a] Acessar conta",
                "----",
                " [d] Depositar",
                " [s] Sacar",
                " [e] Extrato",
                " [l] Listar informações",
                " [q] Sair",
            ]

        CINZA = "\033[90m"
        VERDE = "\033[32m"
        AMARELO = "\033[33m"
        RESET = "\033[0m"

        operacoes = (
            " [d] Depositar",
            " [s] Sacar",
            " [e] Extrato",
            " [l] Listar informações",
        )

        while len(menu_opcoes) < 8:
            menu_opcoes.append("")

        print(f"\033[32m╔{'═' * 77}╗")
        print(f"║  Usuario: {usuario_atual.ljust(75)}\033[32m║")
        print(f"║  Conta:   {conta_atual.ljust(75)}\033[32m║")
        print(f"╠{'═' * 28}╦{'═' * 48}╣")
        print(f"║{'Menu'.center(28)}║{'Info'.center(48)}║")
        print(f"║{' ' * 28}║{' ' * 48}║")
        for i in range(7):
            opcao = menu_opcoes[i]
            texto = opcao.ljust(28)

            if opcao == "----":
                cor = RESET

            elif trava:
                cor = CINZA if opcao != " [q] Sair" else VERDE

            elif logado and opcao in operacoes:
                cor = AMARELO

            elif not logado and opcao in operacoes:
                cor = CINZA

            else:
                cor = VERDE

            item = f"{cor}{texto}{RESET}"
            print(f"║{item}\033[32m║{linhas_msg[i]}║")
        print(f"║{menu_opcoes[7].ljust(28)}║{' ' * 48}║")
        print(f"╚{'═' * 28}╩{'═' * 48}╝\033[0m")

    def entrada():
        largura = 79
        print("\033[32m", end="")
        print("╔" + "═" * (largura - 2) + "╗")
        print("║ => " + " " * (largura - 6) + "║")
        print("╚" + "═" * (largura - 2) + "╝\033[0m", end="\n")
        print("\033[2A", end="")
        print("\033[6G", end="")
        return input()

    def bloco_info(texto, largura=77):
        linhas_render = []

        for linha in texto.splitlines():
            while len(linha) > largura:
                linhas_render.append(linha[:largura])
                linha = linha[largura:]
            linhas_render.append(linha)

        print(f"\033[32m╠{'═' * largura}╣")
        for la in linhas_render:
            print(f"║{la.ljust(largura)}║")
        print(f"╚{'═' * largura}╝\033[0m")

    if status[0] is not None:
        nome_usuario = status[0]["nome"]
        usuario_atual = f"\033[32m{nome_usuario}\033[0m"
    else:
        usuario_atual = (
            "\033[31m"
            + ""
            + "( Acesse uma conta para fazer login! )"
            + ""
            + ""
            + "\033[0m"
        )

    if status[0] is not None and status[1] is not None:
        numero_conta = status[1]["numero"]
        conta_atual = f"\033[34m{numero_conta}\033[0m"
    else:
        conta_atual = "\033[31m( Nenhuma conta )\033[0m"

    logado = True if status[0] is not None else False

    header()
    if info_extra:
        bloco_info(info_extra)
    container(usuario_atual, conta_atual, logado, mensagem, menu_opcoes)

    valor = entrada()

    if valor.strip().lower() == "q" and trava is True:
        raise Cancelado

    return valor


def clear():
    os.system("cls") if os.name == "nt" else os.system("clear")


def validar_cpf(cpf, /):
    if len(cpf) == 14 and cpf[3] == "." and cpf[7] == "." and cpf[11] == "-":
        nums = cpf.replace(".", "").replace("-", "")

        if not nums.isdigit() or len(nums) != 11:
            return None, f"O cpf {cpf} possui caracteres inválidos."
        if nums == nums[0] * 11:
            return None, f"O cpf {cpf} é inválido."

        def calc_dv(n):
            soma = sum(int(n[i]) * (len(n) + 1 - i) for i in range(len(n)))
            resto = soma % 11
            return "0" if resto < 2 else str(11 - resto)

        dv1 = calc_dv(nums[:9])
        dv2 = calc_dv(nums[:9] + dv1)

        if nums[-2:] == dv1 + dv2:
            return nums, None
        else:
            return (
                None,
                f"O cpf {cpf}",
                " é inválido (dígitos verificadores incorretos).",
            )
    else:
        return None, f"O formato do cpf: {cpf}, é invalido."


def validar_data_nascimento(data_nascimento):
    if (
        len(data_nascimento) != 10
        or data_nascimento[2] != "/"
        or data_nascimento[5] != "/"
    ):
        return (
            None,
            f"O formato da data de nascimento: {data_nascimento} , é"
            + ""
            + " inválido.",
        )

    dia_str, mes_str, ano_str = data_nascimento.split("/")

    if not (dia_str.isdigit() and mes_str.isdigit() and ano_str.isdigit()):
        return None, f"A data {data_nascimento} contém caracteres inválidos."

    dia = int(dia_str)
    mes = int(mes_str)
    ano = int(ano_str)

    if not (1 <= mes <= 12):
        return None, f"A data {data_nascimento} é inválida (mês inexistente)."

    if not (1900 <= ano <= 2100):
        return (
            None,
            (
                f"A data {data_nascimento}",
                " é inválida (ano fora do intervalo permitido).",
            ),
        )

    _, dias_no_mes = monthrange(ano, mes)
    if not (1 <= dia <= dias_no_mes):
        return None, f"A data {data_nascimento} é inválida (dia inexistente)."

    return (dia, mes, ano), None


def buscar_usuario(*, cpf_tratado):
    resposta, erro = request_get(
        endpoint="clientes",
        param=cpf_tratado,
    )

    if resposta:
        return resposta["id"], None
    else:
        return None, erro


def acessar_conta(*, cpf):
    cpf_tratado, erro_cpf = validar_cpf(cpf)

    if cpf_tratado is None:
        return erro_cpf, None, None

    id_usuario, erro = buscar_usuario(cpf_tratado=cpf_tratado)

    if id_usuario is None:
        return erro, None, None

    auth_re, auth_e = request_post(
        endpoint="auth/login",
        payload={"id_usuario": id_usuario},
    )

    if not auth_re:
        return auth_e, None, None

    headers_user = {"Authorization": f"Bearer {auth_re['token_acesso']}"}

    resposta, erro = request_get(endpoint="contas", headers=headers_user)

    if erro:
        return erro, None, None

    contas_do_usuario = resposta

    if not contas_do_usuario:
        return "Nenhuma conta encontrada.", None, None

    def contas_para_texto(contas):
        linhas = ["Contas encontradas:\n"]

        for conta in contas:
            linhas.append(f"Conta:   {conta['numero']}")
            linhas.append(f"Id:      {conta['id']}")
            linhas.append(f"Agência: {conta['agencia']}")
            linhas.append("")

        return "\n".join(linhas)

    resposta, _ = request_get(
        endpoint="clientes",
        param=cpf_tratado,
    )

    return (
        contas_para_texto(contas_do_usuario),
        contas_do_usuario,
        resposta,
    )


def buscar_log():
    caminho_log = Path(__file__).parent.parent / "cache" / "log.txt"
    logs = {}
    registro_log = None

    try:
        registro_log = open(caminho_log, "r")

        for line in registro_log:
            try:
                raw = loads(line)
                _id, data = raw
                data["id"] = _id
                logs[_id] = data
            except ValueError:
                continue

    except FileNotFoundError:
        os.makedirs(os.path.dirname(caminho_log), exist_ok=True)
        registro_log = open(caminho_log, "w")
        return {}

    finally:
        if registro_log:
            registro_log.close()

    return logs


def salvar_log(registro):
    caminho_log = Path(__file__).parent.parent / "cache" / "log.txt"
    arquivo = None

    try:
        arquivo = open(caminho_log, "w")

        for _id, data in registro.items():
            arquivo.write(dumps([_id, data]) + "\n")

    finally:
        if arquivo:
            arquivo.close()


class Cancelado(Exception):
    pass
