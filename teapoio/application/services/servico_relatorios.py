from __future__ import annotations

from datetime import date
from typing import Any, Protocol

from teapoio.domain.models.Perfil import Perfil
from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.responsavel import Responsavel
from teapoio.domain.models.rotina import Rotina


class PortaPersistenciaRelatorios(Protocol):
	"""Contrato de persistencia usado pela camada de aplicacao."""

	def carregar_estado(self) -> dict[str, Any]:
		"""Retorna o estado persistido da aplicacao."""

	def salvar_estado(
		self,
		responsaveis: list[Responsavel],
		criancas: list[Crianca],
		rotinas: list[Rotina],
		perfil: Perfil | None,
		data_calendario: date,
	) -> None:
		"""Persiste o estado atual da aplicacao."""


class ServicoRelatorios:
	"""Orquestra carregamento e persistencia de estado da aplicacao."""

	def __init__(self, repositorio: PortaPersistenciaRelatorios) -> None:
		self._repositorio = repositorio

	def carregar_estado_inicial(self) -> dict[str, Any]:
		"""Carrega o estado inicial da aplicacao usando o repositorio."""
		return self._repositorio.carregar_estado()

	def salvar_estado_atual(
		self,
		responsaveis: list[Responsavel],
		criancas: list[Crianca],
		rotinas: list[Rotina],
		perfil: Perfil | None,
		data_calendario: date,
	) -> None:
		"""Salva o estado atual da aplicacao usando o repositorio."""
		self._repositorio.salvar_estado(
			responsaveis=responsaveis,
			criancas=criancas,
			rotinas=rotinas,
			perfil=perfil,
			data_calendario=data_calendario,
		)
