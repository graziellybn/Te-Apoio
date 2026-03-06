from teapoio.domain.models.Perfil import Perfil
from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.perfil_sensorial import PerfilSensorial
from teapoio.domain.models.rotina import Rotina


class ServicoPerfil:
    """[SOLID: SRP, OCP, DIP] Casos de uso de perfil e perfil sensorial."""

    @staticmethod
    def vincular_crianca_ao_perfil(perfil: Perfil, crianca: Crianca) -> None:
        perfil.adicionar_crianca(crianca)

    @staticmethod
    def buscar_crianca_no_perfil(perfil: Perfil, id_crianca: str) -> Crianca | None:
        return perfil.buscar_crianca_por_id(id_crianca)

    @staticmethod
    def criar_ou_atualizar_perfil_sensorial(
        perfil: Perfil,
        crianca: Crianca,
        hipersensibilidades: list[str],
        hipossensibilidades: list[str],
        hiperfocos: list[str],
        seletividade_alimentar: list[str],
        estrategias_regulacao: list[str],
    ) -> PerfilSensorial:
        perfil_sensorial = PerfilSensorial(
            id_crianca=crianca.id_crianca,
            nome=crianca.nome,
            data_nascimento=crianca.data_nascimento.strftime("%d/%m/%Y"),
            hipersensibilidades=hipersensibilidades,
            hipossensibilidades=hipossensibilidades,
            hiperfocos=hiperfocos,
            seletividade_alimentar=seletividade_alimentar,
            estrategias_regulacao=estrategias_regulacao,
        )
        perfil.adicionar_perfil_sensorial(perfil_sensorial)
        return perfil_sensorial

    @staticmethod
    def excluir_crianca(
        criancas: list[Crianca],
        rotinas: list[Rotina],
        perfil: Perfil | None,
        id_crianca: str,
    ) -> tuple[list[Crianca], list[Rotina]]:
        novas_criancas = [item for item in criancas if item.id_crianca != id_crianca]
        novas_rotinas = [r for r in rotinas if r.id_crianca != id_crianca]

        if perfil is not None:
            perfil.remover_crianca(id_crianca)

        return novas_criancas, novas_rotinas
