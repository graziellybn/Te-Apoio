import pytest
from datetime import date

from teapoio.domain.models.evolucao import Evolucao
from teapoio.domain.models.item_rotina import ItemRotina
from teapoio.domain.models.rotina import Rotina


def test_item_rotina_aceita_horario_hh_mm():
	item = ItemRotina("Escovar os dentes", "08:30")
	assert item.horario == "08:30"
	assert item.status == ItemRotina.STATUS_PENDENTE


@pytest.mark.parametrize("horario", ["8:30", "24:00", "08:60", "ab:cd", ""]) 
def test_item_rotina_rejeita_horario_invalido(horario):
	with pytest.raises(ValueError):
		ItemRotina("Tarefa", horario)


def test_item_rotina_rejeita_nome_vazio():
	with pytest.raises(ValueError):
		ItemRotina("   ", "09:00")


def test_rotina_aceita_id_numerico_string_ou_inteiro():
	rotina_texto = Rotina("123456")
	rotina_inteiro = Rotina(123456)
	assert rotina_texto.id_crianca == "123456"
	assert rotina_inteiro.id_crianca == "123456"
	assert isinstance(rotina_texto.data_referencia, date)


def test_rotina_rejeita_id_crianca_nao_numerico():
	with pytest.raises(ValueError):
		Rotina("abc123")


def test_rotina_aceita_data_referencia_em_texto():
	rotina = Rotina("123456", data_referencia="06/03/2026")
	assert rotina.data_formatada == "06/03/2026"


def test_rotina_rejeita_data_referencia_invalida():
	with pytest.raises(ValueError):
		Rotina("123456", data_referencia="31/02/2026")


def test_rotina_nao_permite_horario_duplicado():
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Cafe da manha", "07:00"))

	with pytest.raises(ValueError):
		rotina.adicionar_item(ItemRotina("Escovar dentes", "07:00"))


def test_rotina_ordena_itens_por_horario():
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Dormir", "21:00"))
	rotina.adicionar_item(ItemRotina("Cafe", "07:00"))

	assert [item.horario for item in rotina.itens] == ["07:00", "21:00"]


def test_rotina_marcar_status_com_codigos_numericos():
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Leitura", "10:00"))

	rotina.marcar_status(0, "1")
	assert rotina.itens[0].status == ItemRotina.STATUS_CONCLUIDO

	rotina.marcar_status(0, 2)
	assert rotina.itens[0].status == ItemRotina.STATUS_NAO_REALIZADO

	rotina.marcar_status(0, 3)
	assert rotina.itens[0].status == ItemRotina.STATUS_PENDENTE


def test_rotina_marcar_status_rejeita_codigo_invalido():
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Leitura", "10:00"))

	with pytest.raises(ValueError):
		rotina.marcar_status(0, "9")


def test_rotina_rejeita_indice_invalido_ao_remover():
	rotina = Rotina("123456")
	with pytest.raises(IndexError):
		rotina.remover_item(0)


def test_rotina_editar_item_rejeita_horario_duplicado():
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Item 1", "08:00"))
	rotina.adicionar_item(ItemRotina("Item 2", "09:00"))

	with pytest.raises(ValueError):
		rotina.editar_item(1, "Item 2 atualizado", "08:00")


def test_rotina_resumo_evolucao_retorna_contagens_por_status():
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Item 1", "08:00"))
	rotina.adicionar_item(ItemRotina("Item 2", "09:00"))
	rotina.adicionar_item(ItemRotina("Item 3", "10:00"))

	rotina.marcar_status(0, 1)  # Concluido
	rotina.marcar_status(1, 2)  # Nao realizado

	resumo = rotina.obter_resumo_evolucao()

	assert resumo["total_itens"] == 3
	assert resumo["concluidos"] == 1
	assert resumo["nao_realizados"] == 1
	assert resumo["pendentes"] == 1
	assert resumo["percentual_concluido"] == pytest.approx(33.3333, rel=1e-3)


def test_calcular_evolucao_permanece_compativel_com_percentual():
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Item 1", "08:00"))
	rotina.adicionar_item(ItemRotina("Item 2", "09:00"))

	rotina.marcar_status(0, 1)
	assert rotina.calcular_evolucao() == 50.0


def test_evolucao_a_partir_itens_retorna_contagem_correta():
	itens = [
		ItemRotina("Item 1", "08:00"),
		ItemRotina("Item 2", "09:00"),
		ItemRotina("Item 3", "10:00"),
	]
	itens[0].status = ItemRotina.STATUS_CONCLUIDO
	itens[1].status = ItemRotina.STATUS_NAO_REALIZADO

	evolucao = Evolucao.a_partir_itens(itens)

	assert evolucao.total_itens == 3
	assert evolucao.concluidos == 1
	assert evolucao.nao_realizados == 1
	assert evolucao.pendentes == 1
	assert evolucao.percentual_concluido == pytest.approx(33.3333, rel=1e-3)


def test_rotina_obter_evolucao_retorna_objeto_evolucao():
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Item 1", "08:00"))

	evolucao = rotina.obter_evolucao()

	assert isinstance(evolucao, Evolucao)
	assert evolucao.total_itens == 1
