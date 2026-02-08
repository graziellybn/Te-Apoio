from teapoio.domain.pessoa import Pessoa

class Crianca(Pessoa):
    def __init__(self, nome, idade, cpf, email, telefone, responsavel, nivel_suporte):
        super().__init__(nome, idade, cpf, email, telefone)
        
        self.responsavel = responsavel
        self.nivel_suporte = nivel_suporte
