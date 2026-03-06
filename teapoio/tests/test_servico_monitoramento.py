from teapoio.application.services.servico_monitoramento import ServicoMonitoramento
from teapoio.domain.models.item_rotina import ItemRotina
from teapoio.domain.models.rotina import Rotina


def test_servico_monitoramento_gera_painel_sem_itens():
    servico = ServicoMonitoramento()
    rotina = Rotina("123456")

    linhas = servico.gerar_linhas_painel_rotina(rotina, "Ana")

    assert "Rotina de Ana" in linhas[0]
    assert "Nenhum item cadastrado." in linhas


def test_servico_monitoramento_gera_painel_com_evolucao():
    servico = ServicoMonitoramento()
    rotina = Rotina("123456")
    rotina.adicionar_item(ItemRotina("Item 1", "08:00"))
    rotina.adicionar_item(ItemRotina("Item 2", "09:00"))
    rotina.marcar_status(0, 1)

    linhas = servico.gerar_linhas_painel_rotina(rotina, "Ana")

    assert any("[EVOLUCAO DO DIA]: 50.0% concluido" in linha for linha in linhas)
    assert any("[STATUS] Pendentes: 1 | Nao realizados: 0" in linha for linha in linhas)
