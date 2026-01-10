from python.funcoes import (
    ContaIterador,
    criar_conta,
    criar_usuario,
    deposito,
    mostrar_extrato,
    saque,
)
from python.utils import Cancelado, acessar_conta, clear, mostrar_menu


def main():
    status = [None, None]
    mensagem = ""

    while True:
        opcao = mostrar_menu(status, mensagem, trava=False).lower()

        match opcao:
            case "c":
                try:
                    clear()

                    def espaco(total, texto, offset):
                        return " " * max(
                            0,
                            total - len(texto.strip()) - offset,
                        )

                    def tem_numero(texto):
                        return any(c.isdigit() for c in texto)

                    def formatar_nome(nome):
                        preposicoes = {"de", "da", "do", "dos", "das"}

                        palavras = nome.lower().split()

                        resultado = []
                        for p in palavras:
                            if p in preposicoes:
                                resultado.append(p)
                            else:
                                resultado.append(p.capitalize())

                        return " ".join(resultado)

                    nome = mostrar_menu(
                        status,
                        "Digite seu nome: ",
                    ).strip()

                    if len(nome) > 69 or tem_numero(nome):
                        mensagem = (
                            f"{nome}, tem mais de 69 caracteres."
                            if len(nome) > 69
                            else f"{nome}, não pode conter números."
                        )
                        clear()
                        continue
                    clear()

                    nome = formatar_nome(nome)

                    data_nascimento = mostrar_menu(
                        status,
                        "Digite seu nome: "
                        + nome
                        + (
                            espaco(48, nome, 17)
                            if (len(nome) < 33)
                            else espaco(79, nome, 0)
                        )
                        + "Informe sua data de nascimento, ex(00/00/0000): ",
                    ).strip()

                    if len(data_nascimento) != 10:
                        mensagem = "Formato de data inválido. Use DD/MM/AAAA."
                        clear()
                        continue
                    clear()

                    cpf = mostrar_menu(
                        status,
                        "Digite seu nome: "
                        + nome
                        + (
                            espaco(48, nome, 17)
                            if (len(nome) < 33)
                            else espaco(79, nome, 0)
                        )
                        + "Informe sua data de nascimento, ex(00/00/0000): "
                        + data_nascimento
                        + espaco(48, data_nascimento, 0)
                        + "Informe seu cpf, ex(000.000.000-00): ",
                    ).strip()

                    if len(cpf) != 14:
                        mensagem = "Formato de CPF inválido."
                        clear()
                        continue
                    clear()

                    rua = mostrar_menu(
                        status,
                        "Digite seu nome: "
                        + nome
                        + (
                            espaco(48, nome, 17)
                            if (len(nome) < 33)
                            else espaco(79, nome, 0)
                        )
                        + "Informe sua data de nascimento, ex(00/00/0000): "
                        + data_nascimento
                        + espaco(48, data_nascimento, 0)
                        + "Informe seu cpf, ex(000.000.000-00): "
                        + cpf
                        + espaco(62, cpf, 3)
                        + "Informe o nome da sua rua: ",
                    ).strip()

                    if len(rua) > 58 or rua.isnumeric():
                        mensagem = (
                            f"R.{rua}, tem mais de 58 caracteres."
                            if len(rua) > 58
                            else f"R.{rua}, não pode ser composto apenas por"
                            + ""
                            + " números."
                        )
                        clear()
                        continue
                    clear()

                    numero = mostrar_menu(
                        status,
                        "Informe o nome da sua rua: "
                        + rua
                        + (
                            espaco(48, rua, 27)
                            if (len(rua.strip()) < 21)
                            else espaco(69, rua, 0)
                        )
                        + "Digite o número da sua casa: ",
                    ).strip()

                    if len(numero) > 15:
                        mensagem = "Número da casa inválido."
                        clear()
                        continue
                    clear()

                    bairro = mostrar_menu(
                        status,
                        "Informe o nome da sua rua: "
                        + rua
                        + (
                            espaco(48, rua, 27)
                            if (len(rua.strip()) < 21)
                            else espaco(69, rua, 0)
                        )
                        + "Digite o número da sua casa: "
                        + numero
                        + espaco(48, numero, 29)
                        + "Diga o nome do seu bairro: ",
                    ).strip()

                    if len(bairro) > 35:
                        mensagem = "Nome do bairro possui muitos caracteres."
                        clear()
                        continue
                    clear()

                    cidade = mostrar_menu(
                        status,
                        "Informe o nome da sua rua: "
                        + rua
                        + (
                            espaco(48, rua, 27)
                            if (len(rua.strip()) < 21)
                            else espaco(69, rua, 0)
                        )
                        + "Digite o número da sua casa: "
                        + numero
                        + espaco(48, numero, 29)
                        + "Diga o nome do seu bairro: "
                        + bairro
                        + (
                            espaco(48, bairro, 27)
                            if len(bairro.strip()) < 21
                            else espaco(69, bairro, 0)
                        )
                        + "Qual o nome de sua cidade: ",
                    ).strip()

                    if len(cidade) > 35 or tem_numero(cidade):
                        mensagem = (
                            "Nome da cidade possui muitos caracteres."
                            if len(cidade) > 35
                            else "Nome de cidade não pode conter números."
                        )
                        clear()
                        continue
                    clear()

                    estado = mostrar_menu(
                        status,
                        "Informe o nome da sua rua: "
                        + rua
                        + (
                            espaco(48, rua, 27)
                            if (len(rua.strip()) < 21)
                            else espaco(69, rua, 0)
                        )
                        + "Digite o número da sua casa: "
                        + numero
                        + espaco(48, numero, 29)
                        + "Diga o nome do seu bairro: "
                        + bairro
                        + (
                            espaco(48, bairro, 27)
                            if len(bairro.strip()) < 21
                            else espaco(69, bairro, 0)
                        )
                        + "Qual o nome de sua cidade: "
                        + cidade
                        + (
                            espaco(48, cidade, 27)
                            if len(cidade.strip()) < 21
                            else espaco(69, cidade, 0)
                        )
                        + "Digite a sigla de seu estado (ex: SP): ",
                    ).strip()

                    if len(estado) != 2 or tem_numero(estado):
                        mensagem = (
                            "Estado inválido." + ""
                            ""
                            "" + " Use apenas duas letras (ex: SP)."
                        )
                        clear()
                        continue
                    clear()

                    resultado_usuario, resposta = criar_usuario(
                        nome=nome,
                        data_nascimento=data_nascimento,
                        cpf=cpf,
                        rua=rua.title(),
                        numero=numero.title(),
                        bairro=bairro.title(),
                        cidade=cidade.title(),
                        estado=estado.upper(),
                    )

                    clear()
                    mensagem = resposta
                    if resultado_usuario:
                        mensagem += (
                            " Seja bem-vindo(a),"
                            + ""
                            + ""
                            + ""
                            + f" {resultado_usuario["nome"]}!"
                        )
                except Cancelado:
                    clear()
                    mensagem = "Operação cancelada..."
                    continue

            case "a":
                clear()
                mensagem = (
                    "Você já tem alguma conta corrente?"
                    f"{" "*62}[Sim] quero listar e acessar uma conta específi-"
                    + ""
                    + "ca."
                    f"{" "*45}[Não] quero cadastrar uma nova conta corrente."
                )
                menu_opcoes = [
                    "",
                    "",
                    " [s] Sim",
                    " [n] Não",
                    " [q] Sair",
                ]
                opcao = mostrar_menu(
                    status,
                    mensagem,
                    menu_opcoes,
                    trava=False,
                ).lower()

                match opcao:
                    case "s":
                        try:
                            clear()
                            cpf = mostrar_menu(
                                status,
                                "Digite seu CPF: ",
                                menu_opcoes,
                            )
                            clear()

                            texto, contas, usuario = acessar_conta(
                                cpf=cpf,
                            )

                            if contas is None:
                                mensagem = texto
                                continue

                            num = mostrar_menu(
                                status,
                                mensagem="Digite o ID da conta que"
                                + ""
                                + " quer acessar: ",
                                info_extra=texto,
                            )

                            try:
                                num = int(num)
                            except (TypeError, ValueError):
                                clear()

                                mensagem = (
                                    "Entrada inválida. Apenas valores"
                                    + ""
                                    + ""
                                    + " numéricos."
                                )
                                continue

                            except Exception as e:
                                print("Erro indeterminado: ", e)
                                raise

                            escolhida = None

                            for id_conta, _ in enumerate(contas):
                                if contas[id_conta]["id"] == num:
                                    escolhida = contas[id_conta]
                                    break

                            if escolhida is None:
                                mensagem = "Conta inválida."
                                clear()
                                continue

                            status[0] = usuario
                            status[1] = escolhida
                            mensagem = "Usuario logado com sucesso!"
                            clear()
                        except Cancelado:
                            clear()
                            mensagem = "Operação cancelada..."
                            continue

                    case "n":
                        try:
                            clear()
                            cpf = mostrar_menu(
                                status,
                                "Digite seu CPF: ",
                                menu_opcoes,
                            )

                            resultado_conta, resposta = criar_conta(cpf=cpf)
                            clear()
                            mensagem = resposta

                            if resultado_conta is not None:
                                mensagem += (
                                    f"{" "*14}"
                                    "RETORNO -> "
                                    f"Agência: {resultado_conta['agencia']}, "
                                    f"Conta: {resultado_conta['numero']}, "
                                    f"Saldo: {resultado_conta['saldo']:.2f}"
                                )
                        except Cancelado:
                            clear()
                            mensagem = "Operação cancelada..."
                            continue

                    case "q":
                        mensagem = ""
                        clear()
                        continue

                    case _:
                        clear()
                        mensagem = (
                            "Operação inválida, por favor selecione novamente"
                            "a operação desejada."
                        )

            case "d":
                try:
                    if status[1] is None:
                        clear()
                        mensagem = "Nenhuma conta acessada."
                        continue

                    clear()
                    valor = mostrar_menu(
                        status,
                        "Informe o valor do depósito: ",
                    )

                    try:
                        valor = float(valor)
                    except (ValueError, TypeError):
                        clear()
                        mensagem = (
                            "Operação falhou! Digite um valor numérico "
                            + ""
                            + ""
                            + "válido."
                        )
                        continue
                    except Exception as e:
                        print("Erro inesperado:", e)
                        raise

                    resultado, resposta = deposito(
                        valor,
                        status,
                    )
                    clear()
                    mensagem = resposta

                    mensagem += (
                        " " * 6
                        + "Novo saldo disponivel de: R$ "
                        + (" " * max(0, 8 - len(f"{resultado["saldo"]:.2f}")))
                        + f"{resultado["saldo"]:.2f}"
                        if resultado is not None
                        else ""
                    )
                except Cancelado:
                    clear()
                    mensagem = "Operação cancelada..."
                    continue

            case "s":
                try:
                    if status[1] is None:
                        clear()
                        mensagem = "Nenhuma conta acessada."
                        continue

                    clear()
                    valor = mostrar_menu(
                        status,
                        "Informe o valor do depósito: ",
                    )

                    try:
                        valor = float(valor)
                    except (TypeError, ValueError):
                        clear()
                        mensagem = (
                            "Operação falhou! Digite um valor numérico"
                            + ""
                            + " válido."
                        )
                        continue
                    except Exception as e:
                        print("Erro inesperado:", e)
                        raise

                    resultado, resposta = saque(
                        valor=valor,
                        status=status,
                    )
                    clear()
                    mensagem = resposta

                    mensagem += (
                        " " * 6
                        + "Novo saldo disponivel de: R$ "
                        + (" " * max(0, 8 - len(f"{resultado["saldo"]:.2f}")))
                        + f"{resultado["saldo"]:.2f}"
                        if resultado is not None
                        else ""
                    )
                except Cancelado:
                    clear()
                    mensagem = "Operação cancelada..."
                    continue

            case "e":
                clear()

                if status[1] is None:
                    clear()
                    mensagem = "Nenhuma conta acessada."
                    continue

                clear()
                mostrar_menu(
                    status,
                    mensagem="Pressione ENTER para continuar...",
                    info_extra=mostrar_extrato(status=status),
                    trava=False,
                )
                clear()
                mensagem = ""

            case "l":
                clear()

                if status[0] is None:
                    clear()
                    mensagem = "Nenhuma conta acessada."
                    continue

                usuario = status[0]

                def contas_usuario_para_texto(usuario):
                    linhas = []

                    ano, mes, dia = usuario["data_nascimento"].split("-")

                    data_fmt = f"{dia}/{mes}/{ano}"

                    # Cabeçalho do usuário
                    linhas.append("DADOS DO USUÁRIO")
                    linhas.append("")
                    linhas.append(f"Nome:           {usuario["nome"]}")
                    linhas.append(f"Nascimento:     {data_fmt}")
                    linhas.append(f"CPF:            {usuario["cpf"]}")
                    linhas.append(f"Endereço:       {usuario["endereco"]}")
                    linhas.append("")
                    linhas.append("=" * 55)
                    linhas.append("")
                    linhas.append("CONTAS DO USUÁRIO")
                    linhas.append("")

                    iterador = ContaIterador(usuario["id"])
                    if iterador.erro:
                        linhas.append(iterador.erro)
                    else:
                        for conta in iterador:
                            linhas.append(
                                f"Agência:          {conta['agencia']}",
                            )
                            linhas.append(
                                f"C/C:              {conta['cc']}",
                            )
                            linhas.append(
                                f"Saldo:            R$ {conta['saldo']:.2f}",
                            )
                            linhas.append(
                                f"Limite:           {conta['limite']}",
                            )
                            linhas.append(
                                f"Limite de saques: {conta['limite_saques']}",
                            )
                            linhas.append(
                                f"Numero de saques: {conta['numero_saques']}",
                            )
                            linhas.append("-" * 55)
                    return "\n".join(linhas)

                clear()
                mostrar_menu(
                    status,
                    mensagem="Pressione ENTER para continuar...",
                    info_extra=contas_usuario_para_texto(usuario),
                    trava=False,
                )
                clear()
                mensagem = ""

            case "q":
                clear()
                break

            case _:
                clear()
                mensagem = (
                    "Operação inválida, por favor selecione novamente"
                    "a operação desejada."
                )


if __name__ == "__main__":
    clear()
    main()
