from teapoio.application.services.servico_cadastro import ServicoCadastro
from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.responsavel import Responsavel
import pytest

# TESTES PARA O SERVICO DE CADASTRO
# =======================================

def test_servico_cadastro_cria_responsavel_e_perfil():
    """Valida se o serviço de cadastro cria um responsável e um perfil sensorial vinculado corretamente e retorna os objetos correspondentes"""
    responsavel, perfil = ServicoCadastro.cadastrar_responsavel(
        nome="Maria Silva",
        data_nascimento="01/01/1980",
        email="maria@example.com",
        senha="senha123",
    )

    assert isinstance(responsavel, Responsavel)
    assert perfil.responsavel.id_responsavel == responsavel.id_responsavel

#

def test_servico_cadastro_valida_responsavel_por_id():
    """Valida se o serviço de cadastro consegue validar e encontrar um responsável pelo ID e retorna o objeto correto"""
    responsavel, _ = ServicoCadastro.cadastrar_responsavel(
        nome="Carlos Souza",
        data_nascimento="01/01/1985",
        email="carlos@example.com",
        senha="segura123",
    )

    encontrado = ServicoCadastro.validar_responsavel_por_id(
        [responsavel],
        responsavel.id_responsavel,
    )

    assert encontrado is responsavel


def test_servico_cadastro_cria_crianca():
    """Valida se o serviço de cadastro cria uma criança vinculada ao responsável e retorna o objeto correto"""
    responsavel, _ = ServicoCadastro.cadastrar_responsavel(
        nome="Joao Silva",
        data_nascimento="01/01/1980",
        email="joao@example.com",
        senha="abc12345",
    )

    crianca = ServicoCadastro.cadastrar_crianca(
        responsavel=responsavel,
        nome="Ana Souza",
        data_nascimento="10/07/2015",
        nivel_suporte=2,
    )

    assert isinstance(crianca, Crianca)
    assert crianca.id_responsavel == responsavel.id_responsavel


def test_servico_cadastro_edita_responsavel():
    """Valida se o serviço de cadastro permite editar os dados de um responsável."""
    responsavel, _ = ServicoCadastro.cadastrar_responsavel(
        nome="Maria Silva",
        data_nascimento="01/01/1980",
        email="maria@example.com",
        senha="maria123",
    )

    ServicoCadastro.editar_responsavel(
        responsavel=responsavel,
        nome="Maria Souza",
        email="maria.souza@example.com",
    )

    assert responsavel.nome == "Maria Souza"
    assert responsavel.email == "maria.souza@example.com"


def test_servico_cadastro_edita_crianca():
    """Valida se o serviço de cadastro permite editar os dados de uma criança."""
    responsavel, _ = ServicoCadastro.cadastrar_responsavel(
        nome="Carlos Souza",
        data_nascimento="01/01/1980",
        email="carlos@example.com",
        senha="carlos123",
    )
    crianca = ServicoCadastro.cadastrar_crianca(
        responsavel=responsavel,
        nome="Ana Souza",
        data_nascimento="10/07/2015",
        nivel_suporte=2,
    )

    ServicoCadastro.editar_crianca(
        crianca=crianca,
        nome="Ana Cardoso",
        nivel_suporte="3",
    )

    assert crianca.nome == "Ana Cardoso"
    assert crianca.nivel_suporte == 3


def test_servico_cadastro_rejeita_email_duplicado():
    responsavel, _ = ServicoCadastro.cadastrar_responsavel(
        nome="Maria Silva",
        data_nascimento="01/01/1980",
        email="maria@example.com",
        senha="senha123",
    )

    with pytest.raises(ValueError, match="Ja existe responsavel cadastrado com este email"):
        ServicoCadastro.validar_email_disponivel(
            [responsavel],
            "maria@example.com",
        )


def test_servico_cadastro_permite_senha_repetida_com_emails_diferentes():
    responsavel_1, _ = ServicoCadastro.cadastrar_responsavel(
        nome="Maria Silva",
        data_nascimento="01/01/1980",
        email="maria@example.com",
        senha="senha123",
    )

    responsavel_2, _ = ServicoCadastro.cadastrar_responsavel(
        nome="Joana Souza",
        data_nascimento="01/01/1981",
        email="joana@example.com",
        senha="senha123",
    )

    assert responsavel_1.senha == responsavel_2.senha


def test_servico_cadastro_valida_credenciais_por_id_e_senha():
    responsavel, _ = ServicoCadastro.cadastrar_responsavel(
        nome="Carlos Souza",
        data_nascimento="01/01/1985",
        email="carlos@example.com",
        senha="segura123",
    )

    encontrado = ServicoCadastro.validar_responsavel_por_credenciais(
        [responsavel],
        responsavel.id_responsavel,
        "segura123",
    )

    assert encontrado is responsavel
