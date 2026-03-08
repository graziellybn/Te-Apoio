import pytest
from datetime import date

from teapoio.domain.models.evolucao import Evolucao
from teapoio.domain.models.item_rotina import ItemRotina
from teapoio.domain.models.rotina import Rotina

# Testa se rotina aceita itens com horário no formato HH:MM e status inicial como pendente.
def test_item_rotina_aceita_horario_hh_mm():
	item = ItemRotina("Escovar os dentes", "08:30")
	assert item.horario == "08:30"
	assert item.status == ItemRotina.STATUS_PENDENTE


@pytest.mark.parametrize("horario", ["8:30", "24:00", "08:60", "ab:cd", ""]) 
def test_item_rotina_rejeita_horario_invalido(horario):
	with pytest.raises(ValueError):
		ItemRotina("Tarefa", horario)

# Não aceita nome vazio ou apenas espaços em branco.
def test_item_rotina_rejeita_nome_vazio():
	with pytest.raises(ValueError):
		ItemRotina("   ", "09:00")


def test_item_rotina_permita_observacao_rapida():
	item = ItemRotina("Escovar os dentes", "08:00", observacao="Fez sem resistencia")
	assert item.observacao == "Fez sem resistencia"


def test_item_rotina_rejeita_observacao_muito_longa():
	with pytest.raises(ValueError):
		ItemRotina("Escovar os dentes", "08:00", observacao="a" * 281)


def test_item_rotina_normaliza_tags_e_remove_duplicadas():
	item = ItemRotina("Escovar os dentes", "08:00", tags=["#higiene", "manha", "HIGIENE", " "])
	assert item.tags == ["higiene", "manha"]


def test_item_rotina_rejeita_excesso_de_tags():
	with pytest.raises(ValueError):
		ItemRotina("Escovar os dentes", "08:00", tags=[f"tag{i}" for i in range(9)])

# Testa se a rotina aceita um ID de criança numérico, string ou inteiro e converte para string.
def test_rotina_aceita_id_numerico_string_ou_inteiro():
	rotina_texto = Rotina("123456")
	rotina_inteiro = Rotina(123456)
	assert rotina_texto.id_crianca == "123456"
	assert rotina_inteiro.id_crianca == "123456"
	assert isinstance(rotina_texto.data_referencia, date)

# Garante que rejeita IDs de criança que não sejam numeros
def test_rotina_rejeita_id_crianca_nao_numerico():
	with pytest.raises(ValueError):
		Rotina("abc123")


def test_rotina_aceita_data_referencia_em_texto():
	rotina = Rotina("123456", data_referencia="06/03/2026")
	assert rotina.data_formatada == "06/03/2026"


def test_rotina_atualiza_sentimento_do_dia_com_emoji():
	rotina = Rotina("123456")
	rotina.atualizar_sentimento_dia("bem")
	assert rotina.sentimento_dia == "bem"
	assert rotina.sentimento_dia_info["completo"] == "🙂 Bem"


def test_rotina_rejeita_sentimento_invalido():
	rotina = Rotina("123456")
	with pytest.raises(ValueError):
		rotina.atualizar_sentimento_dia("excelente-demais")

# Não aceita data de referência em formato inválido.
def test_rotina_rejeita_data_referencia_invalida():
	with pytest.raises(ValueError):
		Rotina("123456", data_referencia="31/02/2026")

# Não aceita dois itens com o mesmo horário na rotina.
def test_rotina_nao_permite_horario_duplicado():
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Cafe da manha", "07:00"))

	with pytest.raises(ValueError):
		rotina.adicionar_item(ItemRotina("Escovar dentes", "07:00"))

# Ordena os itens por horário ao adicionar.
def test_rotina_ordena_itens_por_horario():
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Dormir", "21:00"))
	rotina.adicionar_item(ItemRotina("Cafe", "07:00"))

	assert [item.horario for item in rotina.itens] == ["07:00", "21:00"]

# Verifica se Rotina aceita códigos numéricos ou strings para marcar status dos itens.
def test_rotina_marcar_status_com_codigos_numericos():
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Leitura", "10:00"))

	rotina.marcar_status(0, "1")
	assert rotina.itens[0].status == ItemRotina.STATUS_CONCLUIDO

	rotina.marcar_status(0, 2)
	assert rotina.itens[0].status == ItemRotina.STATUS_NAO_REALIZADO

	rotina.marcar_status(0, 3)
	assert rotina.itens[0].status == ItemRotina.STATUS_PENDENTE

# Garante que Rotina rejeita códigos de status inválidos.
def test_rotina_marcar_status_rejeita_codigo_invalido():
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Leitura", "10:00"))

	with pytest.raises(ValueError):
		rotina.marcar_status(0, "9")

# Verifica que Rotina levanta IndexError ao tentar remover item inexistente.
def test_rotina_rejeita_indice_invalido_ao_remover():
	rotina = Rotina("123456")
	with pytest.raises(IndexError):
		rotina.remover_item(0)

# Garante que Rotina não permite editar item para horário já ocupado por outro.
def test_rotina_editar_item_rejeita_horario_duplicado():
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Item 1", "08:00"))
	rotina.adicionar_item(ItemRotina("Item 2", "09:00"))

	with pytest.raises(ValueError):
		rotina.editar_item(1, "Item 2 atualizado", "08:00")

# Testa se Rotina retorna resumo correto da evolução com contagens por status e percentual concluído.
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

# Verifica se cálculo de evolução permanece compatível com percentual concluído.
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

# Testa se Evolucao.a_partir_itens retorna contagens corretas de status e percentual concluído.
def test_rotina_obter_evolucao_retorna_objeto_evolucao():
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Item 1", "08:00"))

	evolucao = rotina.obter_evolucao()

	assert isinstance(evolucao, Evolucao)
	assert evolucao.total_itens == 1

# Verifica se Rotina.obter_evolucao retorna um objeto Evolucao válido.
def test_rotina_aceita_resolvedor_status_customizado():
	class ResolvedorSempreConcluido:
		def resolver(self, status_code):
			return ItemRotina.STATUS_CONCLUIDO

	rotina = Rotina("123456", resolvedor_status=ResolvedorSempreConcluido())
	rotina.adicionar_item(ItemRotina("Item 1", "08:00"))
	rotina.marcar_status(0, "qualquer")

	assert rotina.itens[0].status == ItemRotina.STATUS_CONCLUIDO

# Verifica se Rotina aceita calculadora de evolução customizada para sobrescrever resultados.
def test_rotina_aceita_calculadora_evolucao_customizada():
	class CalculadoraFixa:
		def calcular(self, itens):
			return Evolucao(total_itens=10, concluidos=7, nao_realizados=2, pendentes=1)

	rotina = Rotina("123456", calculadora_evolucao=CalculadoraFixa())
	rotina.adicionar_item(ItemRotina("Item 1", "08:00"))

	assert rotina.calcular_evolucao() == 70.0
	assert rotina.obter_resumo_evolucao()["concluidos"] == 7
