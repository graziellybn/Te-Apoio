from datetime import date
from typing import List, Tuple, Protocol

from teapoio.domain.models.item_rotina import ItemRotina
from teapoio.domain.models.rotina import Rotina

# [SOLID: DIP] Contratos para as fábricas (permite injetar dependências nos testes)
class FabricaItemRotina(Protocol):
    def criar(self, nome: str, horario: str, observacao: str = "", tags: list[str] | None = None) -> ItemRotina: ...

class FabricaRotina(Protocol):
    def criar(self, id_crianca: str | int, data_referencia: date) -> Rotina: ...

# Implementações padrão das fábricas
class FabricaItemPadrao:
    def criar(self, nome: str, horario: str, observacao: str = "", tags: list[str] | None = None) -> ItemRotina:
        return ItemRotina(nome=nome, horario=horario, observacao=observacao, tags=tags)

class FabricaRotinaPadrao:
    def criar(self, id_crianca: str | int, data_referencia: date) -> Rotina:
        return Rotina(id_crianca=id_crianca, data_referencia=data_referencia)


class ServicoRotinas:
    """Orquestrador de casos de uso para a gestão de rotinas."""

    def __init__(self, fabrica_item=None, fabrica_rotina=None):
        self.fabrica_item = fabrica_item or FabricaItemPadrao()
        self.fabrica_rotina = fabrica_rotina or FabricaRotinaPadrao()

    def obter_ou_criar_rotina(self, rotinas: List[Rotina], id_crianca: str, data_referencia: date) -> Tuple[Rotina, bool]:
        """Busca uma rotina existente para a criança e data, ou cria uma nova se não existir."""
        for rotina in rotinas:
            if rotina.id_crianca == str(id_crianca) and rotina.data_referencia == data_referencia:
                return rotina, False
        
        nova_rotina = self.fabrica_rotina.criar(id_crianca=id_crianca, data_referencia=data_referencia)
        rotinas.append(nova_rotina)
        return nova_rotina, True

    def adicionar_item(
        self, 
        rotina: Rotina, 
        nome: str, 
        horario: str, 
        observacao: str = "",     # Recebe a observação opcional
        tags: list[str] | None = None  # Recebe a lista de tags opcional
    ) -> ItemRotina:
        """Adiciona um novo item à rotina repassando todos os detalhes suportados."""
        novo_item = self.fabrica_item.criar(
            nome=nome, 
            horario=horario, 
            observacao=observacao, 
            tags=tags
        )
        rotina.adicionar_item(novo_item)
        return novo_item

    def marcar_status(self, rotina: Rotina, indice: int, status_code: str | int) -> str:
        """Atualiza o status de um item específico da rotina."""
        rotina.marcar_status(indice, status_code)
        return rotina.itens[indice].status

    # ====================================================================
    # MÉTODOS: Gestão Emocional e Psicológica (Acompanhamento TEA)
    # ====================================================================

    def atualizar_sentimento_dia(self, rotina: Rotina, sentimento: str | None) -> None:
        """
        Orquestra a atualização do sentimento geral do dia.
        Ex: 'otimo', 'bem', 'neutro', 'dificil', 'cansativo' (ou numérico 1 a 5).
        """
        rotina.atualizar_sentimento_dia(sentimento)

    def registrar_emocao(self, rotina: Rotina, emocao: str, escala: int) -> None:
        """
        Orquestra o registo de uma emoção detalhada.
        Ex: emocao='ansioso', escala=4 (de 1 a 5).
        """
        rotina.registrar_emocao(emocao, escala)