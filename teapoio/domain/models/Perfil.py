from __future__ import annotations # Permite usar tipos da própria classe antes de serem definidos.

from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.perfil_sensorial import PerfilSensorial 
from teapoio.domain.models.responsavel import Responsavel


# ----------------------------- CLASSE DE PERFIL - INICIALIZAÇÃO + VALIDAÇÕES -----------------------------
class Perfil:
	def __init__(self, responsavel: Responsavel, criancas: list[Crianca] | None = None) -> None:
		"""Inicializa o perfil do responsável, garantindo que seja válido e permitindo a associação 
		de crianças e seus perfis sensoriais."""
		if not isinstance(responsavel, Responsavel):
			raise ValueError("Perfil deve ser criado com um responsável válido.")
		self.responsavel = responsavel
		self.criancas = list(criancas) if criancas else []
		self._perfis_sensoriais: dict[str, PerfilSensorial] = {}


#------------------------ MÉTODOS DE GERENCIAMENTO DE CRIANÇAS -------------------------------
	def adicionar_crianca(self, crianca: Crianca) -> None:
		"""Adiciona uma criança ao perfil, garantindo que seja válida e não exista duplicidade."""
		if not isinstance(crianca, Crianca):
			raise ValueError("Criança inválida para o perfil.")
		if self.buscar_crianca_por_id(crianca.id_crianca) is not None:
			return
		self.criancas.append(crianca)

	def buscar_crianca_por_id(self, id_crianca: str) -> Crianca | None:
		"""serve para localizar rapidamente a criança selecionada quando o usuário alterna de um perfil para outro, 
		garantindo que o sistema saiba qual instância de Crianca está sendo manipulada.."""
		return next((crianca for crianca in self.criancas if crianca.id_crianca == id_crianca), None)

	def remover_crianca(self, id_crianca: str) -> bool:
		"""Remove uma criança do perfil pelo ID, retornando True se removida ou False se não encontrada."""
		tamanho_anterior = len(self.criancas)
		self.criancas = [crianca for crianca in self.criancas if crianca.id_crianca != id_crianca]
		if len(self.criancas) == tamanho_anterior:
			return False
		self._perfis_sensoriais.pop(id_crianca, None)
		return True


    #------------------------ MÉTODOS DE GERENCIAMENTO DE PERFIS SENSORIAIS -------------------------------
	def adicionar_perfil_sensorial(self, perfil_sensorial: PerfilSensorial) -> None:
		"""Adiciona ou atualiza o perfil sensorial de uma criança, garantindo que seja válido e vinculado 
		a uma criança existente."""
		if not isinstance(perfil_sensorial, PerfilSensorial):
			raise ValueError("Perfil sensorial inválido.")
		if self.buscar_crianca_por_id(perfil_sensorial.id_crianca) is None:
			raise ValueError("Não existe criança com este id para vincular perfil sensorial.")
		self._perfis_sensoriais[perfil_sensorial.id_crianca] = perfil_sensorial

	def obter_perfil_sensorial(self, id_crianca: str) -> PerfilSensorial | None:
		"""Obtém o perfil sensorial de uma criança pelo ID, retornando o perfil encontrado ou None."""
		return self._perfis_sensoriais.get(id_crianca)

	def listar_perfis_sensoriais(self) -> dict[str, PerfilSensorial]:
		"""Retorna um dicionário com os perfis sensoriais de todas as crianças do perfil."""
		return dict(self._perfis_sensoriais)
