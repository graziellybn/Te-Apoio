from datetime import date
from typing import Protocol

from teapoio.domain.models.item_rotina import ItemRotina
from teapoio.domain.models.rotina import Rotina


class FabricaItemRotina(Protocol):
	"""[SOLID: ISP, DIP] Contrato minimo para criacao de itens de rotina."""

	def criar(
		self,
		nome: str,
		horario: str,
		observacao: str = "",
		tags: list[str] | None = None,
	) -> ItemRotina:
		"""Cria um ItemRotina a partir dos dados de entrada."""



class FabricaRotina(Protocol):
	"""[SOLID: ISP, DIP] Contrato minimo para criacao de rotinas."""

	def criar(self, id_crianca: str | int, data_referencia: date) -> Rotina:
		"""Cria uma Rotina para crianca e data informadas."""



class FabricaItemRotinaPadrao:
	"""[SOLID: OCP, DIP] Implementacao padrao para criar ItemRotina."""

	def criar(
		self,
		nome: str,
		horario: str,
		observacao: str = "",
		tags: list[str] | None = None,
	) -> ItemRotina:
		return ItemRotina(nome=nome, horario=horario, observacao=observacao, tags=tags)



class FabricaRotinaPadrao:
	"""[SOLID: OCP, DIP] Implementacao padrao para criar Rotina."""

	def criar(self, id_crianca: str | int, data_referencia: date) -> Rotina:
		return Rotina(id_crianca=id_crianca, data_referencia=data_referencia)



class ServicoRotinas:
	"""[SOLID: SRP, OCP, DIP] Casos de uso de rotina da camada de aplicacao."""

	def __init__(
		self,
		fabrica_item: FabricaItemRotina | None = None,
		fabrica_rotina: FabricaRotina | None = None,
	) -> None:
		"""Permite injetar fabricas customizadas para criar itens e rotinas, ou usar as 
		implementacoes padrão."""
		self._fabrica_item = fabrica_item or FabricaItemRotinaPadrao()
		self._fabrica_rotina = fabrica_rotina or FabricaRotinaPadrao()


	def obter_ou_criar_rotina(
		self,
		rotinas: list[Rotina],
		id_crianca: str | int,
		data_referencia: date,
	) -> tuple[Rotina, bool]:
		"""Obtém a rotina existente para a criança e data informadas, ou cria uma nova se não existir."""
		rotina = next(
			(
				rotina_existente
				for rotina_existente in rotinas
				if rotina_existente.id_crianca == str(id_crianca)
				and rotina_existente.data_referencia == data_referencia
			),
			None,
		)
		if rotina is not None:
			return rotina, False

		rotina = self._fabrica_rotina.criar(
			id_crianca=id_crianca,
			data_referencia=data_referencia,
		)
		rotinas.append(rotina)
		return rotina, True

	def adicionar_item(
		self,
		rotina: Rotina,
		nome_item: str,
		horario: str,
		observacao: str = "",
		tags: list[str] | None = None,
	) -> ItemRotina:
		""""Adiciona um novo item à rotina usando a fábrica de itens."""
		item = self._fabrica_item.criar(
			nome=nome_item,
			horario=horario,
			observacao=observacao,
			tags=tags,
		)

		rotina.adicionar_item(item)
		return item

	@staticmethod
	def marcar_status(rotina: Rotina, indice: int, status_code: int | str) -> str:
		"""Marca o status de um item da rotina usando o método da própria rotina."""
		rotina.marcar_status(indice, status_code)
		return rotina.itens[indice].status

	@staticmethod
	def remover_item(rotina: Rotina, indice: int) -> None:
		"""Remove um item da rotina usando o método da própria rotina."""
		rotina.remover_item(indice)
