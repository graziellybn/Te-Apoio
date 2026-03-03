from __future__ import annotations

from typing import Iterable

from teapoio.domain.models.pessoa import Pessoa


class PerfilSensorial(Pessoa):
	def __init__(
		self,
		id_crianca: str,
		nome: str,
		data_nascimento: str,
		hipersensibilidades: Iterable[str] | None = None,
		hipossensibilidades: Iterable[str] | None = None,
		hiperfocos: Iterable[str] | None = None,
		seletividade_alimentar: Iterable[str] | None = None,
		estrategias_regulacao: Iterable[str] | None = None,
	) -> None:
		super().__init__(nome=nome, data_nascimento=data_nascimento)
		self.id_crianca = self._validar_id_crianca(id_crianca)
		self.hipersensibilidades = self._normalizar_lista(hipersensibilidades)
		self.hipossensibilidades = self._normalizar_lista(hipossensibilidades)
		self.hiperfocos = self._normalizar_lista(hiperfocos)
		self.seletividade_alimentar = self._normalizar_lista(seletividade_alimentar)
		self.estrategias_regulacao = self._normalizar_lista(estrategias_regulacao)

	@staticmethod
	def _validar_id_crianca(id_crianca: str) -> str:
		if not isinstance(id_crianca, str):
			raise ValueError("Id da criança deve ser uma string.")
		id_limpo = id_crianca.strip()
		if not id_limpo:
			raise ValueError("Id da criança é obrigatório.")
		return id_limpo

	@staticmethod
	def _normalizar_lista(valores: Iterable[str] | None) -> list[str]:
		if valores is None:
			return []
		lista_normalizada: list[str] = []
		for valor in valores:
			if not isinstance(valor, str):
				raise ValueError("Os itens do perfil sensorial devem ser strings.")
			item = valor.strip()
			if item:
				lista_normalizada.append(item)
		return lista_normalizada

	def obter_status_idade(self) -> str:
		return "Maior de idade" if self.verificar_maioridade() else "Menor de idade"
