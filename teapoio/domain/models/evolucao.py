# teapoio/domain/models/evolucao.py

"""Domain model for tracking the evolution/progress of a child.

This file originally contained no definitions, which caused import
errors when other modules attempted to import ``Evolucao``.  The
class here is intentionally minimal for now and can be expanded as the
project grows.
"""

from __future__ import annotations

from datetime import date
from typing import Optional


class Evolucao:
    def __init__(
        self,
        descricao: Optional[str] = None,
        data: Optional[date] = None,
    ):
        """Create an ``Evolucao`` instance.

        Parameters
        ----------
        descricao : Optional[str]
            A brief description of the evolution event.
        data : Optional[date]
            The date on which the evolution was recorded.
        """
        self.descricao = descricao
        self.data = data

    def __repr__(self) -> str:
        return f"Evolucao(descricao={self.descricao!r}, data={self.data!r})"
