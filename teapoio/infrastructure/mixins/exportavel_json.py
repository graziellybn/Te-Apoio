from __future__ import annotations

import json 
import os  # Usado para operações de sistema de arquivos (fsync, replace)
from pathlib import Path # Usado para manipulação de caminhos de arquivos
from typing import Any  # Tipagem genérica para payloads


#----------------------------- MIXIN EXPORTÁVEL JSON -----------------------------
class ExportavelJsonMixin:
	"""Utilitario compartilhado para leitura e escrita de JSON."""

#------------------------ MÉTODOS DE LEITURA -------------------------------
	@staticmethod
	def _ler_json_arquivo(caminho_arquivo: Path, fallback: Any) -> Any:
		if not caminho_arquivo.exists():
			return fallback

		try:
			with caminho_arquivo.open("r", encoding="utf-8") as arquivo:
				return json.load(arquivo)
		except (OSError, json.JSONDecodeError):
			return fallback

  #------------------------ MÉTODOS DE ESCRITA ------------------------------
	@staticmethod
	def _escrever_json_arquivo(caminho_arquivo: Path, payload: Any) -> None:
		"""Escreve um payload JSON em um arquivo de forma segura, usando escrita atômica e flush 
		para garantir integridade dos dados."""
		caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)
		conteudo = json.dumps(payload, ensure_ascii=False, indent=2)
		if not conteudo.endswith("\n"):
			conteudo += "\n"

		arquivo_temporario = caminho_arquivo.with_suffix(
			f"{caminho_arquivo.suffix}.tmp"
		)

		with arquivo_temporario.open("w", encoding="utf-8") as arquivo:
			arquivo.write(conteudo)
			arquivo.flush()
			os.fsync(arquivo.fileno())

		try:
			arquivo_temporario.replace(caminho_arquivo)
		except OSError:
			# Fallback para ambientes onde replace atomico falha (ex.: lock do OneDrive).
			with caminho_arquivo.open("w", encoding="utf-8") as arquivo_destino:
				arquivo_destino.write(conteudo)
				arquivo_destino.flush()
				os.fsync(arquivo_destino.fileno())
			try:
				arquivo_temporario.unlink(missing_ok=True)
			except OSError:
				pass
