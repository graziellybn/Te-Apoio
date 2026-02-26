from datetime import datetime
from abc import ABC, abstractmethod
import re


class Pessoa(ABC):
    """Classe base abstrata para Pessoa com atributos e métodos comuns."""
    
    def __init__(self, nome: str, data_nascimento: str):
        self.nome = self._validar_nome(nome)
        self.data_nascimento = self._validar_data_nascimento(data_nascimento)
        # ID será gerado pelas subclasses
    
    @staticmethod
    def _validar_nome(nome: str) -> str:
        """Valida se o nome está em formato correto."""
        if not isinstance(nome, str):
            raise ValueError("Nome deve ser uma string.")
        
        nome_limpo = nome.strip()
        
        if not nome_limpo:
            raise ValueError("Nome não pode ser vazio.")
        
        padrao_nome = r"^[a-záàâãéèêíïóôõöúçñA-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ\s]+$"
        
        if not re.match(padrao_nome, nome_limpo):
            raise ValueError(
                "Nome deve conter apenas letras (maiúsculas e minúsculas). "
                "Números e símbolos não são permitidos."
            )
        
        if len(nome_limpo.split()) < 2:
            raise ValueError("Nome deve ter pelo menos um nome válido.")
        
        return nome_limpo
    
    @staticmethod
    def _validar_data_nascimento(data: str) -> str:
        """Valida se a data de nascimento está em formato correto."""
        if not isinstance(data, str):
            raise ValueError("Data deve ser uma string.")
        
        padrao_data = r"^(\d{2})/(\d{2})/(\d{4})$"
        
        if not re.match(padrao_data, data):
            raise ValueError("Data deve estar no formato DD/MM/YYYY com apenas números.")
        
        dia, mes, ano = map(int, data.split('/'))
        
        try:
            data_obj = datetime(ano, mes, dia)
        except ValueError:
            raise ValueError("Data inválida. Verifique dia, mês e ano.")
        
        if data_obj > datetime.now():
            raise ValueError("Data de nascimento não pode ser no futuro.")
        
        return data
    
    @staticmethod
    def _email_valido(email: str) -> bool:
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None

    @staticmethod
    def _validar_email(email: str) -> str:
        """Valida se o email está em formato correto."""
        if not isinstance(email, str):
            raise ValueError("Email deve ser uma string.")
        
        email_limpo = email.strip().lower()
        
        if not email_limpo:
            raise ValueError("Email não pode ser vazio.")
        
        if not Pessoa._email_valido(email_limpo):
            raise ValueError("Email inválido. Use o formato usuario@dominio.com")
        
        return email_limpo
    
    # ==================== MÉTODOS DE NEGÓCIO ====================
    
    def calcular_idade(self) -> int:
        """Calcula a idade da pessoa baseado na data de nascimento."""
        try:
            dia, mes, ano = map(int, self.data_nascimento.split('/'))
            data_nasc = datetime(ano, mes, dia)
            hoje = datetime.now()
            
            idade = hoje.year - data_nasc.year
            
            if (hoje.month, hoje.day) < (data_nasc.month, data_nasc.day):
                idade -= 1
            
            return idade
        except Exception as e:
            raise ValueError(f"Erro ao calcular idade: {str(e)}")
    
    def verificar_maioridade(self) -> bool:
        """Verifica se a pessoa é maior de idade (>= 18 anos)."""
        return self.calcular_idade() >= 18
    
    @abstractmethod
    def obter_status_idade(self) -> str:
        pass
    