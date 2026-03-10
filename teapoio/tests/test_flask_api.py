from teapoio.infrastructure.flask_app import create_app
from teapoio.domain.models.item_rotina import ItemRotina
from datetime import date, datetime, timedelta


def test_api_raiz_retorna_resumo(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    resposta = client.get("/")
    assert resposta.status_code == 200
    assert "text/html" in resposta.content_type
    assert b"TeApoio" in resposta.data

    resposta_api = client.get("/api")
    assert resposta_api.status_code == 200

    payload = resposta_api.get_json()
    assert payload["mensagem"] == "TeApoio API ativa."
    assert payload["rotas_uteis"]["health"] == "/health"


def _criar_responsavel(client):
    resposta = client.post(
        "/responsaveis",
        json={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
    )
    assert resposta.status_code == 201
    return resposta.get_json()["responsavel"]["id_responsavel"]


def _criar_crianca(client, id_responsavel: str):
    resposta = client.post(
        f"/responsaveis/{id_responsavel}/criancas",
        json={
            "nome": "Ana Souza",
            "data_nascimento": "10/07/2015",
            "nivel_suporte": 2,
        },
    )
    assert resposta.status_code == 201
    return resposta.get_json()["crianca"]["id_crianca"]


def _extrair_primeiro_id_crianca_html(html: str) -> str:
    marcador = 'name="id_crianca" value="'
    inicio = html.find(marcador)
    assert inicio != -1
    inicio += len(marcador)
    fim = html.find('"', inicio)
    assert fim != -1
    return html[inicio:fim]


def test_api_cadastro_e_listagem_criancas(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    id_responsavel = _criar_responsavel(client)
    id_crianca = _criar_crianca(client, id_responsavel)

    resposta = client.get(f"/responsaveis/{id_responsavel}/criancas")
    assert resposta.status_code == 200

    payload = resposta.get_json()
    assert len(payload["criancas"]) == 1
    assert payload["criancas"][0]["id_crianca"] == id_crianca


def test_api_fluxo_rotina_item_e_status(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    id_responsavel = _criar_responsavel(client)
    id_crianca = _criar_crianca(client, id_responsavel)

    resposta_item = client.post(
        f"/rotinas/{id_crianca}/itens",
        json={
            "data": "2026-03-07",
            "nome": "Escovar os dentes",
            "horario": "08:00",
        },
    )
    assert resposta_item.status_code == 201

    resposta_status = client.patch(
        f"/rotinas/{id_crianca}/itens/0/status",
        json={
            "data": "2026-03-07",
            "status": 1,
        },
    )
    assert resposta_status.status_code == 200
    assert resposta_status.get_json()["status"] == ItemRotina.STATUS_CONCLUIDO

    resposta_rotina = client.get(f"/rotinas/{id_crianca}?data=2026-03-07")
    assert resposta_rotina.status_code == 200

    rotina = resposta_rotina.get_json()["rotina"]
    assert len(rotina["itens"]) == 1
    assert rotina["itens"][0]["status"] == ItemRotina.STATUS_CONCLUIDO


def test_api_perfil_sensorial(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    id_responsavel = _criar_responsavel(client)
    id_crianca = _criar_crianca(client, id_responsavel)

    resposta_put = client.put(
        f"/criancas/{id_crianca}/perfil-sensorial",
        json={
            "hipersensibilidades": ["som alto"],
            "hipossensibilidades": ["toque leve"],
            "hiperfocos": ["dinossauros"],
            "seletividade_alimentar": ["textura"],
            "estrategias_regulacao": ["fones"],
        },
    )
    assert resposta_put.status_code == 200

    resposta_get = client.get(f"/criancas/{id_crianca}/perfil-sensorial")
    assert resposta_get.status_code == 200

    perfil = resposta_get.get_json()["perfil_sensorial"]
    assert perfil["hiperfocos"] == ["dinossauros"]


def test_api_retorna_erro_para_payload_invalido(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    resposta = client.post("/responsaveis", json={"nome": "SoNome"})
    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()


def test_api_rejeita_email_responsavel_duplicado(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    resposta_1 = client.post(
        "/responsaveis",
        json={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
    )
    assert resposta_1.status_code == 201

    resposta_2 = client.post(
        "/responsaveis",
        json={
            "nome": "Maria Souza",
            "data_nascimento": "01/01/1986",
            "email": "maria@example.com",
            "senha": "outra123",
        },
    )
    assert resposta_2.status_code == 400
    assert "Ja existe responsavel cadastrado com este email." in resposta_2.get_json()["erro"]


def test_api_permite_senha_responsavel_repetida_com_email_diferente(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    resposta_1 = client.post(
        "/responsaveis",
        json={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "senha123",
        },
    )
    assert resposta_1.status_code == 201

    resposta_2 = client.post(
        "/responsaveis",
        json={
            "nome": "Joana Souza",
            "data_nascimento": "01/01/1986",
            "email": "joana@example.com",
            "senha": "senha123",
        },
    )
    assert resposta_2.status_code == 201


def test_web_cadastro_responsavel_funciona_com_secret_key_padrao(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
            "SECRET_KEY": None,
        }
    )
    client = app.test_client()

    resposta = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )

    assert resposta.status_code == 302

def test_web_opcao_ver_perfil_renderiza_dados(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro.status_code == 302

    resposta = client.get("/?secao=perfil")
    assert resposta.status_code == 200
    assert b"Perfil do responsavel" in resposta.data
    assert b"maria@example.com" in resposta.data


def test_web_fluxo_inicial_exibe_criar_conta(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    resposta = client.get("/")
    assert resposta.status_code == 200
    assert b"Criar conta" in resposta.data
    assert b"Ja sou cadastrado." in resposta.data
    assert b"Sair da conta" not in resposta.data


def test_web_nao_exibe_secao_interna_sem_login(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    resposta = client.get("/?secao=criancas")
    assert resposta.status_code == 200
    assert b"Criar conta" in resposta.data
    assert b"Cadastrar crianca" not in resposta.data


def test_web_login_exibe_abas_internas_e_oculta_cadastro_login(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    resposta = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=True,
    )

    assert resposta.status_code == 200
    assert b"Sair da conta" in resposta.data
    assert b"Criancas" in resposta.data
    assert b"Rotina" in resposta.data
    assert b"Ver perfil" in resposta.data
    assert b"Criar conta" not in resposta.data
    assert b"Ja sou cadastrado." not in resposta.data


def test_web_logout_retorna_para_fluxo_inicial(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro.status_code == 302

    logout = client.post("/web/logout", follow_redirects=True)
    assert logout.status_code == 200
    assert b"Criar conta" in logout.data
    assert b"Ja sou cadastrado." in logout.data
    assert b"Sair da conta" not in logout.data


def test_web_altera_status_item_rotina(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro_responsavel = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro_responsavel.status_code == 302

    cadastro_crianca = client.post(
        "/web/crianca/cadastrar",
        data={
            "nome": "Ana Souza",
            "data_nascimento": "10/07/2015",
            "nivel_suporte": "2",
        },
        follow_redirects=False,
    )
    assert cadastro_crianca.status_code == 302

    item_rotina = client.post(
        "/web/rotina/item",
        data={
            "data": "2026-03-07",
            "nome": "Cafe da manha",
            "horario": "08:00",
        },
        follow_redirects=False,
    )
    assert item_rotina.status_code == 302

    resposta_status = client.post(
        "/web/rotina/item/status",
        data={
            "data": "2026-03-07",
            "indice": "0",
            "status": "1",
        },
        follow_redirects=True,
    )

    assert resposta_status.status_code == 200
    assert "Concluído" in resposta_status.get_data(as_text=True)


def test_web_remove_item_rotina(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro_responsavel = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro_responsavel.status_code == 302

    cadastro_crianca = client.post(
        "/web/crianca/cadastrar",
        data={
            "nome": "Ana Souza",
            "data_nascimento": "10/07/2015",
            "nivel_suporte": "2",
        },
        follow_redirects=False,
    )
    assert cadastro_crianca.status_code == 302

    item_rotina = client.post(
        "/web/rotina/item",
        data={
            "data": "2026-03-07",
            "nome": "Lanchar",
            "horario": "08:00",
        },
        follow_redirects=False,
    )
    assert item_rotina.status_code == 302

    resposta_remocao = client.post(
        "/web/rotina/item/remover",
        data={
            "data": "2026-03-07",
            "indice": "0",
        },
        follow_redirects=True,
    )

    assert resposta_remocao.status_code == 200
    assert "Item removido com sucesso." in resposta_remocao.get_data(as_text=True)


def test_web_edita_crianca(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro_responsavel = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro_responsavel.status_code == 302

    cadastro_crianca = client.post(
        "/web/crianca/cadastrar",
        data={
            "nome": "Ana Souza",
            "data_nascimento": "10/07/2015",
            "nivel_suporte": "2",
        },
        follow_redirects=False,
    )
    assert cadastro_crianca.status_code == 302

    pagina_criancas = client.get("/?secao=criancas")
    id_crianca = _extrair_primeiro_id_crianca_html(pagina_criancas.get_data(as_text=True))

    edicao = client.post(
        "/web/crianca/editar",
        data={
            "id_crianca": id_crianca,
            "nome": "Ana Clara",
            "data_nascimento": "",
            "nivel_suporte": "3",
        },
        follow_redirects=True,
    )

    texto = edicao.get_data(as_text=True)
    assert edicao.status_code == 200
    assert "Crianca atualizada com sucesso." in texto
    assert "Ana Clara" in texto


def test_web_exclui_crianca(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro_responsavel = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro_responsavel.status_code == 302

    cadastro_crianca = client.post(
        "/web/crianca/cadastrar",
        data={
            "nome": "Ana Souza",
            "data_nascimento": "10/07/2015",
            "nivel_suporte": "2",
        },
        follow_redirects=False,
    )
    assert cadastro_crianca.status_code == 302

    pagina_criancas = client.get("/?secao=criancas")
    id_crianca = _extrair_primeiro_id_crianca_html(pagina_criancas.get_data(as_text=True))

    exclusao = client.post(
        "/web/crianca/excluir",
        data={
            "id_crianca": id_crianca,
            "confirmacao_1": "sim",
            "confirmacao_2": "EXCLUIR",
        },
        follow_redirects=True,
    )

    texto = exclusao.get_data(as_text=True)
    assert exclusao.status_code == 200
    assert "Crianca excluida com sucesso." in texto
    assert "Nenhuma crianca cadastrada para este responsavel." in texto


def test_web_excluir_crianca_exige_dupla_confirmacao(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro_responsavel = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro_responsavel.status_code == 302

    cadastro_crianca = client.post(
        "/web/crianca/cadastrar",
        data={
            "nome": "Ana Souza",
            "data_nascimento": "10/07/2015",
            "nivel_suporte": "2",
        },
        follow_redirects=False,
    )
    assert cadastro_crianca.status_code == 302

    pagina_criancas = client.get("/?secao=criancas")
    id_crianca = _extrair_primeiro_id_crianca_html(pagina_criancas.get_data(as_text=True))

    exclusao = client.post(
        "/web/crianca/excluir",
        data={
            "id_crianca": id_crianca,
            "confirmacao_1": "",
            "confirmacao_2": "",
        },
        follow_redirects=True,
    )

    texto = exclusao.get_data(as_text=True)
    assert exclusao.status_code == 200
    assert "Para excluir, marque a confirmacao e digite EXCLUIR." in texto
    assert "Ana Souza" in texto


def test_web_edita_responsavel(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro_responsavel = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro_responsavel.status_code == 302

    edicao = client.post(
        "/web/responsavel/editar",
        data={
            "nome": "Maria Souza",
            "data_nascimento": "",
            "email": "maria.souza@example.com",
        },
        follow_redirects=True,
    )

    texto = edicao.get_data(as_text=True)
    assert edicao.status_code == 200
    assert "Dados do responsavel atualizados com sucesso." in texto
    assert "maria.souza@example.com" in texto


def test_web_cadastra_perfil_sensorial(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro_responsavel = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro_responsavel.status_code == 302

    cadastro_crianca = client.post(
        "/web/crianca/cadastrar",
        data={
            "nome": "Ana Souza",
            "data_nascimento": "10/07/2015",
            "nivel_suporte": "2",
        },
        follow_redirects=False,
    )
    assert cadastro_crianca.status_code == 302

    resposta_perfil = client.get("/?secao=perfil")
    html = resposta_perfil.get_data(as_text=True)
    marcador = "value=\""
    inicio = html.find(marcador)
    assert inicio != -1
    inicio += len(marcador)
    fim = html.find('"', inicio)
    id_crianca = html[inicio:fim]
    assert id_crianca

    salvar = client.post(
        "/web/perfil-sensorial/salvar",
        data={
            "id_crianca": id_crianca,
            "hipersensibilidades": "som alto, luz forte",
            "hipossensibilidades": "toque leve",
            "hiperfocos": "dinossauros",
            "seletividade_alimentar": "textura",
            "estrategias_regulacao": "fones",
        },
        follow_redirects=True,
    )

    assert salvar.status_code == 200
    texto = salvar.get_data(as_text=True)
    assert "Perfil sensorial salvo com sucesso." in texto
    assert "Ana Souza (ID:" in texto
    assert "Perfil sensorial: cadastrado." in texto
    assert "Hipersensibilidades: som alto, luz forte" in texto
    assert "Hipossensibilidades: toque leve" in texto
    assert "Hiperfocos: dinossauros" in texto
    assert "Seletividade alimentar: textura" in texto
    assert "Estrategias de regulacao: fones" in texto


def test_web_mostra_onboarding_no_primeiro_acesso_logado(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    resposta = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=True,
    )

    assert resposta.status_code == 200
    assert "Primeiros passos" in resposta.get_data(as_text=True)


def test_web_calendario_seleciona_data(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro_responsavel = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro_responsavel.status_code == 302

    cadastro_crianca = client.post(
        "/web/crianca/cadastrar",
        data={
            "nome": "Ana Souza",
            "data_nascimento": "10/07/2015",
            "nivel_suporte": "2",
        },
        follow_redirects=False,
    )
    assert cadastro_crianca.status_code == 302

    resposta = client.post(
        "/web/calendario/selecionar",
        data={"data": "2026-03-06"},
        follow_redirects=True,
    )

    assert resposta.status_code == 200
    assert "Calendario da rotina" in resposta.get_data(as_text=True)
    assert "2026-03-06" in resposta.get_data(as_text=True)


def test_web_rotina_mostra_evolucao_periodo(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro_responsavel = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro_responsavel.status_code == 302

    cadastro_crianca = client.post(
        "/web/crianca/cadastrar",
        data={
            "nome": "Ana Souza",
            "data_nascimento": "10/07/2015",
            "nivel_suporte": "2",
        },
        follow_redirects=False,
    )
    assert cadastro_crianca.status_code == 302

    base = date.today().isoformat()
    item_rotina = client.post(
        "/web/rotina/item",
        data={
            "data": base,
            "nome": "Tarefa do dia",
            "horario": "08:00",
        },
        follow_redirects=False,
    )
    assert item_rotina.status_code == 302

    resposta = client.get(f"/?secao=rotina&data_rotina={base}")
    assert resposta.status_code == 200
    assert "Evolucao por periodo" in resposta.get_data(as_text=True)

def test_web_salva_observacao_rapida_item_rotina(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro_responsavel = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro_responsavel.status_code == 302

    cadastro_crianca = client.post(
        "/web/crianca/cadastrar",
        data={
            "nome": "Ana Souza",
            "data_nascimento": "10/07/2015",
            "nivel_suporte": "2",
        },
        follow_redirects=False,
    )
    assert cadastro_crianca.status_code == 302

    base = date.today().isoformat()
    item_rotina = client.post(
        "/web/rotina/item",
        data={
            "data": base,
            "nome": "Anotar algo",
            "horario": "08:00",
        },
        follow_redirects=False,
    )
    assert item_rotina.status_code == 302

    resposta = client.post(
        "/web/rotina/item/observacao",
        data={
            "data": base,
            "indice": "0",
            "observacao": "Teve boa resposta ao estimulo.",
        },
        follow_redirects=True,
    )
    assert resposta.status_code == 200
    texto = resposta.get_data(as_text=True)
    assert "Observacao salva com sucesso." in texto
    assert "Teve boa resposta ao estimulo." in texto


def test_web_mostra_alerta_tempo_item_pendente(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro.status_code == 302

    cadastro_crianca = client.post(
        "/web/crianca/cadastrar",
        data={
            "nome": "Ana Souza",
            "data_nascimento": "10/07/2015",
            "nivel_suporte": "2",
        },
        follow_redirects=False,
    )
    assert cadastro_crianca.status_code == 302

    base = date.today().isoformat()
    horario_futuro = (datetime.now() + timedelta(minutes=10)).strftime("%H:%M")
    client.post(
        "/web/rotina/item",
        data={
            "data": base,
            "nome": "Tarefa com horario futuro",
            "horario": horario_futuro,
        },
        follow_redirects=False,
    )

    resposta = client.get(f"/?secao=rotina&data_rotina={base}")
    texto = resposta.get_data(as_text=True)
    assert resposta.status_code == 200
    assert "Falta" in texto
    assert "Atrasada ha" not in texto


def test_web_exporta_relatorio_pdf(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro.status_code == 302

    cadastro_crianca = client.post(
        "/web/crianca/cadastrar",
        data={
            "nome": "Ana Souza",
            "data_nascimento": "10/07/2015",
            "nivel_suporte": "2",
        },
        follow_redirects=False,
    )
    assert cadastro_crianca.status_code == 302

    pagina = client.get("/?secao=criancas")
    id_crianca = _extrair_primeiro_id_crianca_html(pagina.get_data(as_text=True))

    hoje = date.today()
    base = hoje.replace(day=1).isoformat()
    dia_2 = hoje.replace(day=2).isoformat()
    dia_3 = hoje.replace(day=3).isoformat()

    client.post(
        "/web/rotina/sentimento",
        data={"data": base, "sentimento": "bem"},
        follow_redirects=False,
    )
    client.post(
        "/web/rotina/sentimento",
        data={"data": dia_2, "sentimento": "bem"},
        follow_redirects=False,
    )
    client.post(
        "/web/rotina/sentimento",
        data={"data": dia_3, "sentimento": "cansativo"},
        follow_redirects=False,
    )

    resposta = client.get(f"/web/relatorio/pdf?id_crianca={id_crianca}&data={base}")

    assert resposta.status_code == 200
    assert "application/pdf" in resposta.content_type
    assert "attachment;" in resposta.headers.get("Content-Disposition", "")
    assert resposta.data.startswith(b"%PDF")
    assert len(resposta.data) > 1200


def test_api_adiciona_item_rotina_com_tags_e_observacao(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    id_responsavel = _criar_responsavel(client)
    id_crianca = _criar_crianca(client, id_responsavel)

    resposta_item = client.post(
        f"/rotinas/{id_crianca}/itens",
        json={
            "data": "2026-03-07",
            "nome": "Escovar os dentes",
            "horario": "08:00",
            "observacao": "Combinado com reforco positivo",
            "tags": ["higiene", "manha"],
        },
    )
    assert resposta_item.status_code == 201

    resposta_rotina = client.get(f"/rotinas/{id_crianca}?data=2026-03-07")
    assert resposta_rotina.status_code == 200
    item = resposta_rotina.get_json()["rotina"]["itens"][0]
    assert item["observacao"] == "Combinado com reforco positivo"
    assert item["tags"] == ["higiene", "manha"]


def test_web_atualiza_sentimento_dia_com_emoji(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro.status_code == 302

    cadastro_crianca = client.post(
        "/web/crianca/cadastrar",
        data={
            "nome": "Ana Souza",
            "data_nascimento": "10/07/2015",
            "nivel_suporte": "2",
        },
        follow_redirects=False,
    )
    assert cadastro_crianca.status_code == 302

    base = date.today().isoformat()
    resposta = client.post(
        "/web/rotina/sentimento",
        data={
            "data": base,
            "sentimento": "bem",
        },
        follow_redirects=True,
    )
    assert resposta.status_code == 200
    texto = resposta.get_data(as_text=True)
    assert "Sentimento do dia atualizado com sucesso." in texto
    assert "🙂 Bem" in texto


def test_web_salva_tags_no_item_rotina(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATA_FILE": str(tmp_path / "estado_api.json"),
        }
    )
    client = app.test_client()

    cadastro_responsavel = client.post(
        "/web/responsavel/cadastrar",
        data={
            "nome": "Maria Silva",
            "data_nascimento": "01/01/1985",
            "email": "maria@example.com",
            "senha": "maria123",
        },
        follow_redirects=False,
    )
    assert cadastro_responsavel.status_code == 302

    cadastro_crianca = client.post(
        "/web/crianca/cadastrar",
        data={
            "nome": "Ana Souza",
            "data_nascimento": "10/07/2015",
            "nivel_suporte": "2",
        },
        follow_redirects=False,
    )
    assert cadastro_crianca.status_code == 302

    base = date.today().isoformat()
    item_rotina = client.post(
        "/web/rotina/item",
        data={
            "data": base,
            "nome": "Escovar os dentes",
            "horario": "08:00",
        },
        follow_redirects=False,
    )
    assert item_rotina.status_code == 302

    resposta = client.post(
        "/web/rotina/item/observacao",
        data={
            "data": base,
            "indice": "0",
            "observacao": "Aceitou bem o apoio visual.",
            "tags": "higiene, manha",
        },
        follow_redirects=True,
    )
    assert resposta.status_code == 200
    texto = resposta.get_data(as_text=True)
    assert "Observacao salva com sucesso." in texto
    assert "#higiene" in texto
    assert "#manha" in texto
