from datetime import date

from teapoio.application.services.servico_relatorios import ServicoRelatorios


class RepositorioFake:
	def __init__(self, estado_inicial=None):
		self.estado_inicial = estado_inicial
		self.salvamento = None

	def carregar_estado(self):
		return self.estado_inicial

	def salvar_estado(self, responsaveis, criancas, rotinas, perfil, data_calendario):
		self.salvamento = {
			"responsaveis": responsaveis,
			"criancas": criancas,
			"rotinas": rotinas,
			"perfil": perfil,
			"data_calendario": data_calendario,
		}


def test_servico_relatorios_delega_carregamento_para_repositorio():
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
