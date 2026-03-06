from __future__ import annotations

import json
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
		arquivo_temporario = caminho_arquivo.with_suffix(
			f"{caminho_arquivo.suffix}.tmp"
		)

		with arquivo_temporario.open("w", encoding="utf-8") as arquivo:
			json.dump(payload, arquivo, ensure_ascii=False, indent=2)

		arquivo_temporario.replace(caminho_arquivo)
