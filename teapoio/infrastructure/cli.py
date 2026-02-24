from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.responsavel import Responsavel

# ajuste os imports conforme seus arquivos reais:
from teapoio.domain.models.rotina import Rotina, TipoRecorrenciaRotina, DiaSemana
from teapoio.domain.models.item_rotina import ItemRotina

from datetime import date, time
import sys

responsaveis = {}
rotinas = {}  # chave: id da criança -> lista[Rotina]


# =========================
# Funções auxiliares
# =========================
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
                    sys.stdout.write('\x1b[1A')
                    sys.stdout.write('\x1b[2K')
                    sys.stdout.flush()
                print(f"Valor deve ser >= {min_val}.")
                continue
            if max_val is not None and valor_int > max_val:
                if sys.stdout.isatty():
                    sys.stdout.write('\x1b[1A')
                    sys.stdout.write('\x1b[2K')
                    sys.stdout.flush()
                print(f"Valor deve ser <= {max_val}.")
                continue
            return valor_int
        except ValueError:
            if sys.stdout.isatty():
                sys.stdout.write('\x1b[1A')
                sys.stdout.write('\x1b[2K')
                sys.stdout.flush()
            print("Erro. Digite as informações corretamente.")


def input_data_opcional(mensagem: str) -> date | None:
    """
    Formato esperado: DD/MM/AAAA
    Enter vazio => None
    """
    valor = input(mensagem).strip()
    if not valor:
        return None

    try:
        dia, mes, ano = map(int, valor.split("/"))
        return date(ano, mes, dia)
    except Exception:
        print("Data inválida. Use o formato DD/MM/AAAA.")
        return None


def input_time_opcional(mensagem: str) -> time | None:
    """
    Formato esperado: HH:MM
    Enter vazio => None
    """
    valor = input(mensagem).strip()
    if not valor:
        return None

    try:
        hora, minuto = map(int, valor.split(":"))
        return time(hour=hora, minute=minuto)
    except Exception:
        print("Horário inválido. Use o formato HH:MM.")
        return None


def input_nao_vazio(mensagem: str) -> str:
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("Campo obrigatório. Tente novamente.")


def buscar_crianca_por_nome(resp_cpf: str, nome_crianca: str):
    """
    Procura a criança pelo nome dentro do responsável informado.
    Retorna (crianca, responsavel) ou (None, None)
    """
    resp = responsaveis.get(resp_cpf)
    if not resp:
        return None, None

    nome_normalizado = nome_crianca.strip().lower()
    for c in resp.listar_criancas():
        if c.nome.strip().lower() == nome_normalizado:
            return c, resp

    return None, resp


# =========================
# Cadastro de responsável/criança (seu código)
# =========================
def criar_responsavel():
    print("\n=== Cadastro de Responsável ===")
    nome = input("Nome: ")
    idade = input_int("Idade do responsável", min_val=18)
    cpf = input("CPF: ")
    email = input("Email: ").strip()
    telefone = input("Telefone: ").strip()
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
            print(f"Erro ao cadastrar responsável: {e}\n")
    except Exception as e:
        print(f"Erro ao cadastrar responsável: {e}\n")


def adicionar_crianca():
    print("\n=== Adicionar Criança ===")
    resp_cpf = input("CPF do responsável: ")
    resp = responsaveis.get(resp_cpf)
    if not resp:
        print("Responsável não encontrado.\n")
        return

    nome = input("Nome da criança: ")
    idade = input_int("Idade da criança", min_val=0, max_val=17)
    email = input("Email (opcional): ") or None
    telefone = input("Telefone: ").strip()
    nivel = input("Nível de suporte (baixo/moderado/alto): ").lower()

    try:
        crianca = Crianca(
            nome=nome,
            idade=idade,
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



def selecionar_crianca_por_responsavel():
    resp_cpf = input_nao_vazio("CPF do responsável: ")
    nome_crianca = input_nao_vazio("Nome da criança: ")

    crianca, resp = buscar_crianca_por_nome(resp_cpf, nome_crianca)
    if not resp:
        print("Responsável não encontrado.\n")
        return None, None

    if not crianca:
        print("Criança não encontrada para este responsável.\n")
        return None, resp

    return crianca, resp


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


# =========================
# Funções de Rotina (NOVO)
# =========================
def mostrar_sugestoes_rotina():
    print("\nSugestões de rotinas fixas:")
    for idx, sugestao in enumerate(Rotina.sugerir_modelos_fixos(), start=1):
        print(f"{idx}. {sugestao}")
    print()


def escolher_tipo_recorrencia() -> TipoRecorrenciaRotina:
    print("\nTipo de recorrência da rotina:")
    print("1. Data única")
    print("2. Todos os dias")
    print("3. Dias específicos")

    while True:
        op = input("Escolha uma opção: ").strip()
        if op == "1":
            return TipoRecorrenciaRotina.DATA_UNICA
        elif op == "2":
            return TipoRecorrenciaRotina.TODOS_OS_DIAS
        elif op == "3":
            return TipoRecorrenciaRotina.DIAS_ESPECIFICOS
        print("Opção inválida.")


def escolher_dias_semana() -> list[DiaSemana]:
    print("\nInforme os dias da semana (separados por vírgula).")
    print("Opções válidas: SEG, TER, QUA, QUI, SEX, SAB, DOM")
    while True:
        entrada = input("Dias: ").strip().upper()
        if not entrada:
            print("Informe ao menos um dia.")
            continue

        partes = [p.strip() for p in entrada.split(",") if p.strip()]
        dias = []
        erro = False

        mapa = {
            "SEG": DiaSemana.SEG,
            "TER": DiaSemana.TER,
            "QUA": DiaSemana.QUA,
            "QUI": DiaSemana.QUI,
            "SEX": DiaSemana.SEX,
            "SAB": DiaSemana.SAB,
            "DOM": DiaSemana.DOM,
        }

        for p in partes:
            if p not in mapa:
                print(f"Dia inválido: {p}")
                erro = True
                break
            dias.append(mapa[p])

        if erro:
            continue

        # remove duplicados preservando ordem
        dias_unicos = []
        vistos = set()
        for d in dias:
            if d.value not in vistos:
                vistos.add(d.value)
                dias_unicos.append(d)

        return dias_unicos


def cadastrar_itens_da_rotina(rotina: Rotina):
    print("\n=== Cadastro de Itens da Rotina ===")
    print("Cadastre os itens um por um. Digite ENTER no nome para encerrar.\n")

    while True:
        nome = input("Nome do item (ENTER para finalizar): ").strip()
        if not nome:
            break

        descricao = input("Descrição (opcional): ").strip() or None

        horario_inicio = None
        horario_fim = None

        while True:
            horario_inicio = input_time_opcional("Horário de início (HH:MM, opcional): ")
            horario_fim = input_time_opcional("Horário de fim (HH:MM, opcional): ")

            try:
                item = rotina.cadastrar_item_automatico(
                    nome=nome,
                    descricao=descricao,
                    horario_inicio=horario_inicio,
                    horario_fim=horario_fim,
                )
                print(f"Item '{item.nome}' cadastrado com ordem {item.ordem}.\n")
                break
            except Exception as e:
                print(f"Erro ao cadastrar item: {e}")
                print("Tente informar os horários novamente.\n")

    if not rotina.itens:
        print("Atenção: rotina criada sem itens.")


def cadastrar_rotina():
    print("\n=== Cadastrar Rotina ===")

    # localizar criança sem usar CPF
    crianca, resp = selecionar_crianca_por_responsavel()

    if not crianca:
        print("Cadastre a criança antes de criar rotina.\n")
        return

    print(f"Criança encontrada: {crianca.nome} (responsável: {resp.nome})")

    # sugestões
    ver_sugestoes = input("Deseja ver sugestões de rotina fixa? (s/n): ").strip().lower()
    if ver_sugestoes == "s":
        mostrar_sugestoes_rotina()

    nome_rotina = input_nao_vazio("Nome da rotina: ")
    descricao = input("Descrição (opcional): ").strip() or None

    tipo = escolher_tipo_recorrencia()

    data_agendada = None
    dias_semana = []

    if tipo == TipoRecorrenciaRotina.DATA_UNICA:
        while True:
            data_agendada = input_data_opcional("Data agendada (DD/MM/AAAA): ")
            if data_agendada is not None:
                break
            print("A data é obrigatória para rotina de data única.")

    elif tipo == TipoRecorrenciaRotina.DIAS_ESPECIFICOS:
        dias_semana = escolher_dias_semana()

    try:
        rotina = Rotina(
            nome=nome_rotina,
            tipo_recorrencia=tipo,
            crianca_id=crianca.id,
            data_agendada=data_agendada,
            dias_semana=dias_semana,
            descricao=descricao,
        )

        cadastrar_itens_da_rotina(rotina)

        # salvar em memória (usuário pode ter várias rotinas)
        rotinas.setdefault(crianca.id, []).append(rotina)

        print(f"\nRotina '{rotina.nome}' cadastrada com sucesso para {crianca.nome}!")
        print(f"Total de itens: {len(rotina.itens)}\n")

    except Exception as e:
        print(f"Erro ao cadastrar rotina: {e}\n")


def listar_rotinas_da_crianca():
    print("\n=== Listar Rotinas da Criança ===")
    crianca, _ = selecionar_crianca_por_responsavel()
    if not crianca:
        return

    lista = rotinas.get(crianca.id, [])
    if not lista:
        print(f"{crianca.nome} ainda não possui rotinas cadastradas.\n")
        return

    print(f"\nRotinas de {crianca.nome}:")
    for i, rotina in enumerate(lista, start=1):
        print(f"{i}. {rotina.nome} | recorrência: {rotina.tipo_recorrencia.value} | itens: {len(rotina.itens)}")
    print()


def selecionar_rotina_da_crianca(crianca_id: str) -> Rotina | None:
    lista = rotinas.get(crianca_id, [])
    if not lista:
        return None

    print("\nRotinas cadastradas:")
    for i, rotina in enumerate(lista, start=1):
        print(f"{i}. {rotina.nome} ({rotina.tipo_recorrencia.value})")

    idx = input_int("Escolha o número da rotina", min_val=1, max_val=len(lista))
    return lista[idx - 1]


def adicionar_item_em_rotina():
    print("\n=== Adicionar Item em Rotina ===")
    crianca, _ = selecionar_crianca_por_responsavel()
    if not crianca:
        return

    rotina = selecionar_rotina_da_crianca(crianca.id)
    if not rotina:
        print("Nenhuma rotina encontrada para essa criança.\n")
        return

    nome = input_nao_vazio("Nome do item: ")
    descricao = input("Descrição (opcional): ").strip() or None

    while True:
        hi = input_time_opcional("Horário de início (HH:MM, opcional): ")
        hf = input_time_opcional("Horário de fim (HH:MM, opcional): ")
        try:
            item = rotina.cadastrar_item_automatico(
                nome=nome,
                descricao=descricao,
                horario_inicio=hi,
                horario_fim=hf,
            )
            print(f"Item '{item.nome}' adicionado à rotina '{rotina.nome}' com ordem {item.ordem}.\n")
            break
        except Exception as e:
            print(f"Erro ao adicionar item: {e}\n")


def visualizar_itens_da_rotina():
    print("\n=== Visualizar Itens da Rotina ===")
    crianca, _ = selecionar_crianca_por_responsavel()
    if not crianca:
        return

    rotina = selecionar_rotina_da_crianca(crianca.id)
    if not rotina:
        print("Nenhuma rotina encontrada.\n")
        return

    if not rotina.itens:
        print("Essa rotina não possui itens.\n")
        return

    print(f"\nItens da rotina '{rotina.nome}':")
    for item in rotina.itens:
        inicio = item.horario_inicio.strftime("%H:%M") if item.horario_inicio else "--:--"
        fim = item.horario_fim.strftime("%H:%M") if item.horario_fim else "--:--"
        print(f"[{item.ordem}] {item.nome} | início: {inicio} | fim: {fim}")
        if item.descricao:
            print(f"    descrição: {item.descricao}")
    print()


def editar_ordem_item_da_rotina():
    print("\n=== Editar Ordem de Item da Rotina ===")
    crianca, _ = selecionar_crianca_por_responsavel()
    if not crianca:
        return

    rotina = selecionar_rotina_da_crianca(crianca.id)
    if not rotina:
        print("Nenhuma rotina encontrada.\n")
        return

    if not rotina.itens:
        print("A rotina não possui itens para reordenar.\n")
        return

    print(f"\nItens atuais da rotina '{rotina.nome}':")
    for item in rotina.itens:
        print(f"- ID: {item.id} | ordem: {item.ordem} | nome: {item.nome}")

    item_id = input_nao_vazio("Digite o ID do item que deseja mover: ")
    nova_ordem = input_int("Nova ordem", min_val=1)

    try:
        rotina.editar_ordem_item(item_id, nova_ordem)
        print("Ordem atualizada com sucesso! Nova sequência:")
        for item in rotina.itens:
            print(f"  {item.ordem}. {item.nome}")
        print()
    except Exception as e:
        print(f"Erro ao editar ordem: {e}\n")


# =========================
# Menu principal
# =========================
def menu():
    while True:
        print("=== Sistema Teapoio ===")
        print("1. Cadastrar responsável")

        # só mostra opções relacionadas quando houver responsável
        if responsaveis:
            print("2. Adicionar criança")
            print("3. Listar crianças")
            print("4. Cadastrar rotina")
            print("5. Listar rotinas da criança")
            print("6. Adicionar item em rotina")
            print("7. Visualizar itens da rotina")
            print("8. Editar ordem de item da rotina")

        print("0. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            criar_responsavel()
        elif opcao == "2" and responsaveis:
            adicionar_crianca()
        elif opcao == "3" and responsaveis:
            listar_criancas()
        elif opcao == "4" and responsaveis:
            cadastrar_rotina()
        elif opcao == "5" and responsaveis:
            listar_rotinas_da_crianca()
        elif opcao == "6" and responsaveis:
            adicionar_item_em_rotina()
        elif opcao == "7" and responsaveis:
            visualizar_itens_da_rotina()
        elif opcao == "8" and responsaveis:
            editar_ordem_item_da_rotina()
        elif opcao == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida.\n")