from datetime import date
from teapoio.domain.models.pessoa import Pessoa
import uuid

class Responsavel(Pessoa):
    def __init__(self, nome, data_nascimento, email, id_responsavel=None, uuid_func=None):
        super().__init__(nome, data_nascimento, email)

        if id_responsavel:
            self.id_responsavel = str(id_responsavel)
        else:
            self.id_responsavel = self._gerar_id_uuid(uuid_func)

        # Validação de maioridade
        if not self.verificar_maioridade():
            raise ValueError("Responsável deve ter pelo menos 18 anos.")

    @staticmethod
    def _gerar_id_uuid(uuid_func=None) -> str:
        generator = uuid_func if callable(uuid_func) else uuid.uuid4
        id_uuid = generator()
        id_str = str(id_uuid).replace('-', '')
        digitos = ''.join(filter(str.isdigit, id_str))[:6]
        digitos = digitos.ljust(6, '0')
        return digitos

    def obter_status_idade(self) -> str:
        try:
            return "Maior de idade" if self.verificar_maioridade() else "Menor de idade"
        except Exception:
            return "Idade desconhecida"