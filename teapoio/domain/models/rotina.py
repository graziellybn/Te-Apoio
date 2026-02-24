from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from uuid import uuid4

from .item_rotina import ItemRotina


class TipoRecorrenciaRotina(str, Enum):
    DATA_UNICA = "DATA_UNICA"
    TODOS_OS_DIAS = "TODOS_OS_DIAS"
    DIAS_ESPECIFICOS = "DIAS_ESPECIFICOS"


class DiaSemana(str, Enum):
    SEG = "SEG"
    TER = "TER"
    QUA = "QUA"
    QUI = "QUI"
    SEX = "SEX"
    SAB = "SAB"
    DOM = "DOM"


@dataclass
class Rotina:
    nome: str
    tipo_recorrencia: TipoRecorrenciaRotina
    crianca_id: str | None = None
    data_agendada: date | None = None
    dias_semana: list[DiaSemana] = field(default_factory=list)
    descricao: str | None = None
    ativa: bool = True
    itens: list[ItemRotina] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        self.validar()

    def validar(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("O nome da rotina é obrigatório.")

        if not isinstance(self.tipo_recorrencia, TipoRecorrenciaRotina):
            raise TypeError("tipo_recorrencia deve ser do tipo TipoRecorrenciaRotina.")

        # Regras da recorrência
        if self.tipo_recorrencia == TipoRecorrenciaRotina.DATA_UNICA:
            if self.data_agendada is None:
                raise ValueError("Rotina de data única exige uma data_agendada.")
            if self.dias_semana:
                raise ValueError("Rotina de data única não deve ter dias_semana.")

        elif self.tipo_recorrencia == TipoRecorrenciaRotina.TODOS_OS_DIAS:
            if self.data_agendada is not None:
                raise ValueError("Rotina de todos os dias não usa data_agendada.")
            if self.dias_semana:
                raise ValueError("Rotina de todos os dias não usa dias_semana.")

        elif self.tipo_recorrencia == TipoRecorrenciaRotina.DIAS_ESPECIFICOS:
            if not self.dias_semana:
                raise ValueError("Rotina por dias específicos exige ao menos um dia da semana.")
            if self.data_agendada is not None:
                raise ValueError("Rotina por dias específicos não usa data_agendada.")
            self._normalizar_e_validar_dias_semana()

        self._validar_itens()
        self._validar_ordens_unicas()

    def _normalizar_e_validar_dias_semana(self) -> None:
        dias_unicos: list[DiaSemana] = []
        vistos = set()

        for dia in self.dias_semana:
            if not isinstance(dia, DiaSemana):
                raise TypeError("Todos os dias da semana devem ser do tipo DiaSemana.")

            if dia.value not in vistos:
                vistos.add(dia.value)
                dias_unicos.append(dia)

        self.dias_semana = dias_unicos

    def _validar_itens(self) -> None:
        if self.itens is None:
            raise ValueError("A lista de itens da rotina não pode ser None.")

        for item in self.itens:
            if not isinstance(item, ItemRotina):
                raise TypeError("Todos os itens da rotina devem ser ItemRotina.")

    def _validar_ordens_unicas(self) -> None:
        ordens = [item.ordem for item in self.itens]
        if len(ordens) != len(set(ordens)):
            raise ValueError("Não pode haver dois itens com a mesma ordem na rotina.")

    def cadastrar_item(self, item: ItemRotina) -> None:
        if not isinstance(item, ItemRotina):
            raise TypeError("item deve ser uma instância de ItemRotina.")

        if any(i.ordem == item.ordem for i in self.itens):
            raise ValueError(f"Já existe um item com ordem {item.ordem}.")

        self.itens.append(item)
        self._ordenar_itens_por_ordem()

    def cadastrar_item_automatico(
        self,
        nome: str,
        descricao: str | None = None,
        horario_inicio=None,
        horario_fim=None,
    ) -> ItemRotina:
        proxima_ordem = self._proxima_ordem_disponivel()
        item = ItemRotina(
            nome=nome,
            descricao=descricao,
            horario_inicio=horario_inicio,
            horario_fim=horario_fim,
            ordem=proxima_ordem,
        )
        self.itens.append(item)
        self._ordenar_itens_por_ordem()
        return item

    def remover_item(self, item_id: str) -> None:
        quantidade_antes = len(self.itens)
        self.itens = [item for item in self.itens if item.id != item_id]

        if len(self.itens) == quantidade_antes:
            raise ValueError("Item não encontrado para remoção.")

        self.reindexar_ordens()

    def editar_ordem_item(self, item_id: str, nova_ordem: int) -> None:
        if nova_ordem < 1:
            raise ValueError("nova_ordem deve ser >= 1.")

        item_alvo = self.buscar_item_por_id(item_id)
        if item_alvo is None:
            raise ValueError("Item não encontrado.")

        outros_itens = [item for item in self.itens if item.id != item_id]

        if nova_ordem > len(outros_itens) + 1:
            nova_ordem = len(outros_itens) + 1

        novo_indice = nova_ordem - 1
        outros_itens.sort(key=lambda x: x.ordem)
        outros_itens.insert(novo_indice, item_alvo)

        for idx, item in enumerate(outros_itens, start=1):
            item.ordem = idx

        self.itens = outros_itens
        self._validar_ordens_unicas()

    def buscar_item_por_id(self, item_id: str) -> ItemRotina | None:
        for item in self.itens:
            if item.id == item_id:
                return item
        return None

    def reindexar_ordens(self) -> None:
        self._ordenar_itens_por_ordem()
        for idx, item in enumerate(self.itens, start=1):
            item.ordem = idx

    def _ordenar_itens_por_ordem(self) -> None:
        self.itens.sort(key=lambda item: item.ordem)

    def _proxima_ordem_disponivel(self) -> int:
        if not self.itens:
            return 1
        return max(item.ordem for item in self.itens) + 1

    def se_aplica_na_data(self, data_consulta: date) -> bool:
        if self.tipo_recorrencia == TipoRecorrenciaRotina.DATA_UNICA:
            return self.data_agendada == data_consulta

        if self.tipo_recorrencia == TipoRecorrenciaRotina.TODOS_OS_DIAS:
            return True

        if self.tipo_recorrencia == TipoRecorrenciaRotina.DIAS_ESPECIFICOS:
            mapa_weekday = {
                0: DiaSemana.SEG,
                1: DiaSemana.TER,
                2: DiaSemana.QUA,
                3: DiaSemana.QUI,
                4: DiaSemana.SEX,
                5: DiaSemana.SAB,
                6: DiaSemana.DOM,
            }
            dia = mapa_weekday[data_consulta.weekday()]
            return dia in self.dias_semana

        return False

    @staticmethod
    def sugerir_modelos_fixos() -> list[str]:
        return [
            "Rotina de consultas",
            "Rotina de férias",
            "Rotina para dias úteis",
            "Rotina para finais de semana",
        ]