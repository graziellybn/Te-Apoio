import re


class ItemRotina:
    """[SOLID: SRP] Entidade focada apenas em regras do item da rotina."""

    STATUS_PENDENTE = "Pendente"
    STATUS_CONCLUIDO = "Concluído"
    STATUS_NAO_REALIZADO = "Não Realizado"
    STATUS_PERMITIDOS = {STATUS_PENDENTE, STATUS_CONCLUIDO, STATUS_NAO_REALIZADO}
    PADRAO_HORARIO = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
    LIMITE_TAGS = 8
    LIMITE_TAG = 24

    def __init__(
        self,
        nome: str,
        horario: str,
        observacao: str = "",
        tags: list[str] | None = None,
    ):
        self.nome = nome
        self.horario = horario
        self.status = self.STATUS_PENDENTE
        self.observacao = observacao
        self.tags = tags

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

    @property
    def observacao(self) -> str:
        return self.__observacao

    @observacao.setter
    def observacao(self, valor: str) -> None:
        if valor is None:
            self.__observacao = ""
            return
        if not isinstance(valor, str):
            raise TypeError("Observacao deve ser uma string.")

        observacao_limpa = valor.strip()
        if len(observacao_limpa) > 280:
            raise ValueError("Observacao deve ter no maximo 280 caracteres.")

        self.__observacao = observacao_limpa

    @property
    def tags(self) -> list[str]:
        return list(self.__tags)

    @tags.setter
    def tags(self, valor: list[str] | None) -> None:
        if valor is None:
            self.__tags = []
            return
        if not isinstance(valor, list):
            raise TypeError("Tags devem ser uma lista de strings.")

        tags_limpa: list[str] = []
        vistos: set[str] = set()
        for item in valor:
            if not isinstance(item, str):
                raise TypeError("Cada tag deve ser uma string.")
            tag = item.strip().lstrip("#")
            if not tag:
                continue
            if len(tag) > self.LIMITE_TAG:
                raise ValueError(
                    f"Cada tag deve ter no maximo {self.LIMITE_TAG} caracteres."
                )

            chave = tag.casefold()
            if chave in vistos:
                continue
            vistos.add(chave)
            tags_limpa.append(tag)

        if len(tags_limpa) > self.LIMITE_TAGS:
            raise ValueError(f"Use no maximo {self.LIMITE_TAGS} tags por tarefa.")

        self.__tags = tags_limpa

    def atualizar(self, novo_nome: str, novo_horario: str) -> None:
        self.nome = novo_nome
        self.horario = novo_horario

    def atualizar_observacao(self, nova_observacao: str) -> None:
        self.observacao = nova_observacao

    def atualizar_tags(self, novas_tags: list[str] | None) -> None:
        self.tags = novas_tags

    def __str__(self):
        return f"[{self.horario}] {self.nome} (Status: {self.status})"

    def __repr__(self):
        return self.__str__()