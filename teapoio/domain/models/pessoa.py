from datetime import datetime
from abc import ABC, abstractmethod
import re

class Pessoa(ABC):
    """Classe base abstrata para Pessoa com atributos e métodos comuns."""
    
    def __init__(self, nome: str, data_nascimento: str, email: str = None):
        self.nome = self._validar_nome(nome)
        self.data_nascimento = self._validar_data_nascimento(data_nascimento)
        self.email = self._validar_email(email) if email else None
    
    @staticmethod
    def _validar_nome(nome: str) -> str:
        if not isinstance(nome, str):
            raise ValueError("Nome deve ser uma string.")
        
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("Nome não pode ser vazio.")
        
        padrao_nome = r"^[a-zA-ZáàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ\s'-]+$"
        if not re.match(padrao_nome, nome_limpo):
            raise ValueError("Nome inválido.")
        
        if len(nome_limpo.split()) < 2:
            raise ValueError("Nome deve conter pelo menos nome e sobrenome.")
        
        return nome_limpo
    
    @staticmethod
    def _validar_data_nascimento(data: str) -> datetime:
        if not isinstance(data, str):
            raise ValueError("Data deve ser uma string.")
        
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
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, email) is not None

    @staticmethod
    def _validar_email(email: str) -> str:
        if not isinstance(email, str):
            raise ValueError("Email deve ser uma string.")
        
        email_limpo = email.strip().lower()
        if not email_limpo:
            raise ValueError("Email não pode ser vazio.")
        
        if not Pessoa._email_valido(email_limpo):
            raise ValueError("Email inválido. Use o formato usuario@dominio.com")
        
        return email_limpo
    
    def calcular_idade(self) -> int:
        hoje = datetime.now()
        idade = hoje.year - self.data_nascimento.year
        if (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day):
            idade -= 1
        return idade
    
    def verificar_maioridade(self) -> bool:
        return self.calcular_idade() >= 18
    
    @abstractmethod
    def obter_status_idade(self) -> str:
        pass    