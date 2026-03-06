import re


class ItemRotina:
    STATUS_PENDENTE = "Pendente"
    STATUS_CONCLUIDO = "Concluído"
    STATUS_NAO_REALIZADO = "Não Realizado"
    STATUS_PERMITIDOS = {STATUS_PENDENTE, STATUS_CONCLUIDO, STATUS_NAO_REALIZADO}
    PADRAO_HORARIO = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")

    def __init__(self, nome: str, horario: str):
        self.nome = nome
        self.horario = horario
        self.status = self.STATUS_PENDENTE

    @property
    def nome(self) -> str:
        return self.__nome

    @nome.setter
    def nome(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise TypeError("Nome do item deve ser uma string.")

        nome_limpo = valor.strip()
        if not nome_limpo:
            raise ValueError("Nome do item nao pode ser vazio.")

        self.__nome = nome_limpo

    @property
    def horario(self) -> str:
        return self.__horario

    @horario.setter
    def horario(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise TypeError("Horario deve ser uma string no formato HH:MM.")

        horario_limpo = valor.strip()
        if not self.PADRAO_HORARIO.match(horario_limpo):
            raise ValueError("Horario invalido. Use apenas numeros no formato HH:MM (24h).")

        self.__horario = horario_limpo

    @property
    def status(self) -> str:
        return self.__status

    @status.setter
    def status(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise TypeError("Status deve ser uma string.")
        if valor not in self.STATUS_PERMITIDOS:
            permitidos = sorted(self.STATUS_PERMITIDOS)
            raise ValueError(f"Status invalido. Permitidos: {permitidos}.")

        self.__status = valor

    def atualizar(self, novo_nome: str, novo_horario: str) -> None:
        self.nome = novo_nome
        self.horario = novo_horario

    def __str__(self):
        return f"[{self.horario}] {self.nome} (Status: {self.status})"

    def __repr__(self):
        return self.__str__()