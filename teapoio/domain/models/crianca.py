from datetime import date
import uuid
from teapoio.domain.models.pessoa import Pessoa
from teapoio.domain.models.responsavel import Responsavel

class Crianca(Pessoa):
    NIVEIS_SUPORTE_PERMITIDOS = {1, 2, 3}

    def __init__(self, nome: str, data_nascimento: date, responsavel: Responsavel | str,
                 nivel_suporte: int, id_crianca: str | None = None, uuid_func=None) -> None:
        super().__init__(nome, data_nascimento)

        # Geração de ID curto (6 dígitos)
        self.id_crianca = str(id_crianca) if id_crianca else self._gerar_id_uuid(uuid_func)

        # Vínculo obrigatório com Responsável
        if isinstance(responsavel, Responsavel):
            self.id_responsavel = responsavel.id_responsavel
        elif isinstance(responsavel, str):
            self.id_responsavel = responsavel
        else:
            raise ValueError("Criança deve estar vinculada a um Responsável válido.")

        # Validação de nível de suporte
        self.nivel_suporte = nivel_suporte

        # Validação de maioridade
        if self.verificar_maioridade():
            raise ValueError("Criança não pode ser maior de idade.")

    @staticmethod
    def _gerar_id_uuid(uuid_func=None) -> str:
        generator = uuid_func if callable(uuid_func) else uuid.uuid4
        id_uuid = generator()
        id_str = str(id_uuid).replace('-', '')
        digitos = ''.join(filter(str.isdigit, id_str))[:6]
        digitos = digitos.ljust(6, '0')
        return digitos

    @property
    def nivel_suporte(self) -> int:
        return self.__nivel_suporte

    @nivel_suporte.setter
    def nivel_suporte(self, valor: int) -> None:
        if not isinstance(valor, int):
            raise TypeError("Nível de suporte deve ser um número inteiro.")
        if valor not in self.NIVEIS_SUPORTE_PERMITIDOS:
            permitidos = sorted(self.NIVEIS_SUPORTE_PERMITIDOS)
            raise ValueError(f"Nível de suporte inválido. Permitidos: {permitidos}.")
        self.__nivel_suporte = valor

    def idade_em(self, hoje: date | None = None) -> int:
        hoje = hoje or date.today()
        anos = hoje.year - self.data_nascimento.year
        fez_aniversario = (hoje.month, hoje.day) >= (self.data_nascimento.month, self.data_nascimento.day)
        return anos if fez_aniversario else anos - 1

    def obter_status_idade(self) -> str:
        try:
            return "Maior de idade" if self.verificar_maioridade() else "Menor de idade"
        except Exception:
            return "Idade desconhecida"