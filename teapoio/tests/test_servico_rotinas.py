from datetime import date

from teapoio.application.services.servico_rotinas import ServicoRotinas
from teapoio.domain.models.item_rotina import ItemRotina
from teapoio.domain.models.rotina import Rotina

# TESTES PARA O SERVICO DE ROTINAS
# =======================================
# Testa se uma nova rotina é criada quando não existe nenhuma para a criança e data informadas.
def test_servico_obter_ou_criar_rotina_cria_nova_quando_nao_existe():
    servico = ServicoRotinas()
    rotinas: list[Rotina] = []
    data_ref = date.today()

    rotina, criada = servico.obter_ou_criar_rotina(rotinas, "123456", data_ref)

    assert criada is True
    assert rotina.id_crianca == "123456"
    assert rotina.data_referencia == data_ref
    assert len(rotinas) == 1

#  Testa se uma rotina existente é reutilizada quando já foi criada para a mesma criança e data.
def test_servico_obter_ou_criar_rotina_reutiliza_existente():
    servico = ServicoRotinas()
    rotinas: list[Rotina] = []
    data_ref = date.today()

    primeira, _ = servico.obter_ou_criar_rotina(rotinas, "123456", data_ref)
    segunda, criada = servico.obter_ou_criar_rotina(rotinas, "123456", data_ref)

    assert criada is False
    assert primeira is segunda
    assert len(rotinas) == 1

#  Testa se é possível adicionar um item à rotina e marcar seu status como concluído.
def test_servico_adicionar_item_e_marcar_status():
    servico = ServicoRotinas()
    rotina = Rotina("123456", data_referencia=date.today())

    item = servico.adicionar_item(rotina, "Escovar os dentes", "08:00")
    status = servico.marcar_status(rotina, 0, "1")

    assert isinstance(item, ItemRotina)
    assert item.nome == "Escovar os dentes"
    assert status == ItemRotina.STATUS_CONCLUIDO

#   Testa se o serviço de rotinas aceita fábricas customizadas para criar rotinas e itens.

def test_servico_aceita_fabricas_customizadas():
    class FabricaItemFake:
        def criar(self, nome: str, horario: str) -> ItemRotina:
            return ItemRotina(f"fake-{nome}", horario)

    class FabricaRotinaFake:
        def criar(self, id_crianca: str | int, data_referencia: date) -> Rotina:
            return Rotina(id_crianca=id_crianca, data_referencia=data_referencia)

    servico = ServicoRotinas(
        fabrica_item=FabricaItemFake(),
        fabrica_rotina=FabricaRotinaFake(),
    )
    rotinas: list[Rotina] = []
    data_ref = date.today()

    rotina, criada = servico.obter_ou_criar_rotina(rotinas, "123456", data_ref)
    item = servico.adicionar_item(rotina, "Tarefa", "09:00")

    assert criada is True
    assert item.nome == "fake-Tarefa"
