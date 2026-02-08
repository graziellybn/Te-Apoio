from teapoio.domain.pessoa import Pessoa

class Crianca(Pessoa):
    def __init__(self, nome, idade, cpf, email, telefone, responsavel):
        super().__init__(nome, idade, cpf, email, telefone)
        self.responsavel = responsavel
