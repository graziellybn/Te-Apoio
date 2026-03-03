from __future__ import annotations

from datetime import datetime
import os
from typing import List

from teapoio.domain.models.Perfil import Perfil
from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.perfil_sensorial import PerfilSensorial
from teapoio.domain.models.responsavel import Responsavel


class TeApoioCLI:
	def __init__(self) -> None:
		self._responsaveis: List[Responsavel] = []
		self._criancas: List[Crianca] = []
		self._perfil: Perfil | None = None

	def executar(self) -> None:
		self._limpar_tela()
		print("=== TeApoio ===")
		while True:
			self._exibir_menu()
			opcao = input("Escolha uma opção: ").strip()

			if self._cadastro_completo():
				if opcao == "1":
					self._acessar_configuracoes_perfil()
				elif opcao == "2":
					self._acessar_calendario()
				elif opcao == "3":
					print("Encerrando TeApoio CLI.")
					break
				else:
					self._limpar_tela()
					print("Erro: opção inválida. Tente novamente.")
				continue

			if opcao == "1":
				self._cadastrar_responsavel()
			elif opcao == "2":
				self._validar_cadastro_por_id()
			elif opcao == "3":
				print("Encerrando TeApoio.")
				break
			else:
				self._limpar_tela()
				print("Erro: opção inválida. Tente novamente.")

	def _exibir_menu(self) -> None:
		print("\nMenu")
		if self._cadastro_completo():
			responsavel = self._responsaveis[0]
			print(
				f"Olá, {responsavel.nome}!  "
				f"SEU ID: >>> {responsavel.id_responsavel} <<<"
			)
			print("1. Acessar configurações de perfil")
			print("2. Acessar calendário")
			print("3. Sair")
			return

		print("1. Quero me cadastrar")
		print("2. Já sou cadastrado")
		print("3. Sair")

	def _cadastro_completo(self) -> bool:
		return len(self._responsaveis) > 0

	def _cadastrar_responsavel(self) -> None:
		self._limpar_tela()
		print("\nCadastro do responsável")
		print("Digite 0 para retornar à etapa anterior.")

		nome = ""
		data_nascimento = ""
		email = ""
		etapa = 0

		while etapa < 3:
			if etapa == 0:
				resultado = self._ler_nome_valido("Nome: ")
				if resultado is None:
					print("Cadastro cancelado.")
					return
				nome = resultado
				etapa += 1
				continue

			if etapa == 1:
				resultado = self._ler_data_nascimento_valida("Data de nascimento (DD/MM/YYYY): ", precisa_ser_maior=True)
				if resultado is None:
					etapa -= 1
					continue
				data_nascimento = resultado
				etapa += 1
				continue

			resultado = self._ler_email_valido("Email: ")
			if resultado is None:
				etapa -= 1
				continue
			email = resultado
			etapa += 1

		responsavel = Responsavel(nome, data_nascimento, email)
		self._responsaveis.append(responsavel)
		self._perfil = Perfil(responsavel=responsavel)
		print(
			f"\nOlá, {responsavel.nome}! "
			f"Seu cadastro foi validado. "
			f"SEU ID: >>> {responsavel.id_responsavel} <<<"
		)

	def _ler_nome_valido(self, prompt: str) -> str | None:
		while True:
			nome = input(prompt).strip()
			if nome == "0":
				return None
			try:
				Responsavel._validar_nome(nome)
			except ValueError as error:
				self._mostrar_erro(str(error))
				continue
			return nome

	def _ler_data_nascimento_valida(self, prompt: str, precisa_ser_maior: bool) -> str | None:
		while True:
			data_nascimento = input(prompt).strip()
			if data_nascimento == "0":
				return None
			try:
				data_obj = Responsavel._validar_data_nascimento(data_nascimento)
				idade = datetime.now().year - data_obj.year
				if (datetime.now().month, datetime.now().day) < (data_obj.month, data_obj.day):
					idade -= 1
				if precisa_ser_maior and idade < 18:
					raise ValueError("Responsável deve ter pelo menos 18 anos.")
				if not precisa_ser_maior and idade >= 18:
					raise ValueError("Criança não pode ser maior de idade.")
			except ValueError as error:
				self._mostrar_erro(str(error))
				continue
			return data_nascimento

	def _ler_email_valido(self, prompt: str) -> str | None:
		while True:
			email = input(prompt).strip()
			if email == "0":
				return None
			try:
				Responsavel._validar_email(email)
			except ValueError as error:
				self._mostrar_erro(str(error))
				continue
			return email

	def _ler_nome_crianca_valido(self, prompt: str) -> str | None:
		while True:
			nome = input(prompt).strip()
			if nome == "0":
				return None
			try:
				Responsavel._validar_nome(nome)
			except ValueError as error:
				self._mostrar_erro(str(error))
				continue
			return nome

	def _ler_data_nascimento_crianca_valida(self, prompt: str) -> str | None:
		while True:
			resultado = self._ler_data_nascimento_valida(prompt, precisa_ser_maior=False)
			return resultado

	def _ler_nivel_suporte_valido(self, prompt: str) -> int | None:
		while True:
			nivel = input(prompt).strip()
			if nivel == "0":
				return None
			try:
				nivel_int = int(nivel)
				if nivel_int not in {1, 2, 3}:
					raise ValueError("Nível de suporte inválido. Permitidos: [1, 2, 3].")
			except ValueError as error:
				self._mostrar_erro(str(error))
				continue
			return nivel_int

	@staticmethod
	def _limpar_tela() -> None:
		os.system("cls" if os.name == "nt" else "clear")

	def _mostrar_erro(self, mensagem: str) -> None:
		self._limpar_tela()
		print(f"Erro: {mensagem}")

	def _validar_cadastro_por_id(self) -> None:
		self._limpar_tela()
		print("\nJá sou cadastrado")
		if not self._responsaveis:
			print("Nenhum cadastro encontrado. Escolha a opção 1 para se cadastrar.")
			return

		id_informado = input("Digite seu id de validação: ").strip()
		cadastro = next(
			(
				responsavel
				for responsavel in self._responsaveis
				if responsavel.id_responsavel == id_informado
			),
			None,
		)

		if cadastro is None:
			print("Erro: id não encontrado.")
			return

		print(f"Cadastro validado com sucesso, {cadastro.nome}.")
		self._cadastrar_crianca(cadastro)

	def _cadastrar_crianca(self, responsavel: Responsavel) -> None:
		self._limpar_tela()
		print("\nCadastro da criança")
		print("Digite 0 para retornar à etapa anterior.")

		nome = ""
		data_nascimento = ""
		nivel_suporte = 1
		etapa = 0

		while etapa < 3:
			if etapa == 0:
				resultado = self._ler_nome_crianca_valido("Nome da criança: ")
				if resultado is None:
					print("Cadastro da criança cancelado.")
					return
				nome = resultado
				etapa += 1
				continue

			if etapa == 1:
				resultado = self._ler_data_nascimento_crianca_valida("Data de nascimento (DD/MM/YYYY): ")
				if resultado is None:
					etapa -= 1
					continue
				data_nascimento = resultado
				etapa += 1
				continue

			resultado = self._ler_nivel_suporte_valido("Nível de suporte (1, 2 ou 3): ")
			if resultado is None:
				etapa -= 1
				continue
			nivel_suporte = resultado
			etapa += 1

		crianca = Crianca(
			nome=nome,
			data_nascimento=data_nascimento,
			responsavel=responsavel,
			nivel_suporte=nivel_suporte,
		)
		self._criancas.append(crianca)
		if self._perfil is None:
			self._perfil = Perfil(responsavel=responsavel)
		self._perfil.adicionar_crianca(crianca)
		print(
			f"\nCriança cadastrada com sucesso. "
			f"ID da criança: ({crianca.id_crianca})"
		)

	def _acessar_calendario(self) -> None:
		self._limpar_tela()
		print("\nCalendário")
		print("Funcionalidade em desenvolvimento.")

	def _acessar_configuracoes_perfil(self) -> None:
		while True:
			self._limpar_tela()
			self._mostrar_dados_cadastrados()
			print("\nOpções")
			print("1. Adicionar criança")
			print("2. Excluir criança")
			print(f"3. {self._texto_opcao_perfil_sensorial()}")
			print("4. Editar informações de usuário ou criança")
			print("5. Voltar pra tela inicial")

			opcao = input("Escolha uma opção: ").strip()

			if opcao == "1":
				self._adicionar_crianca_no_perfil()
			elif opcao == "2":
				self._excluir_crianca()
			elif opcao == "3":
				self._gerenciar_perfil_sensorial_crianca()
			elif opcao == "4":
				self._editar_informacoes()
			elif opcao == "5":
				return
			else:
				print("Erro: opção inválida.")

	def _texto_opcao_perfil_sensorial(self) -> str:
		if self._perfil and self._perfil.listar_perfis_sensoriais():
			return "Editar perfil sensorial"
		return "Adicionar perfil sensorial da criança"

	def _gerenciar_perfil_sensorial_crianca(self) -> None:
		if self._perfil and self._perfil.listar_perfis_sensoriais():
			self._editar_perfil_sensorial_crianca()
			return
		self._adicionar_perfil_sensorial_crianca()

	def _mostrar_dados_cadastrados(self) -> None:

		if not self._responsaveis:
			print("Erro: cadastro incompleto.")
			return

		responsavel = self._responsaveis[0]

		print("\nINFORMAÇÕES DO PERFIL")
		print("")
		print("[Responsável]")
		print(f"- Nome: {responsavel.nome}")
		print(f"- Data de nascimento: {responsavel.data_nascimento.strftime('%d/%m/%Y')}")
		print(f"- Email: {responsavel.email}")
		print(f"- ID do responsável: {responsavel.id_responsavel}")

		if not self._criancas:
			print("\n[Criança]")
			print("- Nenhuma criança cadastrada.")

		for crianca in self._criancas:
			print("\n[Criança]")
			print(f"- Nome: {crianca.nome}")
			print(f"- Data de nascimento: {crianca.data_nascimento.strftime('%d/%m/%Y')}")
			print(f"- Nível de suporte: {crianca.nivel_suporte}")
			print(f"- ID da criança: {crianca.id_crianca}")

			perfil_sensorial = self._perfil.obter_perfil_sensorial(crianca.id_crianca) if self._perfil else None
			if perfil_sensorial is None:
				print("- Perfil sensorial: não cadastrado")
				continue

			print("- Perfil sensorial:")
			print(f"  • Hipersensibilidades: {', '.join(perfil_sensorial.hipersensibilidades) or 'Não informado'}")
			print(f"  • Hipossensibilidades: {', '.join(perfil_sensorial.hipossensibilidades) or 'Não informado'}")
			print(f"  • Hiperfocos: {', '.join(perfil_sensorial.hiperfocos) or 'Não informado'}")
			print(f"  • Seletividade alimentar: {', '.join(perfil_sensorial.seletividade_alimentar) or 'Não informado'}")
			print(f"  • Estratégias de regulação: {', '.join(perfil_sensorial.estrategias_regulacao) or 'Não informado'}")


	def _adicionar_perfil_sensorial_crianca(self) -> None:
		if self._perfil is None:
			print("Erro: perfil do responsável não encontrado.")
			return

		if not self._criancas:
			print("Não há crianças cadastradas.")
			return

		id_crianca = input("Informe o ID da criança (ou 0 para voltar): ").strip()
		if id_crianca == "0":
			return

		crianca = self._perfil.buscar_crianca_por_id(id_crianca)
		if crianca is None:
			print("Erro: criança não encontrada para o ID informado.")
			return

		print("Digite 0 para voltar ao campo anterior.")
		campos = [
			"Hipersensibilidades",
			"Hipossensibilidades",
			"Hiperfocos",
			"Seletividade alimentar",
			"Estratégias de regulação",
		]
		respostas: list[list[str] | None] = [None] * len(campos)
		etapa = 0

		while etapa < len(campos):
			nome_campo = campos[etapa]
			entrada = input(f"{nome_campo} (separe por vírgula): ").strip()

			if entrada == "0":
				if etapa == 0:
					print("Você já está no primeiro campo.")
					continue
				etapa -= 1
				self._limpar_tela()
				print("Cadastro de perfil sensorial")
				print("Digite 0 para voltar ao campo anterior.")
				continue

			respostas[etapa] = [item.strip() for item in entrada.split(",") if item.strip()] if entrada else []
			etapa += 1

		hipersensibilidades = respostas[0] or []
		hipossensibilidades = respostas[1] or []
		hiperfocos = respostas[2] or []
		seletividade_alimentar = respostas[3] or []
		estrategias_regulacao = respostas[4] or []

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
		self._perfil.adicionar_perfil_sensorial(perfil_sensorial)
		print("Perfil sensorial cadastrado com sucesso.")

	def _editar_perfil_sensorial_crianca(self) -> None:
		if self._perfil is None:
			print("Erro: perfil do responsável não encontrado.")
			return

		if not self._criancas:
			print("Não há crianças cadastradas.")
			return

		id_crianca = input("Informe o ID da criança para editar (ou 0 para voltar): ").strip()
		if id_crianca == "0":
			return

		crianca = self._perfil.buscar_crianca_por_id(id_crianca)
		if crianca is None:
			print("Erro: criança não encontrada para o ID informado.")
			return

		perfil_atual = self._perfil.obter_perfil_sensorial(id_crianca)
		if perfil_atual is None:
			print("Erro: não existe perfil sensorial cadastrado para essa criança.")
			return

		print("Digite 0 para voltar ao campo anterior.")

		campos = [
			("Hipersensibilidades", perfil_atual.hipersensibilidades),
			("Hipossensibilidades", perfil_atual.hipossensibilidades),
			("Hiperfocos", perfil_atual.hiperfocos),
			("Seletividade alimentar", perfil_atual.seletividade_alimentar),
			("Estratégias de regulação", perfil_atual.estrategias_regulacao),
		]
		respostas: list[list[str] | None] = [None] * len(campos)
		etapa = 0

		while etapa < len(campos):
			nome_campo, valor_atual = campos[etapa]
			texto_atual = ", ".join(valor_atual) or "Não informado"
			entrada = input(f"{nome_campo} [{texto_atual}]: ").strip()

			if entrada == "0":
				if etapa == 0:
					print("Você já está no primeiro campo.")
					continue
				etapa -= 1
				self._limpar_tela()
				print("Edição de perfil sensorial")
				print("Digite 0 para voltar ao campo anterior.")
				continue

			respostas[etapa] = [item.strip() for item in entrada.split(",") if item.strip()] if entrada else []
			etapa += 1

		hipersensibilidades = respostas[0] or []
		hipossensibilidades = respostas[1] or []
		hiperfocos = respostas[2] or []
		seletividade_alimentar = respostas[3] or []
		estrategias_regulacao = respostas[4] or []

		perfil_editado = PerfilSensorial(
			id_crianca=crianca.id_crianca,
			nome=crianca.nome,
			data_nascimento=crianca.data_nascimento.strftime("%d/%m/%Y"),
			hipersensibilidades=hipersensibilidades,
			hipossensibilidades=hipossensibilidades,
			hiperfocos=hiperfocos,
			seletividade_alimentar=seletividade_alimentar,
			estrategias_regulacao=estrategias_regulacao,
		)
		self._perfil.adicionar_perfil_sensorial(perfil_editado)
		print("Perfil sensorial atualizado com sucesso.")

	def _adicionar_crianca_no_perfil(self) -> None:
		if not self._responsaveis:
			print("Erro: nenhum responsável cadastrado.")
			return

		responsavel = self._responsaveis[0]
		self._cadastrar_crianca(responsavel)

	def _editar_informacoes(self) -> None:
		print("\n1. Editar informações do usuário")
		print("2. Editar informações da criança")
		print("3. Voltar")
		opcao = input("Escolha uma opção: ").strip()

		if opcao == "1":
			self._editar_usuario()
		elif opcao == "2":
			self._editar_crianca_por_id()
		elif opcao == "3":
			return
		else:
			print("Erro: opção inválida.")

	def _editar_usuario(self) -> None:
		if not self._responsaveis:
			print("Erro: nenhum responsável cadastrado.")
			return

		responsavel = self._responsaveis[0]
		nome = input(f"Novo nome (Enter para manter '{responsavel.nome}'): ").strip()
		data = input("Nova data de nascimento (DD/MM/YYYY) (Enter para manter): ").strip()
		email = input(f"Novo email (Enter para manter '{responsavel.email}'): ").strip()

		try:
			if nome:
				responsavel.nome = Responsavel._validar_nome(nome)
			if data:
				data_obj = Responsavel._validar_data_nascimento(data)
				idade = datetime.now().year - data_obj.year
				if (datetime.now().month, datetime.now().day) < (data_obj.month, data_obj.day):
					idade -= 1
				if idade < 18:
					raise ValueError("Responsável deve ter pelo menos 18 anos.")
				responsavel.data_nascimento = data_obj
			if email:
				responsavel.email = Responsavel._validar_email(email)
		except ValueError as error:
			print(f"Erro: {error}")
			return

		print("Informações do usuário atualizadas com sucesso.")

	def _editar_crianca_por_id(self) -> None:
		if not self._criancas:
			print("Não há crianças cadastradas.")
			return

		id_crianca = input("Informe o ID da criança (ou 0 para voltar): ").strip()
		if id_crianca == "0":
			return

		crianca = next((item for item in self._criancas if item.id_crianca == id_crianca), None)
		if crianca is None:
			print("Erro: criança não encontrada para o ID informado.")
			return

		nome = input(f"Novo nome (Enter para manter '{crianca.nome}'): ").strip()
		data = input("Nova data de nascimento (DD/MM/YYYY) (Enter para manter): ").strip()
		nivel = input(f"Novo nível de suporte (1, 2 ou 3) (Enter para manter '{crianca.nivel_suporte}'): ").strip()

		try:
			if nome:
				crianca.nome = Responsavel._validar_nome(nome)
			if data:
				data_obj = Responsavel._validar_data_nascimento(data)
				idade = datetime.now().year - data_obj.year
				if (datetime.now().month, datetime.now().day) < (data_obj.month, data_obj.day):
					idade -= 1
				if idade >= 18:
					raise ValueError("Criança não pode ser maior de idade.")
				crianca.data_nascimento = data_obj
			if nivel:
				crianca.nivel_suporte = int(nivel)
		except (ValueError, TypeError) as error:
			print(f"Erro: {error}")
			return

		print("Informações da criança atualizadas com sucesso.")

	def _excluir_crianca(self) -> None:
		if not self._criancas:
			print("Erro: não há criança cadastrada para excluir.")
			return

		id_crianca = input("Informe o ID da criança que deseja excluir (ou 0 para voltar): ").strip()
		if id_crianca == "0":
			return

		crianca = next((item for item in self._criancas if item.id_crianca == id_crianca), None)
		if crianca is None:
			print("Erro: criança não encontrada para o ID informado.")
			return

		confirmacao = input(f"Confirma exclusão da criança {crianca.nome}? (S/N): ").strip().lower()
		if confirmacao != "s":
			print("Exclusão cancelada.")
			return

		self._criancas = [item for item in self._criancas if item.id_crianca != id_crianca]
		if self._perfil is not None:
			self._perfil.remover_crianca(id_crianca)
		print("Criança excluída com sucesso.")

	@staticmethod
	def _ler_lista_texto(prompt: str) -> list[str]:
		texto = input(prompt).strip()
		if not texto:
			return []
		return [item.strip() for item in texto.split(",") if item.strip()]


def executar_cli() -> None:
	cli = TeApoioCLI()
	cli.executar()

