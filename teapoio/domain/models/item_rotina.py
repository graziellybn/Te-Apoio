class ItemRotina:
    def __init__(self, nome, descricao, ordem, recorrencia, sensibilidades=None, seletividades=None):
        self.nome = nome
        self.descricao = descricao
        self.ordem = ordem
        self.recorrencia = recorrencia  # lista de dias da semana
        self.sensibilidades = sensibilidades or []
        self.seletividades = seletividades or []
        self.execucoes = []

    def executar(self, data, observacao=""):
        self.execucoes.append({"data": data, "observacao": observacao})

