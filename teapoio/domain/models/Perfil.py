from __future__ import annotations

from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.perfil_sensorial import PerfilSensorial
from teapoio.domain.models.responsavel import Responsavel


class Perfil:
	def __init__(self, responsavel: Responsavel, criancas: list[Crianca] | None = None) -> None:
		if not isinstance(responsavel, Responsavel):
			raise ValueError("Perfil deve ser criado com um responsável válido.")
		self.responsavel = responsavel
		self.criancas = list(criancas) if criancas else []
		self._perfis_sensoriais: dict[str, PerfilSensorial] = {}

	def adicionar_crianca(self, crianca: Crianca) -> None:
		if not isinstance(crianca, Crianca):
			raise ValueError("Criança inválida para o perfil.")
		if self.buscar_crianca_por_id(crianca.id_crianca) is not None:
			return
		self.criancas.append(crianca)

	def buscar_crianca_por_id(self, id_crianca: str) -> Crianca | None:
		return next((crianca for crianca in self.criancas if crianca.id_crianca == id_crianca), None)

	def remover_crianca(self, id_crianca: str) -> bool:
		tamanho_anterior = len(self.criancas)
		self.criancas = [crianca for crianca in self.criancas if crianca.id_crianca != id_crianca]
		if len(self.criancas) == tamanho_anterior:
			return False
		self._perfis_sensoriais.pop(id_crianca, None)
		return True

	def adicionar_perfil_sensorial(self, perfil_sensorial: PerfilSensorial) -> None:
		if not isinstance(perfil_sensorial, PerfilSensorial):
			raise ValueError("Perfil sensorial inválido.")
		if self.buscar_crianca_por_id(perfil_sensorial.id_crianca) is None:
			raise ValueError("Não existe criança com este id para vincular perfil sensorial.")
		self._perfis_sensoriais[perfil_sensorial.id_crianca] = perfil_sensorial

	def obter_perfil_sensorial(self, id_crianca: str) -> PerfilSensorial | None:
		return self._perfis_sensoriais.get(id_crianca)

	def listar_perfis_sensoriais(self) -> dict[str, PerfilSensorial]:
		return dict(self._perfis_sensoriais)
