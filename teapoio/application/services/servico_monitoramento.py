from teapoio.domain.models.rotina import Rotina


class ServicoMonitoramento:
	"""[SOLID: SRP, OCP, DIP] Casos de uso de monitoramento/evolucao."""

	@staticmethod
	def obter_resumo_rotina(rotina: Rotina) -> dict:
		return rotina.obter_resumo_evolucao()

	def gerar_linhas_painel_rotina(self, rotina: Rotina, nome_crianca: str) -> list[str]:
		linhas = [f"\n--- Rotina de {nome_crianca} ({rotina.data_formatada}) ---"]

		if not rotina.itens:
			linhas.append("Nenhum item cadastrado.")
			linhas.append("-" * 30)
			return linhas

		for i, item in enumerate(rotina.itens):
			linhas.append(f"{i + 1}. {item}")

		# incluir emoções registradas, se houver
		emocoes = rotina.obter_emocoes()
		if emocoes:
			linhas.append("\n[EMOCOES DETALHADAS]")
			for emo, escala in emocoes.items():
				linhas.append(f" - {emo}: {escala}")

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
