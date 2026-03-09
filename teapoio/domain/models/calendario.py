import calendar
from datetime import date
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
	from teapoio.domain.models.rotina import Rotina


class FabricaRotina(Protocol):
	"""[SOLID: ISP, DIP] Contrato minimo para criar rotinas por data."""

	def criar(self, id_crianca: str | int, data_referencia: date) -> "Rotina":
		"""Cria uma rotina para a crianca na data informada."""


class FabricaRotinaPadrao:
	"""[SOLID: OCP, DIP] Fabrica padrao desacoplada de calendario."""

	def criar(self, id_crianca: str | int, data_referencia: date) -> "Rotina":
		from teapoio.domain.models.rotina import Rotina

		return Rotina(id_crianca=id_crianca, data_referencia=data_referencia)


class CalendarioRotina:
	"""[SOLID: SRP, DIP] Responsavel por selecao/validacao de datas de rotina."""

	# Mapeamento de meses
	MESES_PT_BR = {
		1: "janeiro",
		2: "fevereiro",
		3: "março",
		4: "abril",
		5: "maio",
		6: "junho",
		7: "julho",
		8: "agosto",
		9: "setembro",
		10: "outubro",
		11: "novembro",
		12: "dezembro",
	}
	CABECALHO_DIAS = "dom seg ter qua qui sex sab"

	def __init__(
		self,
		data_inicial: date | None = None,
		fabrica_rotina: FabricaRotina | None = None,
	) -> None:
		"""Define data inicial (hoje por padrão)"""
		
		self._data_selecionada = data_inicial or date.today()
		# Usa fábrica padrão se nenhuma for passada 
		self._fabrica_rotina = fabrica_rotina or FabricaRotinaPadrao()


	@property
	def data_selecionada(self) -> date:
		"""Retorna a data atualmente selecionada."""
		return self._data_selecionada
	

	def selecionar_data(self, dia: int, mes: int, ano: int) -> date:
		"""Seleciona uma data específica, validando partes e evitando futuro."""
		self._validar_partes_data(dia, mes, ano)
		try:
			nova_data = date(ano, mes, dia)
		except ValueError as erro:
			raise ValueError("Data invalida para o calendario.") from erro

		if nova_data > date.today():
			raise ValueError("Nao e permitido selecionar data no futuro.")

		self._data_selecionada = nova_data
		return nova_data

	def selecionar_hoje(self) -> date:
		"""Seleciona automaticamente a data de hoje."""
		self._data_selecionada = date.today()
		return self._data_selecionada

	def exibir_mes(self, mes: int | None = None, ano: int | None = None) -> str:
		"""Gera uma representação textual do calendário do mês/ano."""
		mes_ref = mes or self._data_selecionada.month
		ano_ref = ano or self._data_selecionada.year
		self._validar_mes_ano(mes_ref, ano_ref)

		calendario_mes = calendar.Calendar(firstweekday=6)
		semanas = calendario_mes.monthdayscalendar(ano_ref, mes_ref)

		titulo = f"{self.MESES_PT_BR[mes_ref].capitalize()} {ano_ref}"
		linhas = [titulo.center(21), self.CABECALHO_DIAS]
		for semana in semanas:
			linhas.append(" ".join(f"{dia:>3}" if dia else "   " for dia in semana))

		return "\n".join(linhas)


	def criar_rotina_para_data(self, id_crianca: str | int) -> "Rotina":
		"""Cria uma rotina para a criança na data atualmente selecionada."""
		return self._fabrica_rotina.criar(
			id_crianca=id_crianca,
			data_referencia=self._data_selecionada,
		)

	@staticmethod
	def _validar_partes_data(dia: int, mes: int, ano: int) -> None:
		"""Valida se dia, mês e ano são inteiros e coerentes com o ano atual."""

		ano_atual = date.today().year
		if not all(isinstance(valor, int) for valor in (dia, mes, ano)):
			raise TypeError("Dia, mes e ano devem ser numeros inteiros.")
		if ano != ano_atual:
			raise ValueError(f"Ano deve ser o atual ({ano_atual}).")
		if mes < 1 or mes > 12:
			raise ValueError("Mes deve estar entre 1 e 12.")
		if dia < 1 or dia > 31:
			raise ValueError("Dia deve estar entre 1 e 31.")

	
	@staticmethod
	def _validar_mes_ano(mes: int, ano: int) -> None:
		"""Valida se mês e ano são inteiros e se o ano é o atual."""

		ano_atual = date.today().year
		if not isinstance(mes, int) or not isinstance(ano, int):
			raise TypeError("Mes e ano devem ser numeros inteiros.")
		if mes < 1 or mes > 12:
			raise ValueError("Mes deve estar entre 1 e 12.")
		if ano != ano_atual:
			raise ValueError(f"Ano deve ser o atual ({ano_atual}).")
		
        