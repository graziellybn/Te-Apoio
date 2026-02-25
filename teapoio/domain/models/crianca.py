from datetime import date
from typing import Optional, TYPE_CHECKING
from uuid import uuid4
from teapoio.domain.models.pessoa import Pessoa

if TYPE_CHECKING:
    from teapoio.domain.models.perfil_sensorial import PerfilSensorial

class Crianca(Pessoa):
    NIVEIS_SUPORTE_VALIDOS = {"baixo", "moderado", "alto"}

    def __init__(self, nome: str, nivel_suporte: str,
                 responsavel_id: str,
                 idade: int = 0,
                 data_nascimento: Optional[date] = None,
                 id: Optional[str] = None):

        super().__init__(nome, idade)

        if nivel_suporte not in self.NIVEIS_SUPORTE_VALIDOS:
            raise ValueError(f"Nível de suporte inválido. Valores permitidos: {self.NIVEIS_SUPORTE_VALIDOS}")

        if not responsavel_id:
            raise ValueError("Toda criança deve ter um responsável vinculado.")

        self.id = id or str(uuid4())
        self.responsavel_id = responsavel_id
        self.nivel_suporte = nivel_suporte
        self.data_nascimento = data_nascimento
        self.perfil_sensorial: Optional["PerfilSensorial"] = None

    def calcular_idade(self) -> int:
        if self.data_nascimento:
            hoje = date.today()
            return hoje.year - self.data_nascimento.year - (
                (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
        return self.idade

    def __repr__(self):
        return (f"Crianca(id={self.id}, nome={self.nome}, idade={self.calcular_idade()}, "
                f"nivel_suporte={self.nivel_suporte})")

