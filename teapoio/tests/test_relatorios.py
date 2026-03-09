from datetime import date

from teapoio.application.services.servico_relatorios import ServicoRelatorios


class RepositorioFake:
	def __init__(self, estado_inicial=None):
		"""Repositório fake para testes, que simula o comportamento de carregar e salvar o estado sem acessar um arquivo real"""
		self.estado_inicial = estado_inicial
		self.salvamento = None

	def carregar_estado(self):
		"""Simula o carregamento do estado, retornando o estado inicial definido no construtor"""
		return self.estado_inicial

	def salvar_estado(self, responsaveis, criancas, rotinas, perfil, data_calendario):
		"""Simula o salvamento do estado, armazenando os dados recebidos em um atributo para posterior 
		verificação nos testes"""
		self.salvamento = {
			"responsaveis": responsaveis,
			"criancas": criancas,
			"rotinas": rotinas,
			"perfil": perfil,
			"data_calendario": data_calendario,
		}


def test_servico_relatorios_delega_carregamento_para_repositorio():
	"""Valida se o serviço de relatórios delega o carregamento do estado para o repositório 
	e retorna os dados corretamente	"""
	estado_esperado = {
		"responsaveis": [],
		"criancas": [],
		"rotinas": [],
		"perfil": None,
		"data_calendario": date(2026, 3, 6),
	}
	servico = ServicoRelatorios(
		repositorio=RepositorioFake(estado_inicial=estado_esperado)
	)

	estado = servico.carregar_estado_inicial()

	assert estado is estado_esperado


def test_servico_relatorios_delega_salvamento_para_repositorio():
	"""Valida se o serviço de relatórios delega o salvamento do estado para o repositório e 
	passa os dados corretamente"""
	repositorio = RepositorioFake(estado_inicial={})
	servico = ServicoRelatorios(repositorio=repositorio)

	servico.salvar_estado_atual(
		responsaveis=[],
		criancas=[],
		rotinas=[],
		perfil=None,
		data_calendario=date(2026, 3, 6),
	)

	assert repositorio.salvamento is not None
	assert repositorio.salvamento["data_calendario"] == date(2026, 3, 6)
