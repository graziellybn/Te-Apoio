from __future__ import annotations

import calendar
from collections import Counter
from datetime import date, datetime
from datetime import timedelta
import os
from typing import Any

from flask import Flask, Response, flash, jsonify, redirect, render_template, request, session, url_for

from teapoio.application.services.servico_cadastro import ServicoCadastro
from teapoio.application.services.servico_monitoramento import ServicoMonitoramento
from teapoio.application.services.servico_perfil import ServicoPerfil
from teapoio.application.services.servico_relatorios import ServicoRelatorios
from teapoio.application.services.servico_rotinas import ServicoRotinas
from teapoio.domain.models.Perfil import Perfil
from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.item_rotina import ItemRotina
from teapoio.domain.models.responsavel import Responsavel
from teapoio.domain.models.rotina import Rotina, obter_sugestoes_tea
from teapoio.infrastructure.persistence.Relatorio import RepositorioRelatorio


def _erro(mensagem: str, status_code: int):
    return jsonify({"erro": mensagem}), status_code


def _normalizar_lista_strings(payload: dict[str, Any], campo: str) -> list[str]:
    valor = payload.get(campo, [])
    if valor is None:
        return []
    if not isinstance(valor, list):
        raise ValueError(f"Campo '{campo}' deve ser uma lista de strings.")

    lista: list[str] = []
    for item in valor:
        if not isinstance(item, str):
            raise ValueError(f"Campo '{campo}' deve conter apenas strings.")
        texto = item.strip()
        if texto:
            lista.append(texto)
    return lista


def _parse_data(valor: str | None, padrao: date | None = None) -> date:
    if valor is None or not valor.strip():
        return padrao or date.today()

    texto = valor.strip()
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue

    raise ValueError("Data invalida. Use AAAA-MM-DD ou DD/MM/AAAA.")


def _normalizar_lista_texto_livre(valor: str | None) -> list[str]:
    if valor is None:
        return []

    texto = str(valor).replace(";", ",").replace("\n", ",")
    return [item.strip() for item in texto.split(",") if item.strip()]


def _normalizar_tags_texto_livre(valor: str | None) -> list[str]:
    tags_brutas = _normalizar_lista_texto_livre(valor)
    tags: list[str] = []
    vistos: set[str] = set()
    for item in tags_brutas:
        for parte in _normalizar_tags_texto_livre(item):
            tag = parte.lstrip("#").strip()
            if not tag:
                continue
            chave = tag.casefold()
            if chave in vistos:
                continue
            vistos.add(chave)
            tags.append(tag)
    return tags


TAGS_PREDEFINIDAS = [
    "higiene",
    "alimentacao",
    "escola",
    "lazer",
    "sono",
    "social",
    "terapia",
    "sensorial",
]


def _normalizar_tags_form(form_data: Any, campo: str = "tags") -> list[str]:
    tags_brutas: list[str] = []

    getlist = getattr(form_data, "getlist", None)
    if callable(getlist):
        tags_brutas = [str(item) for item in getlist(campo) if str(item).strip()]

    if not tags_brutas:
        valor_unico = ""
        getter = getattr(form_data, "get", None)
        if callable(getter):
            valor_unico = str(getter(campo, "") or "")
        return _normalizar_tags_texto_livre(valor_unico)

    tags: list[str] = []
    vistos: set[str] = set()
    for item in tags_brutas:
        partes = _normalizar_lista_texto_livre(item)
        if not partes:
            partes = [item]
        for parte in partes:
            tag = parte.lstrip("#").strip()
            if not tag:
                continue
            chave = tag.casefold()
            if chave in vistos:
                continue
            vistos.add(chave)
            tags.append(tag)
    return tags


def _mes_nome_pt_br(mes: int) -> str:
    nomes = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Marco",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro",
    }
    return nomes.get(mes, "Mes")


def _dados_calendario(mes: int, ano: int, data_selecionada: date) -> dict[str, Any]:
    hoje = date.today()
    calendario_mes = calendar.Calendar(firstweekday=6)
    semanas_brutas = calendario_mes.monthdatescalendar(ano, mes)

    semanas: list[list[dict[str, Any]]] = []
    for semana in semanas_brutas:
        linha: list[dict[str, Any]] = []
        for dia in semana:
            linha.append(
                {
                    "dia": dia.day,
                    "data_iso": dia.isoformat(),
                    "mes_atual": dia.month == mes,
                    "hoje": dia == hoje,
                    "selecionado": dia == data_selecionada,
                    "bloqueado": dia > hoje,
                }
            )
        semanas.append(linha)

    mes_anterior = 12 if mes == 1 else mes - 1
    ano_anterior = ano - 1 if mes == 1 else ano
    mes_proximo = 1 if mes == 12 else mes + 1
    ano_proximo = ano + 1 if mes == 12 else ano

    return {
        "mes": mes,
        "ano": ano,
        "mes_nome": _mes_nome_pt_br(mes),
        "semanas": semanas,
        "mes_anterior": mes_anterior,
        "ano_anterior": ano_anterior,
        "mes_proximo": mes_proximo,
        "ano_proximo": ano_proximo,
        "permite_anterior": ano_anterior >= hoje.year,
        "permite_proximo": ano_proximo <= hoje.year,
    }


def _resumo_periodo_rotinas(
    rotinas: list[Rotina],
    id_crianca: str,
    data_base: date,
    periodo: str,
) -> dict[str, Any]:
    if periodo == "semana":
        inicio = data_base - timedelta(days=data_base.weekday())
        fim = inicio + timedelta(days=6)
        titulo = "Semana"
    else:
        dia_final = calendar.monthrange(data_base.year, data_base.month)[1]
        inicio = date(data_base.year, data_base.month, 1)
        fim = date(data_base.year, data_base.month, dia_final)
        titulo = "Mes"

    total = 0
    concluidos = 0
    pendentes = 0
    nao_realizados = 0

    for rotina in rotinas:
        if rotina.id_crianca != id_crianca:
            continue
        if not (inicio <= rotina.data_referencia <= fim):
            continue

        for item in rotina.itens:
            total += 1
            if item.status == ItemRotina.STATUS_CONCLUIDO:
                concluidos += 1
            elif item.status == ItemRotina.STATUS_NAO_REALIZADO:
                nao_realizados += 1
            else:
                pendentes += 1

    percentual = (concluidos / total * 100) if total else 0.0
    return {
        "titulo": titulo,
        "inicio": inicio.strftime("%d/%m/%Y"),
        "fim": fim.strftime("%d/%m/%Y"),
        "total_itens": total,
        "concluidos": concluidos,
        "pendentes": pendentes,
        "nao_realizados": nao_realizados,
        "percentual_concluido": percentual,
    }


def _resumo_sentimentos_mes(
    rotinas: list[Rotina],
    id_crianca: str,
    data_base: date,
) -> dict[str, Any]:
    dia_final = calendar.monthrange(data_base.year, data_base.month)[1]
    inicio = date(data_base.year, data_base.month, 1)
    fim = date(data_base.year, data_base.month, dia_final)

    rotinas_mes = [
        rotina
        for rotina in rotinas
        if rotina.id_crianca == id_crianca and inicio <= rotina.data_referencia <= fim
    ]

    contador: Counter[str] = Counter()
    for rotina in rotinas_mes:
        if rotina.sentimento_dia:
            contador[rotina.sentimento_dia] += 1

    sentimento_mais_frequente = "Nao informado"
    if contador:
        codigo_mais_frequente = max(contador.items(), key=lambda item: item[1])[0]
        dados = Rotina.SENTIMENTOS_DIA.get(codigo_mais_frequente, {})
        emoji = str(dados.get("emoji", "")).strip()
        label = str(dados.get("label", codigo_mais_frequente)).strip()
        sentimento_mais_frequente = f"{emoji} {label}".strip()

    distribuicao: list[dict[str, Any]] = []
    for escala, codigo in sorted(Rotina.SENTIMENTO_POR_ESCALA.items()):
        dados = Rotina.SENTIMENTOS_DIA.get(codigo, {})
        distribuicao.append(
            {
                "codigo": codigo,
                "escala": escala,
                "label": str(dados.get("label", codigo)),
                "emoji": str(dados.get("emoji", "")),
                "quantidade": int(contador.get(codigo, 0)),
            }
        )

    return {
        "inicio": inicio.strftime("%d/%m/%Y"),
        "fim": fim.strftime("%d/%m/%Y"),
        "dias_com_rotina": len(rotinas_mes),
        "dias_com_sentimento": sum(contador.values()),
        "sentimento_mais_frequente": sentimento_mais_frequente,
        "distribuicao": distribuicao,
    }


def _aplicar_alertas_tempo(
    rotina: dict[str, Any],
    data_ref: date,
    agora: datetime | None = None,
) -> list[dict[str, Any]]:
    if data_ref != date.today():
        return []

    agora_ref = agora or datetime.now()
    lembretes: list[dict[str, Any]] = []
    for item in rotina.get("itens", []):
        status = str(item.get("status", "")).strip()
        horario = str(item.get("horario", "")).strip()
        if status != ItemRotina.STATUS_PENDENTE:
            continue
        if not horario:
            continue

        try:
            horario_obj = datetime.strptime(horario, "%H:%M").time()
        except ValueError:
            continue

        data_hora_item = datetime.combine(data_ref, horario_obj)
        delta_minutos = int((data_hora_item - agora_ref).total_seconds() / 60)
        alerta_texto = ""
        alerta_tipo = ""

        if delta_minutos < 0:
            atraso = abs(delta_minutos)
            alerta_texto = f"Atrasada ha {atraso} min"
            alerta_tipo = "late"
        elif delta_minutos <= 15:
            alerta_texto = f"Falta {delta_minutos} min"
            alerta_tipo = "soon"
        else:
            continue

        item["alerta_tempo_texto"] = alerta_texto
        item["alerta_tempo_tipo"] = alerta_tipo
        lembretes.append(
            {
                "nome": item.get("nome", ""),
                "horario": horario,
                "alerta": alerta_texto,
                "tipo": alerta_tipo,
            }
        )

    return lembretes


def _gerar_pdf_simples(linhas: list[str]) -> bytes:
    def _escapar_pdf_texto(valor: str) -> str:
        return valor.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    comandos: list[str] = []
    y = 800
    for linha in linhas:
        texto = _escapar_pdf_texto(linha)
        comandos.append(f"BT /F1 10 Tf 40 {y} Td ({texto}) Tj ET")
        y -= 14
        if y < 40:
            break

    stream = "\n".join(comandos).encode("latin-1", errors="replace")

    objetos = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        f"5 0 obj << /Length {len(stream)} >> stream\n".encode("ascii")
        + stream
        + b"\nendstream\nendobj\n",
    ]

    pdf = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets = [0]
    for objeto in objetos:
        offsets.append(len(pdf))
        pdf += objeto

    xref_inicio = len(pdf)
    pdf += f"xref\n0 {len(offsets)}\n".encode("ascii")
    pdf += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf += f"{offset:010d} 00000 n \n".encode("ascii")

    pdf += (
        f"trailer << /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref_inicio}\n%%EOF"
    ).encode("ascii")
    return pdf


def _linha_barra_textual(texto: str) -> bool:
    conteudo = texto.strip()
    if not conteudo:
        return False
    if conteudo == "Sem sentimentos registrados no mes.":
        return True
    return "|" in conteudo and "(" in conteudo and conteudo.endswith(")")


def _eh_titulo_grafico_sentimentos(texto: str) -> bool:
    conteudo = texto.strip().casefold()
    return "grafico" in conteudo and "sentimentos" in conteudo and "barras" in conteudo


def _gerar_pdf_fallback_com_grafico(
    linhas: list[str],
    distribuicao_sentimentos: list[dict[str, Any]],
) -> bytes:
    def _escapar_pdf_texto(valor: str) -> str:
        return valor.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    comandos: list[str] = []
    y = 800.0
    ignorar_barras_textuais = False

    for linha in linhas:
        conteudo = str(linha).strip()

        if not conteudo:
            y -= 8
            ignorar_barras_textuais = False
            if y < 55:
                break
            continue

        if _eh_titulo_grafico_sentimentos(conteudo):
            texto = _escapar_pdf_texto(conteudo)
            comandos.append(f"0 0 0 rg BT /F1 10 Tf 40 {y:.2f} Td ({texto}) Tj ET")
            y -= 14

            chart_left = 62.0
            chart_bottom = max(95.0, y - 110.0)
            chart_width = 450.0
            chart_height = 92.0

            # eixo horizontal
            comandos.append(
                f"0.80 0.80 0.80 rg {chart_left:.2f} {chart_bottom:.2f} {chart_width:.2f} 0.8 re f"
            )
            # eixo vertical
            comandos.append(
                f"0.80 0.80 0.80 rg {chart_left:.2f} {chart_bottom:.2f} 0.8 {chart_height:.2f} re f"
            )

            valores = [int(item.get("quantidade", 0)) for item in distribuicao_sentimentos]
            rotulos = [str(item.get("label", "")).strip() for item in distribuicao_sentimentos]
            maximo = max(valores, default=0)

            if maximo <= 0 or not valores:
                aviso = _escapar_pdf_texto("Sem sentimentos registrados no mes.")
                comandos.append(
                    f"0 0 0 rg BT /F1 9 Tf {chart_left + 8:.2f} {chart_bottom + 36:.2f} Td ({aviso}) Tj ET"
                )
            else:
                total = max(1, len(valores))
                slot = chart_width / total
                bar_width = max(18.0, min(50.0, slot * 0.56))

                for indice, quantidade in enumerate(valores):
                    x = chart_left + (indice * slot) + ((slot - bar_width) / 2)
                    altura = 0.0
                    if quantidade > 0:
                        altura = max(3.0, (quantidade / maximo) * chart_height)

                    if altura > 0:
                        comandos.append(
                            f"0.06 0.46 0.43 rg {x:.2f} {chart_bottom:.2f} {bar_width:.2f} {altura:.2f} re f"
                        )

                    qtd_txt = _escapar_pdf_texto(str(quantidade))
                    comandos.append(
                        f"0 0 0 rg BT /F1 8 Tf {x + 2:.2f} {chart_bottom + altura + 4:.2f} Td ({qtd_txt}) Tj ET"
                    )

                    rotulo = _escapar_pdf_texto(rotulos[indice][:12])
                    comandos.append(
                        f"0 0 0 rg BT /F1 7 Tf {x - 2:.2f} {chart_bottom - 10:.2f} Td ({rotulo}) Tj ET"
                    )

            y = chart_bottom - 20
            ignorar_barras_textuais = True
            if y < 55:
                break
            continue

        if ignorar_barras_textuais and _linha_barra_textual(conteudo):
            continue

        ignorar_barras_textuais = False
        texto = _escapar_pdf_texto(conteudo)
        comandos.append(f"0 0 0 rg BT /F1 10 Tf 40 {y:.2f} Td ({texto}) Tj ET")
        y -= 14
        if y < 40:
            break

    stream = "\n".join(comandos).encode("latin-1", errors="replace")

    objetos = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n",
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
        f"5 0 obj << /Length {len(stream)} >> stream\n".encode("ascii")
        + stream
        + b"\nendstream\nendobj\n",
    ]

    pdf = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets = [0]
    for objeto in objetos:
        offsets.append(len(pdf))
        pdf += objeto

    xref_inicio = len(pdf)
    pdf += f"xref\n0 {len(offsets)}\n".encode("ascii")
    pdf += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf += f"{offset:010d} 00000 n \n".encode("ascii")

    pdf += (
        f"trailer << /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref_inicio}\n%%EOF"
    ).encode("ascii")
    return pdf


def _gerar_pdf_com_grafico(
    linhas: list[str],
    distribuicao_sentimentos: list[dict[str, Any]],
) -> bytes:
    try:
        from io import BytesIO

        from reportlab.graphics.charts.barcharts import VerticalBarChart
        from reportlab.graphics.shapes import Drawing, String
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except Exception:
        return _gerar_pdf_fallback_com_grafico(linhas, distribuicao_sentimentos)

    def _escapar_html(texto: str) -> str:
        return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _desenho_grafico() -> Drawing:
        desenho = Drawing(520, 240)
        rotulos = [str(item.get("label", "")).strip() for item in distribuicao_sentimentos]
        valores = [int(item.get("quantidade", 0)) for item in distribuicao_sentimentos]

        if not valores or max(valores, default=0) <= 0:
            desenho.add(
                String(
                    24,
                    120,
                    "Sem sentimentos registrados no mes.",
                    fontName="Helvetica",
                    fontSize=10,
                    fillColor=colors.HexColor("#1f2a2c"),
                )
            )
            return desenho

        grafico = VerticalBarChart()
        grafico.x = 38
        grafico.y = 46
        grafico.width = 450
        grafico.height = 155
        grafico.data = [valores]
        grafico.strokeColor = colors.HexColor("#9aa7a9")
        grafico.valueAxis.valueMin = 0
        maximo = max(valores)
        grafico.valueAxis.valueMax = maximo + 1
        grafico.valueAxis.valueStep = max(1, (maximo + 1 + 4) // 5)
        grafico.categoryAxis.categoryNames = rotulos
        grafico.categoryAxis.labels.angle = 20
        grafico.categoryAxis.labels.dy = -14
        grafico.categoryAxis.labels.fontName = "Helvetica"
        grafico.categoryAxis.labels.fontSize = 8
        grafico.bars[0].fillColor = colors.HexColor("#0f766e")
        grafico.bars[0].strokeColor = colors.HexColor("#0b5d57")
        desenho.add(grafico)
        return desenho

    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=34,
        rightMargin=34,
        topMargin=34,
        bottomMargin=34,
        title="Relatorio TeApoio",
        pageCompression=0,
    )

    estilos_base = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "TeApoioTitulo",
        parent=estilos_base["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=18,
        spaceAfter=8,
    )
    estilo_secao = ParagraphStyle(
        "TeApoioSecao",
        parent=estilos_base["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        spaceBefore=4,
        spaceAfter=4,
    )
    estilo_texto = ParagraphStyle(
        "TeApoioTexto",
        parent=estilos_base["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        spaceAfter=2,
    )

    historia: list[Any] = []
    titulo_renderizado = False
    ignorar_barras_textuais = False
    for linha in linhas:
        texto = str(linha)
        conteudo = texto.strip()

        if not conteudo:
            ignorar_barras_textuais = False
            historia.append(Spacer(1, 5))
            continue

        if _eh_titulo_grafico_sentimentos(conteudo):
            historia.append(Paragraph(_escapar_html(conteudo), estilo_secao))
            historia.append(_desenho_grafico())
            historia.append(Spacer(1, 8))
            ignorar_barras_textuais = True
            continue

        if ignorar_barras_textuais and _linha_barra_textual(conteudo):
            continue

        if not titulo_renderizado:
            historia.append(Paragraph(_escapar_html(conteudo), estilo_titulo))
            titulo_renderizado = True
            continue

        if ":" not in conteudo and (len(conteudo) <= 38 or conteudo.isupper()):
            historia.append(Paragraph(_escapar_html(conteudo), estilo_secao))
        else:
            historia.append(Paragraph(_escapar_html(conteudo), estilo_texto))

    try:
        documento.build(historia)
        return buffer.getvalue()
    except Exception:
        return _gerar_pdf_fallback_com_grafico(linhas, distribuicao_sentimentos)


class EstadoApi:
    """Mantem estado de dominio em memoria e persiste no mesmo JSON da CLI."""

    def __init__(self, caminho_arquivo: str | None = None) -> None:
        repositorio = RepositorioRelatorio(caminho_arquivo=caminho_arquivo)
        self._servico_relatorios = ServicoRelatorios(repositorio=repositorio)
        estado = self._servico_relatorios.carregar_estado_inicial()

        self.responsaveis: list[Responsavel] = estado["responsaveis"]
        self.criancas: list[Crianca] = estado["criancas"]
        self.rotinas: list[Rotina] = estado["rotinas"]
        self.perfil: Perfil | None = estado["perfil"]
        self.data_calendario: date = estado["data_calendario"]

        self.servico_cadastro = ServicoCadastro()
        self.servico_monitoramento = ServicoMonitoramento()
        self.servico_perfil = ServicoPerfil()
        self.servico_rotinas = ServicoRotinas()

    def persistir(self) -> None:
        self._servico_relatorios.salvar_estado_atual(
            responsaveis=self.responsaveis,
            criancas=self.criancas,
            rotinas=self.rotinas,
            perfil=self.perfil,
            data_calendario=self.data_calendario,
        )

    def buscar_responsavel(self, id_responsavel: str) -> Responsavel | None:
        return next(
            (r for r in self.responsaveis if r.id_responsavel == id_responsavel),
            None,
        )

    def buscar_crianca(self, id_crianca: str) -> Crianca | None:
        return next((c for c in self.criancas if c.id_crianca == id_crianca), None)

    def listar_criancas_responsavel(self, id_responsavel: str) -> list[Crianca]:
        return [c for c in self.criancas if c.id_responsavel == id_responsavel]

    def obter_perfil_responsavel(self, responsavel: Responsavel) -> Perfil:
        if self.perfil is None:
            self.perfil = Perfil(
                responsavel=responsavel,
                criancas=self.listar_criancas_responsavel(responsavel.id_responsavel),
            )
            return self.perfil

        if self.perfil.responsavel.id_responsavel != responsavel.id_responsavel:
            # Mantem o mesmo comportamento geral da CLI: um perfil ativo por vez.
            self.perfil = Perfil(
                responsavel=responsavel,
                criancas=self.listar_criancas_responsavel(responsavel.id_responsavel),
            )
        return self.perfil

    @staticmethod
    def responsavel_para_dict(responsavel: Responsavel) -> dict[str, Any]:
        return {
            "id_responsavel": responsavel.id_responsavel,
            "nome": responsavel.nome,
            "data_nascimento": responsavel.data_nascimento.strftime("%d/%m/%Y"),
            "email": responsavel.email,
        }

    @staticmethod
    def crianca_para_dict(crianca: Crianca) -> dict[str, Any]:
        return {
            "id_crianca": crianca.id_crianca,
            "id_responsavel": crianca.id_responsavel,
            "nome": crianca.nome,
            "data_nascimento": crianca.data_nascimento.strftime("%d/%m/%Y"),
            "nivel_suporte": crianca.nivel_suporte,
        }

    @staticmethod
    def item_para_dict(item: ItemRotina) -> dict[str, Any]:
        return {
            "nome": item.nome,
            "horario": item.horario,
            "status": item.status,
            "observacao": item.observacao,
            "tags": item.tags,
        }

    def rotina_para_dict(self, rotina: Rotina) -> dict[str, Any]:
        resumo = self.servico_monitoramento.obter_resumo_rotina(rotina)
        return {
            "id_crianca": rotina.id_crianca,
            "data_referencia": rotina.data_referencia.isoformat(),
            "sentimento_dia": rotina.sentimento_dia,
            "sentimento_dia_info": rotina.sentimento_dia_info,
            "itens": [self.item_para_dict(item) for item in rotina.itens],
            # campo mantido para compatibilidade de emoções detalhadas
            "emocoes": rotina.obter_emocoes(),
            "resumo": resumo,
        }

    @staticmethod
    def perfil_sensorial_para_dict(perfil_sensorial) -> dict[str, Any]:
        return {
            "id_crianca": perfil_sensorial.id_crianca,
            "nome": perfil_sensorial.nome,
            "data_nascimento": perfil_sensorial.data_nascimento.strftime("%d/%m/%Y"),
            "hipersensibilidades": perfil_sensorial.hipersensibilidades,
            "hipossensibilidades": perfil_sensorial.hipossensibilidades,
            "hiperfocos": perfil_sensorial.hiperfocos,
            "seletividade_alimentar": perfil_sensorial.seletividade_alimentar,
            "estrategias_regulacao": perfil_sensorial.estrategias_regulacao,
        }


def create_app(config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    if config:
        app.config.update(config)

    # Flask define SECRET_KEY por padrao como None; tambem evitamos valor vazio vindo do ambiente.
    secret_key_cfg = app.config.get("SECRET_KEY")
    secret_key_env = os.getenv("TEAPOIO_SECRET_KEY", "")

    secret_key = ""
    if isinstance(secret_key_cfg, str):
        secret_key = secret_key_cfg.strip()
    elif secret_key_cfg:
        secret_key = str(secret_key_cfg)

    if not secret_key:
        secret_key = secret_key_env.strip()

    if not secret_key:
        secret_key = "teapoio-dev"

    app.config["SECRET_KEY"] = secret_key
    app.secret_key = secret_key

    estado = EstadoApi(caminho_arquivo=app.config.get("DATA_FILE"))

    def _responsavel_sessao() -> Responsavel | None:
        id_responsavel = str(session.get("responsavel_id", "")).strip()
        if not id_responsavel:
            return None

        responsavel = estado.buscar_responsavel(id_responsavel)
        if responsavel is None:
            session.pop("responsavel_id", None)
            session.pop("crianca_id", None)
            return None
        return responsavel

    def _crianca_sessao(responsavel: Responsavel | None) -> Crianca | None:
        id_crianca = str(session.get("crianca_id", "")).strip()
        if not id_crianca:
            return None

        crianca = estado.buscar_crianca(id_crianca)
        if crianca is None:
            session.pop("crianca_id", None)
            return None

        if responsavel is not None and crianca.id_responsavel != responsavel.id_responsavel:
            session.pop("crianca_id", None)
            return None

        return crianca

    def _secao_valida(secao_bruta: str | None, autenticado: bool) -> str:
        secao = str(secao_bruta or "").strip().lower()
        if autenticado:
            secoes_permitidas = {"criancas", "rotina", "perfil"}
            return secao if secao in secoes_permitidas else "criancas"

        secoes_permitidas = {"cadastro", "login"}
        return secao if secao in secoes_permitidas else "cadastro"

    def _dados_perfil_responsavel(responsavel: Responsavel) -> dict[str, Any]:
        criancas = estado.listar_criancas_responsavel(responsavel.id_responsavel)
        perfil_ativo = (
            estado.perfil
            if estado.perfil is not None
            and estado.perfil.responsavel.id_responsavel == responsavel.id_responsavel
            else None
        )

        criancas_payload: list[dict[str, Any]] = []
        for crianca in criancas:
            perfil_sensorial_payload = None
            if perfil_ativo is not None:
                perfil_sensorial = perfil_ativo.obter_perfil_sensorial(crianca.id_crianca)
                if perfil_sensorial is not None:
                    perfil_sensorial_payload = estado.perfil_sensorial_para_dict(perfil_sensorial)

            criancas_payload.append(
                {
                    "id_crianca": crianca.id_crianca,
                    "nome": crianca.nome,
                    "data_nascimento": crianca.data_nascimento.strftime("%d/%m/%Y"),
                    "nivel_suporte": crianca.nivel_suporte,
                    "perfil_sensorial": perfil_sensorial_payload,
                }
            )

        return {
            "responsavel": estado.responsavel_para_dict(responsavel),
            "quantidade_criancas": len(criancas_payload),
            "criancas": criancas_payload,
        }

    def _dados_onboarding(
        responsavel: Responsavel | None,
        criancas_responsavel: list[Crianca],
    ) -> dict[str, Any] | None:
        if responsavel is None:
            return None

        ids_criancas = {crianca.id_crianca for crianca in criancas_responsavel}
        tem_crianca = bool(ids_criancas)
        tem_rotina = any(
            rotina.id_crianca in ids_criancas and bool(rotina.itens)
            for rotina in estado.rotinas
        )

        perfil_ativo = (
            estado.perfil
            if estado.perfil is not None
            and estado.perfil.responsavel.id_responsavel == responsavel.id_responsavel
            else None
        )
        tem_sensorial = False
        if perfil_ativo is not None:
            tem_sensorial = any(
                perfil_ativo.obter_perfil_sensorial(id_crianca) is not None
                for id_crianca in ids_criancas
            )

        tem_observacao = any(
            (item.observacao or "").strip()
            for rotina in estado.rotinas
            if rotina.id_crianca in ids_criancas
            for item in rotina.itens
        )

        passos = [
            {"titulo": "Cadastre a primeira crianca", "feito": tem_crianca, "secao": "criancas"},
            {"titulo": "Monte a primeira rotina", "feito": tem_rotina, "secao": "rotina"},
            {"titulo": "Adicione uma observacao de tarefa", "feito": tem_observacao, "secao": "rotina"},
            {"titulo": "Preencha o perfil sensorial", "feito": tem_sensorial, "secao": "perfil"},
        ]
        completo = all(item["feito"] for item in passos)
        return {"mostrar": not completo, "passos": passos}

    @app.get("/")
    def pagina_inicial():
        responsavel = _responsavel_sessao()
        crianca = _crianca_sessao(responsavel)
        secao = _secao_valida(
            request.args.get("secao"),
            autenticado=responsavel is not None,
        )
        criancas_responsavel = (
            estado.listar_criancas_responsavel(responsavel.id_responsavel)
            if responsavel is not None
            else []
        )

        rotina_exibicao = None
        perfil_visualizacao = None
        data_rotina = str(request.args.get("data_rotina", "")).strip()
        sugestoes_rotina = obter_sugestoes_tea() if secao == "rotina" else []
        calendario_exibicao = None
        evolucao_periodo = None
        lembretes_rotina = []
        onboarding = _dados_onboarding(responsavel, criancas_responsavel)
        sentimentos_disponiveis = Rotina.opcoes_sentimento_dia() if secao == "rotina" else []

        if secao == "rotina" and crianca is not None and not data_rotina:
            data_rotina = date.today().isoformat()

        if secao == "perfil" and responsavel is not None:
            perfil_visualizacao = _dados_perfil_responsavel(responsavel)

        if secao == "rotina" and crianca is not None and data_rotina:
            try:
                data_ref = _parse_data(data_rotina)
                if data_ref > date.today():
                    raise ValueError("Nao e permitido selecionar data no futuro.")

                estado.data_calendario = data_ref
                rotina, criada = estado.servico_rotinas.obter_ou_criar_rotina(
                    rotinas=estado.rotinas,
                    id_crianca=crianca.id_crianca,
                    data_referencia=data_ref,
                )
                if criada:
                    estado.persistir()
                rotina_exibicao = estado.rotina_para_dict(rotina)
                evolucao_periodo = {
                    "semana": _resumo_periodo_rotinas(
                        estado.rotinas,
                        crianca.id_crianca,
                        data_ref,
                        "semana",
                    ),
                    "mes": _resumo_periodo_rotinas(
                        estado.rotinas,
                        crianca.id_crianca,
                        data_ref,
                        "mes",
                    ),
                }
                lembretes_rotina = _aplicar_alertas_tempo(rotina_exibicao, data_ref)
            except ValueError as erro:
                flash(str(erro), "erro")

        if secao == "rotina":
            hoje = date.today()
            cal_mes_raw = request.args.get("cal_mes")
            cal_ano_raw = request.args.get("cal_ano")
            cal_mes = estado.data_calendario.month
            cal_ano = estado.data_calendario.year
            try:
                if cal_mes_raw is not None:
                    cal_mes = int(str(cal_mes_raw).strip())
                if cal_ano_raw is not None:
                    cal_ano = int(str(cal_ano_raw).strip())
                if not 1 <= cal_mes <= 12:
                    raise ValueError
                if cal_ano != hoje.year:
                    raise ValueError
            except ValueError:
                cal_mes = estado.data_calendario.month
                cal_ano = estado.data_calendario.year

            calendario_exibicao = _dados_calendario(
                mes=cal_mes,
                ano=cal_ano,
                data_selecionada=estado.data_calendario,
            )

        return render_template(
            "index.html",
            secao=secao,
            responsavel_selecionado=responsavel,
            crianca_selecionada=crianca,
            responsaveis=estado.responsaveis,
            criancas_responsavel=criancas_responsavel,
            rotina_exibicao=rotina_exibicao,
            data_rotina=data_rotina,
            sugestoes_rotina=sugestoes_rotina,
            calendario_exibicao=calendario_exibicao,
            evolucao_periodo=evolucao_periodo,
            lembretes_rotina=lembretes_rotina,
            perfil_visualizacao=perfil_visualizacao,
            onboarding=onboarding,
            sentimentos_disponiveis=sentimentos_disponiveis,
            tags_predefinidas=TAGS_PREDEFINIDAS,
        )

    @app.post("/web/responsavel/cadastrar")
    def web_cadastrar_responsavel():
        nome = request.form.get("nome", "")
        data_nascimento = request.form.get("data_nascimento", "")
        email = request.form.get("email", "")
        senha = request.form.get("senha", "")

        try:
            estado.servico_cadastro.validar_email_disponivel(estado.responsaveis, email)
            responsavel, perfil = estado.servico_cadastro.cadastrar_responsavel(
                nome=nome,
                data_nascimento=data_nascimento,
                email=email,
                senha=senha,
            )
        except (TypeError, ValueError) as erro:
            flash(str(erro), "erro")
            return redirect(url_for("pagina_inicial", secao="cadastro"))

        estado.responsaveis.append(responsavel)
        estado.perfil = perfil
        estado.persistir()
        session["responsavel_id"] = responsavel.id_responsavel
        session.pop("crianca_id", None)
        flash(f"Responsavel cadastrado. ID: {responsavel.id_responsavel}", "sucesso")
        return redirect(url_for("pagina_inicial", secao="criancas"))

    @app.post("/web/responsavel/selecionar")
    def web_selecionar_responsavel():
        id_responsavel = str(request.form.get("id_responsavel", "")).strip()
        senha = request.form.get("senha", "")
        responsavel = estado.servico_cadastro.validar_responsavel_por_credenciais(
            estado.responsaveis,
            id_responsavel,
            senha,
        )
        if responsavel is None:
            flash("ID ou senha invalidos.", "erro")
            return redirect(url_for("pagina_inicial", secao="login"))

        session["responsavel_id"] = responsavel.id_responsavel
        session.pop("crianca_id", None)
        flash(f"Responsavel selecionado: {responsavel.nome}", "sucesso")
        return redirect(url_for("pagina_inicial", secao="criancas"))

    @app.post("/web/logout")
    def web_logout():
        session.pop("responsavel_id", None)
        session.pop("crianca_id", None)
        flash("Sessao encerrada com sucesso.", "sucesso")
        return redirect(url_for("pagina_inicial", secao="cadastro"))

    @app.post("/web/crianca/cadastrar")
    def web_cadastrar_crianca():
        responsavel = _responsavel_sessao()
        if responsavel is None:
            flash("Selecione um responsavel antes de cadastrar crianca.", "erro")
            return redirect(url_for("pagina_inicial", secao="cadastro"))

        try:
            crianca = estado.servico_cadastro.cadastrar_crianca(
                responsavel=responsavel,
                nome=request.form.get("nome", ""),
                data_nascimento=request.form.get("data_nascimento", ""),
                nivel_suporte=int(request.form.get("nivel_suporte", "")),
            )
        except (TypeError, ValueError) as erro:
            flash(str(erro), "erro")
            return redirect(url_for("pagina_inicial", secao="criancas"))

        estado.criancas.append(crianca)
        perfil = estado.obter_perfil_responsavel(responsavel)
        estado.servico_perfil.vincular_crianca_ao_perfil(perfil, crianca)
        estado.persistir()

        session["crianca_id"] = crianca.id_crianca
        flash(f"Crianca cadastrada. ID: {crianca.id_crianca}", "sucesso")
        return redirect(url_for("pagina_inicial", secao="criancas"))

    @app.post("/web/crianca/selecionar")
    def web_selecionar_crianca():
        responsavel = _responsavel_sessao()
        if responsavel is None:
            flash("Selecione um responsavel antes de escolher crianca.", "erro")
            return redirect(url_for("pagina_inicial", secao="cadastro"))

        id_crianca = str(request.form.get("id_crianca", "")).strip()
        crianca = estado.buscar_crianca(id_crianca)
        if crianca is None or crianca.id_responsavel != responsavel.id_responsavel:
            flash("Crianca nao encontrada para o responsavel selecionado.", "erro")
            return redirect(url_for("pagina_inicial", secao="criancas"))

        session["crianca_id"] = crianca.id_crianca
        flash(f"Crianca selecionada: {crianca.nome}", "sucesso")
        return redirect(url_for("pagina_inicial", secao="criancas"))

    @app.post("/web/crianca/editar")
    def web_editar_crianca():
        responsavel = _responsavel_sessao()
        if responsavel is None:
            flash("Faca login para editar crianca.", "erro")
            return redirect(url_for("pagina_inicial", secao="cadastro"))

        id_crianca = str(request.form.get("id_crianca", "")).strip()
        crianca = estado.buscar_crianca(id_crianca)
        if crianca is None or crianca.id_responsavel != responsavel.id_responsavel:
            flash("Crianca nao encontrada para edicao.", "erro")
            return redirect(url_for("pagina_inicial", secao="criancas"))

        try:
            estado.servico_cadastro.editar_crianca(
                crianca=crianca,
                nome=request.form.get("nome", ""),
                data_nascimento=request.form.get("data_nascimento", ""),
                nivel_suporte=request.form.get("nivel_suporte", ""),
            )
            estado.servico_perfil.sincronizar_dados_crianca_no_perfil_sensorial(
                perfil=estado.perfil,
                crianca=crianca,
            )
            estado.persistir()
        except (TypeError, ValueError) as erro:
            flash(str(erro), "erro")
            return redirect(url_for("pagina_inicial", secao="criancas"))

        flash("Crianca atualizada com sucesso.", "sucesso")
        return redirect(url_for("pagina_inicial", secao="criancas"))

    @app.post("/web/crianca/excluir")
    def web_excluir_crianca():
        responsavel = _responsavel_sessao()
        if responsavel is None:
            flash("Faca login para excluir crianca.", "erro")
            return redirect(url_for("pagina_inicial", secao="cadastro"))

        id_crianca = str(request.form.get("id_crianca", "")).strip()
        crianca = estado.buscar_crianca(id_crianca)
        if crianca is None or crianca.id_responsavel != responsavel.id_responsavel:
            flash("Crianca nao encontrada para exclusao.", "erro")
            return redirect(url_for("pagina_inicial", secao="criancas"))

        confirmacao_1 = str(request.form.get("confirmacao_1", "")).strip().lower()
        confirmacao_2 = str(request.form.get("confirmacao_2", "")).strip().upper()
        if confirmacao_1 != "sim" or confirmacao_2 != "EXCLUIR":
            flash(
                "Para excluir, marque a confirmacao e digite EXCLUIR.",
                "erro",
            )
            return redirect(url_for("pagina_inicial", secao="criancas"))

        estado.criancas, estado.rotinas = estado.servico_perfil.excluir_crianca(
            criancas=estado.criancas,
            rotinas=estado.rotinas,
            perfil=estado.perfil,
            id_crianca=id_crianca,
        )
        if session.get("crianca_id") == id_crianca:
            session.pop("crianca_id", None)
        estado.persistir()
        flash("Crianca excluida com sucesso.", "sucesso")
        return redirect(url_for("pagina_inicial", secao="criancas"))

    @app.post("/web/responsavel/editar")
    def web_editar_responsavel():
        responsavel = _responsavel_sessao()
        if responsavel is None:
            flash("Faca login para editar seus dados.", "erro")
            return redirect(url_for("pagina_inicial", secao="cadastro"))

        nome = request.form.get("nome", "")
        data_nascimento = request.form.get("data_nascimento", "")
        email = request.form.get("email", "")

        try:
            email_limpo = email.strip()
            if email_limpo:
                outros_responsaveis = [
                    item
                    for item in estado.responsaveis
                    if item.id_responsavel != responsavel.id_responsavel
                ]
                estado.servico_cadastro.validar_email_disponivel(
                    outros_responsaveis,
                    email_limpo,
                )

            estado.servico_cadastro.editar_responsavel(
                responsavel=responsavel,
                nome=nome,
                data_nascimento=data_nascimento,
                email=email,
            )
            estado.persistir()
        except (TypeError, ValueError) as erro:
            flash(str(erro), "erro")
            return redirect(url_for("pagina_inicial", secao="perfil"))

        flash("Dados do responsavel atualizados com sucesso.", "sucesso")
        return redirect(url_for("pagina_inicial", secao="perfil"))

    @app.post("/web/rotina/item")
    def web_adicionar_item_rotina():
        responsavel = _responsavel_sessao()
        crianca = _crianca_sessao(responsavel)
        if crianca is None:
            flash("Selecione uma crianca antes de adicionar item de rotina.", "erro")
            return redirect(url_for("pagina_inicial", secao="criancas"))

        data_texto = request.form.get("data", "")
        try:
            data_ref = _parse_data(data_texto)
            rotina, _ = estado.servico_rotinas.obter_ou_criar_rotina(
                rotinas=estado.rotinas,
                id_crianca=crianca.id_crianca,
                data_referencia=data_ref,
            )
            estado.servico_rotinas.adicionar_item(
                rotina=rotina,
                nome_item=request.form.get("nome", ""),
                horario=request.form.get("horario", ""),
                observacao=request.form.get("observacao", ""),
                tags=_normalizar_tags_form(request.form, "tags"),
            )
            estado.persistir()
        except (TypeError, ValueError) as erro:
            flash(str(erro), "erro")
            return redirect(url_for("pagina_inicial", secao="rotina", data_rotina=data_texto))

        flash("Item de rotina adicionado com sucesso.", "sucesso")
        return redirect(url_for("pagina_inicial", secao="rotina", data_rotina=data_ref.isoformat()))

    @app.post("/web/rotina/consultar")
    def web_consultar_rotina():
        responsavel = _responsavel_sessao()
        crianca = _crianca_sessao(responsavel)
        if crianca is None:
            flash("Selecione uma crianca antes de consultar rotina.", "erro")
            return redirect(url_for("pagina_inicial", secao="criancas"))

        data_texto = request.form.get("data", "")
        try:
            data_ref = _parse_data(data_texto)
        except ValueError as erro:
            flash(str(erro), "erro")
            return redirect(url_for("pagina_inicial", secao="rotina", data_rotina=data_texto))

        return redirect(url_for("pagina_inicial", secao="rotina", data_rotina=data_ref.isoformat()))

    @app.post("/web/calendario/selecionar")
    def web_calendario_selecionar_data():
        responsavel = _responsavel_sessao()
        crianca = _crianca_sessao(responsavel)
        if crianca is None:
            flash("Selecione uma crianca antes de usar o calendario.", "erro")
            return redirect(url_for("pagina_inicial", secao="criancas"))

        data_texto = request.form.get("data", "")
        try:
            data_ref = _parse_data(data_texto)
            if data_ref > date.today():
                raise ValueError("Nao e permitido selecionar data no futuro.")
            if data_ref.year != date.today().year:
                raise ValueError(f"Ano deve ser o atual ({date.today().year}).")
            estado.data_calendario = data_ref
            estado.persistir()
        except ValueError as erro:
            flash(str(erro), "erro")
            return redirect(url_for("pagina_inicial", secao="rotina"))

        return redirect(url_for("pagina_inicial", secao="rotina", data_rotina=data_ref.isoformat()))

    @app.post("/web/calendario/hoje")
    def web_calendario_hoje():
        responsavel = _responsavel_sessao()
        crianca = _crianca_sessao(responsavel)
        if crianca is None:
            flash("Selecione uma crianca antes de usar o calendario.", "erro")
            return redirect(url_for("pagina_inicial", secao="criancas"))

        estado.data_calendario = date.today()
        estado.persistir()
        return redirect(
            url_for(
                "pagina_inicial",
                secao="rotina",
                data_rotina=estado.data_calendario.isoformat(),
            )
        )

    @app.post("/web/rotina/sentimento")
    def web_salvar_sentimento_rotina():
        responsavel = _responsavel_sessao()
        crianca = _crianca_sessao(responsavel)
        if crianca is None:
            flash("Selecione uma crianca antes de registrar sentimento.", "erro")
            return redirect(url_for("pagina_inicial", secao="criancas"))

        data_texto = request.form.get("data", "")
        sentimento = request.form.get("sentimento", "")
        try:
            data_ref = _parse_data(data_texto)
            rotina, _ = estado.servico_rotinas.obter_ou_criar_rotina(
                rotinas=estado.rotinas,
                id_crianca=crianca.id_crianca,
                data_referencia=data_ref,
            )
            rotina.atualizar_sentimento_dia(sentimento)
            estado.persistir()
        except (TypeError, ValueError) as erro:
            flash(str(erro), "erro")
            return redirect(url_for("pagina_inicial", secao="rotina", data_rotina=data_texto))

        flash("Sentimento do dia atualizado com sucesso.", "sucesso")
        return redirect(url_for("pagina_inicial", secao="rotina", data_rotina=data_ref.isoformat()))

    @app.post("/web/rotina/emocao")
    def web_salvar_emocao_rotina():
        responsavel = _responsavel_sessao()
        crianca = _crianca_sessao(responsavel)
        if crianca is None:
            flash("Selecione uma crianca antes de registrar emoção.", "erro")
            return redirect(url_for("pagina_inicial", secao="criancas"))

        data_texto = request.form.get("data", "")
        emocao = request.form.get("emocao", "")
        escala = request.form.get("escala", "")
        try:
            data_ref = _parse_data(data_texto)
            rotina, _ = estado.servico_rotinas.obter_ou_criar_rotina(
                rotinas=estado.rotinas,
                id_crianca=crianca.id_crianca,
                data_referencia=data_ref,
            )
            rotina.registrar_emocao(emocao, int(escala))
            estado.persistir()
        except (TypeError, ValueError) as erro:
            flash(str(erro), "erro")
            return redirect(url_for("pagina_inicial", secao="rotina", data_rotina=data_texto))

        flash("Emoção registrada com sucesso.", "sucesso")
        return redirect(url_for("pagina_inicial", secao="rotina", data_rotina=data_ref.isoformat()))

    @app.post("/web/perfil-sensorial/salvar")
    def web_salvar_perfil_sensorial():
        responsavel = _responsavel_sessao()
        if responsavel is None:
            flash("Faca login para cadastrar perfil sensorial.", "erro")
            return redirect(url_for("pagina_inicial", secao="cadastro"))

        id_crianca = str(request.form.get("id_crianca", "")).strip()
        crianca = estado.buscar_crianca(id_crianca)
        if crianca is None or crianca.id_responsavel != responsavel.id_responsavel:
            flash("Crianca invalida para cadastro de perfil sensorial.", "erro")
            return redirect(url_for("pagina_inicial", secao="perfil"))

        try:
            perfil = estado.obter_perfil_responsavel(responsavel)
            estado.servico_perfil.criar_ou_atualizar_perfil_sensorial(
                perfil=perfil,
                crianca=crianca,
                hipersensibilidades=_normalizar_lista_texto_livre(
                    request.form.get("hipersensibilidades", ""),
                ),
                hipossensibilidades=_normalizar_lista_texto_livre(
                    request.form.get("hipossensibilidades", ""),
                ),
                hiperfocos=_normalizar_lista_texto_livre(
                    request.form.get("hiperfocos", ""),
                ),
                seletividade_alimentar=_normalizar_lista_texto_livre(
                    request.form.get("seletividade_alimentar", ""),
                ),
                estrategias_regulacao=_normalizar_lista_texto_livre(
                    request.form.get("estrategias_regulacao", ""),
                ),
            )
            estado.persistir()
        except (TypeError, ValueError) as erro:
            flash(str(erro), "erro")
            return redirect(url_for("pagina_inicial", secao="perfil"))

        flash("Perfil sensorial salvo com sucesso.", "sucesso")
        flash(
            (
                f"{crianca.nome} (ID: {crianca.id_crianca}) - "
                f"Nivel {crianca.nivel_suporte} - "
                f"Nascimento {crianca.data_nascimento.strftime('%d/%m/%Y')}"
            ),
            "sucesso",
        )
        flash("Perfil sensorial: cadastrado.", "sucesso")
        return redirect(url_for("pagina_inicial", secao="perfil"))

    @app.get("/web/relatorio/pdf")
    def web_exportar_relatorio_pdf():
        responsavel = _responsavel_sessao()
        if responsavel is None:
            flash("Faca login para exportar relatorio.", "erro")
            return redirect(url_for("pagina_inicial", secao="cadastro"))

        criancas_responsavel = estado.listar_criancas_responsavel(responsavel.id_responsavel)
        if not criancas_responsavel:
            flash("Cadastre uma crianca antes de exportar relatorio.", "erro")
            return redirect(url_for("pagina_inicial", secao="criancas"))

        id_crianca_url = str(request.args.get("id_crianca", "")).strip()
        data_texto = str(request.args.get("data", "")).strip()
        data_ref = _parse_data(data_texto, padrao=estado.data_calendario)
        if data_ref > date.today():
            flash("Nao e permitido exportar relatorio com data futura.", "erro")
            return redirect(url_for("pagina_inicial", secao="rotina"))

        crianca = next(
            (
                item
                for item in criancas_responsavel
                if item.id_crianca == id_crianca_url
            ),
            None,
        )
        if crianca is None:
            id_sessao = str(session.get("crianca_id", "")).strip()
            crianca = next(
                (item for item in criancas_responsavel if item.id_crianca == id_sessao),
                criancas_responsavel[0],
            )

        rotina, criada = estado.servico_rotinas.obter_ou_criar_rotina(
            rotinas=estado.rotinas,
            id_crianca=crianca.id_crianca,
            data_referencia=data_ref,
        )
        if criada:
            estado.persistir()

        perfil = estado.obter_perfil_responsavel(responsavel)
        perfil_sensorial = perfil.obter_perfil_sensorial(crianca.id_crianca)
        resumo = estado.servico_monitoramento.obter_resumo_rotina(rotina)
        resumo_mes_itens = _resumo_periodo_rotinas(
            estado.rotinas,
            crianca.id_crianca,
            data_ref,
            "mes",
        )
        resumo_mes_sentimentos = _resumo_sentimentos_mes(
            estado.rotinas,
            crianca.id_crianca,
            data_ref,
        )

        distribuicao_mes = resumo_mes_sentimentos["distribuicao"]

        linhas = [
            "Relatorio TeApoio - Visao Geral",
            f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "",
            "DADOS PRINCIPAIS",
            f"Responsavel: {responsavel.nome}",
            f"Email: {responsavel.email}",
            f"Crianca: {crianca.nome} (ID {crianca.id_crianca})",
            f"Mes de referencia: {_mes_nome_pt_br(data_ref.month)}/{data_ref.year}",
            "",
            "RESUMO MENSAL",
            f"- Periodo analisado: {resumo_mes_sentimentos['inicio']} ate {resumo_mes_sentimentos['fim']}",
            f"- Dias com rotina registrada: {resumo_mes_sentimentos['dias_com_rotina']}",
            f"- Dias com sentimento registrado: {resumo_mes_sentimentos['dias_com_sentimento']}",
            f"- Itens no mes: {resumo_mes_itens['total_itens']}",
            f"- Concluidos: {resumo_mes_itens['concluidos']}",
            f"- Pendentes: {resumo_mes_itens['pendentes']}",
            f"- Nao realizados: {resumo_mes_itens['nao_realizados']}",
            f"- Percentual concluido no mes: {resumo_mes_itens['percentual_concluido']:.1f}%",
            "",
            "GRAFICO DE SENTIMENTOS NO MES (BARRAS)",
        ]

        linhas.extend(
            [
                "",
                "DETALHE DO DIA SELECIONADO",
                f"Data da rotina: {data_ref.strftime('%d/%m/%Y')}",
                f"Sentimento do dia: {rotina.sentimento_dia_info['label']}",
                "",
                "RESUMO DA ROTINA DO DIA",
                f"- Concluidos: {resumo['concluidos']}",
                f"- Pendentes: {resumo['pendentes']}",
                f"- Nao realizados: {resumo['nao_realizados']}",
                f"Percentual concluido: {resumo['percentual_concluido']:.1f}%",
            ]
        )

        linhas.extend(["", "PERFIL SENSORIAL"])
        if perfil_sensorial is None:
            linhas.append("- Nao cadastrado.")
        else:
            linhas.extend(
                [
                    "- Hipersensibilidades: "
                    + (", ".join(perfil_sensorial.hipersensibilidades) or "Nao informado"),
                    "- Hipossensibilidades: "
                    + (", ".join(perfil_sensorial.hipossensibilidades) or "Nao informado"),
                    "- Hiperfocos: "
                    + (", ".join(perfil_sensorial.hiperfocos) or "Nao informado"),
                    "- Seletividade alimentar: "
                    + (", ".join(perfil_sensorial.seletividade_alimentar) or "Nao informado"),
                    "- Estrategias de regulacao: "
                    + (", ".join(perfil_sensorial.estrategias_regulacao) or "Nao informado"),
                ]
            )

        pdf_bytes = _gerar_pdf_com_grafico(linhas, distribuicao_mes)
        nome_arquivo = f"relatorio_{crianca.id_crianca}_{data_ref.isoformat()}.pdf"
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'},
        )

    @app.post("/web/rotina/item/status")
    def web_alterar_status_item_rotina():
        responsavel = _responsavel_sessao()
        crianca = _crianca_sessao(responsavel)
        if crianca is None:
            flash("Selecione uma crianca antes de alterar status da rotina.", "erro")
            return redirect(url_for("pagina_inicial", secao="criancas"))

        data_texto = request.form.get("data", "")
        indice_texto = str(request.form.get("indice", "")).strip()
        status_texto = str(request.form.get("status", "")).strip()

        try:
            data_ref = _parse_data(data_texto)
            indice = int(indice_texto)
            status_code = int(status_texto)
            rotina, _ = estado.servico_rotinas.obter_ou_criar_rotina(
                rotinas=estado.rotinas,
                id_crianca=crianca.id_crianca,
                data_referencia=data_ref,
            )
            estado.servico_rotinas.marcar_status(
                rotina=rotina,
                indice=indice,
                status_code=status_code,
            )
            estado.persistir()
        except (TypeError, ValueError, IndexError) as erro:
            flash(str(erro), "erro")
            return redirect(url_for("pagina_inicial", secao="rotina", data_rotina=data_texto))

        flash("Status do item atualizado com sucesso.", "sucesso")
        return redirect(url_for("pagina_inicial", secao="rotina", data_rotina=data_ref.isoformat()))

    @app.post("/web/rotina/item/observacao")
    def web_salvar_observacao_item_rotina():
        responsavel = _responsavel_sessao()
        crianca = _crianca_sessao(responsavel)
        if crianca is None:
            flash("Selecione uma crianca antes de registrar observacao.", "erro")
            return redirect(url_for("pagina_inicial", secao="criancas"))

        data_texto = request.form.get("data", "")
        indice_texto = str(request.form.get("indice", "")).strip()
        observacao = request.form.get("observacao", "")

        try:
            data_ref = _parse_data(data_texto)
            indice = int(indice_texto)
            rotina, _ = estado.servico_rotinas.obter_ou_criar_rotina(
                rotinas=estado.rotinas,
                id_crianca=crianca.id_crianca,
                data_referencia=data_ref,
            )
            rotina.itens[indice].atualizar_observacao(observacao)
            rotina.itens[indice].atualizar_tags(_normalizar_tags_form(request.form, "tags"))
            estado.persistir()
        except (TypeError, ValueError, IndexError) as erro:
            flash(str(erro), "erro")
            return redirect(url_for("pagina_inicial", secao="rotina", data_rotina=data_texto))

        flash("Observacao salva com sucesso.", "sucesso")
        return redirect(url_for("pagina_inicial", secao="rotina", data_rotina=data_ref.isoformat()))

    @app.post("/web/rotina/item/remover")
    def web_remover_item_rotina():
        responsavel = _responsavel_sessao()
        crianca = _crianca_sessao(responsavel)
        if crianca is None:
            flash("Selecione uma crianca antes de remover item da rotina.", "erro")
            return redirect(url_for("pagina_inicial", secao="criancas"))

        data_texto = request.form.get("data", "")
        indice_texto = str(request.form.get("indice", "")).strip()

        try:
            data_ref = _parse_data(data_texto)
            indice = int(indice_texto)
            rotina = next(
                (
                    item
                    for item in estado.rotinas
                    if item.id_crianca == crianca.id_crianca
                    and item.data_referencia == data_ref
                ),
                None,
            )
            if rotina is None:
                raise ValueError("Rotina nao encontrada para a data informada.")
            estado.servico_rotinas.remover_item(rotina=rotina, indice=indice)
            estado.persistir()
        except (TypeError, ValueError, IndexError) as erro:
            flash(str(erro), "erro")
            return redirect(url_for("pagina_inicial", secao="rotina", data_rotina=data_texto))

        flash("Item removido com sucesso.", "sucesso")
        return redirect(url_for("pagina_inicial", secao="rotina", data_rotina=data_ref.isoformat()))

    @app.get("/api")
    def raiz_api():
        return jsonify(
            {
                "mensagem": "TeApoio API ativa.",
                "rotas_uteis": {
                    "home": "/",
                    "health": "/health",
                    "responsaveis": "/responsaveis",
                    "sugestoes_rotina": "/sugestoes-rotina",
                },
            }
        )

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"})

    @app.get("/sugestoes-rotina")
    def listar_sugestoes_rotina():
        return jsonify({"sugestoes": obter_sugestoes_tea()})

    @app.get("/responsaveis")
    def listar_responsaveis():
        return jsonify(
            {
                "responsaveis": [
                    estado.responsavel_para_dict(responsavel)
                    for responsavel in estado.responsaveis
                ]
            }
        )

    @app.get("/responsaveis/<id_responsavel>")
    def obter_responsavel(id_responsavel: str):
        responsavel = estado.buscar_responsavel(id_responsavel)
        if responsavel is None:
            return _erro("Responsavel nao encontrado.", 404)

        criancas = estado.listar_criancas_responsavel(id_responsavel)
        return jsonify(
            {
                "responsavel": estado.responsavel_para_dict(responsavel),
                "criancas": [estado.crianca_para_dict(crianca) for crianca in criancas],
            }
        )

    @app.post("/responsaveis")
    def cadastrar_responsavel():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _erro("Corpo JSON invalido.", 400)

        try:
            estado.servico_cadastro.validar_email_disponivel(
                estado.responsaveis,
                payload.get("email", ""),
            )
            responsavel, perfil = estado.servico_cadastro.cadastrar_responsavel(
                nome=payload.get("nome", ""),
                data_nascimento=payload.get("data_nascimento", ""),
                email=payload.get("email", ""),
                senha=payload.get("senha", ""),
            )
        except (TypeError, ValueError) as erro:
            return _erro(str(erro), 400)

        estado.responsaveis.append(responsavel)
        estado.perfil = perfil
        estado.persistir()
        return (
            jsonify({"responsavel": estado.responsavel_para_dict(responsavel)}),
            201,
        )

    @app.post("/responsaveis/<id_responsavel>/criancas")
    def cadastrar_crianca(id_responsavel: str):
        responsavel = estado.buscar_responsavel(id_responsavel)
        if responsavel is None:
            return _erro("Responsavel nao encontrado.", 404)

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _erro("Corpo JSON invalido.", 400)

        try:
            crianca = estado.servico_cadastro.cadastrar_crianca(
                responsavel=responsavel,
                nome=payload.get("nome", ""),
                data_nascimento=payload.get("data_nascimento", ""),
                nivel_suporte=int(payload.get("nivel_suporte")),
            )
        except (TypeError, ValueError) as erro:
            return _erro(str(erro), 400)

        estado.criancas.append(crianca)
        perfil = estado.obter_perfil_responsavel(responsavel)
        estado.servico_perfil.vincular_crianca_ao_perfil(perfil, crianca)
        estado.persistir()
        return jsonify({"crianca": estado.crianca_para_dict(crianca)}), 201

    @app.get("/responsaveis/<id_responsavel>/criancas")
    def listar_criancas_responsavel(id_responsavel: str):
        responsavel = estado.buscar_responsavel(id_responsavel)
        if responsavel is None:
            return _erro("Responsavel nao encontrado.", 404)

        criancas = estado.listar_criancas_responsavel(id_responsavel)
        return jsonify({"criancas": [estado.crianca_para_dict(c) for c in criancas]})

    @app.patch("/criancas/<id_crianca>")
    def editar_crianca(id_crianca: str):
        crianca = estado.buscar_crianca(id_crianca)
        if crianca is None:
            return _erro("Crianca nao encontrada.", 404)

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _erro("Corpo JSON invalido.", 400)

        nivel_payload = payload.get("nivel_suporte", "")
        nivel_suporte = "" if nivel_payload in (None, "") else str(nivel_payload)

        try:
            estado.servico_cadastro.editar_crianca(
                crianca=crianca,
                nome=payload.get("nome", ""),
                data_nascimento=payload.get("data_nascimento", ""),
                nivel_suporte=nivel_suporte,
            )
            estado.servico_perfil.sincronizar_dados_crianca_no_perfil_sensorial(
                perfil=estado.perfil,
                crianca=crianca,
            )
        except (TypeError, ValueError) as erro:
            return _erro(str(erro), 400)

        estado.persistir()
        return jsonify({"crianca": estado.crianca_para_dict(crianca)})

    @app.delete("/criancas/<id_crianca>")
    def excluir_crianca(id_crianca: str):
        crianca = estado.buscar_crianca(id_crianca)
        if crianca is None:
            return _erro("Crianca nao encontrada.", 404)

        estado.criancas, estado.rotinas = estado.servico_perfil.excluir_crianca(
            criancas=estado.criancas,
            rotinas=estado.rotinas,
            perfil=estado.perfil,
            id_crianca=id_crianca,
        )
        estado.persistir()
        return jsonify({"mensagem": "Crianca excluida com sucesso."})

    @app.put("/criancas/<id_crianca>/perfil-sensorial")
    def criar_ou_atualizar_perfil_sensorial(id_crianca: str):
        crianca = estado.buscar_crianca(id_crianca)
        if crianca is None:
            return _erro("Crianca nao encontrada.", 404)

        responsavel = estado.buscar_responsavel(crianca.id_responsavel)
        if responsavel is None:
            return _erro("Responsavel da crianca nao encontrado.", 404)

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _erro("Corpo JSON invalido.", 400)

        perfil = estado.obter_perfil_responsavel(responsavel)

        try:
            perfil_sensorial = estado.servico_perfil.criar_ou_atualizar_perfil_sensorial(
                perfil=perfil,
                crianca=crianca,
                hipersensibilidades=_normalizar_lista_strings(
                    payload,
                    "hipersensibilidades",
                ),
                hipossensibilidades=_normalizar_lista_strings(
                    payload,
                    "hipossensibilidades",
                ),
                hiperfocos=_normalizar_lista_strings(payload, "hiperfocos"),
                seletividade_alimentar=_normalizar_lista_strings(
                    payload,
                    "seletividade_alimentar",
                ),
                estrategias_regulacao=_normalizar_lista_strings(
                    payload,
                    "estrategias_regulacao",
                ),
            )
        except (TypeError, ValueError) as erro:
            return _erro(str(erro), 400)

        estado.persistir()
        return jsonify(
            {
                "perfil_sensorial": estado.perfil_sensorial_para_dict(
                    perfil_sensorial,
                )
            }
        )

    @app.get("/criancas/<id_crianca>/perfil-sensorial")
    def obter_perfil_sensorial(id_crianca: str):
        if estado.perfil is None:
            return _erro("Perfil sensorial nao encontrado.", 404)

        perfil_sensorial = estado.perfil.obter_perfil_sensorial(id_crianca)
        if perfil_sensorial is None:
            return _erro("Perfil sensorial nao encontrado.", 404)

        return jsonify(
            {
                "perfil_sensorial": estado.perfil_sensorial_para_dict(
                    perfil_sensorial,
                )
            }
        )

    @app.get("/rotinas/<id_crianca>")
    def obter_rotina(id_crianca: str):
        crianca = estado.buscar_crianca(id_crianca)
        if crianca is None:
            return _erro("Crianca nao encontrada.", 404)

        try:
            data_ref = _parse_data(
                request.args.get("data"),
                padrao=estado.data_calendario,
            )
        except ValueError as erro:
            return _erro(str(erro), 400)

        rotina, criada = estado.servico_rotinas.obter_ou_criar_rotina(
            rotinas=estado.rotinas,
            id_crianca=id_crianca,
            data_referencia=data_ref,
        )
        if criada:
            estado.persistir()

        return jsonify({"rotina": estado.rotina_para_dict(rotina)})

    @app.post("/rotinas/<id_crianca>/itens")
    def adicionar_item_rotina(id_crianca: str):
        crianca = estado.buscar_crianca(id_crianca)
        if crianca is None:
            return _erro("Crianca nao encontrada.", 404)

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _erro("Corpo JSON invalido.", 400)

        try:
            data_ref = _parse_data(payload.get("data"), padrao=estado.data_calendario)
            rotina, _ = estado.servico_rotinas.obter_ou_criar_rotina(
                rotinas=estado.rotinas,
                id_crianca=id_crianca,
                data_referencia=data_ref,
            )
            item = estado.servico_rotinas.adicionar_item(
                rotina=rotina,
                nome_item=payload.get("nome", ""),
                horario=payload.get("horario", ""),
                observacao=str(payload.get("observacao", "")),
                tags=_normalizar_lista_strings(payload, "tags"),
            )
        except (TypeError, ValueError) as erro:
            return _erro(str(erro), 400)

        estado.persistir()
        return jsonify({"item": estado.item_para_dict(item)}), 201

    @app.patch("/rotinas/<id_crianca>/itens/<int:indice>/status")
    def marcar_status_item_rotina(id_crianca: str, indice: int):
        crianca = estado.buscar_crianca(id_crianca)
        if crianca is None:
            return _erro("Crianca nao encontrada.", 404)

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _erro("Corpo JSON invalido.", 400)

        try:
            data_ref = _parse_data(payload.get("data"), padrao=estado.data_calendario)
            rotina, _ = estado.servico_rotinas.obter_ou_criar_rotina(
                rotinas=estado.rotinas,
                id_crianca=id_crianca,
                data_referencia=data_ref,
            )
            status = estado.servico_rotinas.marcar_status(
                rotina=rotina,
                indice=indice,
                status_code=payload.get("status"),
            )
        except (TypeError, ValueError, IndexError) as erro:
            return _erro(str(erro), 400)

        estado.persistir()
        return jsonify({"indice": indice, "status": status})

    @app.delete("/rotinas/<id_crianca>/itens/<int:indice>")
    def remover_item_rotina(id_crianca: str, indice: int):
        crianca = estado.buscar_crianca(id_crianca)
        if crianca is None:
            return _erro("Crianca nao encontrada.", 404)

        try:
            data_ref = _parse_data(
                request.args.get("data"),
                padrao=estado.data_calendario,
            )
            rotina = next(
                (
                    item
                    for item in estado.rotinas
                    if item.id_crianca == id_crianca
                    and item.data_referencia == data_ref
                ),
                None,
            )
            if rotina is None:
                return _erro("Rotina nao encontrada para a data informada.", 404)

            estado.servico_rotinas.remover_item(rotina=rotina, indice=indice)
        except (TypeError, ValueError, IndexError) as erro:
            return _erro(str(erro), 400)

        estado.persistir()
        return jsonify({"mensagem": "Item removido com sucesso."})

    @app.patch("/rotinas/<id_crianca>/sentimento")
    def atualizar_sentimento_rotina(id_crianca: str):
        crianca = estado.buscar_crianca(id_crianca)
        if crianca is None:
            return _erro("Crianca nao encontrada.", 404)

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _erro("Corpo JSON invalido.", 400)

        try:
            data_ref = _parse_data(payload.get("data"), padrao=estado.data_calendario)
            rotina, _ = estado.servico_rotinas.obter_ou_criar_rotina(
                rotinas=estado.rotinas,
                id_crianca=id_crianca,
                data_referencia=data_ref,
            )
            rotina.atualizar_sentimento_dia(payload.get("sentimento", ""))
        except (TypeError, ValueError) as erro:
            return _erro(str(erro), 400)

        estado.persistir()
        return jsonify({"sentimento_dia": rotina.sentimento_dia, "sentimento_dia_info": rotina.sentimento_dia_info})

    @app.patch("/rotinas/<id_crianca>/emocao")
    def registrar_emocao_rotina(id_crianca: str):
        crianca = estado.buscar_crianca(id_crianca)
        if crianca is None:
            return _erro("Crianca nao encontrada.", 404)

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _erro("Corpo JSON invalido.", 400)

        try:
            data_ref = _parse_data(payload.get("data"), padrao=estado.data_calendario)
            rotina, _ = estado.servico_rotinas.obter_ou_criar_rotina(
                rotinas=estado.rotinas,
                id_crianca=id_crianca,
                data_referencia=data_ref,
            )
            emot = payload.get("emocao")
            escala = payload.get("escala")
            if emot is None or escala is None:
                raise ValueError("Campos 'emocao' e 'escala' sao obrigatorios.")
            rotina.registrar_emocao(emot, int(escala))
        except (TypeError, ValueError) as erro:
            return _erro(str(erro), 400)

        estado.persistir()
        return jsonify({"emocoes": rotina.obter_emocoes()}), 200

    return app
