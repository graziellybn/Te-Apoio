import uuid
from teapoio.domain.models.pessoa import Pessoa
from teapoio.domain.models.responsavel import Responsavel

class Crianca(Pessoa):
    def __init__(self, nome, data_nascimento, responsavel, id_crianca=None, uuid_func=None):
        super().__init__(nome, data_nascimento)

        generator = uuid_func if callable(uuid_func) else uuid.uuid4
        self.id_crianca = str(id_crianca) if id_crianca else str(generator())

        if isinstance(responsavel, Responsavel):
            self.id_responsavel = responsavel.id_responsavel
        elif isinstance(responsavel, str):
            self.id_responsavel = responsavel
        else:
            raise ValueError("Criança deve estar vinculada a um Responsável válido")

        # Validação extra: garantir que seja menor de idade
        if self.verificar_maioridade():
            raise ValueError("Criança não pode ser maior de idade.")

    def obter_status_idade(self) -> str:
        try:
            return "Maior de idade" if self.verificar_maioridade() else "Menor de idade"
        except Exception:
            return "Idade desconhecida"