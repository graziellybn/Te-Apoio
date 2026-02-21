# teapoio/infrastructure/cli.py
from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.responsavel import Responsavel
import sys

responsaveis = {}

# Funções auxiliares para validar entrada
def input_int(mensagem: str, min_val: int | None = None, max_val: int | None = None) -> int:
    range_text = ""
    if min_val is not None and max_val is not None:
        range_text = f" ({min_val}-{max_val})"
    elif min_val is not None:
        range_text = f" (>= {min_val})"
    elif max_val is not None:
        range_text = f" (<= {max_val})"

    prompt = mensagem if mensagem.endswith(" ") else mensagem + " "

    while True:
        if range_text:
            valor = input(prompt + range_text + ": ")
        else:
            valor = input(prompt)
        try:
            valor_int = int(valor)
            if min_val is not None and valor_int < min_val:
                if sys.stdout.isatty():
                    # limpa a linha com a entrada do usuário
                    sys.stdout.write('\x1b[1A')
                    sys.stdout.write('\x1b[2K')
                    sys.stdout.flush()
                print(f"Responsável deve ter {min_val} ou mais anos.")
                continue
            if max_val is not None and valor_int > max_val:
                if sys.stdout.isatty():
                    sys.stdout.write('\x1b[1A')
                    sys.stdout.write('\x1b[2K')
                    sys.stdout.flush()
                print(f"Criança deve ter {max_val} ou menos anos.")
                continue
            return valor_int
        except ValueError:
            if sys.stdout.isatty():
                sys.stdout.write('\x1b[1A')
                sys.stdout.write('\x1b[2K')
                sys.stdout.flush()
            print("Erro. Digite as informações corretamente.")

def criar_responsavel():
    print("\n=== Criar Responsável ===")
    nome = input("Nome: ")
    # valida idade no input: responsável deve ter >= 18 anos
    idade = input_int("Idade do responsável", min_val=18)
    cpf = input("CPF: ")
    email = input("Email: ")
    telefone = input("Telefone: ")
    tipo = input("Tipo de responsável (Mãe/Pai/etc): ")
    endereco = input("Endereço (opcional): ") or None
    quant = input_int("Quantidade de crianças: ")

    try:
        resp = Responsavel(nome, idade, cpf, email, telefone, tipo, endereco, quant_criancas=quant)
        responsaveis[cpf] = resp
        print(f"Responsável {nome} criado com sucesso!\n")
    except ValueError as e:
        msg = str(e)
        if "Responsável deve ter 18 anos" in msg:
            print("Responsável deve ter 18 ou mais.\n")
        else:
            print(f"Erro ao criar responsável: {e}\n")
    except Exception as e:
        print(f"Erro ao criar responsável: {e}\n")

def adicionar_crianca():
    print("\n=== Adicionar Criança ===")
    resp_cpf = input("CPF do responsável: ")
    resp = responsaveis.get(resp_cpf)
    if not resp:
        print("Responsável não encontrado.\n")
        return

    nome = input("Nome da criança: ")
    idade = input_int("Idade da criança", min_val=0, max_val=17)
    cpf = input("CPF: ")
    email = input("Email: ")
    telefone = input("Telefone: ")
    nivel = input("Nível de suporte (baixo/moderado/alto): ").lower()

    try:
        crianca = Crianca(
            nome=nome,
            idade=idade,
            cpf=cpf,
            email=email,
            telefone=telefone,
            responsavel=resp,
            nivel_suporte=nivel
        )
        resp.adicionar_crianca(crianca)
        print(f"Criança {nome} adicionada ao responsável {resp.nome}.\n")
    except ValueError as e:
        msg = str(e)
        if "Idade da criança" in msg or "Idade da criança deve estar" in msg:
            print("Erro ao adicionar criança: idade inválida. Idade válida: 0–17 anos.\n")
        else:
            print(f"Erro ao adicionar criança: {e}\n")
    except Exception as e:
        print(f"Erro ao adicionar criança: {e}\n")

def listar_criancas():
    print("\n=== Listar Crianças ===")
    resp_cpf = input("CPF do responsável: ")
    resp = responsaveis.get(resp_cpf)
    if not resp:
        print("Responsável não encontrado.\n")
        return

    if not resp.listar_criancas():
        print(f"{resp.nome} ainda não tem crianças cadastradas.\n")
        return

    print(f"\nCrianças de {resp.nome}:")
    for c in resp.listar_criancas():
        print(f"- {c.nome}, {c.idade} anos, suporte: {c.nivel_suporte}")
    print()

def menu():
    while True:
        print("=== Sistema Teapoio ===")
        print("1. Criar responsável")
        print("2. Adicionar criança")
        print("3. Listar crianças")
        print("0. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            criar_responsavel()
        elif opcao == "2":
            adicionar_crianca()
        elif opcao == "3":
            listar_criancas()
        elif opcao == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida.\n")


