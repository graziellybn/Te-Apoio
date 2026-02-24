from datetime import date
from typing import Optional
from uuid import uuid4

from teapoio.domain.models.pessoa import Pessoa
from teapoio.domain.models.responsavel import Responsavel


class Crianca(Pessoa):
    NIVEIS_SUPORTE_VALIDOS = {"baixo", "moderado", "alto"}

    def __init__(self, nome: str, idade: int,
                 responsavel: Responsavel, nivel_suporte: str,
                 data_nascimento: Optional[date] = None,
                 email: str | None = None,
                 telefone: str | None = None):

        super().__init__(nome, idade, cpf=None, email=email, telefone=telefone)

        if idade < 0 or idade > 17:
            raise ValueError("Idade da criança deve estar entre 0 e 17 anos.")

        if not responsavel:
            raise ValueError("Toda criança deve ter um responsável vinculado.")

        if nivel_suporte not in self.NIVEIS_SUPORTE_VALIDOS:
            raise ValueError(f"Nível de suporte inválido. Valores permitidos: {self.NIVEIS_SUPORTE_VALIDOS}")

        self.id = str(uuid4())
        self.responsavel = responsavel
        self.nivel_suporte = nivel_suporte
        self.data_nascimento = data_nascimento

    def calcular_idade(self) -> int:
        if self.data_nascimento:
            hoje = date.today()
            return hoje.year - self.data_nascimento.year - (
                (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
        return self.idade

    def __repr__(self):
        return (f"Crianca(nome={self.nome}, idade={self.calcular_idade()}, "
                f"responsavel={self.responsavel.nome}, nivel_suporte={self.nivel_suporte})")
