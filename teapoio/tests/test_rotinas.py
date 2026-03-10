import pytest
from datetime import date

from teapoio.domain.models.evolucao import Evolucao
from teapoio.domain.models.item_rotina import ItemRotina
from teapoio.domain.models.rotina import Rotina


def test_item_rotina_aceita_horario_hh_mm():
	"""Valida se o item da rotina aceita um horário no formato HH:MM e tem status inicial como pendente"""
	item = ItemRotina("Escovar os dentes", "08:30")
	assert item.horario == "08:30"
	assert item.status == ItemRotina.STATUS_PENDENTE


@pytest.mark.parametrize("horario", ["8:30", "24:00", "08:60", "ab:cd", ""]) 
def test_item_rotina_rejeita_horario_invalido(horario):
	"""Valida se o item da rotina rejeita horários em formatos inválidos e lança um erro"""
	with pytest.raises(ValueError):
		ItemRotina("Tarefa", horario)


def test_item_rotina_rejeita_nome_vazio():
	"""Valida se o item da rotina rejeita um nome vazio ou composto apenas por espaços em branco e lança um erro"""
	with pytest.raises(ValueError):
		ItemRotina("   ", "09:00")


def test_rotina_aceita_id_numerico_string_ou_inteiro():
	"""Valida se a rotina aceita um ID de criança numérico, string ou inteiro e converte para string, 
	e se a data de referência é inicializada corretamente"""
	rotina_texto = Rotina("123456")
	rotina_inteiro = Rotina(123456)
	assert rotina_texto.id_crianca == "123456"
	assert rotina_inteiro.id_crianca == "123456"
	assert isinstance(rotina_texto.data_referencia, date)


def test_rotina_rejeita_id_crianca_nao_numerico():
	"""Valida se a rotina rejeita um ID de criança que não seja numérico e lança um erro"""
	with pytest.raises(ValueError):
		Rotina("abc123")


def test_rotina_aceita_data_referencia_em_texto():
	"""Valida se a rotina aceita uma data de referência em formato de texto DD/MM/YYYY e 
	converte para date"""
	rotina = Rotina("123456", data_referencia="06/03/2026")
	assert rotina.data_formatada == "06/03/2026"


def test_rotina_rejeita_data_referencia_invalida():
	"""Valida se a rotina rejeita uma data de referência inválida (ex: 31 de fevereiro) e lança um erro"""
	with pytest.raises(ValueError):
		Rotina("123456", data_referencia="31/02/2026")


def test_rotina_nao_permite_horario_duplicado():
	"""Valida se a rotina não permite adicionar dois itens com o mesmo horário e lança um erro"""
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Cafe da manha", "07:00"))

	with pytest.raises(ValueError):
		rotina.adicionar_item(ItemRotina("Escovar dentes", "07:00"))


def test_rotina_ordena_itens_por_horario():
	"""Valida se a rotina ordena os itens por horário ao adicioná-los, mesmo que sejam adicionados fora de ordem cronológica"""
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Dormir", "21:00"))
	rotina.adicionar_item(ItemRotina("Cafe", "07:00"))

	assert [item.horario for item in rotina.itens] == ["07:00", "21:00"]


def test_rotina_marcar_status_com_codigos_numericos():
	"""Valida se a rotina aceita códigos numéricos ou strings para marcar o status dos itens e atualiza corretamente"""
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Leitura", "10:00"))

	rotina.marcar_status(0, "1")
	assert rotina.itens[0].status == ItemRotina.STATUS_CONCLUIDO

	rotina.marcar_status(0, 2)
	assert rotina.itens[0].status == ItemRotina.STATUS_NAO_REALIZADO

	rotina.marcar_status(0, 3)
	assert rotina.itens[0].status == ItemRotina.STATUS_PENDENTE


def test_rotina_marcar_status_rejeita_codigo_invalido():
	"""Valida se a rotina rejeita códigos de status inválidos (ex: 9) e lança um erro"""
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Leitura", "10:00"))

	with pytest.raises(ValueError):
		rotina.marcar_status(0, "9")


def test_rotina_rejeita_indice_invalido_ao_remover():
	"""Valida se a rotina rejeita um índice inválido ao tentar remover um item e lança um erro"""
	rotina = Rotina("123456")
	with pytest.raises(IndexError):
		rotina.remover_item(0)


def test_rotina_editar_item_rejeita_horario_duplicado():
	"""Valida se a rotina rejeita a edição de um item para um horário que já está ocupado por outro item e lança um erro"""
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Item 1", "08:00"))
	rotina.adicionar_item(ItemRotina("Item 2", "09:00"))

	with pytest.raises(ValueError):
		rotina.editar_item(1, "Item 2 atualizado", "08:00")


def test_rotina_resumo_evolucao_retorna_contagens_por_status():
	"""Valida se o resumo de evolução da rotina retorna as contagens corretas de itens por status e o percentual concluído"""
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
	"""Valida se o cálculo de evolução da rotina permanece compatível com o percentual concluído, mesmo que a lógica interna seja alterada para usar um resolvedor de status ou calculadora de evolução customizada"""
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Item 1", "08:00"))
	rotina.adicionar_item(ItemRotina("Item 2", "09:00"))

	rotina.marcar_status(0, 1)
	assert rotina.calcular_evolucao() == 50.0


def test_evolucao_a_partir_itens_retorna_contagem_correta():
	"""Valida se o método Evolucao.a_partir_itens retorna as contagens corretas de itens por status e o percentual concluído com base em uma lista de itens da rotina"""
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
	"""Valida se o método obter_evolucao da rotina retorna um objeto Evolucao com as contagens corretas de itens por status"""
	rotina = Rotina("123456")
	rotina.adicionar_item(ItemRotina("Item 1", "08:00"))

	evolucao = rotina.obter_evolucao()

	assert isinstance(evolucao, Evolucao)
	assert evolucao.total_itens == 1


def test_rotina_aceita_resolvedor_status_customizado():
	"""Valida se a rotina aceita um resolvedor de status customizado para determinar o status dos itens ao marcar e se o status é atualizado corretamente com base na lógica do resolvedor"""
	class ResolvedorSempreConcluido:
		def resolver(self, status_code):
			return ItemRotina.STATUS_CONCLUIDO

	rotina = Rotina("123456", resolvedor_status=ResolvedorSempreConcluido())
	rotina.adicionar_item(ItemRotina("Item 1", "08:00"))
	rotina.marcar_status(0, "qualquer")

	assert rotina.itens[0].status == ItemRotina.STATUS_CONCLUIDO



def test_rotina_aceita_calculadora_evolucao_customizada():
	"""Valida se a rotina aceita uma calculadora de evolução customizada para sobrescrever os resultados do cálculo de evolução e se o resultado é retornado corretamente com base na lógica da calculadora"""
	class CalculadoraFixa:
		def calcular(self, itens):
			return Evolucao(total_itens=10, concluidos=7, nao_realizados=2, pendentes=1)

	rotina = Rotina("123456", calculadora_evolucao=CalculadoraFixa())
	rotina.adicionar_item(ItemRotina("Item 1", "08:00"))

	assert rotina.calcular_evolucao() == 70.0
	assert rotina.obter_resumo_evolucao()["concluidos"] == 7

	# ============================================================
# TESTES DA CLASSE ROTINA - SENTIMENTOS E EMOÇÕES DETALHADAS

def test_rotina_atualizar_sentimento_dia_valido():
    """Valida se a rotina aceita e normaliza sentimentos válidos, por texto ou escala numérica"""
    rotina = Rotina("123456")
    
    rotina.atualizar_sentimento_dia("Otimo") # Letra maiúscula
    assert rotina.sentimento_dia == "otimo"
    assert rotina.sentimento_dia_info["escala"] == "5"

    rotina.atualizar_sentimento_dia("1") # Escala numérica em string
    assert rotina.sentimento_dia == "cansativo"
    
def test_rotina_rejeita_sentimento_dia_invalido():
    """Valida se a rotina lança erro ao tentar registrar um sentimento que não existe no mapeamento"""
    rotina = Rotina("123456")
    with pytest.raises(ValueError, match="Sentimento invalido"):
        rotina.atualizar_sentimento_dia("nervoso")

def test_rotina_registrar_emocao_detalhada_valida():
    """Valida se as emoções detalhadas são registradas corretamente no dicionário interno usando escala de 1 a 5"""
    rotina = Rotina("123456")
    rotina.registrar_emocao("Feliz", 5)
    rotina.registrar_emocao("ansioso", 2)
    
    emocoes = rotina.obter_emocoes()
    assert emocoes["feliz"] == 5
    assert emocoes["ansioso"] == 2
    assert len(emocoes) == 2

def test_rotina_rejeita_emocao_detalhada_com_escala_invalida():
    """Valida se a rotina lança erro ao tentar dar uma nota fora da escala 1..5 para uma emoção"""
    rotina = Rotina("123456")
    with pytest.raises(ValueError, match="Escala de emoção deve ser inteiro entre 1 e 5"):
        rotina.registrar_emocao("feliz", 6)
        
def test_rotina_rejeita_emocao_detalhada_nao_cadastrada():
    """Valida se a rotina lança erro ao tentar avaliar uma emoção que não está na lista EMOCOES_DETALHADAS"""
    rotina = Rotina("123456")
    with pytest.raises(ValueError, match="Emoção inválida"):
        rotina.registrar_emocao("apaixonado", 5)

# ============================================================
# TESTES DA CLASSE ITEM ROTINA - OBSERVAÇÕES E TAGS

def test_item_rotina_aceita_observacao_valida():
    """Valida se o item aceita e armazena corretamente uma observação dentro do limite de caracteres"""
    item = ItemRotina("Almoço", "12:00", observacao="Lembrar de comer vegetais")
    assert item.observacao == "Lembrar de comer vegetais"

def test_item_rotina_limpa_espacos_observacao():
    """Valida se o item limpa os espaços em branco no início e fim da observação"""
    item = ItemRotina("Almoço", "12:00")
    item.atualizar_observacao("  Lembrar de comer vegetais  ")
    assert item.observacao == "Lembrar de comer vegetais"

def test_item_rotina_rejeita_observacao_muito_longa():
    """Valida se o item rejeita observações com mais de 280 caracteres"""
    observacao_longa = "a" * 281
    with pytest.raises(ValueError, match="Observacao deve ter no maximo 280 caracteres."):
        ItemRotina("Almoço", "12:00", observacao=observacao_longa)

def test_item_rotina_aceita_e_limpa_tags_validas():
    """Valida se o item aceita tags, remove o símbolo # e limpa espaços em branco"""
    item = ItemRotina("Estudar", "14:00", tags=["#escola", "  matematica  ", "#foco"])
    # Note que a propriedade retorna uma lista de tags limpas
    assert item.tags == ["escola", "matematica", "foco"]

def test_item_rotina_remove_tags_duplicadas_ignorando_case():
    """Valida se o item remove tags duplicadas, mesmo se estiverem com maiúsculas/minúsculas diferentes"""
    item = ItemRotina("Estudar", "14:00", tags=["#escola", "Escola", "ESCOLA", "foco"])
    assert item.tags == ["escola", "foco"]
    assert len(item.tags) == 2

def test_item_rotina_rejeita_tag_muito_longa():
    """Valida se o item rejeita tags individuais que ultrapassam o limite de 30 caracteres"""
    tag_longa = "a" * 31
    with pytest.raises(ValueError, match="Cada tag deve ter no maximo 30 caracteres."):
        ItemRotina("Estudar", "14:00", tags=["escola", tag_longa])

def test_item_rotina_rejeita_excesso_de_tags():
    """Valida se o item rejeita a inserção de mais de 10 tags"""
    tags_excessivas = [f"tag{i}" for i in range(11)] # Cria uma lista com 11 tags
    with pytest.raises(ValueError, match="Use no maximo 10 tags por tarefa."):
        ItemRotina("Estudar", "14:00", tags=tags_excessivas)

def test_item_rotina_ignora_tags_vazias():
    """Valida se strings vazias ou compostas apenas por espaços/hashtags são ignoradas ao setar tags"""
    item = ItemRotina("Estudar", "14:00")
    item.atualizar_tags(["#escola", "   ", "#", "foco"])
    assert item.tags == ["escola", "foco"]

def test_item_rotina_aceita_none_para_observacao_e_tags():
    """Valida se passar None para observação ou tags as inicializa com os valores padrão (vazios)"""
    item = ItemRotina("Estudar", "14:00", observacao=None, tags=None)
    assert item.observacao == ""
    assert item.tags == []