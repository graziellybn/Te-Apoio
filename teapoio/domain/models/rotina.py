from datetime import date, datetime
from typing import Iterable, List, Protocol # Tipagem e contratos de interface

from teapoio.domain.models.evolucao import Evolucao # Classe de evolução da rotina
from teapoio.domain.models.item_rotina import ItemRotina # Classe de item da rotina


#----------------------------- PROTOCOLOS (CONTRATOS) -----------------------------
class ResolvedorStatusRotina(Protocol):
    """[SOLID: ISP, DIP] Contrato minimo para resolver codigo de status."""

    def resolver(self, status_code: int | str) -> str:
        """Retorna um status valido de ItemRotina para o codigo informado."""

class CalculadoraEvolucaoRotina(Protocol):
    """[SOLID: ISP, DIP] Contrato minimo para calcular evolucao da rotina."""

    def calcular(self, itens: Iterable[ItemRotina]) -> Evolucao:
        """Retorna uma Evolucao calculada para os itens informados."""


#----------------------------- IMPLEMENTAÇÕES PADRÃO -----------------------------
class ResolvedorStatusPadrao:
    """[SOLID: OCP, DIP] Implementacao padrao de resolucao de status."""

    MAPA_STATUS = {
        1: ItemRotina.STATUS_CONCLUIDO,
        2: ItemRotina.STATUS_NAO_REALIZADO,
        3: ItemRotina.STATUS_PENDENTE,
    }


    def resolver(self, status_code: int | str) -> str:
        """Retorna um status valido de ItemRotina para o codigo informado."""
        if isinstance(status_code, str):
            codigo_limpo = status_code.strip()
            if not codigo_limpo.isdigit():
                raise ValueError("Codigo de status deve ser numerico (1, 2 ou 3).")
            status_code = int(codigo_limpo)
        elif not isinstance(status_code, int):
            raise TypeError("Codigo de status deve ser inteiro ou string numerica.")

        if status_code not in self.MAPA_STATUS:
            raise ValueError("Codigo de status invalido. Use 1, 2 ou 3.")

        return self.MAPA_STATUS[status_code]


class CalculadoraEvolucaoPadrao:
    """[SOLID: OCP, DIP] Implementacao padrao de calculo de evolucao."""

    def calcular(self, itens: Iterable[ItemRotina]) -> Evolucao:
        """Retorna uma Evolucao calculada para os itens informados."""
        return Evolucao.a_partir_itens(itens)



#----------------------------- CLASSE ROTINA -----------------------------
class Rotina:
    """[SOLID: SRP, OCP, DIP] Entidade de rotina com regras de dominio.

    A classe suporta registro de sentimentos e emocoes detalhadas em escala.
    """
    # Definições de sentimentos do dia, mapeando código para emoji, label e escala.
    SENTIMENTOS_DIA = {
        "otimo": {"emoji": "🤩", "label": "Otimo", "escala": 5},
        "bem": {"emoji": "🙂", "label": "Bem", "escala": 4},
        "neutro": {"emoji": "😐", "label": "Neutro", "escala": 3},
        "dificil": {"emoji": "😟", "label": "Dificil", "escala": 2},
        "cansativo": {"emoji": "😴", "label": "Cansativo", "escala": 1},
    }

    # Mapeamento inverso de escala para sentimento, para facilitar normalizacao de entrada.
    SENTIMENTO_POR_ESCALA = {
        5: "otimo",
        4: "bem",
        3: "neutro",
        2: "dificil",
        1: "cansativo",
    }

    # Lista de emoções que podem ser pontuadas de 1..5
    EMOCOES_DETALHADAS = [
        "feliz",
        "calmo",
        "ansioso",
        "irritado",
        "frustrado",
        "triste",
        "sobrecarregado",
        "confuso",
        "entediado",
    ]


#------------------------ INICIALIZAÇÃO E VALIDAÇÃO -------------------------------
    def __init__(
        self,
        id_crianca,
        data_referencia=None,
        sentimento_dia: str | None = None,
        resolvedor_status: ResolvedorStatusRotina | None = None,
        calculadora_evolucao: CalculadoraEvolucaoRotina | None = None,
    ):
        """Inicializa a rotina de uma criança para um dia específico, com validação de dados e configuração de 
        estratégias."""
        self.id_crianca = self._validar_id_crianca(id_crianca)
        self.data_referencia = self._validar_data_referencia(data_referencia)
        self.itens: List[ItemRotina] = []
        self.sentimento_dia = sentimento_dia
        # estrutura para emoções detalhadas: cada emoção mapeia para escala 1..5
        self._emocao_escalas: dict[str, int] = {}
        self._resolvedor_status = resolvedor_status or ResolvedorStatusPadrao()
        self._calculadora_evolucao = calculadora_evolucao or CalculadoraEvolucaoPadrao()



#---------------------- MÉTODOS DE APOIO À SENTIMENTOS ----------------------
    @classmethod
    def opcoes_sentimento_dia(cls) -> list[dict[str, str]]:
        """Retorna a lista de opções de sentimento do dia, com código, emoji, label e escala para cada opção."""
        return [
            {
                "codigo": codigo,
                "emoji": dados["emoji"],
                "label": dados["label"],
                "escala": str(dados["escala"]),
                "completo": f"{dados['emoji']} {dados['label']}",
            }
            for codigo, dados in cls.SENTIMENTOS_DIA.items()
        ]

    @classmethod
    def sentimento_por_escala(cls, escala: int) -> str:
        """Retorna o código de sentimento correspondente à escala numérica, ou levanta erro se a escala for 
        inválida."""
        if escala not in cls.SENTIMENTO_POR_ESCALA:
            raise ValueError("Escala de sentimento invalida. Use 1, 2, 3, 4 ou 5.")
        return cls.SENTIMENTO_POR_ESCALA[escala]

    @classmethod
    def normalizar_sentimento_entrada(cls, valor: str | None) -> str:
        """Normaliza a entrada de sentimento do dia, aceitando código, label ou escala, e retornando o código."""
        if valor is None:
            return ""
        if not isinstance(valor, str):
            raise TypeError("Sentimento do dia deve ser uma string.")

        sentimento = valor.strip().lower()
        if not sentimento:
            return ""

        if sentimento.isdigit():
            return cls.sentimento_por_escala(int(sentimento))

        if sentimento not in cls.SENTIMENTOS_DIA:
            permitidos = ", ".join(sorted(cls.SENTIMENTOS_DIA))
            raise ValueError(f"Sentimento invalido. Permitidos: {permitidos} ou escala 1..5.")

        return sentimento

    @classmethod
    def opcoes_emocoes_detalhadas(cls) -> list[str]:
        """Retorna a lista de emoções que podem ser pontuadas."""
        return list(cls.EMOCOES_DETALHADAS)



#------------------------ MÉTODOS DE VALIDAÇÃO -------------------------------
    @staticmethod
    def _validar_id_crianca(id_crianca) -> str:
        """Valida o ID da criança, garantindo que seja uma string numérica ou inteiro positivo."""
        if isinstance(id_crianca, int):
            if id_crianca <= 0:
                raise ValueError("id_crianca deve ser um numero positivo.")
            return str(id_crianca)

        if isinstance(id_crianca, str):
            valor = id_crianca.strip()
            if not valor:
                raise ValueError("id_crianca nao pode ser vazio.")
            if not valor.isdigit():
                raise ValueError("id_crianca deve conter apenas numeros.")
            return valor

        raise TypeError("id_crianca deve ser string numerica ou inteiro.")


    @staticmethod
    def _validar_data_referencia(data_referencia) -> date:
        """Valida a data de referência, garantindo que seja uma data ou string válida, ou None para hoje."""
        if data_referencia is None:
            return date.today()

        if isinstance(data_referencia, date):
            return data_referencia

        if isinstance(data_referencia, str):
            valor = data_referencia.strip()
            if not valor:
                raise ValueError("data_referencia nao pode ser vazia.")

            formatos = ("%d/%m/%Y", "%Y-%m-%d")
            for formato in formatos:
                try:
                    return datetime.strptime(valor, formato).date()
                except ValueError:
                    continue
            raise ValueError("Data invalida. Use DD/MM/AAAA ou AAAA-MM-DD.")

        raise TypeError("data_referencia deve ser date, string valida ou None.")

        


#---------------------------- PROPRIEDADES -------------------------------------
    @property
    def data_formatada(self) -> str:
        """Retorna a data de referência formatada como string no formato DD/MM/YYYY."""
        return self.data_referencia.strftime("%d/%m/%Y")

    @property
    def sentimento_dia(self) -> str:
        return self.__sentimento_dia

    @sentimento_dia.setter
    def sentimento_dia(self, valor: str | None) -> None:
        self.__sentimento_dia = self.normalizar_sentimento_entrada(valor)

    @property
    def sentimento_dia_info(self) -> dict[str, str]:
        if not self.sentimento_dia:
            return {
                "codigo": "",
                "emoji": "",
                "label": "Nao informado",
                "escala": "",
                "completo": "Nao informado",
            }

        dados = self.SENTIMENTOS_DIA[self.sentimento_dia]
        return {
            "codigo": self.sentimento_dia,
            "emoji": dados["emoji"],
            "label": dados["label"],
            "escala": str(dados["escala"]),
            "completo": f"{dados['emoji']} {dados['label']}",
        }

   

#------------------------------ GERENCIAMENTO DE ITENS DA ROTINA ---------------------------------
    def adicionar_item(self, item):
        """Adiciona um item à rotina, validando seu tipo e horário."""
        if not isinstance(item, ItemRotina):
            raise TypeError("A rotina aceita apenas objetos do tipo ItemRotina.")

        if any(item_existente.horario == item.horario for item_existente in self.itens):
            raise ValueError(f"Ja existe um item cadastrado no horario {item.horario}.")

        self.itens.append(item)
        self.itens.sort(key=lambda item_rotina: item_rotina.horario)

    def remover_item(self, indice):
        """Remove um item da rotina pelo índice."""
        self._validar_indice(indice, len(self.itens))
        self.itens.pop(indice)

    def editar_item(self, indice, novo_nome, novo_horario):
        """Edita um item da rotina pelo índice."""
        self._validar_indice(indice, len(self.itens))

        for posicao, item in enumerate(self.itens):
            if posicao != indice and item.horario == novo_horario:
                raise ValueError(f"Ja existe um item cadastrado no horario {novo_horario}.")

        self.itens[indice].atualizar(novo_nome, novo_horario)
        self.itens.sort(key=lambda item_rotina: item_rotina.horario)


    def marcar_status(self, indice, status_code):
        """Marca o status de um item da rotina pelo índice e código de status."""
        self._validar_indice(indice, len(self.itens))
        self.itens[indice].status = self._resolvedor_status.resolver(status_code)

    @staticmethod
    def _validar_indice(indice, total_itens: int) -> None:
        """Valida se o indice é um inteiro dentro do intervalo de itens da rotina."""
        if not isinstance(indice, int):
            raise TypeError("Indice deve ser um numero inteiro.")
        if not 0 <= indice < total_itens:
            raise IndexError("Indice invalido.")



#-------------------------------- MÉTODOS DE EVOLUÇÃO -------------------------------------
    def calcular_evolucao(self):
        """Calcula a evolução da rotina."""
        return self.obter_evolucao().percentual_concluido

    def obter_evolucao(self) -> Evolucao:
        """Obtém a evolução da rotina."""
        return self._calculadora_evolucao.calcular(self.itens)

    def obter_resumo_evolucao(self):
        """Obtém um resumo da evolução da rotina."""
        return self.obter_evolucao().to_dict()

    def atualizar_sentimento_dia(self, sentimento: str | None) -> None:
        self.sentimento_dia = sentimento



# ------------------------------- MÉTODOS DE REGISTRO DE EMOÇÕES DETALHADAS ---------------------------------
    def registrar_emocao(self, emot: str, escala: int) -> None:
        """Armazena uma escala de 1..5 para uma das emoções detalhadas."""
        if not isinstance(emot, str):
            raise TypeError("Emoção deve ser uma string.")
        chave = emot.strip().lower()
        if chave not in self.EMOCOES_DETALHADAS:
            permitidas = ", ".join(sorted(self.EMOCOES_DETALHADAS))
            raise ValueError(f"Emoção inválida. Permitidas: {permitidas}.")
        if not isinstance(escala, int) or escala < 1 or escala > 5:
            raise ValueError("Escala de emoção deve ser inteiro entre 1 e 5.")
        self._emocao_escalas[chave] = escala

    def obter_emocoes(self) -> dict[str, int]:
        """Retorna cópia das emoções registradas e suas escalas."""
        return dict(self._emocao_escalas)

def obter_sugestoes_tea():
    """Retorna uma lista de sugestões de itens de rotina comuns."""
    return [
        {"nome": "Escovar os dentes", "cat": "Higiene"},
        {"nome": "Café da manhã", "cat": "Alimentação"},
        {"nome": "Arrumar a mochila", "cat": "Escola"},
        {"nome": "Tempo de Tela/Tablet", "cat": "Lazer"},
        {"nome": "Banho e Pijama", "cat": "Higiene"},
        {"nome": "História de dormir", "cat": "Sono"}
    ]

