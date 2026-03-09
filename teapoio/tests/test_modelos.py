import pytest
from teapoio.domain.models.Perfil import Perfil
from teapoio.domain.models.responsavel import Responsavel
from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.perfil_sensorial import PerfilSensorial
from teapoio.domain.models.pessoa import Pessoa
from datetime import datetime


# TESTES DA CLASSE PESSOA (ABSTRATA) - VALIDAÇÃO DE DADOS
# ========================================================
class PessoaTest(Pessoa):
    def obter_status_idade(self) -> str:
        return "stub"
    

def test_nome_valido_real():
    "Valida se o nome é válido (apenas letras, acentos, espaços e hífens, e deve conter pelo menos nome e sobrenome)"
    assert Pessoa._validar_nome("João da Silva") == "João da Silva"

def test_nome_invalido_real():
    "Valida se o nome é inválido (contém números ou caracteres especiais)"
    with pytest.raises(ValueError):
        Pessoa._validar_nome("João123")


def test_data_nascimento_valida_real():
    """Valida se a data de nascimento é válida (formato DD/MM/YYYY, data real, não pode ser no futuro)"""
    data = Pessoa._validar_data_nascimento("15/08/1990")
    assert data.year == 1990
    assert data.month == 8
    assert data.day == 15

def test_data_nascimento_futuro_real():
    "Valida se a data de nascimento é inválida (data no futuro)"
    ano_futuro = datetime.now().year + 1
    with pytest.raises(ValueError):
        Pessoa._validar_data_nascimento(f"01/01/{ano_futuro}")


def test_email_valido_real():
    "Valida se o email é válido (formato correto, não vazio)"
    email = Pessoa._validar_email("maria.silva@gmail.com")
    assert email == "maria.silva@gmail.com"

def test_email_invalido_real():
    "Valida se o email é inválido (formato incorreto, sem @ ou domínio)"
    with pytest.raises(ValueError):
        Pessoa._validar_email("maria.silva#gmail.com")


def test_calcular_idade_real():
    "Valida se o cálculo da idade está correto e se a verificação de maioridade funciona"
    p = PessoaTest("Carlos Souza", "20/05/1985", "carlos@example.com")
    idade = p.calcular_idade()
    assert idade > 30  # deve ser maior que 30 anos hoje
    assert p.verificar_maioridade() is True


# ============================================================
# TESTES DA CLASSE RESPONSÁVEL - REGRAS DE NEGÓCIO

def test_responsavel_maior_de_idade():
    """Valida se o responsável é maior de idade"""
    r = Responsavel(
        nome="Maria Silva",
        data_nascimento="01/01/1980",  
        email="maria@example.com"
    )
    assert r.verificar_maioridade() is True
    assert len(r.id_responsavel) == 6


# Aparece uma mensagem de erro clara para o usuário e pede novamente até digitar uma idade válida)
def test_responsavel_menor_de_idade():
    """Valida se o responsável é menor de idade e lança um erro"""
    with pytest.raises(ValueError):
        Responsavel(
            nome="Pedro Júnior",
            data_nascimento="01/01/2010",  
            email="pedro@example.com"
        )


def test_crianca_vinculada_responsavel():
    """Valida se a criança está vinculada ao responsável e se o nível de suporte é válido"""
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


# Aparece uma mensagem de erro clara para o usuário e pede novamente até digitar uma idade válida
def test_crianca_maior_de_idade():
    """Valida se a criança é maior de idade e lança um erro"""
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

# TESTES DA CLASSE perfil sensorial - REGRAS DE NEGÓCIO
def test_perfil_sensorial_herda_dados_de_pessoa_e_vincula_id():
    """Valida se o perfil sensorial herda os dados de pessoa e vincula o ID da criança corretamente"""
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
    """Valida se o perfil adiciona e busca o perfil sensorial da criança corretamente"""
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