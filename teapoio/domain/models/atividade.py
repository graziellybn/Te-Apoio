from __future__ import annotations


class Atividade:
    """Representa uma atividade realizada no dia, com tipo categorizado.

    Tipos válidos são definidos em :data:`TIPOS`. O nome é uma string não
    vazia, e o tipo é normalizado para minúsculas para simplificar comparações.
    """

    TIPOS = {"cognitivo", "social", "lazer"}

    def __init__(self, nome: str, tipo: str):
        if not isinstance(nome, str):
            raise TypeError("Nome da atividade deve ser uma string.")
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("Nome da atividade nao pode ser vazio.")
        self.nome = nome_limpo

        if not isinstance(tipo, str):
            raise TypeError("Tipo da atividade deve ser uma string.")
        tipo_limpo = tipo.strip().lower()
        if tipo_limpo not in self.TIPOS:
            permitidos = ", ".join(sorted(self.TIPOS))
            raise ValueError(f"Tipo de atividade invalido. Permitidos: {permitidos}.")
        self.tipo = tipo_limpo

    def to_dict(self) -> dict[str, str]:
        return {"nome": self.nome, "tipo": self.tipo}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Atividade):
            return False
        return self.nome == other.nome and self.tipo == other.tipo

    def __repr__(self) -> str:
        return f"Atividade(nome={self.nome!r}, tipo={self.tipo!r})"