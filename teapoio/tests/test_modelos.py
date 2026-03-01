import pytest
from teapoio.domain.models.responsavel import Responsavel
from teapoio.domain.models.crianca import Crianca


def test_responsavel_maior_de_idade():
    r = Responsavel(
        nome="Maria Silva",
        data_nascimento="01/01/1980",  # ✅ formato DD/MM/YYYY
        email="maria@example.com"
    )
    assert r.verificar_maioridade() is True
    assert len(r.id_responsavel) == 6


def test_responsavel_menor_de_idade():
    with pytest.raises(ValueError):
        Responsavel(
            nome="Pedro Júnior",
            data_nascimento="01/01/2010",  # ✅ formato DD/MM/YYYY
            email="pedro@example.com"
        )


def test_crianca_vinculada_responsavel():
    r = Responsavel(
        nome="Carlos Souza",
        data_nascimento="20/05/1985",  # ✅ formato DD/MM/YYYY
        email="carlos@example.com"
    )
    c = Crianca(
        nome="Ana Souza",
        data_nascimento="10/07/2015",  # ✅ formato DD/MM/YYYY
        responsavel=r,
        nivel_suporte=2
    )
    assert c.id_responsavel == r.id_responsavel
    assert c.nivel_suporte == 2
    assert c.obter_status_idade() == "Menor de idade"


def test_crianca_maior_de_idade():
    r = Responsavel(
        nome="João Silva",
        data_nascimento="15/03/1980",  # ✅ formato DD/MM/YYYY
        email="joao@example.com"
    )
    with pytest.raises(ValueError):
        Crianca(
            nome="Lucas Souza",
            data_nascimento="15/03/2000",  # ✅ formato DD/MM/YYYY
            responsavel=r,
            nivel_suporte=1
        )