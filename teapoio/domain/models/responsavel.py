from datetime import date
from teapoio.domain.models.pessoa import Pessoa
import uuid

class Responsavel(Pessoa):
    """[SOLID: LSP] Implementacao concreta substituivel de Pessoa."""


    def __init__(self, nome, data_nascimento, email, senha, id_responsavel=None, uuid_func=None):
        """Inicializa uma instância de responsável, validando seus dados."""
   
        super().__init__(nome, data_nascimento, email)
        self.senha = self._validar_senha(senha)

        if id_responsavel:
            self.id_responsavel = str(id_responsavel)
        else:
            self.id_responsavel = self._gerar_id_uuid(uuid_func)

        # Validação de maioridade
        if not self.verificar_maioridade():
            raise ValueError("Responsável deve ter pelo menos 18 anos.")


    @staticmethod
    def _validar_senha(senha: str) -> str:
        if not isinstance(senha, str):
            raise ValueError("Senha deve ser uma string.")

        senha_limpa = senha.strip()
        if len(senha_limpa) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres.")

        return senha_limpa

    def confere_senha(self, senha_informada: str) -> bool:
        if not isinstance(senha_informada, str):
            return False
        return self.senha == senha_informada.strip()

    @staticmethod
    def _gerar_id_uuid(uuid_func=None) -> str:
        """Gera um ID numérico de 6 dígitos a partir de UUID."""
        generator = uuid_func if callable(uuid_func) else uuid.uuid4
        id_uuid = generator()
        id_str = str(id_uuid).replace('-', '')
        digitos = ''.join(filter(str.isdigit, id_str))[:6]
        digitos = digitos.ljust(6, '0')
        return digitos

    def obter_status_idade(self) -> str:
        """Retorna status de idade do responsável."""
        return "Maior de idade"