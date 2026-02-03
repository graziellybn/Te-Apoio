
class Crianca:
    def __init__(self, nome, idade, genero):
        self.nome = nome
        self.idade = idade
        self.genero = genero

    def informacoes_crianca(self):
        return f"Crianca(nome={self.nome}, idade={self.idade}, genero={self.genero})"

c1 = Crianca("Ana", 7, "Feminino")
print(c1.informacoes_crianca())