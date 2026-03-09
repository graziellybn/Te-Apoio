from datetime import date
import json

from teapoio.domain.models.Perfil import Perfil
from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.item_rotina import ItemRotina
from teapoio.domain.models.perfil_sensorial import PerfilSensorial
from teapoio.domain.models.responsavel import Responsavel
from teapoio.domain.models.rotina import Rotina
from teapoio.infrastructure.persistence.Relatorio import RepositorioRelatorio


def test_repositorio_salva_e_carrega_estado_completo(tmp_path):
    """Valida se o repositório salva e carrega o estado completo mantendo a integridade dos dados"""
    arquivo = tmp_path / "estado.json"
    repositorio = RepositorioRelatorio(caminho_arquivo=arquivo)

    responsavel = Responsavel(
        nome="Maria Souza",
        data_nascimento="01/01/1985",
        email="maria@example.com",
        senha="maria123",
    )
    crianca = Crianca(
        nome="Ana Souza",
        data_nascimento="10/07/2015",
        responsavel=responsavel,
        nivel_suporte=2,
    )
    perfil = Perfil(responsavel=responsavel, criancas=[crianca])
    perfil_sensorial = PerfilSensorial(
        id_crianca=crianca.id_crianca,
        nome=crianca.nome,
        data_nascimento="10/07/2015",
        hipersensibilidades=["som alto"],
        estrategias_regulacao=["fones"],
    )
    perfil.adicionar_perfil_sensorial(perfil_sensorial)

    rotina = Rotina(id_crianca=crianca.id_crianca, data_referencia=date(2026, 3, 1))
    rotina.atualizar_sentimento_dia("bem")
    item = ItemRotina(nome="Escovar os dentes", horario="08:00", tags=["higiene", "manha"])
    item.status = ItemRotina.STATUS_CONCLUIDO
    item.observacao = "Fez com apoio visual"
    rotina.adicionar_item(item)

    repositorio.salvar_estado(
        responsaveis=[responsavel],
        criancas=[crianca],
        rotinas=[rotina],
        perfil=perfil,
        data_calendario=date(2026, 3, 2),
    )

    with arquivo.open("r", encoding="utf-8") as arquivo_json:
        payload = json.load(arquivo_json)

    assert "criancas" not in payload
    assert len(payload["responsaveis"]) == 1
    assert len(payload["responsaveis"][0]["criancas"]) == 1
    assert payload["responsaveis"][0]["criancas"][0]["id_crianca"] == crianca.id_crianca
    assert payload["responsaveis"][0]["senha"] == "maria123"

    estado = repositorio.carregar_estado()

    assert len(estado["responsaveis"]) == 1
    assert len(estado["criancas"]) == 1
    assert len(estado["rotinas"]) == 1
    assert estado["perfil"] is not None
    assert estado["data_calendario"] == date(2026, 3, 2)

    responsavel_carregado = estado["responsaveis"][0]
    crianca_carregada = estado["criancas"][0]
    rotina_carregada = estado["rotinas"][0]
    perfil_carregado = estado["perfil"]

    assert responsavel_carregado.id_responsavel == responsavel.id_responsavel
    assert crianca_carregada.id_crianca == crianca.id_crianca
    assert rotina_carregada.id_crianca == crianca.id_crianca
    assert rotina_carregada.sentimento_dia == "bem"
    assert rotina_carregada.itens[0].status == ItemRotina.STATUS_CONCLUIDO
    assert rotina_carregada.itens[0].observacao == "Fez com apoio visual"
    assert rotina_carregada.itens[0].tags == ["higiene", "manha"]
    assert perfil_carregado.obter_perfil_sensorial(crianca.id_crianca) is not None


def test_repositorio_json_invalido_retorna_estado_vazio(tmp_path):
    """Valida se o repositório retorna um estado vazio quando o arquivo JSON está inválido"""
    arquivo = tmp_path / "estado_invalido.json"
    arquivo.write_text("{ json-invalido", encoding="utf-8")

    repositorio = RepositorioRelatorio(caminho_arquivo=arquivo)
    estado = repositorio.carregar_estado()

    assert estado["responsaveis"] == []
    assert estado["criancas"] == []
    assert estado["rotinas"] == []
    assert estado["perfil"] is None
    assert isinstance(estado["data_calendario"], date)


def test_repositorio_inicializa_arquivo_vazio_com_json_valido(tmp_path):
    """Valida se o repositório inicializa um arquivo vazio com um JSON válido e retorna um estado vazio ao carregar"""
    arquivo = tmp_path / "estado_vazio.json"
    arquivo.write_text("", encoding="utf-8")

    repositorio = RepositorioRelatorio(caminho_arquivo=arquivo)
    estado = repositorio.carregar_estado()

    assert estado["responsaveis"] == []
    assert estado["criancas"] == []
    assert estado["rotinas"] == []
    assert estado["perfil"] is None
    assert isinstance(estado["data_calendario"], date)

    with arquivo.open("r", encoding="utf-8") as arquivo_json:
        payload = json.load(arquivo_json)

    assert payload["responsaveis"] == []
    assert payload["rotinas"] == []
    assert payload["perfil"] is None
    assert isinstance(payload["data_calendario"], str)


def test_repositorio_salva_aviso_quando_responsavel_nao_tem_crianca(tmp_path):
    """Valida se o repositório salva um aviso quando o responsável não possui nenhuma criança cadastrada"""
    arquivo = tmp_path / "estado_sem_crianca.json"
    repositorio = RepositorioRelatorio(caminho_arquivo=arquivo)

    responsavel = Responsavel(
        nome="Maria Souza",
        data_nascimento="01/01/1985",
        email="maria@example.com",
        senha="maria123",
    )

    repositorio.salvar_estado(
        responsaveis=[responsavel],
        criancas=[],
        rotinas=[],
        perfil=None,
        data_calendario=date(2026, 3, 2),
    )

    with arquivo.open("r", encoding="utf-8") as arquivo_json:
        """Valida se o repositório salva um aviso quando o responsável não possui nenhuma criança cadastrada"""
        payload = json.load(arquivo_json)

    responsavel_json = payload["responsaveis"][0]
    assert responsavel_json["criancas"] == []
    assert responsavel_json["aviso_crianca"] == "crianca nao cadastrada"
