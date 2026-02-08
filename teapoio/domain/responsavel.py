from teapoio.domain.pessoa import Pessoa
from teapoio.domain.crianca import Crianca
 
class Responsavel(Pessoa):
    def __init__(self, nome, idade, cpf, email, telefone, tipo_responsavel, crianca, quant_criancas):
        super().__init__(nome, idade, cpf, email, telefone)
        self.tipo_responsavel = tipo_responsavel
        self.criancas = [crianca] if crianca else []
        self.quant_criancas = quant_criancas

    def criar_responsavel(nome, idade, cpf, email, telefone, tipo_responsavel, quant_criancas):
        return Responsavel(
            nome=nome,
            idade=idade,
            cpf=cpf,
            email=email,
            telefone=telefone,
            tipo_responsavel=tipo_responsavel,
            crianca=None,          # começa sem criança associada
            quant_criancas=quant_criancas
    )


    def adicionar_crianca(self, crianca):
        if len(self.criancas) < self.quant_criancas:
            self.criancas.append(crianca)
        else:
            raise ValueError("Número máximo de crianças atingido para este responsável.")
        
    def remover_crianca(self, crianca):
        if crianca in self.criancas:
            self.criancas.remove(crianca)
        else:
            raise ValueError("Criança não encontrada na lista deste responsável.")
    def listar_criancas(self):
        return self.criancas


