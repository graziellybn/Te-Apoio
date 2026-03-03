import pytest
from teapoio.domain.models.Perfil import Perfil
from teapoio.domain.models.responsavel import Responsavel
from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.perfil_sensorial import PerfilSensorial


def test_responsavel_maior_de_idade():
    r = Responsavel(
        nome="Maria Silva",
        data_nascimento="01/01/1980",  
        email="maria@example.com"
    )
    assert r.verificar_maioridade() is True
    assert len(r.id_responsavel) == 6


def test_responsavel_menor_de_idade():
    with pytest.raises(ValueError):
        Responsavel(
            nome="Pedro Júnior",
            data_nascimento="01/01/2010",  
            email="pedro@example.com"
        )


def test_crianca_vinculada_responsavel():
    r = Responsavel(
        nome="Carlos Souza",
        data_nascimento="20/05/1985",  
        email="carlos@example.com"
    )
    c = Crianca(
        nome="Ana Souza",
        data_nascimento="10/07/2015",  
        responsavel=r,
        nivel_suporte=2
    )
    assert c.id_responsavel == r.id_responsavel
    assert c.nivel_suporte == 2
    assert c.obter_status_idade() == "Menor de idade"


def test_crianca_maior_de_idade():
    r = Responsavel(
        nome="João Silva",
        data_nascimento="15/03/1980",  
        email="joao@example.com"
    )
    with pytest.raises(ValueError):
        Crianca(
            nome="Lucas Souza",
            data_nascimento="15/03/2000",  
            responsavel=r,
            nivel_suporte=1
        )


def test_perfil_sensorial_herda_dados_de_pessoa_e_vincula_id():
    perfil = PerfilSensorial(
        id_crianca="123456",
        nome="Ana Souza",
        data_nascimento="10/07/2015",
        hipersensibilidades=["som alto"],
    )

    assert perfil.id_crianca == "123456"
    assert perfil.nome == "Ana Souza"
    assert perfil.hipersensibilidades == ["som alto"]


def test_perfil_adiciona_e_busca_perfil_sensorial_da_crianca():
    r = Responsavel(
        nome="Carlos Souza",
        data_nascimento="20/05/1985",
        email="carlos@example.com"
    )
    c = Crianca(
        nome="Ana Souza",
        data_nascimento="10/07/2015",
        responsavel=r,
        nivel_suporte=2
    )
    perfil = Perfil(responsavel=r, criancas=[c])

    perfil_sensorial = PerfilSensorial(
        id_crianca=c.id_crianca,
        nome=c.nome,
        data_nascimento="10/07/2015",
        hiperfocos=["quebra-cabeça"],
    )
    perfil.adicionar_perfil_sensorial(perfil_sensorial)

    assert perfil.obter_perfil_sensorial(c.id_crianca) is not None
    assert perfil.obter_perfil_sensorial(c.id_crianca).hiperfocos == ["quebra-cabeça"]