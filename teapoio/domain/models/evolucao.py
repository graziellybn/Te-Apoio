from dataclasses import dataclass # Usada para criar value objects imutáveis
from typing import Iterable # Usada para tipagem de coleções

from teapoio.domain.models.item_rotina import ItemRotina


#----------------------------- CLASSE EVOLUCAO -----------------------------
@dataclass(frozen=True)
class Evolucao:
	"""[SOLID: SRP] Value object para indicadores de progresso da rotina."""

	total_itens: int
	concluidos: int
	nao_realizados: int
	pendentes: int

#------------------------------ PROPRIEDADES ----------------------------------------
	@property
	def percentual_concluido(self) -> float:
		"""Calcula o percentual de conclusão da rotina."""
		if self.total_itens == 0:
			return 0.0
		return (self.concluidos / self.total_itens) * 100


#------------------------------- MÉTODOS DE CRIAÇÃO ---------------------------------------
	@classmethod
	def a_partir_itens(cls, itens: Iterable[ItemRotina]) -> "Evolucao":
		"""Cria uma instância de Evolucao a partir de uma coleção de itens de rotina."""
		itens_lista = list(itens)
		total = len(itens_lista)

		concluidos = sum(
			1 for item in itens_lista if item.status == ItemRotina.STATUS_CONCLUIDO
		)
		nao_realizados = sum(
			1 for item in itens_lista if item.status == ItemRotina.STATUS_NAO_REALIZADO
		)
		pendentes = sum(
			1 for item in itens_lista if item.status == ItemRotina.STATUS_PENDENTE
		)

		return cls(
			total_itens=total,
			concluidos=concluidos,
			nao_realizados=nao_realizados,
			pendentes=pendentes,
		)


#------------------------ MÉTODOS DE EXPORTAÇÃO -----------------------------
	def to_dict(self) -> dict:
		"""
        Converte o objeto Evolucao em um dicionário.

        Returns:
            dict: Representação com métricas e percentual concluído.
        """
		return {
			"total_itens": self.total_itens,
			"concluidos": self.concluidos,
			"nao_realizados": self.nao_realizados,
			"pendentes": self.pendentes,
			"percentual_concluido": self.percentual_concluido,
		}

