from datetime import datetime # Importação do módulo datetime para manipulação de datas.
from abc import ABC, abstractmethod # Usada para criar classes abstratas e métodos obrigatórios
import re # Importação do módulo de expressões regulares para validação de strings.


# ----------------------------- INICIALIZAÇÃO -----------------------------
class Pessoa(ABC):
    """[SOLID: LSP, ISP] Classe base abstrata para tipos de pessoa."""
    
    def __init__(self, nome: str, data_nascimento: str, email: str = None):
        """Inicializa uma instância de pessoa, validando seus dados."""
        self.nome = self._validar_nome(nome)
        self.data_nascimento = self._validar_data_nascimento(data_nascimento)
        self.email = self._validar_email(email) if email else None
    

# ------------------------ MÉTODOS DE VALIDAÇÃO -------------------------------
    @staticmethod
    def _validar_nome(nome: str) -> str:
        """Valida o nome da pessoa, garantindo que seja uma string não vazia."""
        if not isinstance(nome, str):
            raise ValueError("Nome deve ser uma string.")
        
        # Validação de caracteres permitidos (letras, acentos, espaços, hífens e apóstrofos).
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("Nome não pode ser vazio.")
        
        # Validação de formato (pelo menos nome e sobrenome).
        padrao_nome = r"^[a-zA-ZáàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ\s'-]+$"
        if not re.match(padrao_nome, nome_limpo):
            raise ValueError("Nome inválido.")
        
        # Validação de pelo menos nome e sobrenome (mínimo 2 palavras).
        if len(nome_limpo.split()) < 2:
            raise ValueError("Nome deve conter pelo menos nome e sobrenome.")
        
        return nome_limpo
    

    @staticmethod
    def _validar_data_nascimento(data: str) -> datetime:
        """Valida a data de nascimento, garantindo que seja uma string no formato DD/MM/YYYY e 
        não seja futura."""
        if not isinstance(data, str):
            raise ValueError("Data deve ser uma string.")
        
        # Validação de formato usando regex (DD/MM/YYYY).
        padrao_data = r"^(\d{2})/(\d{2})/(\d{4})$"
        if not re.match(padrao_data, data):
            raise ValueError("Data deve estar no formato DD/MM/YYYY.")
        
        dia, mes, ano = map(int, data.split('/'))
        try:
            data_obj = datetime(ano, mes, dia)
        except ValueError:
            raise ValueError("Data inválida. Verifique dia, mês e ano.")
        
        if data_obj > datetime.now():
            raise ValueError("Data de nascimento não pode ser no futuro.")
        
        return data_obj
    

    @staticmethod
    def _email_valido(email: str) -> bool:
        """Valida o formato do email."""
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None

    @staticmethod
    def _validar_email(email: str) -> str:
        """Valida o email, garantindo que seja uma string no formato correto."""
        if not isinstance(email, str):
            raise ValueError("Email deve ser uma string.")
        
        # Validação de formato usando regex.
        email_limpo = email.strip().lower()
        if not email_limpo:
            raise ValueError("Email não pode ser vazio.")
        
        if not Pessoa._email_valido(email_limpo):
            raise ValueError("Email inválido. Use o formato usuario@dominio.com")
        
        return email_limpo
    

# ------------------------ MÉTODOS DE VERIFICAÇÃO -------------------------------

    def calcular_idade(self) -> int:
        """Calcula a idade da pessoa com base na data de nascimento."""
        hoje = datetime.now()
        idade = hoje.year - self.data_nascimento.year
        if (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day):
            idade -= 1
        return idade
    
    def verificar_maioridade(self) -> bool:
        """Verifica se a pessoa é maior de idade (18 anos ou mais)."""
        return self.calcular_idade() >= 18
    
# ----------------------------- MÉTODOS ABSTRATOS -----------------------------
    @abstractmethod
    def obter_status_idade(self) -> str:
        """Retorna uma string indicando o status de idade da pessoa (ex: 'Menor de idade', 'Maior de idade')."""
        pass    