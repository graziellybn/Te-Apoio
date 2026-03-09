# TeApoio

O TeApoio é um projeto desenvolvido por alunos do curso de Engenharia de Software da Universidade Federal do Cariri (UFCA) para a discilipna de POO (Programação Orientada a Objetos). Ele trata-se de um sistema backend desenvolvido em Python, destinado ao monitoramento e à geração de relatórios para o acompanhamento de crianças com Transtorno do Espectro Autista (TEA). O foco do projeto é a aplicação prática dos principais conceitos de POO, conforme os requisitos da disciplina.

---

## 🎯 Objetivo do Projeto

O sistema tem como objetivo permitir o registro de rotina da criança (como crises, atividades e marcos de desenvolvimento), possibilitando o monitoramento e acompanhamenro desses dados ao longo do tempo através da geração de relatórios com diferentes enfoques (clínico, educacional e estatístico).

---

## 👥 Equipe

- Grazielly Bibiano do Nascimento — GitHub: graziellybn  
- Pedro Kauan Cardoso da Silva — GitHub: DevPKauan01  
- Ramona Vitória Clemente Cardoso — GitHub: ramona-dev  


---

## 🏗️ Arquitetura

O sistema segue uma arquitetura em camadas, separando claramente as responsabilidades:

- **Domínio**: entidades e regras de negócio centrais
- **Aplicação**: serviços e casos de uso
- **Infraestrutura**: persistência de dados

As camadas de domínio não dependem das camadas superiores.

---

## 🚀 Backend Flask (API)

O projeto agora pode ser executado como backend HTTP com Flask, reutilizando as regras de dominio e os servicos da CLI.

### Como executar:

```bash
pip install -r requirements.txt
python -m teapoio.infrastructure.main
```

A API será iniciada por padrão em `http://127.0.0.1:5000`.

### Variáveis de ambiente opcionais

- `TEAPOIO_HOST` (padrao: `127.0.0.1`)
- `TEAPOIO_PORT` (padrao: `5000`)
- `TEAPOIO_DEBUG` (`1` ou `0`, padrao: `1`)

### Rotas principais

- `GET /health`
- `GET /responsaveis`
- `POST /responsaveis`
- `GET /responsaveis/<id_responsavel>`
- `GET /responsaveis/<id_responsavel>/criancas`
- `POST /responsaveis/<id_responsavel>/criancas`
- `PATCH /criancas/<id_crianca>`
- `DELETE /criancas/<id_crianca>`
- `PUT /criancas/<id_crianca>/perfil-sensorial`
- `GET /criancas/<id_crianca>/perfil-sensorial`
- `GET /rotinas/<id_crianca>?data=AAAA-MM-DD`
- `POST /rotinas/<id_crianca>/itens`
- `PATCH /rotinas/<id_crianca>/itens/<indice>/status`
- `DELETE /rotinas/<id_crianca>/itens/<indice>?data=AAAA-MM-DD`
- `GET /sugestoes-rotina`

---

## 📋 Requisitos Funcionais (RF)

- RF01 — Cadastro do responsável
Cadastro de um responsável, armazenando dados como nome, email, data de nascimento. Após o cadastro é gerado um id automaticamente a ser vinculado com o usuário. Todas as informações são editáveis(exc:ID).

- RF02 — Cadastro do perfil da criança
Cadastro do perfil de uma criança vinculada ao responsável, incluindo idade, nível de suporte e informações essenciais ao acompanhamento. Permite apartir do id de um responsável seguir com o cadastro, todas as informações são editáveis(exc: ID).

- RF03 — Cadastro de perfil sensorial
Cadastro de informações sensoriais e preferências (hiperfocos, seletividades e sensibilidades) associadas à criança. Sendo todas editáveis após o primeiro ato de cadastro. 

- RF04 — Cadastro de rotina fixa
O sistema permite cadastrar uma rotina fixa composta por itens de rotina.

- RF05 — Definição de recorrência por item da rotina
O sistema permite que o cadastro de itens que compoem a rotina, por dados como: nome, descrição, horário, categoria e tag. Eles são editáveis e podem ser recorrentes.

- RF06 — Registro de rotina executada (diária)
O sistema permite registrar, por data, a execução da rotina (itens realizados e observações).

- RF07 — Detecção de mudanças na rotina
O sistema deve comparar a rotina executada com a rotina fixa prevista para a data e identificar mudanças (desvios), registrando o resultado.

- RF08 — Listagem e consulta de eventos por período
O sistema permite listar eventos e registros em um intervalo de datas para fins de acompanhamento.

- RF09 — Geração de relatórios por período
O sistema permite gerar relatórios a partir dos dados registrados, em um período selecionado.

- RF10— Integração dos desvios da rotina nos relatórios
Os relatórios devem incluir informações sobre a estabilidade da rotina e os desvios identificados no período, quando existirem registrosm além de conter gráficos com a evolução a partir do registro de item de rotina feito. 
---

## ⚙️ Requisitos Não Funcionais (RNF)

- RNF01 — Confiabilidade e integridade dos registros
O sistema garante que registros de eventos, rotinas executadas e dados do perfil sejam armazenados e recuperados sem inconsistências por conta da persistência.

- RNF02 — Validação e tratamento de erros
O sistema valida entradas e retornar erros de forma explícita e compreensível (ex.: dados inválidos, período incorreto, recurso inexistente).

- RNF03 — Manutenibilidade
O sistema deve ser organizado de forma a facilitar evolução e manutenção, evitando duplicação de lógica e concentrando regras de negócio em componentes apropriados.

- RNF04 — Padrão de código e legibilidade
O código deve manter padronização de nomes, organização e estilo, priorizando a legibilidade para trabalho em equipe.
---

## 📌 Regras de Negócio (RB)
### Cadastro e perfil

- RB01 — Vínculo responsável–criança
Cada responsável pode cadastrar (N) perfis de criança no escopo atual do projeto, porém todas elas devem ser criadas e vinculadas a partir de um responsável. 

- RB02 — Nível de suporte válido
O nível de suporte da criança deve estar dentro de um conjunto válido (ex.: 1 a 3). Valores fora do intervalo devem ser rejeitados.

- RB03 — Verificação de idade
O responsável pode ser apenas maior de idade, o cálculo é feito com base na data de nascimento. Datas no futuro não são aceitas.

- RB04 - Validações gerais
Cadastro de usuário (Pessoa) deve ter nome e sobrenome, idade deve ser válida, o email deve ter @ e deve ter senha válida. Exceções serão tratadas com erro. 


### Rotina fixa e recorrência

- RB05 — Item de rotina deve ter recorrência definida
Todo item cadastrado na rotina fixa deve indicar ao menos um dia da semana para repetição.

### Rotina executada e detecção de mudanças

- RB06 — ItemRotina deve estar associado a uma data/horário
Cada registro de rotina deve possuir data única (não pode existir dois registros de rotina para a mesma data, a menos que exista atualização explícita).

### Monitoramento por eventos

- RB09 — Evento deve ser válido para ser registrado
Todo evento deve passar por validação antes de ser persistido (ex.: crise exige intensidade dentro de um intervalo).

- RB10 — Tipos de evento têm comportamentos diferentes
Eventos diferentes devem ter validações e resumos específicos, explorando polimorfismo (ex.: crise possui intensidade; marco possui descrição; atividade possui nome/tipo).

### Relatórios

- RB11 — Relatório depende do período selecionado
Todo relatório deve ser gerado com base em um período (data inicial e final) e deve considerar apenas registros dentro desse intervalo.

- RB12 — Tipo de relatório define regras de geração
Cada tipo de relatório deve possuir estratégia própria de geração, podendo produzir seções e métricas diferentes baseados na rotina cadastro e na realização como "concluido".

- RB13 — Relatório deve incluir estabilidade da rotina quando houver dados
Se existirem rotinas executadas no período, o relatório deve apresentar síntese de desvios (quantidade por tipo e itens mais impactados).

---
## 🗂 Estrutura de Pastas
```
README.md
requirements.txt   # Dependências do projeto.
teapoio_data.json  # Base de dados local em JSON utilizada pela aplicação.
teapoio/
├── __init__.py
├── application/   # Camada de aplicação com os serviços e casos de uso.
│   └── services/
│       ├── servico_cadastro.py
│       ├── servico_monitoramento.py
│       ├── servico_perfil.py
│       ├── servico_relatorios.py
│       └── servico_rotinas.py
├── domain/        # Entidades e regras de negócio centrais do sistema.
│   └── models/ 
│       ├── calendario.py
│       ├── crianca.py
│       ├── evolucao.py
│       ├── item_rotina.py
│       ├── Perfil.py
│       ├── perfil_sensorial.py
│       ├── pessoa.py
│       ├── responsavel.py
│       └── rotina.py
├── infrastructure/ # CLI, API Flask, persistência e recursos de interface.
│   ├── cli.py
│   ├── flask_app.py
│   ├── main.py
│   ├── mixins/
│   │   └── exportavel_json.py
│   ├── persistence/
│   │   └── Relatorio.py
│   ├── static/
│   │   └── style.css
│   └── templates/
│       └── index.html
└── tests/          # Testes automatizados das regras, serviços e API.
    ├── test_calendario.py
    ├── test_flask_api.py
    ├── test_modelos.py
    ├── test_persistencia.py
    ├── test_relatorios.py
    ├── test_rotinas.py
    ├── test_servico_cadastro.py
    ├── test_servico_monitoramento.py
    ├── test_servico_perfil.py
    └── test_servico_rotinas.py
```

