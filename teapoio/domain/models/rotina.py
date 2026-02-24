from teapoio.domain.models.item_rotina import ItemRotina

class Rotina:
    def __init__(self, nome, descricao, crianca, responsavel, dias_semana=None):
        self.nome = nome
        self.descricao = descricao
        self.crianca = crianca
        self.responsavel = responsavel
        self.dias_semana = dias_semana or []
        self.itens = [] # item rotina
        self.execucoes = []

    def adicionar_item(self, item: ItemRotina):
        self.itens.append(item)

    def registrar_execucao(self, data, itens_realizados, observacoes=""):
        execucao = {"data": data, "itens_realizados": itens_realizados, "observacoes": observacoes}
        self.execucoes.append(execucao)

class DiasSemana:
    SEGUNDA = "Segunda-feira"
    TERCA = "Terça-feira"
    QUARTA = "Quarta-feira"
    QUINTA = "Quinta-feira"
    SEXTA = "Sexta-feira"
    SABADO = "Sábado"
    DOMINGO = "Domingo"

    def validar(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome da rotina é obrigatório.")

        if not self.dias_semana:
            raise ValueError("A rotina deve ter pelo menos um dia da semana.")

        if not self.itens:
            raise ValueError("A rotina deve ter pelo menos um item.")
        