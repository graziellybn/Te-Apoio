from datetime import date # Importação de date para manipulação de datas.
from teapoio.domain.models.pessoa import Pessoa # Importação da classe base Pessoa para herança.
import uuid # Importação do módulo uuid para geração de identificadores únicos.


#-------------------------- INICIALIZAÇÃO + VALIDAÇÕES BÁSICAS ----------------------------------
class Responsavel(Pessoa):
    """[SOLID: LSP] Implementacao concreta substituivel de Pessoa."""

    def __init__(self, nome, data_nascimento, email, id_responsavel=None, uuid_func=None):
        """Inicializa uma instância de responsável, validando seus dados."""
   
        #Validação de senha
        super().__init__(nome, data_nascimento, email)
        self.senha = self._validar_senha(senha)

        #Atribuição/geração do ID do responsável
        if id_responsavel:
            self.id_responsavel = str(id_responsavel)
        else:
            self.id_responsavel = self._gerar_id_uuid(uuid_func)

        # Validação de maioridade
        if not self.verificar_maioridade():
            raise ValueError("Responsável deve ter pelo menos 18 anos.")


#----------------------------- MÉTODOS AUXILIARES DE VALIDAÇÃO ----------------------------
    @staticmethod
    def _validar_senha(senha: str) -> str:
        """Valida a senha do responsável, garantindo que seja uma string com pelo menos 6 caracteres."""
        if not isinstance(senha, str):
            raise ValueError("Senha deve ser uma string.")

        senha_limpa = senha.strip()
        if len(senha_limpa) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres.")

        return senha_limpa


#----------------------------- MÉTODOS UTILITÁRIOS ----------------------------
    def confere_senha(self, senha_informada: str) -> bool:
        """"Verifica se a senha informada corresponde à senha do responsável."""
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

#----------------------------- REGRAS DE NEGÓCIO ----------------------------
    def obter_status_idade(self) -> str:
        """Retorna uma string indicando se o responsável é menor ou maior de idade."""
        try:
            return "Maior de idade" if self.verificar_maioridade() else "Menor de idade"
        except Exception:
            return "Idade desconhecida"