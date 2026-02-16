from teapoio.domain.models.conquista import Conquista
class Progresso_conquista(Conquista):
    def __init__(self, nome, data, recompensa, criterios, nivel_dificuldade, categoria, status):
        super().__init__(nome, data, recompensa, criterios, nivel_dificuldade, categoria)
        self.status = status # atingida, em progresso, não iniciada  