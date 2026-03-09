# TeApoio

Este é um projeto desenvolvido por alunos do curso de Engenharia de Software da Universidade Federal do Cariri (UFCA). Trata-se de um sistema backend desenvolvido em Python, destinado ao monitoramento e à geração de relatórios para o acompanhamento de crianças com Transtorno do Espectro Autista (TEA). O foco do projeto é a aplicação prática dos principais conceitos de Programação Orientada a Objetos (POO), conforme os requisitos da disciplina.

---

## 👥 Equipe

- Grazielly Bibiano do Nascimento — GitHub: graziellybn  
- Pedro Kauan Cardoso da Silva — GitHub: DevPKauan01  
- Ramona Vitória Clemente Cardoso — GitHub: ramona-dev  

---

## 🎯 Objetivo do Projeto

O sistema tem como objetivo permitir o registro de eventos do cotidiano da criança (como crises, atividades e marcos de desenvolvimento), possibilitando o monitoramento desses dados ao longo do tempo e a geração de relatórios com diferentes enfoques (clínico, educacional e estatístico).

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

### Executar

```bash
pip install -r requirements.txt
python -m teapoio.infrastructure.main
```

A API sera iniciada por padrao em `http://127.0.0.1:5000`.

### Variaveis de ambiente opcionais

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
O sistema deve permitir cadastrar um responsável, armazenando dados básicos de identificação (ex.: nome e e-mail).

- RF02 — Cadastro do perfil da criança
O sistema deve permitir cadastrar o perfil de uma criança vinculada ao responsável, incluindo idade, nível de suporte e informações essenciais ao acompanhamento.

- RF03 — Cadastro de perfil sensorial
O sistema deve permitir registrar informações sensoriais e preferências (hiperfocos, seletividades e sensibilidades) associadas à criança.

- RF04 — Cadastro de rotina fixa (baseline)
O sistema deve permitir cadastrar uma rotina fixa composta por itens de rotina.

- RF05 — Definição de recorrência por item da rotina
O sistema deve permitir que cada item da rotina seja configurado com recorrência semanal (seleção de dias da semana em que se repete).

- RF06 — Registro de rotina executada (diária)
O sistema deve permitir registrar, por data, a execução da rotina (itens realizados e observações).

- RF07 — Detecção de mudanças na rotina
O sistema deve comparar a rotina executada com a rotina fixa prevista para a data e identificar mudanças (desvios), registrando o resultado.

- RF08 — Registro de eventos do monitoramento
O sistema deve permitir registrar eventos do cotidiano da criança, contemplando no mínimo três tipos: crise, marco de desenvolvimento e atividade.

- RF09 — Listagem e consulta de eventos por período
O sistema deve permitir listar eventos e registros em um intervalo de datas para fins de acompanhamento.

- RF10 — Geração de relatórios por período
O sistema deve permitir gerar relatórios a partir dos dados registrados, em um período selecionado.

- RF11 — Tipos de relatório (estratégias)
O sistema deve disponibilizar pelo menos três tipos de relatório com enfoques distintos: clínico, educacional e estatístico.

- RF12 — Integração dos desvios da rotina nos relatórios
Os relatórios devem incluir informações sobre a estabilidade da rotina e os desvios identificados no período, quando existirem registros.
---

## ⚙️ Requisitos Não Funcionais (RNF)

- RNF01 — Confiabilidade e integridade dos registros
O sistema deve garantir que registros de eventos, rotinas executadas e desvios sejam armazenados e recuperados sem inconsistências.

- RNF02 — Validação e tratamento de erros
O sistema deve validar entradas e retornar erros de forma explícita e compreensível (ex.: dados inválidos, período incorreto, recurso inexistente).

- RNF03 — Manutenibilidade
O sistema deve ser organizado de forma a facilitar evolução e manutenção, evitando duplicação de lógica e concentrando regras de negócio em componentes apropriados.


- RNF04 — Padrão de código e legibilidade
O código deve manter padronização de nomes, organização e estilo, priorizando a legibilidade para trabalho em equipe.
---

## 📌 Regras de Negócio (RB)
### Cadastro e perfil

- RB01 — Vínculo responsável–criança
Cada responsável possuirá exatamente um perfil de criança no escopo atual do projeto. (Extensões futuras podem permitir múltiplas crianças.)

- RB02 — Nível de suporte válido
O nível de suporte da criança deve estar dentro de um conjunto válido (ex.: 1 a 3). Valores fora do intervalo devem ser rejeitados.

### Rotina fixa e recorrência

- RB03 — Item de rotina deve ter recorrência definida
Todo item cadastrado na rotina fixa deve indicar ao menos um dia da semana para repetição.

- RB04 — Itens previstos dependem da data
Para uma data específica, apenas itens cuja recorrência inclua o dia da semana correspondente são considerados “previstos”.

### Rotina executada e detecção de mudanças

- RB05 — Rotina executada deve estar associada a uma data
Cada registro de rotina executada deve possuir data única (não pode existir dois registros de rotina executada para a mesma data, a menos que exista atualização explícita).

- RB06 — Desvio por omissão
Um item previsto que não apareça na rotina executada deve ser registrado como desvio do tipo “omissão”.

- RB07 — Desvio por execução não prevista
Um item executado que não pertença aos itens previstos do dia deve ser registrado como desvio do tipo “execução extra/não prevista”.

- RB08 — Desvio deve ser persistido e reaproveitado
O resultado da comparação (lista de desvios) deve ser armazenado para uso em relatórios e estatísticas, evitando recalcular sem necessidade.

### Monitoramento por eventos

- RB09 — Evento deve ser válido para ser registrado
Todo evento deve passar por validação antes de ser persistido (ex.: crise exige intensidade dentro de um intervalo).

- RB10 — Tipos de evento têm comportamentos diferentes
Eventos diferentes devem ter validações e resumos específicos, explorando polimorfismo (ex.: crise possui intensidade; marco possui descrição; atividade possui nome/tipo).

### Relatórios

- RB11 — Relatório depende do período selecionado
Todo relatório deve ser gerado com base em um período (data inicial e final) e deve considerar apenas registros dentro desse intervalo.

- RB12 — Tipo de relatório define regras de geração
Cada tipo de relatório deve possuir estratégia própria de geração, podendo produzir seções e métricas diferentes (ex.: clínico prioriza crises; estatístico agrega frequências; educacional prioriza marcos).

- RB13 — Relatório deve incluir estabilidade da rotina quando houver dados
Se existirem rotinas executadas no período, o relatório deve apresentar síntese de desvios (quantidade por tipo e itens mais impactados).

---
## 🗂 Estrutura de Pastas
```
README.md
requirements.txt
teapoio_data.json
teapoio/
├── __init__.py
├── application/
│   └── services/
│       ├── servico_cadastro.py
│       ├── servico_monitoramento.py
│       ├── servico_perfil.py
│       ├── servico_relatorios.py
│       └── servico_rotinas.py
├── domain/
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
├── infrastructure/
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
└── tests/
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
- **teapoio/application/** -> Camada de aplicação com os serviços e casos de uso.
- **teapoio/domain/** -> Entidades e regras de negócio centrais do sistema.
- **teapoio/infrastructure/** -> CLI, API Flask, persistência e recursos de interface.
- **teapoio/tests/** -> Testes automatizados das regras, serviços e API.
- **requirements.txt** -> Dependências do projeto.
- **teapoio_data.json** -> Base de dados local em JSON utilizada pela aplicação.
