from __future__ import annotations

from datetime import datetime
import os
from typing import List

from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.responsavel import Responsavel


class TeApoioCLI:
	def __init__(self) -> None:
		self._responsaveis: List[Responsavel] = []
		self._criancas: List[Crianca] = []

	def executar(self) -> None:
		self._limpar_tela()
		print("=== TeApoio ===")
		while True:
			self._exibir_menu()
			opcao = input("Escolha uma opção: ").strip()

			if self._cadastro_completo():
				if opcao == "1":
					self._visualizar_informacoes_por_id()
				elif opcao == "2":
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
			print("1. Visualizar minhas informações")
			print("2. Sair")
			return

		print("1. Quero me cadastrar")
		print("2. Já sou cadastrado")
		print("3. Sair")

	def _cadastro_completo(self) -> bool:
		return len(self._responsaveis) > 0 and len(self._criancas) > 0

	def _cadastrar_responsavel(self) -> None:
		self._limpar_tela()
		nome = self._ler_nome_valido()
		data_nascimento = self._ler_data_nascimento_valida()
		email = self._ler_email_valido()

		responsavel = Responsavel(nome, data_nascimento, email)
		self._responsaveis.append(responsavel)
		print(
			f"\nOlá, {responsavel.nome}! "
			f"Seu cadastro foi validado. "
			f"SEU ID: >>> {responsavel.id_responsavel} <<<"
		)

	def _ler_nome_valido(self) -> str:
		while True:
			nome = input("Nome: ").strip()
			try:
				Responsavel._validar_nome(nome)
			except ValueError as error:
				self._limpar_tela()
				print(f"Erro: {error}")
				continue
			return nome

	def _ler_data_nascimento_valida(self) -> str:
		while True:
			data_nascimento = input("Data de nascimento (DD/MM/YYYY): ").strip()
			try:
				data_obj = Responsavel._validar_data_nascimento(data_nascimento)
				idade = datetime.now().year - data_obj.year
				if (datetime.now().month, datetime.now().day) < (data_obj.month, data_obj.day):
					idade -= 1
				if idade < 18:
					raise ValueError("Responsável deve ter pelo menos 18 anos.")
			except ValueError as error:
				self._limpar_tela()
				print(f"Erro: {error}")
				continue
			return data_nascimento

	def _ler_email_valido(self) -> str:
		while True:
			email = input("Email: ").strip()
			try:
				Responsavel._validar_email(email)
			except ValueError as error:
				self._limpar_tela()
				print(f"Erro: {error}")
				continue
			return email

	def _ler_nome_crianca_valido(self) -> str:
		while True:
			nome = input("Nome da criança: ").strip()
			try:
				Responsavel._validar_nome(nome)
			except ValueError as error:
				self._limpar_tela()
				print("\nCadastro da criança")
				print(f"Erro: {error}")
				continue
			return nome

	def _ler_data_nascimento_crianca_valida(self) -> str:
		while True:
			data_nascimento = input("Data de nascimento (DD/MM/YYYY): ").strip()
			try:
				data_obj = Responsavel._validar_data_nascimento(data_nascimento)
				idade = datetime.now().year - data_obj.year
				if (datetime.now().month, datetime.now().day) < (data_obj.month, data_obj.day):
					idade -= 1
				if idade >= 18:
					raise ValueError("Criança não pode ser maior de idade.")
			except ValueError as error:
				self._limpar_tela()
				print("\nCadastro da criança")
				print(f"Erro: {error}")
				continue
			return data_nascimento

	def _ler_nivel_suporte_valido(self) -> int:
		while True:
			nivel = input("Nível de suporte (1, 2 ou 3): ").strip()
			try:
				nivel_int = int(nivel)
				if nivel_int not in {1, 2, 3}:
					raise ValueError("Nível de suporte inválido. Permitidos: [1, 2, 3].")
			except ValueError as error:
				self._limpar_tela()
				print("\nCadastro da criança")
				print(f"Erro: {error}")
				continue
			return nivel_int

	@staticmethod
	def _limpar_tela() -> None:
		os.system("cls" if os.name == "nt" else "clear")

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
		nome = self._ler_nome_crianca_valido()
		data_nascimento = self._ler_data_nascimento_crianca_valida()
		nivel_suporte = self._ler_nivel_suporte_valido()

		crianca = Crianca(
			nome=nome,
			data_nascimento=data_nascimento,
			responsavel=responsavel,
			nivel_suporte=nivel_suporte,
		)
		self._criancas.append(crianca)
		print(
			f"\nCriança cadastrada com sucesso. "
			f"ID da criança: ({crianca.id_crianca})"
		)

	def _visualizar_informacoes_por_id(self) -> None:
		self._limpar_tela()
		print("\nVisualizar informações")

		if not self._responsaveis or not self._criancas:
			print("Erro: cadastro incompleto.")
			return

		responsavel = self._responsaveis[0]
		crianca = self._criancas[0]

		print("\nSeus dados")
		print(f"Nome: {responsavel.nome}")
		print(f"Data de nascimento: {responsavel.data_nascimento.strftime('%d/%m/%Y')}")
		print(f"Email: {responsavel.email}")

		print("\nDados da criança")
		print(f"Nome: {crianca.nome}")
		print(f"Data de nascimento: {crianca.data_nascimento.strftime('%d/%m/%Y')}")
		print(f"Nível de suporte: {crianca.nivel_suporte}")
		print(f"ID da criança: {crianca.id_crianca}")


def executar_cli() -> None:
	cli = TeApoioCLI()
	cli.executar()

# py -m teapoio.infrastructure.main