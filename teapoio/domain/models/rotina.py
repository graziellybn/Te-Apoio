class Rotina:
    def __init__(self, nome, descricao, crianca, responsavel):
        self.nome = nome
        self.descricao = descricao
        self.crianca = crianca
        self.responsavel = responsavel
        self.itens = [] # item rotina
        self.execucoes = []

    def adicionar_item(self, item: ItemRotina):
        self.itens.append(item)

    def registrar_execucao(self, data, itens_realizados, observacoes=""):
        execucao = {"data": data, "itens_realizados": itens_realizados, "observacoes": observacoes}
        self.execucoes.append(execucao)
