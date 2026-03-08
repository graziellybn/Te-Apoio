from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

from teapoio.domain.models.Perfil import Perfil
from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.item_rotina import ItemRotina
from teapoio.domain.models.perfil_sensorial import PerfilSensorial
from teapoio.domain.models.responsavel import Responsavel
from teapoio.domain.models.rotina import Rotina
from teapoio.infrastructure.mixins.exportavel_json import ExportavelJsonMixin


class SerializadorEstadoRelatorio:
    """Converte estado da aplicacao entre objetos de dominio e dicionarios JSON."""

    @staticmethod
    def estado_vazio() -> dict[str, Any]:
        return {
            "responsaveis": [],
            "criancas": [],
            "rotinas": [],
            "perfil": None,
            "data_calendario": date.today(),
        }

    def serializar_estado(
        self,
        responsaveis: list[Responsavel],
        criancas: list[Crianca],
        rotinas: list[Rotina],
        perfil: Perfil | None,
        data_calendario: date,
    ) -> dict[str, Any]:
        criancas_por_responsavel: dict[str, list[Crianca]] = {}
        for crianca in criancas:
            criancas_por_responsavel.setdefault(crianca.id_responsavel, []).append(crianca)

        return {
            "responsaveis": [
                self._serializar_responsavel(
                    item,
                    criancas_por_responsavel.get(item.id_responsavel, []),
                )
                for item in responsaveis
            ],
            "rotinas": [self._serializar_rotina(item) for item in rotinas],
            "perfil": self._serializar_perfil(perfil),
            "data_calendario": data_calendario.isoformat(),
        }

    def desserializar_estado(self, dados: Any) -> dict[str, Any]:
        if not isinstance(dados, dict):
            return self.estado_vazio()

        responsaveis: list[Responsavel] = []
        responsaveis_por_id: dict[str, Responsavel] = {}
        for bruto in dados.get("responsaveis", []):
            responsavel = self._desserializar_responsavel(bruto)
            if responsavel is None:
                continue
            responsaveis.append(responsavel)
            responsaveis_por_id[responsavel.id_responsavel] = responsavel

        criancas: list[Crianca] = []
        for bruto in self._coletar_criancas_brutas(dados):
            crianca = self._desserializar_crianca(bruto, responsaveis_por_id)
            if crianca is None:
                continue
            criancas.append(crianca)

        perfil = self._desserializar_perfil(
            dados.get("perfil"),
            responsaveis=responsaveis,
            criancas=criancas,
            responsaveis_por_id=responsaveis_por_id,
        )

        rotinas: list[Rotina] = []
        for bruto in dados.get("rotinas", []):
            rotina = self._desserializar_rotina(bruto)
            if rotina is None:
                continue
            rotinas.append(rotina)

        return {
            "responsaveis": responsaveis,
            "criancas": criancas,
            "rotinas": rotinas,
            "perfil": perfil,
            "data_calendario": self._desserializar_data_calendario(
                dados.get("data_calendario")
            ),
        }

    @staticmethod
    def _normalizar_data_nascimento(valor: Any) -> str:
        if not isinstance(valor, str):
            raise ValueError("Data de nascimento invalida para persistencia.")

        data_str = valor.strip()
        if not data_str:
            raise ValueError("Data de nascimento vazia para persistencia.")

        for formato in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                data_obj = datetime.strptime(data_str, formato)
                return data_obj.strftime("%d/%m/%Y")
            except ValueError:
                continue

        raise ValueError("Data de nascimento fora de formato esperado.")

    def _serializar_responsavel(
        self,
        responsavel: Responsavel,
        criancas_responsavel: list[Crianca],
    ) -> dict[str, Any]:
        payload = {
            "id_responsavel": responsavel.id_responsavel,
            "nome": responsavel.nome,
            "data_nascimento": responsavel.data_nascimento.strftime("%d/%m/%Y"),
            "email": responsavel.email,
            "senha": responsavel.senha,
            "criancas": [
                self._serializar_crianca(item)
                for item in criancas_responsavel
            ],
        }
        if not criancas_responsavel:
            payload["aviso_crianca"] = "crianca nao cadastrada"
        return payload

    @staticmethod
    def _coletar_criancas_brutas(dados: dict[str, Any]) -> list[dict[str, Any]]:
        criancas_brutas: list[dict[str, Any]] = []

        # Compatibilidade com formato antigo (lista no topo)
        criancas_topo = dados.get("criancas", [])
        if isinstance(criancas_topo, list):
            for bruto in criancas_topo:
                if isinstance(bruto, dict):
                    criancas_brutas.append(bruto)

        # Novo formato: criancas aninhadas em cada responsavel
        responsaveis_brutos = dados.get("responsaveis", [])
        if isinstance(responsaveis_brutos, list):
            for bruto_responsavel in responsaveis_brutos:
                if not isinstance(bruto_responsavel, dict):
                    continue

                id_responsavel = bruto_responsavel.get("id_responsavel")
                criancas_vinculadas = bruto_responsavel.get("criancas", [])
                if not isinstance(criancas_vinculadas, list):
                    continue

                for bruto_crianca in criancas_vinculadas:
                    if not isinstance(bruto_crianca, dict):
                        continue
                    if "id_crianca" not in bruto_crianca:
                        continue

                    if "id_responsavel" not in bruto_crianca and id_responsavel is not None:
                        bruto_crianca = {
                            **bruto_crianca,
                            "id_responsavel": id_responsavel,
                        }
                    criancas_brutas.append(bruto_crianca)

        criancas_unicas: list[dict[str, Any]] = []
        ids_vistos: set[str] = set()
        for bruto in criancas_brutas:
            id_crianca = str(bruto.get("id_crianca", "")).strip()
            if not id_crianca or id_crianca in ids_vistos:
                continue
            ids_vistos.add(id_crianca)
            criancas_unicas.append(bruto)

        return criancas_unicas

    def _desserializar_responsavel(self, bruto: Any) -> Responsavel | None:
        if not isinstance(bruto, dict):
            return None

        try:
            id_responsavel = bruto.get("id_responsavel")
            senha = bruto.get("senha")
            if not isinstance(senha, str) or not senha.strip():
                senha = f"legado-{str(id_responsavel or '').strip() or '000000'}"

            return Responsavel(
                nome=bruto.get("nome"),
                data_nascimento=self._normalizar_data_nascimento(
                    bruto.get("data_nascimento")
                ),
                email=bruto.get("email"),
                senha=senha,
                id_responsavel=id_responsavel,
            )
        except (TypeError, ValueError):
            return None

    def _serializar_crianca(self, crianca: Crianca) -> dict[str, Any]:
        return {
            "id_crianca": crianca.id_crianca,
            "id_responsavel": crianca.id_responsavel,
            "nome": crianca.nome,
            "data_nascimento": crianca.data_nascimento.strftime("%d/%m/%Y"),
            "nivel_suporte": crianca.nivel_suporte,
        }

    def _desserializar_crianca(
        self,
        bruto: Any,
        responsaveis_por_id: dict[str, Responsavel],
    ) -> Crianca | None:
        if not isinstance(bruto, dict):
            return None

        id_responsavel = str(bruto.get("id_responsavel", "")).strip()
        if not id_responsavel:
            return None

        responsavel = responsaveis_por_id.get(id_responsavel) or id_responsavel

        try:
            return Crianca(
                nome=bruto.get("nome"),
                data_nascimento=self._normalizar_data_nascimento(
                    bruto.get("data_nascimento")
                ),
                responsavel=responsavel,
                nivel_suporte=int(bruto.get("nivel_suporte")),
                id_crianca=bruto.get("id_crianca"),
            )
        except (TypeError, ValueError):
            return None

    def _serializar_perfil(self, perfil: Perfil | None) -> dict[str, Any] | None:
        if perfil is None:
            return None

        perfis_sensoriais = [
            self._serializar_perfil_sensorial(item)
            for item in perfil.listar_perfis_sensoriais().values()
        ]
        return {
            "id_responsavel": perfil.responsavel.id_responsavel,
            "perfis_sensoriais": perfis_sensoriais,
        }

    @staticmethod
    def _serializar_perfil_sensorial(perfil_sensorial: PerfilSensorial) -> dict[str, Any]:
        return {
            "id_crianca": perfil_sensorial.id_crianca,
            "nome": perfil_sensorial.nome,
            "data_nascimento": perfil_sensorial.data_nascimento.strftime("%d/%m/%Y"),
            "hipersensibilidades": perfil_sensorial.hipersensibilidades,
            "hipossensibilidades": perfil_sensorial.hipossensibilidades,
            "hiperfocos": perfil_sensorial.hiperfocos,
            "seletividade_alimentar": perfil_sensorial.seletividade_alimentar,
            "estrategias_regulacao": perfil_sensorial.estrategias_regulacao,
        }

    def _desserializar_perfil(
        self,
        bruto: Any,
        responsaveis: list[Responsavel],
        criancas: list[Crianca],
        responsaveis_por_id: dict[str, Responsavel],
    ) -> Perfil | None:
        if not responsaveis:
            return None

        id_responsavel = ""
        perfis_sensoriais_brutos: list[Any] = []
        if isinstance(bruto, dict):
            id_responsavel = str(bruto.get("id_responsavel", "")).strip()
            bruto_perfis = bruto.get("perfis_sensoriais", [])
            if isinstance(bruto_perfis, list):
                perfis_sensoriais_brutos = bruto_perfis

        responsavel = responsaveis_por_id.get(id_responsavel) or responsaveis[0]
        perfil = Perfil(responsavel=responsavel, criancas=criancas)

        for bruto_perfil in perfis_sensoriais_brutos:
            perfil_sensorial = self._desserializar_perfil_sensorial(bruto_perfil)
            if perfil_sensorial is None:
                continue
            try:
                perfil.adicionar_perfil_sensorial(perfil_sensorial)
            except ValueError:
                continue

        return perfil

    def _desserializar_perfil_sensorial(self, bruto: Any) -> PerfilSensorial | None:
        if not isinstance(bruto, dict):
            return None

        try:
            return PerfilSensorial(
                id_crianca=bruto.get("id_crianca"),
                nome=bruto.get("nome"),
                data_nascimento=self._normalizar_data_nascimento(
                    bruto.get("data_nascimento")
                ),
                hipersensibilidades=bruto.get("hipersensibilidades", []),
                hipossensibilidades=bruto.get("hipossensibilidades", []),
                hiperfocos=bruto.get("hiperfocos", []),
                seletividade_alimentar=bruto.get("seletividade_alimentar", []),
                estrategias_regulacao=bruto.get("estrategias_regulacao", []),
            )
        except (TypeError, ValueError):
            return None

    def _serializar_rotina(self, rotina: Rotina) -> dict[str, Any]:
        return {
            "id_crianca": rotina.id_crianca,
            "data_referencia": rotina.data_referencia.isoformat(),
            "sentimento_dia": rotina.sentimento_dia,
            "itens": [self._serializar_item_rotina(item) for item in rotina.itens],
        }

    @staticmethod
    def _serializar_item_rotina(item: ItemRotina) -> dict[str, Any]:
        return {
            "nome": item.nome,
            "horario": item.horario,
            "status": item.status,
            "observacao": item.observacao,
            "tags": item.tags,
        }

    def _desserializar_rotina(self, bruto: Any) -> Rotina | None:
        if not isinstance(bruto, dict):
            return None

        try:
            rotina = Rotina(
                id_crianca=bruto.get("id_crianca"),
                data_referencia=self._desserializar_data_referencia(
                    bruto.get("data_referencia")
                ),
                sentimento_dia=bruto.get("sentimento_dia"),
            )
        except (TypeError, ValueError):
            return None

        itens_brutos = bruto.get("itens", [])
        if not isinstance(itens_brutos, list):
            return rotina

        for bruto_item in itens_brutos:
            item = self._desserializar_item_rotina(bruto_item)
            if item is None:
                continue
            try:
                rotina.adicionar_item(item)
            except ValueError:
                continue

        return rotina

    @staticmethod
    def _desserializar_item_rotina(bruto: Any) -> ItemRotina | None:
        if not isinstance(bruto, dict):
            return None

        try:
            observacao = bruto.get("observacao")
            tags_brutas = bruto.get("tags", [])
            tags: list[str]
            if isinstance(tags_brutas, list):
                tags = [item for item in tags_brutas if isinstance(item, str)]
            elif isinstance(tags_brutas, str):
                tags = [item.strip() for item in tags_brutas.split(",") if item.strip()]
            else:
                tags = []

            item = ItemRotina(
                nome=bruto.get("nome"),
                horario=bruto.get("horario"),
                observacao=observacao if isinstance(observacao, str) else "",
                tags=tags,
            )
            status = bruto.get("status")
            if isinstance(status, str):
                item.status = status
            return item
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _desserializar_data_referencia(valor: Any) -> date:
        if not isinstance(valor, str):
            raise ValueError("Data de referencia invalida.")

        data_str = valor.strip()
        for formato in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(data_str, formato).date()
            except ValueError:
                continue

        raise ValueError("Data de referencia fora de formato esperado.")

    @staticmethod
    def _desserializar_data_calendario(valor: Any) -> date:
        if isinstance(valor, str):
            data_str = valor.strip()
            for formato in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(data_str, formato).date()
                except ValueError:
                    continue

        return date.today()


class RepositorioRelatorio(ExportavelJsonMixin):
    """Implementacao de persistencia do estado em arquivo JSON."""

    @staticmethod
    def _caminho_arquivo_padrao() -> Path:
        # Usa sempre a raiz do projeto para evitar salvar em cwd inesperado.
        return Path(__file__).resolve().parents[3] / "teapoio_data.json"

    def __init__(
        self,
        caminho_arquivo: str | Path | None = None,
        serializador: SerializadorEstadoRelatorio | None = None,
    ) -> None:
        self._caminho_arquivo = (
            self._caminho_arquivo_padrao()
            if caminho_arquivo is None
            else Path(caminho_arquivo)
        )
        self._serializador = serializador or SerializadorEstadoRelatorio()

    def carregar_estado(self) -> dict[str, Any]:
        dados = self._ler_json_arquivo(caminho_arquivo=self._caminho_arquivo, fallback=None)
        estado = self._serializador.desserializar_estado(dados)

        # Se arquivo estiver ausente, vazio ou invalido, recria com estrutura valida.
        if not isinstance(dados, dict) or not dados:
            self.salvar_estado(
                responsaveis=estado["responsaveis"],
                criancas=estado["criancas"],
                rotinas=estado["rotinas"],
                perfil=estado["perfil"],
                data_calendario=estado["data_calendario"],
            )

        return estado

    def salvar_estado(
        self,
        responsaveis: list[Responsavel],
        criancas: list[Crianca],
        rotinas: list[Rotina],
        perfil: Perfil | None,
        data_calendario: date,
    ) -> None:
        payload = self._serializador.serializar_estado(
            responsaveis=responsaveis,
            criancas=criancas,
            rotinas=rotinas,
            perfil=perfil,
            data_calendario=data_calendario,
        )
        self._escrever_json_arquivo(caminho_arquivo=self._caminho_arquivo, payload=payload)