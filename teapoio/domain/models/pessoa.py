from datetime import datetime
import re
import uuid


class Pessoa:
    
    def __init__(self, nome: str, data_nascimento: str):

        self.id_pessoa = self._gerar_id_uuid()
        self.nome = self._validar_nome(nome)
        self.data_nascimento = self._validar_data_nascimento(data_nascimento)
    
    
    @staticmethod
    def _gerar_id_uuid() -> str:

        # Gera um uuid4
        id_uuid = uuid.uuid4()
        
        # Converte para string e remove os hífens
        id_str = str(id_uuid).replace('-', '')
        
        # Extrai os 6 primeiros dígitos numéricos
        digitos = ''.join(filter(str.isdigit, id_str))[:6]
        
        # Se não conseguir 6 dígitos, completa com zeros
        digitos = digitos.ljust(6, '0')
        
        return digitos
    
    @staticmethod
    def _validar_nome(nome: str) -> str:

        if not isinstance(nome, str):
            raise ValueError("Nome deve ser uma string.")
        
        # Remove espaços extras
        nome_limpo = nome.strip()
        
        if not nome_limpo:
            raise ValueError("Nome não pode ser vazio.")
        
        # Valida se contém apenas letras e espaços (maiúsculas, minúsculas e acentuação)
        # Aceita: A-Z, a-z, acentos, espaços
        padrao_nome = r"^[a-záàâãéèêíïóôõöúçñA-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ\s]+$"
        
        if not re.match(padrao_nome, nome_limpo):
            raise ValueError(
                "Nome deve conter apenas letras (maiúsculas e minúsculas). "
                "Números e símbolos não são permitidos."
            )
        
        # Valida se tem pelo menos 2 caracteres (nome e sobrenome)
        if len(nome_limpo.split()) < 2:
            raise ValueError("Nome deve ter pelo menos um nome válido.")
        
        return nome_limpo
    
    @staticmethod
    def _validar_data_nascimento(data: str) -> str:

        if not isinstance(data, str):
            raise ValueError("Data deve ser uma string.")
        
   
        padrao_data = r"^(\d{2})/(\d{2})/(\d{4})$"
        
        if not re.match(padrao_data, data):
            raise ValueError("Data deve estar no formato DD/MM/YYYY com apenas números.")
        
        # Extrai dia, mês e ano
        dia, mes, ano = map(int, data.split('/'))
        
        # Valida se a data é válida
        try:
            data_obj = datetime(ano, mes, dia)
        except ValueError:
            raise ValueError("Data inválida. Verifique dia, mês e ano.")
        
        # Valida se a data não é no futuro
        if data_obj > datetime.now():
            raise ValueError("Data de nascimento não pode ser no futuro.")
        
        return data
    
    @staticmethod
    def _validar_email(email: str) -> str:

        if not isinstance(email, str):
            raise ValueError("Email deve ser uma string.")
        
        email_limpo = email.strip().lower()
        
        if not email_limpo:
            raise ValueError("Email não pode ser vazio.")
        
        # Verifica se contém @
        if '@' not in email_limpo:
            raise ValueError("Email deve conter o símbolo @.")
        
        # Padrão: usuario@(gmail|hotmail).com
        padrao_email = r"^[a-z0-9._+-]+@(gmail|hotmail)\.com$"
        
        if not re.match(padrao_email, email_limpo):
            raise ValueError(
                "Email deve estar no formato: usuario@(gmail|hotmail).com"
            )
        
        return email_limpo
    
    # ==================== MÉTODOS DE NEGÓCIO ====================
    
    def calcular_idade(self) -> int:
  
        try:
            dia, mes, ano = map(int, self.data_nascimento.split('/'))
            data_nasc = datetime(ano, mes, dia)
            hoje = datetime.now()
            
            idade = hoje.year - data_nasc.year
            
            # Ajusta se ainda não fez aniversário este ano
            if (hoje.month, hoje.day) < (data_nasc.month, data_nasc.day):
                idade -= 1
            
            return idade
        except Exception as e:
            raise ValueError(f"Erro ao calcular idade: {str(e)}")
    
    def verificar_maioridade(self) -> bool:

        return self.calcular_idade() >= 18
    
    def obter_status_idade(self) -> str:

        return "Responsável" if self.verificar_maioridade() else "Criança"
    
    # ==================== REPRESENTAÇÕES (Usadas Apenas Nos Testes) ====================
    
    def __str__(self) -> str:
        """Retorna uma representação em string da pessoa."""
        return (f"Pessoa(id={self.id_pessoa}, nome='{self.nome}', "
                f"idade={self.calcular_idade()} anos, status={self.obter_status_idade()})")
    
    def __repr__(self) -> str:
        """Retorna uma representação técnica da pessoa."""
        return (f"Pessoa(id_pessoa='{self.id_pessoa}', nome='{self.nome}', "
                f"data_nascimento='{self.data_nascimento}')")
    
    def exibir_informacoes(self) -> str:
        """
        Retorna as informações da pessoa de forma formatada.
        
        Returns:
            str: Informações formatadas
        """
        return f"""
╔════════════════════════════════════╗
║            INFORMACOES             ║
╚════════════════════════════════════╝
ID:                {self.id_pessoa}
Nome:              {self.nome}
Data Nascimento:   {self.data_nascimento}
Idade:             {self.calcular_idade()} anos
Tipo:              {self.obter_status_idade()}
╚════════════════════════════════════╝
"""