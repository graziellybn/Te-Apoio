import sys
from datetime import date

from teapoio.domain.models.responsavel import Responsavel
from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.perfil_sensorial import PerfilSensorial
from teapoio.domain.events.eventos import Evento
from teapoio.infrastructure.persistence import repository


# ══════════════════════════════════════════════════════════
# Helpers de entrada
# ══════════════════════════════════════════════════════════

def _limpar_linha():
    if sys.stdout.isatty():
        sys.stdout.write('\x1b[1A\x1b[2K')
        sys.stdout.flush()


def separador(char="─", largura=50):
    print(char * largura)


# ══════════════════════════════════════════════════════════
# Cadastro de Responsável
# ══════════════════════════════════════════════════════════

def _coletar_dados_responsavel() -> Responsavel | None:
    """
    Coleta dados do responsável passo a passo.
    Retorna Responsavel ou None se o usuário quiser voltar ao menu inicial.
    """
    campos = [
        ("nome",           "Nome completo: "),
        ("email",          "E-mail: "),
        ("telefone",       "Telefone: "),
        ("tipo",           "Tipo de responsável (Mãe/Pai/Outro): "),
        ("endereco",       "Endereço (opcional, Enter para pular): "),
        ("quant_criancas", "Quantidade de crianças a cadastrar (1-3): "),
    ]

    dados: dict = {}
    idx = 0

    separador()
    print("=== Cadastro de Responsável ===")
    print("(Digite 'voltar' para retornar ao menu inicial)")
    separador()

    while idx < len(campos):
        chave, mensagem = campos[idx]

        if chave == "quant_criancas":
            valor = input(mensagem).strip()
            if valor.lower() == "voltar":
                if idx == 0:
                    return None
                idx -= 1
                continue
            if valor not in ("1", "2", "3"):
                print("Escolha 1, 2 ou 3.")
                continue
            dados[chave] = int(valor)

        elif chave == "endereco":
            valor = input(mensagem).strip()
            if valor.lower() == "voltar":
                if idx == 0:
                    return None
                idx -= 1
                continue
            dados[chave] = valor or None

        else:
            valor = input(mensagem).strip()
            if valor.lower() == "voltar":
                if idx == 0:
                    return None
                idx -= 1
                continue
            if not valor:
                print("Campo obrigatório.")
                continue
            dados[chave] = valor

        idx += 1

    resp = Responsavel(
        nome=dados["nome"],
        email=dados["email"],
        telefone=dados["telefone"],
        tipo_responsavel=dados["tipo"],
        endereco=dados.get("endereco"),
        quant_criancas=dados["quant_criancas"],
    )
    return resp


# ══════════════════════════════════════════════════════════
# Cadastro de Crianças
# ══════════════════════════════════════════════════════════

def _coletar_dados_crianca(numero: int, total: int, responsavel_id: str) -> Crianca | None:
    """
    Coleta dados de uma criança.
    Retorna Crianca ou None se usuário quiser voltar.
    """
    campos = [
        ("nome",            f"Nome da criança {numero}/{total}: "),
        ("data_nascimento", "Data de nascimento (DD/MM/AAAA, Enter para pular): "),
        ("nivel_suporte",   "Nível de suporte (baixo/moderado/alto): "),
    ]

    dados: dict = {}
    idx = 0

    separador()
    print(f"=== Cadastro de Criança {numero}/{total} ===")
    print("(Digite 'voltar' para retornar à etapa anterior)")
    separador()

    while idx < len(campos):
        chave, mensagem = campos[idx]

        if chave == "data_nascimento":
            valor = input(mensagem).strip()
            if valor.lower() == "voltar":
                if idx == 0:
                    return None
                idx -= 1
                continue
            if valor:
                try:
                    dia, mes, ano = map(int, valor.split("/"))
                    dados[chave] = date(ano, mes, dia)
                except Exception:
                    print("Data inválida. Use DD/MM/AAAA.")
                    continue
            else:
                dados[chave] = None

        elif chave == "nivel_suporte":
            valor = input(mensagem).strip().lower()
            if valor == "voltar":
                if idx == 0:
                    return None
                idx -= 1
                continue
            if valor not in ("baixo", "moderado", "alto"):
                print("Nível inválido. Use: baixo, moderado ou alto.")
                continue
            dados[chave] = valor

        else:
            valor = input(mensagem).strip()
            if valor.lower() == "voltar":
                if idx == 0:
                    return None
                idx -= 1
                continue
            if not valor:
                print("Campo obrigatório.")
                continue
            dados[chave] = valor

        idx += 1

    crianca = Crianca(
        nome=dados["nome"],
        nivel_suporte=dados["nivel_suporte"],
        responsavel_id=responsavel_id,
        data_nascimento=dados.get("data_nascimento"),
    )
    return crianca


# ══════════════════════════════════════════════════════════
# Fluxo de Cadastro Completo
# ══════════════════════════════════════════════════════════

def fluxo_cadastro() -> tuple | None:
    """
    Conduz o fluxo completo de cadastro: responsável → crianças.
    Retorna (responsavel, criancas) ou None para voltar ao menu.
    """
    resp = _coletar_dados_responsavel()
    if resp is None:
        return None

    repository.salvar_responsavel(resp)
    separador()
    print("\u2714 Responsável cadastrado com sucesso!")
    print(f"  Nome : {resp.nome}")
    print(f"  ID   : {resp.id}")
    separador()

    total = resp.quant_criancas
    criancas: list[Crianca] = []
    i = 0

    while i < total:
        crianca = _coletar_dados_crianca(i + 1, total, resp.id)
        if crianca is None:
            if i == 0:
                novo_resp = _coletar_dados_responsavel()
                if novo_resp is None:
                    return None
                repository.salvar_responsavel(novo_resp)
                resp = novo_resp
                total = resp.quant_criancas
                criancas = []
                continue
            else:
                i -= 1
                criancas.pop()
                continue

        repository.salvar_crianca(crianca)
        resp.adicionar_crianca(crianca)
        criancas.append(crianca)

        separador()
        print("\u2714 Criança cadastrada com sucesso!")
        print(f"  Nome : {crianca.nome}")
        print(f"  ID   : {crianca.id}")
        separador()
        i += 1

    print("\nTodos os cadastros concluídos. Entrando no sistema...\n")
    return resp, criancas


# ══════════════════════════════════════════════════════════
# Tela do Sistema Principal
# ══════════════════════════════════════════════════════════

def tela_sistema(resp: Responsavel, criancas: list[Crianca]):
    while True:
        separador("═")
        print(f"  SISTEMA TE APOIO  —  Olá, {resp.nome}!")
        separador("═")
        print("\nCrianças cadastradas:")
        for c in criancas:
            dn = c.data_nascimento.strftime("%d/%m/%Y") if c.data_nascimento else "—"
            print(f"  [{c.id[:8]}]  {c.nome}  |  Nasc.: {dn}  |  Suporte: {c.nivel_suporte}")

        print("\nO que deseja fazer?")
        print("  1. Configurações de Perfil")
        print("  2. Calendário")
        print("  0. Sair")
        separador()

        op = input("Opção: ").strip()
        if op == "1":
            criancas = tela_configuracoes(resp, criancas)
        elif op == "2":
            tela_calendario(criancas)
        elif op == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida.\n")


# ══════════════════════════════════════════════════════════
# Configurações de Perfil
# ══════════════════════════════════════════════════════════

def _exibir_dados_cadastrados(resp: Responsavel, criancas: list[Crianca]):
    separador()
    print("=== Dados Cadastrados ===")
    separador()
    print(f"Responsável: {resp.nome}  [ID: {resp.id[:8]}]")
    print(f"  E-mail   : {resp.email or '—'}")
    print(f"  Telefone : {resp.telefone or '—'}")
    print(f"  Tipo     : {resp.tipo_responsavel}")
    print(f"  Endereço : {resp.endereco or '—'}")
    print()
    print("Crianças:")
    for c in criancas:
        dn = c.data_nascimento.strftime("%d/%m/%Y") if c.data_nascimento else "—"
        print(f"  [{c.id[:8]}] {c.nome}  |  Nasc.: {dn}  |  Suporte: {c.nivel_suporte}")
        if c.perfil_sensorial:
            ps = c.perfil_sensorial
            print("    Perfil Sensorial:")
            print(f"      Tátil    — sensibilidades: {ps.tatil_sensibilidades or '—'}  |  preferências: {ps.tatil_preferencias or '—'}")
            print(f"      Auditivo — sensibilidades: {ps.auditivo_sensibilidades or '—'}  |  preferências: {ps.auditivo_preferencias or '—'}")
            print(f"      Visual   — sensibilidades: {ps.visual_sensibilidades or '—'}  |  preferências: {ps.visual_preferencias or '—'}")
    separador()


def tela_configuracoes(resp: Responsavel, criancas: list[Crianca]) -> list[Crianca]:
    while True:
        _exibir_dados_cadastrados(resp, criancas)
        print("Configurações de Perfil:")
        print("  1. Adicionar/Atualizar Perfil Sensorial da Criança")
        print("  2. Editar Informações")
        print("  3. Excluir Criança")
        print("  0. Voltar")
        separador()

        op = input("Opção: ").strip()
        if op == "1":
            criancas = _adicionar_perfil_sensorial(criancas)
        elif op == "2":
            resp, criancas = _editar_informacoes(resp, criancas)
        elif op == "3":
            criancas = _excluir_crianca(resp, criancas)
        elif op == "0":
            break
        else:
            print("Opção inválida.\n")

    return criancas


def _buscar_crianca_por_id_parcial(criancas: list[Crianca], parcial: str) -> Crianca | None:
    parcial = parcial.lower()
    for c in criancas:
        if c.id.lower().startswith(parcial) or c.id[:8].lower().startswith(parcial):
            return c
    return None


def _adicionar_perfil_sensorial(criancas: list[Crianca]) -> list[Crianca]:
    if not criancas:
        print("Nenhuma criança cadastrada.\n")
        return criancas

    print("\n=== Adicionar/Atualizar Perfil Sensorial ===")
    print("IDs disponíveis:")
    for c in criancas:
        print(f"  [{c.id[:8]}] {c.nome}")

    id_parcial = input("Digite o ID (ou parte) da criança: ").strip().lower()
    crianca = _buscar_crianca_por_id_parcial(criancas, id_parcial)
    if not crianca:
        print("Criança não encontrada.\n")
        return criancas

    print(f"\nPreenchendo perfil sensorial para: {crianca.nome}")
    print("(Enter para manter o valor atual)")

    ps = crianca.perfil_sensorial or PerfilSensorial()

    resp_ts = input(f"Tátil — sensibilidades [{ps.tatil_sensibilidades or ''}]: ").strip()
    if resp_ts:
        ps.tatil_sensibilidades = resp_ts
    resp_tp = input(f"Tátil — preferências [{ps.tatil_preferencias or ''}]: ").strip()
    if resp_tp:
        ps.tatil_preferencias = resp_tp
    resp_as = input(f"Auditivo — sensibilidades [{ps.auditivo_sensibilidades or ''}]: ").strip()
    if resp_as:
        ps.auditivo_sensibilidades = resp_as
    resp_ap = input(f"Auditivo — preferências [{ps.auditivo_preferencias or ''}]: ").strip()
    if resp_ap:
        ps.auditivo_preferencias = resp_ap
    resp_vs = input(f"Visual — sensibilidades [{ps.visual_sensibilidades or ''}]: ").strip()
    if resp_vs:
        ps.visual_sensibilidades = resp_vs
    resp_vp = input(f"Visual — preferências [{ps.visual_preferencias or ''}]: ").strip()
    if resp_vp:
        ps.visual_preferencias = resp_vp

    crianca.perfil_sensorial = ps
    repository.salvar_crianca(crianca)
    print(f"\u2714 Perfil sensorial de {crianca.nome} atualizado.\n")
    return criancas


def _editar_informacoes(resp: Responsavel, criancas: list[Crianca]) -> tuple:
    print("\n=== Editar Informações ===")
    print("  1. Editar dados do responsável")
    print("  2. Editar dados de uma criança")
    print("  0. Voltar")

    op = input("Opção: ").strip()
    if op == "1":
        resp = _editar_responsavel(resp)
    elif op == "2":
        criancas = _editar_crianca(criancas)
    return resp, criancas


def _editar_responsavel(resp: Responsavel) -> Responsavel:
    print(f"\nEditando dados de {resp.nome}")
    print("(Enter para manter o valor atual)")

    novo_nome = input(f"Nome [{resp.nome}]: ").strip() or resp.nome
    novo_email = input(f"E-mail [{resp.email or ''}]: ").strip() or resp.email
    novo_tel = input(f"Telefone [{resp.telefone or ''}]: ").strip() or resp.telefone
    novo_tipo = input(f"Tipo [{resp.tipo_responsavel}]: ").strip() or resp.tipo_responsavel
    novo_end = input(f"Endereço [{resp.endereco or ''}]: ").strip()

    resp.nome = novo_nome
    resp.email = novo_email
    resp.telefone = novo_tel
    resp.tipo_responsavel = novo_tipo
    resp.endereco = novo_end or resp.endereco or None

    repository.salvar_responsavel(resp)
    print("\u2714 Dados do responsável atualizados.\n")
    return resp


def _editar_crianca(criancas: list[Crianca]) -> list[Crianca]:
    if not criancas:
        print("Nenhuma criança cadastrada.\n")
        return criancas

    print("\nIDs disponíveis:")
    for c in criancas:
        print(f"  [{c.id[:8]}] {c.nome}")

    id_parcial = input("Digite o ID (ou parte) da criança: ").strip().lower()
    crianca = _buscar_crianca_por_id_parcial(criancas, id_parcial)
    if not crianca:
        print("Criança não encontrada.\n")
        return criancas

    print(f"\nEditando dados de {crianca.nome}")
    print("(Enter para manter o valor atual)")

    novo_nome = input(f"Nome [{crianca.nome}]: ").strip() or crianca.nome

    dn_str = crianca.data_nascimento.strftime("%d/%m/%Y") if crianca.data_nascimento else ""
    nova_dn_str = input(f"Data de nascimento [{dn_str}]: ").strip()
    if nova_dn_str:
        try:
            dia, mes, ano = map(int, nova_dn_str.split("/"))
            crianca.data_nascimento = date(ano, mes, dia)
        except Exception:
            print("Data inválida, mantendo anterior.")

    novo_nivel = input(f"Nível de suporte [{crianca.nivel_suporte}] (baixo/moderado/alto): ").strip().lower()
    if novo_nivel in ("baixo", "moderado", "alto"):
        crianca.nivel_suporte = novo_nivel
    elif novo_nivel:
        print("Nível inválido, mantendo anterior.")

    crianca.nome = novo_nome
    repository.salvar_crianca(crianca)
    print(f"\u2714 Dados de {crianca.nome} atualizados.\n")
    return criancas


def _excluir_crianca(resp: Responsavel, criancas: list[Crianca]) -> list[Crianca]:
    if not criancas:
        print("Nenhuma criança cadastrada.\n")
        return criancas

    print("\n=== Excluir Criança ===")
    print("IDs disponíveis:")
    for c in criancas:
        print(f"  [{c.id[:8]}] {c.nome}")

    id_parcial = input("Digite o ID (ou parte) da criança: ").strip().lower()
    crianca = _buscar_crianca_por_id_parcial(criancas, id_parcial)
    if not crianca:
        print("Criança não encontrada.\n")
        return criancas

    confirmacao = input(f"Confirmar exclusão de '{crianca.nome}'? (s/n): ").strip().lower()
    if confirmacao == "s":
        repository.excluir_crianca(crianca.id)
        criancas = [c for c in criancas if c.id != crianca.id]
        try:
            resp.remover_crianca_por_id(crianca.id)
        except Exception:
            pass
        print(f"\u2714 Criança {crianca.nome} excluída.\n")
    else:
        print("Exclusão cancelada.\n")

    return criancas


# ══════════════════════════════════════════════════════════
# Calendário
# ══════════════════════════════════════════════════════════

def tela_calendario(criancas: list[Crianca]):
    eventos = repository.carregar_eventos()

    while True:
        separador()
        print("=== Calendário ===")
        separador()

        ids_criancas = {c.id for c in criancas}
        eventos_filtrados = [e for e in eventos if e.crianca_id in ids_criancas]

        if eventos_filtrados:
            print("Eventos agendados:")
            for e in sorted(eventos_filtrados, key=lambda x: x.data):
                nome_crianca = next((c.nome for c in criancas if c.id == e.crianca_id), e.crianca_id[:8])
                linha = f"  [{e.id[:8]}] {e.data.strftime('%d/%m/%Y')} — {e.titulo}  |  {nome_crianca}"
                if e.descricao:
                    linha += f"  |  {e.descricao}"
                print(linha)
        else:
            print("Nenhum evento cadastrado.")

        print()
        print("  1. Adicionar evento")
        print("  2. Excluir evento")
        print("  0. Voltar")
        separador()

        op = input("Opção: ").strip()
        if op == "1":
            novo = _adicionar_evento(criancas)
            if novo:
                eventos.append(novo)
        elif op == "2":
            eventos = _excluir_evento(eventos, criancas)
        elif op == "0":
            break
        else:
            print("Opção inválida.\n")


def _adicionar_evento(criancas: list[Crianca]) -> Evento | None:
    print("\n=== Adicionar Evento ===")
    if not criancas:
        print("Nenhuma criança cadastrada.\n")
        return None

    print("Crianças disponíveis:")
    for c in criancas:
        print(f"  [{c.id[:8]}] {c.nome}")

    id_parcial = input("ID da criança: ").strip().lower()
    crianca = _buscar_crianca_por_id_parcial(criancas, id_parcial)
    if not crianca:
        print("Criança não encontrada.\n")
        return None

    titulo = input("Título do evento: ").strip()
    if not titulo:
        print("Título obrigatório.\n")
        return None

    data_evento = None
    while data_evento is None:
        data_str = input("Data do evento (DD/MM/AAAA): ").strip()
        try:
            dia, mes, ano = map(int, data_str.split("/"))
            data_evento = date(ano, mes, dia)
        except Exception:
            print("Data inválida. Use DD/MM/AAAA.")

    descricao = input("Descrição (opcional): ").strip()

    evento = Evento(
        titulo=titulo,
        crianca_id=crianca.id,
        data=data_evento,
        descricao=descricao,
    )
    repository.salvar_evento(evento)
    print(f"\u2714 Evento '{titulo}' adicionado.\n")
    return evento


def _excluir_evento(eventos: list[Evento], criancas: list[Crianca]) -> list[Evento]:
    ids_criancas = {c.id for c in criancas}
    eventos_filtrados = [e for e in eventos if e.crianca_id in ids_criancas]

    if not eventos_filtrados:
        print("Nenhum evento para excluir.\n")
        return eventos

    print("\nEventos disponíveis:")
    for e in eventos_filtrados:
        print(f"  [{e.id[:8]}] {e.data.strftime('%d/%m/%Y')} — {e.titulo}")

    id_parcial = input("ID do evento: ").strip().lower()
    evento = next(
        (e for e in eventos_filtrados
         if e.id.lower().startswith(id_parcial) or e.id[:8].lower().startswith(id_parcial)),
        None
    )
    if not evento:
        print("Evento não encontrado.\n")
        return eventos

    confirmacao = input(f"Confirmar exclusão de '{evento.titulo}'? (s/n): ").strip().lower()
    if confirmacao == "s":
        repository.excluir_evento(evento.id)
        eventos = [e for e in eventos if e.id != evento.id]
        print("\u2714 Evento excluído.\n")
    else:
        print("Cancelado.\n")

    return eventos


# ══════════════════════════════════════════════════════════
# Menu Inicial
# ══════════════════════════════════════════════════════════

def menu():
    while True:
        separador("═")
        print("       TE APOIO — Sistema de Gestão       ")
        separador("═")
        print("  1. Cadastro")
        print("  2. Sair")
        separador()

        op = input("Opção: ").strip()

        if op == "1":
            resultado = fluxo_cadastro()
            if resultado is not None:
                resp, criancas = resultado
                tela_sistema(resp, criancas)

        elif op == "2":
            print("Até logo!")
            break
        else:
            print("Opção inválida.\n")
