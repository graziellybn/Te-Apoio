class ItemRotina:
    def __init__(self, nome: str, horario: str):
        self.nome = nome
        self.horario = horario
        # O status nasce sempre como "Pendente"
        self.status = "Pendente"

    def __str__(self):
        # Essa formatação é usada quando o 'print' é chamado na lista da rotina
        return f"[{self.horario}] {self.nome} (Status: {self.status})"

    def __repr__(self):
        return self.__str__()