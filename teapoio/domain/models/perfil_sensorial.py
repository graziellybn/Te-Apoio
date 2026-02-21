class PerfilSensorial:
    def __init__(self, sensibilidades=None, seletividades=None):
        self._sensibilidades = sensibilidades or []
        self._seletividades = seletividades or []

    # Getters
    def get_sensibilidades(self):
        return list(self._sensibilidades)

    def get_seletividades(self):
        return list(self._seletividades)

    # Setters com validação
    def adicionar_sensibilidade(self, sensibilidade: str):
        if sensibilidade not in self._sensibilidades:
            self._sensibilidades.append(sensibilidade)

    def adicionar_seletividade(self, seletividade: str):
        if seletividade not in self._seletividades:
            self._seletividades.append(seletividade)

    def avaliar_item(self, item_rotina):
        conflitos = []
        for s in item_rotina.get_sensibilidades():
            if s in self._sensibilidades:
                conflitos.append(s)
        for sel in item_rotina.get_seletividades():
            if sel in self._seletividades:
                conflitos.append(sel)

        return conflitos