from typing import List
from teapoio.domain.models.item_rotina import ItemRotina
# Não precisa importar Crianca ou Responsavel aqui se não for usar os objetos,
# apenas o ID basta.

class Rotina:
    # CORREÇÃO 1: Usei 'id_crianca' (sem cedilha) nos dois lugares
    def __init__(self, id_crianca):
        self.id_crianca = id_crianca 
        self.itens: List[ItemRotina] = [] # Inicialização correta da lista tipada

    def adicionar_item(self, item):
        self.itens.append(item)
        print(f"Item '{item.nome}' adicionado com sucesso!")

    def remover_item(self, indice):
        if 0 <= indice < len(self.itens):
            removido = self.itens.pop(indice)
            print(f"Item '{removido.nome}' removido.")
            # A evolução será recalculada na próxima vez que exibir
        else:
            print("Índice inválido.")

    def editar_item(self, indice, novo_nome, novo_horario):
        if 0 <= indice < len(self.itens):
            self.itens[indice].nome = novo_nome
            self.itens[indice].horario = novo_horario
            print("Item atualizado com sucesso.")
        else:
            print("Índice inválido.")

    def marcar_status(self, indice, status_code):
        # Conversão de input string para int, se necessário, ou comparação direta
        # Ajuste conforme o que vem do seu teclado (string '1' ou int 1)
        if 0 <= indice < len(self.itens):
            if str(status_code) == '1':
                self.itens[indice].status = "Concluído"
            elif str(status_code) == '2':
                self.itens[indice].status = "Não Realizado"
            else:
                self.itens[indice].status = "Pendente"
            print(f"Status alterado para: {self.itens[indice].status}")
        else:
            print("Item não encontrado.")

    def calcular_evolucao(self):
        total = len(self.itens)
        if total == 0:
            return 0.0
        
        concluidos = sum(1 for item in self.itens if item.status == "Concluído")
        return (concluidos / total) * 100

    # CORREÇÃO 2: O método agora aceita o nome opcionalmente para exibir, 
    # ou usa o ID se o nome não for passado.
    def exibir_rotina(self, nome_crianca_display=None):
        identificacao = nome_crianca_display if nome_crianca_display else f"ID {self.id_crianca}"
        
        print(f"\n--- Rotina de {identificacao} ---")
        
        if not self.itens:
            print("Nenhum item cadastrado.")
        else:
            for i, item in enumerate(self.itens):
                print(f"{i + 1}. {item}") 
            
            progresso = self.calcular_evolucao()
            print(f"\n[EVOLUÇÃO DO DIA]: {progresso:.1f}% concluído")
        print("-" * 30)

# Função auxiliar mantida igual
def obter_sugestoes_tea():
    return [
        {"nome": "Escovar os dentes", "cat": "Higiene"},
        {"nome": "Café da manhã", "cat": "Alimentação"},
        {"nome": "Arrumar a mochila", "cat": "Escola"},
        {"nome": "Tempo de Tela/Tablet", "cat": "Lazer"},
        {"nome": "Banho e Pijama", "cat": "Higiene"},
        {"nome": "História de dormir", "cat": "Sono"}
    ]