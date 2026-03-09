from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, timedelta
from typing import Iterable

from teapoio.domain.models.rotina import Rotina


class ServicoEstatisticas:
    """Calcula resumos estatísticos a partir de rotinas históricas.

    As estatísticas atuais abrangem:

    * Distribuição de atividades por tipo e por nome dentro de cada tipo nos
      últimos `dias` dias.
    * Distribuição de tipos de atividade nos últimos `dias` dias.
    * Média de escala para cada emoção detalhada nos últimos `dias` dias.

    Todas as funções aceitam uma sequência de instâncias de :class:`Rotina` e
    filtram automaticamente aquelas cuja data de referência esteja dentro do
    intervalo de interesse.
    """

    @staticmethod
    def _filtrar_periodo(rotinas: Iterable[Rotina], dias: int) -> list[Rotina]:
        if dias <= 0:
            raise ValueError("Dias deve ser positivo.")
        limite = date.today() - timedelta(days=dias)
        return [r for r in rotinas if r.data_referencia >= limite]

    @classmethod
    def atividades_por_tipo_e_nome(
        cls, rotinas: Iterable[Rotina], dias: int = 30
    ) -> dict[str, dict[str, float]]:
        """Retorna percentuais de cada atividade dentro de cada tipo.

        O retorno tem a forma:

        {
            "lazer": {"passeio": 30.0, "jogo": 20.0, ...},
            "cognitivo": {"estudo": 50.0, ...},
        }
        """
        periodo = cls._filtrar_periodo(rotinas, dias)
        contadores: dict[str, Counter[str]] = {
            tipo: Counter() for tipo in Rotina.TIPOS_ATIVIDADE
        }
        for r in periodo:
            for a in r.atividades:
                contadores.setdefault(a.tipo, Counter())[a.nome] += 1

        resultado: dict[str, dict[str, float]] = {}
        for tipo, ctr in contadores.items():
            total = sum(ctr.values())
            if total == 0:
                resultado[tipo] = {}
                continue
            resultado[tipo] = {
                nome: 100.0 * contagem / total for nome, contagem in ctr.items()
            }
        return resultado

    @classmethod
    def distribuicao_tipos_atividade(cls, rotinas: Iterable[Rotina], dias: int = 30) -> dict[str, float]:
        """Percentual de cada tipo de atividade (lazer/social/cognitivo)."""
        periodo = cls._filtrar_periodo(rotinas, dias)
        tipo_ctr: Counter[str] = Counter()
        for r in periodo:
            for a in r.atividades:
                tipo_ctr[a.tipo] += 1
        total = sum(tipo_ctr.values())
        if total == 0:
            return {tipo: 0.0 for tipo in Rotina.TIPOS_ATIVIDADE}
        return {tipo: 100.0 * contagem / total for tipo, contagem in tipo_ctr.items()}

    @classmethod
    def medias_emocoes(cls, rotinas: Iterable[Rotina], dias: int = 30) -> dict[str, float]:
        """Média aritmética da escala de cada emoção nos últimos `dias` dias."""
        periodo = cls._filtrar_periodo(rotinas, dias)
        soma: defaultdict[str, int] = defaultdict(int)
        contagem: defaultdict[str, int] = defaultdict(int)
        for r in periodo:
            for emo, escala in r.obter_emocoes().items():
                soma[emo] += escala
                contagem[emo] += 1
        retorno: dict[str, float] = {}
        for emo in Rotina.EMOCOES_DETALHADAS:
            if contagem.get(emo, 0):
                retorno[emo] = soma[emo] / contagem[emo]
            else:
                retorno[emo] = 0.0
        return retorno
