from __future__ import annotations

from datetime import date, datetime
import os
from typing import List

# --- SEUS IMPORTS EXISTENTES ---
from teapoio.domain.models.Perfil import Perfil
from teapoio.domain.models.crianca import Crianca
from teapoio.domain.models.responsavel import Responsavel
from teapoio.application.services.servico_cadastro import ServicoCadastro
from teapoio.application.services.servico_monitoramento import ServicoMonitoramento
from teapoio.application.services.servico_perfil import ServicoPerfil
from teapoio.application.services.servico_relatorios import ServicoRelatorios
from teapoio.application.services.servico_rotinas import ServicoRotinas
from teapoio.infrastructure.persistence.Relatorio import RepositorioRelatorio

# --- NOVOS IMPORTS (Certifique-se que os arquivos estão na pasta correta) ---
# Ajuste o caminho 'teapoio.domain.models...' conforme sua estrutura de pastas real
from teapoio.domain.models.rotina import Rotina, obter_sugestoes_tea
from teapoio.domain.models.calendario import CalendarioRotina


class TeApoioCLI:
    """[SOLID: SRP, DIP] Camada de interface/entrada de dados do sistema."""

    def __init__(
        self,
        servico_cadastro: ServicoCadastro | None = None,
        servico_monitoramento: ServicoMonitoramento | None = None,
        servico_perfil: ServicoPerfil | None = None,
        servico_relatorios: ServicoRelatorios | None = None,
        servico_rotinas: ServicoRotinas | None = None,
        calendario: CalendarioRotina | None = None,
        repositorio: RepositorioRelatorio | None = None,
    ) -> None:
        repositorio_relatorios = repositorio or RepositorioRelatorio()
        self._servico_relatorios = servico_relatorios or ServicoRelatorios(
            repositorio=repositorio_relatorios
        )
        estado = self._servico_relatorios.carregar_estado_inicial()

        self._responsaveis: List[Responsavel] = estado["responsaveis"]
        self._criancas: List[Crianca] = estado["criancas"]
        self._rotinas: List[Rotina] = estado["rotinas"]
        self._servico_cadastro = servico_cadastro or ServicoCadastro()
        self._servico_monitoramento = servico_monitoramento or ServicoMonitoramento()
        self._servico_perfil = servico_perfil or ServicoPerfil()
        self._servico_rotinas = servico_rotinas or ServicoRotinas()
        self._calendario = calendario or CalendarioRotina(
            data_inicial=estado["data_calendario"]
        )
        self._perfil: Perfil | None = estado["perfil"]
        # Sessao ativa deve ser iniciada apenas apos validacao por ID.
        self._responsavel_logado: Responsavel | None = None

    def _persistir_estado(self) -> None:
        self._servico_relatorios.salvar_estado_atual(
            responsaveis=self._responsaveis,
            criancas=self._criancas,
            rotinas=self._rotinas,
            perfil=self._perfil,
            data_calendario=self._calendario.data_selecionada,
        )

    def _persistir_estado_seguro(self, contexto: str = "") -> None:
        try:
            self._persistir_estado()
        except OSError as erro:
            if contexto:
                print(f"Aviso: nao foi possivel salvar os dados ({contexto}): {erro}")
            else:
                print(f"Aviso: nao foi possivel salvar os dados: {erro}")

    def executar(self) -> None:
        self._limpar_tela()
        print("=== TeApoio ===")
        try:
            while True:
                self._exibir_menu()
                opcao = input("Escolha uma opção: ").strip()

                if self._sessao_autenticada():
                    if opcao == "1":
                        self._acessar_configuracoes_perfil()
                    elif opcao == "2":
                        self._acessar_calendario()
                    # --- NOVA OPÇÃO ---
                    elif opcao == "3":
                        self._acessar_menu_rotinas()
                    # ------------------
                    elif opcao == "4":
                        self._encerrar_sessao()
                    else:
                        self._limpar_tela()
                        print("Erro: opção inválida. Tente novamente.")

                    self._persistir_estado_seguro("menu autenticado")
                    continue

                # Menu inicial (Login/Cadastro)
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

                self._persistir_estado_seguro("menu inicial")
        finally:
            self._persistir_estado_seguro("encerramento")

    def _exibir_menu(self) -> None:
        print("\nMenu Principal")
        if self._sessao_autenticada():
            responsavel = self._responsavel_logado
            if responsavel is None:
                return
            print(
                f"Olá, {responsavel.nome}!  "
                f"SEU ID: >>> {responsavel.id_responsavel} <<<"
            )
            print("1. Acessar configurações de perfil")
            print("2. Acessar calendário")
            print("3. Acessar rotina")  # Nova opção
            print("4. Sair da conta")
            return

        print("1. Quero me cadastrar")
        print("2. Já sou cadastrado")
        print("3. Sair")

    def _sessao_autenticada(self) -> bool:
        return self._responsavel_logado is not None

    def _obter_criancas_do_responsavel(self, id_responsavel: str) -> list[Crianca]:
        return [
            crianca
            for crianca in self._criancas
            if crianca.id_responsavel == id_responsavel
        ]

    def _obter_criancas_do_responsavel_logado(self) -> list[Crianca]:
        if self._responsavel_logado is None:
            return []
        return self._obter_criancas_do_responsavel(
            self._responsavel_logado.id_responsavel
        )

    def _buscar_crianca_do_responsavel_logado(self, id_crianca: str) -> Crianca | None:
        return next(
            (
                crianca
                for crianca in self._obter_criancas_do_responsavel_logado()
                if crianca.id_crianca == id_crianca
            ),
            None,
        )

    def _encerrar_sessao(self) -> None:
        self._responsavel_logado = None
        self._limpar_tela()
        print("Sessao encerrada com sucesso.")

    # ... [MÉTODOS DE CADASTRO MANTIDOS IGUAIS] ...
    # (Pulei a repetição dos métodos _cadastrar_responsavel, _ler_nome_valido, etc.
    #  Eles continuam existindo exatamente como no seu código original)

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

        responsavel, perfil = self._servico_cadastro.cadastrar_responsavel(
            nome=nome,
            data_nascimento=data_nascimento,
            email=email,
        )
        self._responsaveis.append(responsavel)
        self._perfil = perfil
        self._responsavel_logado = responsavel
        self._persistir_estado()
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
        cadastro = self._servico_cadastro.validar_responsavel_por_id(
            self._responsaveis,
            id_informado,
        )

        if cadastro is None:
            print("Erro: id não encontrado.")
            return

        self._responsavel_logado = cadastro
        if self._perfil is None:
            self._perfil = Perfil(responsavel=cadastro)
            self._persistir_estado()

        print(f"Cadastro validado com sucesso, {cadastro.nome}.")
        if not self._obter_criancas_do_responsavel(cadastro.id_responsavel):
            resposta = input("Nenhuma criança cadastrada. Deseja cadastrar agora? (S/N): ").strip().lower()
            if resposta == "s":
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

        crianca = self._servico_cadastro.cadastrar_crianca(
            responsavel=responsavel,
            nome=nome,
            data_nascimento=data_nascimento,
            nivel_suporte=nivel_suporte,
        )
        self._criancas.append(crianca)
        if self._perfil is None:
            self._perfil = Perfil(responsavel=responsavel)
        self._servico_perfil.vincular_crianca_ao_perfil(self._perfil, crianca)
        self._persistir_estado()
        print(
            f"\nCriança cadastrada com sucesso. "
            f"ID da criança: ({crianca.id_crianca})"
        )

    def _acessar_calendario(self) -> None:
        while True:
            self._limpar_tela()
            data_atual = self._calendario.data_selecionada
            print("\nCalendario da rotina")
            print(f"Data selecionada: {data_atual.strftime('%d/%m/%Y')}")
            print(self._calendario.exibir_mes())
            print("1. Escolher dia/mes/ano")
            print("2. Voltar para hoje")
            print("3. Abrir rotina da data selecionada")
            print("4. Voltar")

            opcao = input("Opcao: ").strip()

            if opcao == "1":
                self._selecionar_data_calendario()
            elif opcao == "2":
                self._calendario.selecionar_hoje()
                self._persistir_estado()
                input("Data atualizada para hoje. Enter para continuar...")
            elif opcao == "3":
                self._acessar_menu_rotinas(data_rotina=self._calendario.data_selecionada)
            elif opcao == "4":
                return
            else:
                input("Opcao invalida. Enter para continuar...")

    def _selecionar_data_calendario(self) -> None:
        try:
            dia = int(input("Dia (1-31): ").strip())
            mes = int(input("Mes (1-12): ").strip())
            ano = int(input(f"Ano (somente {date.today().year}): ").strip())
            data_escolhida = self._calendario.selecionar_data(dia, mes, ano)
            self._persistir_estado()
            print(f"Data selecionada: {data_escolhida.strftime('%d/%m/%Y')}")
        except (TypeError, ValueError) as erro:
            print(f"Nao foi possivel selecionar a data: {erro}")
        input("Enter para continuar...")

    # --- IMPLEMENTAÇÃO DA LÓGICA DE ROTINA ---

    def _acessar_menu_rotinas(self, data_rotina: date | None = None) -> None:
        """Gerencia o fluxo de selecionar uma criança e abrir sua rotina."""
        self._limpar_tela()
        data_base = data_rotina or self._calendario.data_selecionada
        criancas_responsavel = self._obter_criancas_do_responsavel_logado()
        
        if not criancas_responsavel:
            print("\nVocê precisa cadastrar uma criança primeiro.")
            input("Pressione Enter para voltar...")
            return

        # Selecionar Criança
        print(f"\n--- Selecao de crianca para rotina ({data_base.strftime('%d/%m/%Y')}) ---")
        for i, crianca in enumerate(criancas_responsavel):
            print(f"{i + 1}. {crianca.nome} (ID: {crianca.id_crianca})")
        print("0. Voltar")

        escolha = input("Escolha o número da criança: ").strip()
        
        if escolha == "0":
            return

        try:
            indice = int(escolha) - 1
            if 0 <= indice < len(criancas_responsavel):
                crianca_selecionada = criancas_responsavel[indice]

                rotina_atual, criada = self._servico_rotinas.obter_ou_criar_rotina(
                    rotinas=self._rotinas,
                    id_crianca=crianca_selecionada.id_crianca,
                    data_referencia=data_base,
                )

                if criada:
                    print(
                        f"Nova rotina criada para {crianca_selecionada.nome} em "
                        f"{data_base.strftime('%d/%m/%Y')}."
                    )
                    self._persistir_estado()
                
                self._menu_operacoes_rotina(rotina_atual, crianca_selecionada.nome)
            else:
                print("Opção inválida.")
        except ValueError:
            print("Entrada inválida.")
            input("Pressione Enter para continuar...")

    def _menu_operacoes_rotina(self, rotina: Rotina, nome_crianca: str) -> None:
        """Menu interno para manipular os itens da rotina."""
        while True:
            self._limpar_tela()
            self._exibir_rotina(rotina, nome_crianca)

            print("\n[Ações da Rotina]")
            print("1. Adicionar tarefa")
            print("2. Marcar tarefa como Concluída/Pendente")
            print("3. Remover tarefa")
            print("4. Ver sugestões (Banco TEA)")
            print("5. Voltar")

            opcao = input("Opção: ").strip()

            if opcao == "1":
                nome_item = input("Nome da tarefa: ").strip()
                horario = input("Horário sugerido (ex: 08:00): ").strip()
                if not nome_item:
                    print("Digite um nome para a tarefa.")
                    input("Enter para continuar...")
                    continue

                try:
                    self._servico_rotinas.adicionar_item(
                        rotina=rotina,
                        nome_item=nome_item,
                        horario=horario,
                    )
                    self._persistir_estado()
                    input("Tarefa adicionada! Enter para continuar...")
                except (TypeError, ValueError) as erro:
                    print(f"Não foi possível adicionar a tarefa: {erro}")
                    input("Enter para continuar...")

            elif opcao == "2":
                idx_str = input("Número do item para alterar status: ").strip()
                try:
                    idx = int(idx_str) - 1
                    print("1 = Concluído | 2 = Não Realizado | 3 = Pendente")
                    status_code = input("Novo status: ").strip()
                    self._servico_rotinas.marcar_status(rotina, idx, status_code)
                    self._persistir_estado()
                    input("Status atualizado! Enter para continuar...")
                except (TypeError, ValueError, IndexError) as erro:
                    print(f"Não foi possível atualizar o status: {erro}")
                    input("Enter para continuar...")

            elif opcao == "3":
                idx_str = input("Número do item para remover: ").strip()
                try:
                    idx = int(idx_str) - 1
                    self._servico_rotinas.remover_item(rotina, idx)
                    self._persistir_estado()
                    input("Item removido! Enter para continuar...")
                except (TypeError, ValueError, IndexError) as erro:
                    print(f"Não foi possível remover o item: {erro}")
                    input("Enter para continuar...")

            elif opcao == "4":
                sugestoes = obter_sugestoes_tea()
                print("\n--- Sugestões de Rotina (TEA) ---")
                for i, sug in enumerate(sugestoes):
                    print(f"{i+1}. {sug['nome']} ({sug['cat']})")
                print("\nDica: Digite o nome acima na opção 'Adicionar tarefa'.")
                input("Pressione Enter para voltar...")

            elif opcao == "5":
                break

    def _exibir_rotina(self, rotina: Rotina, nome_crianca: str) -> None:
        """[SOLID: SRP] Responsavel por apresentar rotina no terminal."""
        for linha in self._servico_monitoramento.gerar_linhas_painel_rotina(rotina, nome_crianca):
            print(linha)

    # ------------------------------------------------------------------

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
        if self._responsavel_logado is None:
            print("Erro: cadastro incompleto.")
            return

        responsavel = self._responsavel_logado
        criancas_responsavel = self._obter_criancas_do_responsavel_logado()

        print("\nINFORMAÇÕES DO PERFIL")
        print("")
        print("[Responsável]")
        print(f"- Nome: {responsavel.nome}")
        print(f"- Data de nascimento: {responsavel.data_nascimento.strftime('%d/%m/%Y')}")
        print(f"- Email: {responsavel.email}")
        print(f"- ID do responsável: {responsavel.id_responsavel}")

        if not criancas_responsavel:
            print("\n[Criança]")
            print("- Nenhuma criança cadastrada.")

        for crianca in criancas_responsavel:
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

        if not self._obter_criancas_do_responsavel_logado():
            print("Não há crianças cadastradas.")
            return

        id_crianca = input("Informe o ID da criança (ou 0 para voltar): ").strip()
        if id_crianca == "0":
            return

        crianca = self._buscar_crianca_do_responsavel_logado(id_crianca)
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

        self._servico_perfil.criar_ou_atualizar_perfil_sensorial(
            perfil=self._perfil,
            crianca=crianca,
            hipersensibilidades=hipersensibilidades,
            hipossensibilidades=hipossensibilidades,
            hiperfocos=hiperfocos,
            seletividade_alimentar=seletividade_alimentar,
            estrategias_regulacao=estrategias_regulacao,
        )
        self._persistir_estado()
        print("Perfil sensorial cadastrado com sucesso.")

    def _editar_perfil_sensorial_crianca(self) -> None:
        if self._perfil is None:
            print("Erro: perfil do responsável não encontrado.")
            return

        if not self._obter_criancas_do_responsavel_logado():
            print("Não há crianças cadastradas.")
            return

        id_crianca = input("Informe o ID da criança para editar (ou 0 para voltar): ").strip()
        if id_crianca == "0":
            return

        crianca = self._buscar_crianca_do_responsavel_logado(id_crianca)
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

        self._servico_perfil.criar_ou_atualizar_perfil_sensorial(
            perfil=self._perfil,
            crianca=crianca,
            hipersensibilidades=hipersensibilidades,
            hipossensibilidades=hipossensibilidades,
            hiperfocos=hiperfocos,
            seletividade_alimentar=seletividade_alimentar,
            estrategias_regulacao=estrategias_regulacao,
        )
        self._persistir_estado()
        print("Perfil sensorial atualizado com sucesso.")

    def _adicionar_crianca_no_perfil(self) -> None:
        if self._responsavel_logado is None:
            print("Erro: nenhum responsável cadastrado.")
            return

        responsavel = self._responsavel_logado
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
        if self._responsavel_logado is None:
            print("Erro: nenhum responsável cadastrado.")
            return

        responsavel = self._responsavel_logado
        nome = input(f"Novo nome (Enter para manter '{responsavel.nome}'): ").strip()
        data = input("Nova data de nascimento (DD/MM/YYYY) (Enter para manter): ").strip()
        email = input(f"Novo email (Enter para manter '{responsavel.email}'): ").strip()

        try:
            self._servico_cadastro.editar_responsavel(
                responsavel=responsavel,
                nome=nome,
                data_nascimento=data,
                email=email,
            )
        except ValueError as error:
            print(f"Erro: {error}")
            return

        self._persistir_estado()
        print("Informações do usuário atualizadas com sucesso.")

    def _editar_crianca_por_id(self) -> None:
        if not self._obter_criancas_do_responsavel_logado():
            print("Não há crianças cadastradas.")
            return

        id_crianca = input("Informe o ID da criança (ou 0 para voltar): ").strip()
        if id_crianca == "0":
            return

        crianca = self._buscar_crianca_do_responsavel_logado(id_crianca)
        if crianca is None:
            print("Erro: criança não encontrada para o ID informado.")
            return

        nome = input(f"Novo nome (Enter para manter '{crianca.nome}'): ").strip()
        data = input("Nova data de nascimento (DD/MM/YYYY) (Enter para manter): ").strip()
        nivel = input(f"Novo nível de suporte (1, 2 ou 3) (Enter para manter '{crianca.nivel_suporte}'): ").strip()

        try:
            self._servico_cadastro.editar_crianca(
                crianca=crianca,
                nome=nome,
                data_nascimento=data,
                nivel_suporte=nivel,
            )
            self._servico_perfil.sincronizar_dados_crianca_no_perfil_sensorial(
                perfil=self._perfil,
                crianca=crianca,
            )
        except (ValueError, TypeError) as error:
            print(f"Erro: {error}")
            return

        self._persistir_estado()
        print("Informações da criança atualizadas com sucesso.")

    def _excluir_crianca(self) -> None:
        if not self._obter_criancas_do_responsavel_logado():
            print("Erro: não há criança cadastrada para excluir.")
            return

        id_crianca = input("Informe o ID da criança que deseja excluir (ou 0 para voltar): ").strip()
        if id_crianca == "0":
            return

        crianca = self._buscar_crianca_do_responsavel_logado(id_crianca)
        if crianca is None:
            print("Erro: criança não encontrada para o ID informado.")
            return

        confirmacao = input(f"Confirma exclusão da criança {crianca.nome}? (S/N): ").strip().lower()
        if confirmacao != "s":
            print("Exclusão cancelada.")
            return

        self._criancas, self._rotinas = self._servico_perfil.excluir_crianca(
            criancas=self._criancas,
            rotinas=self._rotinas,
            perfil=self._perfil,
            id_crianca=id_crianca,
        )
        self._persistir_estado()
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