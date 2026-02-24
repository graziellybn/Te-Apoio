from dataclasses import dataclass, field
from datetime import time
from uuid import uuid4


@dataclass
class ItemRotina:

    nome: str
    descricao: str | None = None
    horario_inicio: time | None = None
    horario_fim: time | None = None
    ordem: int = 1
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        self.validar()

    def validar(self) -> None:
        # Nome é obrigatório
        if not self.nome or not self.nome.strip():
            raise ValueError("O nome do item da rotina é obrigatório.")

        # Ordem precisa ser positiva
        if self.ordem < 1:
            raise ValueError("A ordem do item deve ser maior ou igual a 1.")

        if self.horario_fim is not None and self.horario_inicio is None:
            raise ValueError(
                "Não é permitido informar apenas horário de fim sem horário de início."
            )

        # Se ambos existirem, fim não pode ser antes do início
        if self.horario_inicio is not None and self.horario_fim is not None:
            if self.horario_fim < self.horario_inicio:
                raise ValueError("O horário de fim não pode ser anterior ao horário de início.")

    def atualizar_dados(
        self,
        nome: str | None = None,
        descricao: str | None = None,
        horario_inicio: time | None = None,
        horario_fim: time | None = None,
    ) -> None:

        if nome is not None:
            self.nome = nome
        self.descricao = descricao
        self.horario_inicio = horario_inicio
        self.horario_fim = horario_fim
        self.validar()