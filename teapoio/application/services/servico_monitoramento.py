from teapoio.domain.models.rotina import Rotina


class ServicoMonitoramento:
	"""[SOLID: SRP, OCP, DIP] Casos de uso de monitoramento/evolucao."""

	@staticmethod
	def obter_resumo_rotina(rotina: Rotina) -> dict:
		"""Gera um resumo da evolução da rotina, incluindo percentual concluído e status dos itens."""
		return rotina.obter_resumo_evolucao()

	def gerar_linhas_painel_rotina(self, rotina: Rotina, nome_crianca: str) -> list[str]:
		"""Gera as linhas de texto para exibir no painel de monitoramento da rotina."""
		linhas = [f"\n--- Rotina de {nome_crianca} ({rotina.data_formatada}) ---"]

		if not rotina.itens:
			linhas.append("Nenhum item cadastrado.")
			linhas.append("-" * 30)
			return linhas

		for i, item in enumerate(rotina.itens):
			linhas.append(f"{i + 1}. {item}")

		resumo = self.obter_resumo_rotina(rotina)
		linhas.append(
			f"\n[EVOLUCAO DO DIA]: {resumo['percentual_concluido']:.1f}% concluido "
			f"({resumo['concluidos']}/{resumo['total_itens']})"
		)
		linhas.append(
			f"[STATUS] Pendentes: {resumo['pendentes']} | "
			f"Nao realizados: {resumo['nao_realizados']}"
		)
		linhas.append("-" * 30)
		return linhas
