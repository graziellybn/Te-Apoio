from datetime import date, datetime
from typing import Iterable, List, Protocol

from teapoio.domain.models.evolucao import Evolucao
from teapoio.domain.models.item_rotina import ItemRotina


class ResolvedorStatusRotina(Protocol):
    """[SOLID: ISP, DIP] Contrato minimo para resolver codigo de status."""

    def resolver(self, status_code: int | str) -> str:
        """Retorna um status valido de ItemRotina para o codigo informado."""


class CalculadoraEvolucaoRotina(Protocol):
    """[SOLID: ISP, DIP] Contrato minimo para calcular evolucao da rotina."""

    def calcular(self, itens: Iterable[ItemRotina]) -> Evolucao:
        """Retorna uma Evolucao calculada para os itens informados."""


class ResolvedorStatusPadrao:
    """[SOLID: OCP, DIP] Implementacao padrao de resolucao de status."""

    MAPA_STATUS = {
        1: ItemRotina.STATUS_CONCLUIDO,
        2: ItemRotina.STATUS_NAO_REALIZADO,
        3: ItemRotina.STATUS_PENDENTE,
    }

    def resolver(self, status_code: int | str) -> str:
        if isinstance(status_code, str):
            codigo_limpo = status_code.strip()
            if not codigo_limpo.isdigit():
                raise ValueError("Codigo de status deve ser numerico (1, 2 ou 3).")
            status_code = int(codigo_limpo)
        elif not isinstance(status_code, int):
            raise TypeError("Codigo de status deve ser inteiro ou string numerica.")

        if status_code not in self.MAPA_STATUS:
            raise ValueError("Codigo de status invalido. Use 1, 2 ou 3.")

        return self.MAPA_STATUS[status_code]


class CalculadoraEvolucaoPadrao:
    """[SOLID: OCP, DIP] Implementacao padrao de calculo de evolucao."""

    def calcular(self, itens: Iterable[ItemRotina]) -> Evolucao:
        return Evolucao.a_partir_itens(itens)


class Rotina:
    """[SOLID: SRP, OCP, DIP] Entidade de rotina com regras de dominio."""

    def __init__(
        self,
        id_crianca,
        data_referencia=None,
        resolvedor_status: ResolvedorStatusRotina | None = None,
        calculadora_evolucao: CalculadoraEvolucaoRotina | None = None,
    ):
        self.id_crianca = self._validar_id_crianca(id_crianca)
        self.data_referencia = self._validar_data_referencia(data_referencia)
        self.itens: List[ItemRotina] = []
        self._resolvedor_status = resolvedor_status or ResolvedorStatusPadrao()
        self._calculadora_evolucao = calculadora_evolucao or CalculadoraEvolucaoPadrao()

    @staticmethod
    def _validar_id_crianca(id_crianca) -> str:
        if isinstance(id_crianca, int):
            if id_crianca <= 0:
                raise ValueError("id_crianca deve ser um numero positivo.")
            return str(id_crianca)

        if isinstance(id_crianca, str):
            valor = id_crianca.strip()
            if not valor:
                raise ValueError("id_crianca nao pode ser vazio.")
            if not valor.isdigit():
                raise ValueError("id_crianca deve conter apenas numeros.")
            return valor

        raise TypeError("id_crianca deve ser string numerica ou inteiro.")

    @staticmethod
    def _validar_data_referencia(data_referencia) -> date:
        if data_referencia is None:
            return date.today()

        if isinstance(data_referencia, date):
            return data_referencia

        if isinstance(data_referencia, str):
            valor = data_referencia.strip()
            if not valor:
                raise ValueError("data_referencia nao pode ser vazia.")

            formatos = ("%d/%m/%Y", "%Y-%m-%d")
            for formato in formatos:
                try:
                    return datetime.strptime(valor, formato).date()
                except ValueError:
                    continue
            raise ValueError("Data invalida. Use DD/MM/AAAA ou AAAA-MM-DD.")

        raise TypeError("data_referencia deve ser date, string valida ou None.")

    @property
    def data_formatada(self) -> str:
        return self.data_referencia.strftime("%d/%m/%Y")

    @staticmethod
    def _validar_indice(indice, total_itens: int) -> None:
        if not isinstance(indice, int):
            raise TypeError("Indice deve ser um numero inteiro.")
        if not 0 <= indice < total_itens:
            raise IndexError("Indice invalido.")

    def adicionar_item(self, item):
        if not isinstance(item, ItemRotina):
            raise TypeError("A rotina aceita apenas objetos do tipo ItemRotina.")

        if any(item_existente.horario == item.horario for item_existente in self.itens):
            raise ValueError(f"Ja existe um item cadastrado no horario {item.horario}.")

        self.itens.append(item)
        self.itens.sort(key=lambda item_rotina: item_rotina.horario)

    def remover_item(self, indice):
        self._validar_indice(indice, len(self.itens))
        self.itens.pop(indice)

    def editar_item(self, indice, novo_nome, novo_horario):
        self._validar_indice(indice, len(self.itens))

        for posicao, item in enumerate(self.itens):
            if posicao != indice and item.horario == novo_horario:
                raise ValueError(f"Ja existe um item cadastrado no horario {novo_horario}.")

        self.itens[indice].atualizar(novo_nome, novo_horario)
        self.itens.sort(key=lambda item_rotina: item_rotina.horario)

    def marcar_status(self, indice, status_code):
        self._validar_indice(indice, len(self.itens))
        self.itens[indice].status = self._resolvedor_status.resolver(status_code)

    def calcular_evolucao(self):
        return self.obter_evolucao().percentual_concluido

    def obter_evolucao(self) -> Evolucao:
        return self._calculadora_evolucao.calcular(self.itens)

    def obter_resumo_evolucao(self):
        return self.obter_evolucao().to_dict()

def obter_sugestoes_tea():
    return [
        {"nome": "Escovar os dentes", "cat": "Higiene"},
        {"nome": "Café da manhã", "cat": "Alimentação"},
        {"nome": "Arrumar a mochila", "cat": "Escola"},
        {"nome": "Tempo de Tela/Tablet", "cat": "Lazer"},
        {"nome": "Banho e Pijama", "cat": "Higiene"},
        {"nome": "História de dormir", "cat": "Sono"}
    ]

