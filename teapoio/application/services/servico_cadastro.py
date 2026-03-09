from datetime import datetime

from teapoio.domain.models.Perfil import Perfil
from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.responsavel import Responsavel


class ServicoCadastro:
    """[SOLID: SRP, OCP, DIP] Casos de uso de cadastro e edicao de pessoas."""

    @staticmethod
    def cadastrar_responsavel(nome: str, data_nascimento: str, email: str) -> tuple[Responsavel, Perfil]:
        responsavel = Responsavel(nome, data_nascimento, email)
        perfil = Perfil(responsavel=responsavel)
        return responsavel, perfil

    @staticmethod
    def validar_responsavel_por_id(
        responsaveis: list[Responsavel],
        id_informado: str,
    ) -> Responsavel | None:
        return next(
            (r for r in responsaveis if r.id_responsavel == id_informado),
            None,
        )

    @staticmethod
    def cadastrar_crianca(
        responsavel: Responsavel,
        nome: str,
        data_nascimento: str,
        nivel_suporte: int,
    ) -> Crianca:
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
    ) -> Responsavel:
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

        return responsavel

    @staticmethod
    def editar_crianca(
        crianca: Crianca,
        nome: str = "",
        data_nascimento: str = "",
        nivel_suporte: str = "",
    ) -> Crianca:
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
