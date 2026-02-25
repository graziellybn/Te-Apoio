import json
import os
from datetime import date
from teapoio.domain.models.responsavel import Responsavel
from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.perfil_sensorial import PerfilSensorial
from teapoio.domain.events.eventos import Evento

ARQUIVO_DADOS = os.path.join(os.path.dirname(__file__), "..", "..", "..", "dados.json")


def _caminho_dados() -> str:
    return os.path.abspath(ARQUIVO_DADOS)


def _carregar_dados() -> dict:
    caminho = _caminho_dados()
    if not os.path.exists(caminho):
        return {"responsaveis": [], "criancas": [], "eventos": []}
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"responsaveis": [], "criancas": [], "eventos": []}


def _salvar_dados(dados: dict) -> None:
    caminho = _caminho_dados()
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# ── Responsável ──────────────────────────────────────────────

def salvar_responsavel(resp: Responsavel) -> None:
    dados = _carregar_dados()
    entrada = {
        "id": resp.id,
        "nome": resp.nome,
        "email": resp.email or "",
        "telefone": resp.telefone or "",
        "tipo_responsavel": resp.tipo_responsavel,
        "endereco": resp.endereco or "",
        "quant_criancas": resp.quant_criancas,
    }
    for i, r in enumerate(dados["responsaveis"]):
        if r["id"] == resp.id:
            dados["responsaveis"][i] = entrada
            _salvar_dados(dados)
            return
    dados["responsaveis"].append(entrada)
    _salvar_dados(dados)


def carregar_responsaveis() -> list[Responsavel]:
    dados = _carregar_dados()
    resultado = []
    for r in dados.get("responsaveis", []):
        resp = Responsavel(
            id=r["id"],
            nome=r["nome"],
            email=r.get("email", ""),
            telefone=r.get("telefone", ""),
            tipo_responsavel=r.get("tipo_responsavel", ""),
            endereco=r.get("endereco") or None,
            quant_criancas=r.get("quant_criancas", 1),
        )
        resultado.append(resp)
    return resultado


# ── Criança ──────────────────────────────────────────────────

def salvar_crianca(crianca: Crianca) -> None:
    dados = _carregar_dados()
    perfil = crianca.perfil_sensorial.to_dict() if crianca.perfil_sensorial else None
    entrada = {
        "id": crianca.id,
        "nome": crianca.nome,
        "data_nascimento": crianca.data_nascimento.strftime("%d/%m/%Y") if crianca.data_nascimento else "",
        "nivel_suporte": crianca.nivel_suporte,
        "responsavel_id": crianca.responsavel_id,
        "perfil_sensorial": perfil,
    }
    for i, c in enumerate(dados["criancas"]):
        if c["id"] == crianca.id:
            dados["criancas"][i] = entrada
            _salvar_dados(dados)
            return
    dados["criancas"].append(entrada)
    _salvar_dados(dados)


def carregar_criancas() -> list[Crianca]:
    dados = _carregar_dados()
    resultado = []
    for c in dados.get("criancas", []):
        dn = None
        if c.get("data_nascimento"):
            try:
                dia, mes, ano = map(int, c["data_nascimento"].split("/"))
                dn = date(ano, mes, dia)
            except Exception:
                pass
        crianca = Crianca(
            id=c["id"],
            nome=c["nome"],
            nivel_suporte=c.get("nivel_suporte", "baixo"),
            responsavel_id=c.get("responsavel_id", ""),
            data_nascimento=dn,
        )
        if c.get("perfil_sensorial"):
            crianca.perfil_sensorial = PerfilSensorial.from_dict(c["perfil_sensorial"])
        resultado.append(crianca)
    return resultado


def excluir_crianca(crianca_id: str) -> None:
    dados = _carregar_dados()
    dados["criancas"] = [c for c in dados["criancas"] if c["id"] != crianca_id]
    _salvar_dados(dados)


# ── Eventos ──────────────────────────────────────────────────

def salvar_evento(evento: Evento) -> None:
    dados = _carregar_dados()
    entrada = evento.to_dict()
    for i, e in enumerate(dados.get("eventos", [])):
        if e["id"] == evento.id:
            dados["eventos"][i] = entrada
            _salvar_dados(dados)
            return
    dados.setdefault("eventos", []).append(entrada)
    _salvar_dados(dados)


def carregar_eventos() -> list[Evento]:
    dados = _carregar_dados()
    resultado = []
    for e in dados.get("eventos", []):
        try:
            resultado.append(Evento.from_dict(e))
        except Exception:
            pass
    return resultado


def excluir_evento(evento_id: str) -> None:
    dados = _carregar_dados()
    dados["eventos"] = [e for e in dados.get("eventos", []) if e["id"] != evento_id]
    _salvar_dados(dados)
