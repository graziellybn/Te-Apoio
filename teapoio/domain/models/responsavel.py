# teapoio/domain/models/responsavel.py
from typing import TYPE_CHECKING
from uuid import uuid4
from teapoio.domain.models.pessoa import Pessoa

if TYPE_CHECKING:
    from teapoio.domain.models.crianca import Crianca

class Responsavel(Pessoa):
    def __init__(self, nome, email, telefone, tipo_responsavel,
        endereco: str | None = None, quant_criancas=1,
        idade: int | None = None, cpf: str | None = None,
        id: str | None = None,
    ):
        super().__init__(nome, idade, cpf, email, telefone)
        self.id = id or str(uuid4())
        self.tipo_responsavel = tipo_responsavel
        self.endereco = endereco
        self.criancas: list["Crianca"] = []
        self.quant_criancas = quant_criancas

    def adicionar_crianca(self, crianca: "Crianca"):
        if len(self.criancas) < self.quant_criancas:
            self.criancas.append(crianca)
        else:
            raise ValueError("Número máximo de crianças atingido para este responsável.")

    def remover_crianca_por_id(self, crianca_id: str):
        for c in self.criancas:
            if c.id == crianca_id:
                self.criancas.remove(c)
                return
        raise ValueError("Criança não encontrada na lista deste responsável.")

    def listar_criancas(self) -> list["Crianca"]:
        return self.criancas
