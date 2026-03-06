from teapoio.application.services.servico_cadastro import ServicoCadastro
from teapoio.application.services.servico_perfil import ServicoPerfil
from teapoio.domain.models.Perfil import Perfil


def _criar_perfil_com_crianca() -> tuple[Perfil, object]:
    responsavel, perfil = ServicoCadastro.cadastrar_responsavel(
        nome="Carlos Souza",
        data_nascimento="01/01/1980",
        email="carlos@example.com",
    )
    crianca = ServicoCadastro.cadastrar_crianca(
        responsavel=responsavel,
        nome="Ana Souza",
        data_nascimento="10/07/2015",
        nivel_suporte=2,
    )
    ServicoPerfil.vincular_crianca_ao_perfil(perfil, crianca)
    return perfil, crianca


def test_servico_perfil_busca_crianca_no_perfil():
    perfil, crianca = _criar_perfil_com_crianca()

    encontrada = ServicoPerfil.buscar_crianca_no_perfil(perfil, crianca.id_crianca)

    assert encontrada is crianca


def test_servico_perfil_cria_ou_atualiza_perfil_sensorial():
    perfil, crianca = _criar_perfil_com_crianca()

    perfil_sensorial = ServicoPerfil.criar_ou_atualizar_perfil_sensorial(
        perfil=perfil,
        crianca=crianca,
        hipersensibilidades=["som alto"],
        hipossensibilidades=[],
        hiperfocos=["quebra-cabeca"],
        seletividade_alimentar=["textura"],
        estrategias_regulacao=["respirar"],
    )

    assert perfil_sensorial.id_crianca == crianca.id_crianca
    assert perfil.obter_perfil_sensorial(crianca.id_crianca) is not None


def test_servico_perfil_exclui_crianca_e_rotinas_relacionadas():
    perfil, crianca = _criar_perfil_com_crianca()
    from teapoio.domain.models.rotina import Rotina

    rotinas = [
        Rotina(id_crianca=crianca.id_crianca),
        Rotina(id_crianca="999999"),
    ]

    novas_criancas, novas_rotinas = ServicoPerfil.excluir_crianca(
        criancas=[crianca],
        rotinas=rotinas,
        perfil=perfil,
        id_crianca=crianca.id_crianca,
    )

    assert len(novas_criancas) == 0
    assert len(novas_rotinas) == 1
    assert novas_rotinas[0].id_crianca == "999999"


def test_servico_perfil_sincroniza_nome_e_data_no_perfil_sensorial_apos_edicao():
    perfil, crianca = _criar_perfil_com_crianca()
    ServicoPerfil.criar_ou_atualizar_perfil_sensorial(
        perfil=perfil,
        crianca=crianca,
        hipersensibilidades=["som alto"],
        hipossensibilidades=[],
        hiperfocos=[],
        seletividade_alimentar=[],
        estrategias_regulacao=[],
    )

    ServicoCadastro.editar_crianca(
        crianca=crianca,
        nome="Ana Cardoso",
        data_nascimento="11/07/2015",
    )

    sincronizado = ServicoPerfil.sincronizar_dados_crianca_no_perfil_sensorial(
        perfil=perfil,
        crianca=crianca,
    )
    perfil_sensorial = perfil.obter_perfil_sensorial(crianca.id_crianca)

    assert sincronizado is True
    assert perfil_sensorial is not None
    assert perfil_sensorial.nome == "Ana Cardoso"
    assert perfil_sensorial.data_nascimento == crianca.data_nascimento
