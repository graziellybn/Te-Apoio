from dataclasses import dataclass, field
from datetime import date
from uuid import uuid4


@dataclass
class Evento:
    titulo: str
    crianca_id: str
    data: date
    descricao: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "crianca_id": self.crianca_id,
            "data": self.data.strftime("%d/%m/%Y"),
            "descricao": self.descricao,
        }

    @staticmethod
    def from_dict(data: dict) -> "Evento":
        dia, mes, ano = map(int, data["data"].split("/"))
        return Evento(
            id=data["id"],
            titulo=data["titulo"],
            crianca_id=data["crianca_id"],
            data=date(ano, mes, dia),
            descricao=data.get("descricao", ""),
        )
