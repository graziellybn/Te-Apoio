import pytest
from teapoio.domain.models.responsavel import Responsavel
from teapoio.domain.models.crianca import Crianca

# -------------------------------
# Testes para Responsavel
# -------------------------------

def test_responsavel_maior_de_idade_valido():
    r = Responsavel("João Silva", "10/05/1990", "joao@gmail.com")
    assert r.nome == "João Silva"
    assert r.verificar_maioridade() is True
    assert r.obter_status_idade() == "Maior de idade"
    assert r.id_responsavel is not None

def test_responsavel_menor_de_idade_invalido():
    with pytest.raises(ValueError, match="Responsável deve ter pelo menos 18 anos."):
        Responsavel("Maria Souza", "15/03/2010", "maria@hotmail.com")

# -------------------------------
# Testes para Crianca
# -------------------------------

def test_crianca_valida_vinculada_responsavel():
    r = Responsavel("Carlos Pereira", "20/01/1980", "carlos@gmail.com")
    c = Crianca("Pedro Pereira", "15/03/2015", r)
    assert c.nome == "Pedro Pereira"
    assert c.verificar_maioridade() is False
    assert c.obter_status_idade() == "Menor de idade"
    assert c.id_responsavel == r.id_responsavel

def test_crianca_maior_de_idade_invalida():
    r = Responsavel("Ana Costa", "01/01/1985", "ana@gmail.com")
    with pytest.raises(ValueError, match="Criança não pode ser maior de idade."):
        Crianca("Carlos Costa", "01/01/1990", r)

def test_crianca_vinculo_invalido():
    with pytest.raises(ValueError, match="Criança deve estar vinculada a um Responsável válido"):
        Crianca("José Silva", "10/10/2010", None)