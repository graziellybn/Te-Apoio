# teapoio/domain/models/evolucao.py
from __future__ import annotations

from datetime import date
from typing import Optional


class Evolucao:
    def __init__(self,
        descricao: Optional[str] = None,
        data: Optional[date] = None,
    ):
        self.descricao = descricao
        self.data = data

    def __repr__(self) -> str:
        return f"Evolucao(descricao={self.descricao!r}, data={self.data!r})"
