# TeApoio

Este é um projeto desenvolvido por alunos do curso de Engenharia de Software da Universidade Federal do Cariri (UFCA). Trata-se de um sistema backend desenvolvido em Python com FastAPI, destinado ao monitoramento e à geração de relatórios para o acompanhamento de crianças com Transtorno do Espectro Autista (TEA). O foco do projeto é a aplicação prática dos principais conceitos de Programação Orientada a Objetos (POO), conforme os requisitos da disciplina.

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
- **Interface**: API desenvolvida com FastAPI

As camadas de domínio não dependem das camadas superiores.

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

- RNF03 — Usabilidade via API
A API deve possuir endpoints consistentes e documentação automática (ex.: OpenAPI/Swagger), permitindo testar o sistema sem interface gráfica.

- RNF04 — Manutenibilidade
O sistema deve ser organizado de forma a facilitar evolução e manutenção, evitando duplicação de lógica e concentrando regras de negócio em componentes apropriados.

- RNF05 — Testabilidade
As regras de negócio devem ser implementadas de forma que possam ser testadas independentemente da camada de API.

- RNF06 — Padrão de código e legibilidade
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
teapoio/
│
├── application/
│   ├── factories/
│   │   ├── seletor_relatorio.py
│   │   └── fabrica_eventos.py
│   ├── reports/
│   │   ├── gerador_relatorio.py
│   │   ├── relatorio_clinico.py
│   │   ├── relatorio_educacional.py
│   │   └── relatorio_estatistico.py
│   └── services/
│       ├── servico_monitoramento.py
│       ├── servico_relatorios.py
│       └── servico_rotina.py
│
├── domain/
│   ├── entities/
│   │   ├── crianca.py
│   │   ├── item_executado.py
│   │   ├── rotina_executada.py
│   │   ├── desvio_rotina.py
│   │   ├── item_rotina.py
│   │   ├── perfil_sensorial.py
│   │   ├── recorrencia.py
│   │   ├── relatorio.py
│   │   ├── responsavel.py
│   │   └── rotina_fixa.py
│   ├── events/
│   │   ├── evento.py
│   │   ├── evento_atividade.py
│   │   ├── evento_crise.py
│   │   ├── evento_marco.py
│   │   └── evento_rotina_alterada.py
│   └── mixins/
│       └── exportavel_json.py
│
├── infrastructure/
│   └── interface/
│       ├── api/
│       │   ├── eventos.py
│       │   ├── rotinas.py
│       │   ├── relatorios.py
│       │   └── main.py
│       └── repositories/
│           ├── evento_repository.py
│           ├── in_memory_evento_repo.py
│           ├── in_memory_rotina_repo.py
│           └── rotina_repository.py
│
├── tests/
│   ├── test_eventos.py
│   ├── test_mocks.py
│   ├── test_relatorios.py
│   └── test_rotinas.py
│
└── README.md
```
- **application/** → Orquestra lógica de uso, relatórios e serviços.  
- **domain/** → Contém entidades, eventos e regras de negócio centrais.  
- **infrastructure/** → Implementações concretas de acesso a dados e API.  
- **tests/** → Testes unitários e de integração.  
- **README.md** → Documentação principal do projeto.
