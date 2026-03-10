from datetime import datetime

from teapoio.domain.models.Perfil import Perfil
from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.responsavel import Responsavel


class ServicoCadastro:
    """[SOLID: SRP, OCP, DIP] Casos de uso de cadastro e edicao de pessoas."""

    @staticmethod
    def cadastrar_responsavel(nome: str, data_nascimento: str, email: str, senha: str) -> tuple[Responsavel, Perfil]:
        """Cria um novo responsável e seu perfil associado."""
        responsavel = Responsavel(nome, data_nascimento, email, senha)

        perfil = Perfil(responsavel=responsavel)
        return responsavel, perfil

    @staticmethod
    def validar_email_disponivel(
        responsaveis: list[Responsavel],
        email: str,
    ) -> None:
        email_normalizado = Responsavel._validar_email(email)
        if any(item.email == email_normalizado for item in responsaveis):
            raise ValueError("Ja existe responsavel cadastrado com este email.")

    @staticmethod
    def validar_responsavel_por_id(
        responsaveis: list[Responsavel],
        id_informado: str,
    ) -> Responsavel | None:
        """Valida a existência de um responsável pelo ID informado."""
        return next(
            (r for r in responsaveis if r.id_responsavel == id_informado),
            None,
        )

    @staticmethod
    def validar_responsavel_por_credenciais(
        responsaveis: list[Responsavel],
        id_informado: str,
        senha_informada: str,
    ) -> Responsavel | None:
        cadastro = ServicoCadastro.validar_responsavel_por_id(
            responsaveis,
            id_informado,
        )
        if cadastro is None:
            return None
        if not cadastro.confere_senha(senha_informada):
            return None
        return cadastro

    @staticmethod
    def cadastrar_crianca(
        responsavel: Responsavel,
        nome: str,
        data_nascimento: str,
        nivel_suporte: int,
    ) -> Crianca:
        """Cria uma nova criança associada a um responsável."""
        return Crianca(
            nome=nome,
            data_nascimento=data_nascimento,
            responsavel=responsavel,
            nivel_suporte=nivel_suporte,
        )

    @staticmethod
    def editar_responsavel(
        responsavel: Responsavel,
        nome: str = "",
        data_nascimento: str = "",
        email: str = "",
        senha: str = "",
    ) -> Responsavel:
        """Edita os dados de um responsável existente."""
        if nome:
            responsavel.nome = Responsavel._validar_nome(nome)

        if data_nascimento:
            data_obj = Responsavel._validar_data_nascimento(data_nascimento)
            idade = datetime.now().year - data_obj.year
            if (datetime.now().month, datetime.now().day) < (data_obj.month, data_obj.day):
                idade -= 1
            if idade < 18:
                raise ValueError("Responsável deve ter pelo menos 18 anos.")
            responsavel.data_nascimento = data_obj

        if email:
            responsavel.email = Responsavel._validar_email(email)

        if senha:
            responsavel.senha = Responsavel._validar_senha(senha)

        return responsavel

    @staticmethod
    def editar_crianca(
        crianca: Crianca,
        nome: str = "",
        data_nascimento: str = "",
        nivel_suporte: str = "",
    ) -> Crianca:
        """Edita os dados de uma criança existente."""
        if nome:
            crianca.nome = Responsavel._validar_nome(nome)

        if data_nascimento:
            data_obj = Responsavel._validar_data_nascimento(data_nascimento)
            idade = datetime.now().year - data_obj.year
            if (datetime.now().month, datetime.now().day) < (data_obj.month, data_obj.day):
                idade -= 1
            if idade >= 18:
                raise ValueError("Criança não pode ser maior de idade.")
            crianca.data_nascimento = data_obj

        if nivel_suporte:
            crianca.nivel_suporte = int(nivel_suporte)

        return crianca
