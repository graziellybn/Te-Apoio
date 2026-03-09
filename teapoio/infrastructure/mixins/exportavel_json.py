from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class ExportavelJsonMixin:
	"""Utilitario compartilhado para leitura e escrita de JSON."""

	@staticmethod
	def _ler_json_arquivo(caminho_arquivo: Path, fallback: Any) -> Any:
		if not caminho_arquivo.exists():
			return fallback

		try:
			with caminho_arquivo.open("r", encoding="utf-8") as arquivo:
				return json.load(arquivo)
		except (OSError, json.JSONDecodeError):
			return fallback

	@staticmethod
	def _escrever_json_arquivo(caminho_arquivo: Path, payload: Any) -> None:
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
