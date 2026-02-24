# teapoio/domain/models/responsavel.py
from typing import TYPE_CHECKING
from teapoio.domain.models.pessoa import Pessoa

if TYPE_CHECKING:
    from teapoio.domain.models.crianca import Crianca

class Responsavel(Pessoa):
    def __init__(self, nome, idade, cpf, email, telefone, tipo_responsavel,
        endereco: str | None = None, crianca=None, quant_criancas=0,
    ):

        # Validação: responsável deve ser maior de idade (>= 18)
        if idade is None or idade < 18:
            raise ValueError("Responsável deve ter 18 anos ou mais.")

        super().__init__(nome, idade, cpf, email, telefone)
        self.tipo_responsavel = tipo_responsavel
        self.endereco = endereco
        self.criancas: list["Crianca"] = [crianca] if crianca else []
        self.quant_criancas = quant_criancas

    @staticmethod
    def criar_responsavel(nome, idade, cpf, email, telefone, tipo_responsavel, quant_criancas,
        endereco: str | None = None,
    ):
        return Responsavel(
            nome=nome,
            idade=idade,
            cpf=cpf,
            email=email,
            telefone=telefone,
            tipo_responsavel=tipo_responsavel,
            endereco=endereco,
            crianca=None,          # começa sem criança associada
            quant_criancas=quant_criancas
        )

    def adicionar_crianca(self, crianca: "Crianca"):
        if len(self.criancas) < self.quant_criancas:
            self.criancas.append(crianca)
        else:
            raise ValueError("Número máximo de crianças atingido para este responsável.")

    def remover_crianca(self, crianca: "Crianca"):
        if crianca in self.criancas:
            self.criancas.remove(crianca)
        else:
            raise ValueError("Criança não encontrada na lista deste responsável.")

    def listar_criancas(self) -> list["Crianca"]:
        return self.criancas
