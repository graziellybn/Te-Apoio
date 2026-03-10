# TeApoio

O TeApoio é um projeto desenvolvido por alunos do curso de Engenharia de Software da Universidade Federal do Cariri (UFCA) para a discilipna de POO (Programação Orientada a Objetos). Ele trata-se de um sistema backend desenvolvido em Python, destinado ao monitoramento e à geração de relatórios para o acompanhamento de crianças com Transtorno do Espectro Autista (TEA). O foco do projeto é a aplicação prática dos principais conceitos de POO, conforme os requisitos da disciplina.

---

## 🎯 Objetivo do Projeto

O sistema permite registrar informações relacionadas à rotina da criança, como atividades realizadas, eventos relevantes e observações do dia a dia.

Esses dados podem ser acompanhados ao longo do tempo e utilizados para gerar relatórios com diferentes enfoques, como análise de rotina, acompanhamento educacional ou observações de comportamento.

O projeto tem como foco principal demonstrar a aplicação prática dos conceitos estudados na disciplina de *POO*, especialmente na organização do domínio e na separação entre lógica de negócio e infraestrutura.

---

## 👥 Equipe

- *Grazielly Bibiano do Nascimento* — GitHub: graziellybn  
- *Pedro Kauan Cardoso da Silva* — GitHub: DevPKauan01  
- *Ramona Vitória Clemente Cardoso* — GitHub: ramona-dev  

---

## 🏗️ Arquitetura

O sistema foi organizado utilizando uma *arquitetura em camadas*, separando claramente as responsabilidades entre as partes do projeto.

- *Domínio*: contém as entidades principais e regras de negócio do sistema  
- *Aplicação*: contém serviços responsáveis por coordenar os casos de uso  
- *Infraestrutura*: responsável por persistência de dados, interface CLI e API  

Essa organização permite que o domínio permaneça independente das interfaces externas, facilitando manutenção e evolução do sistema.

---

## 📋 Requisitos Funcionais (RF)
RF01 — Cadastro do responsável
Cadastro de um responsável contendo informações como nome, email e data de nascimento. Após o cadastro é gerado automaticamente um identificador único (ID).

RF02 — Cadastro do perfil da criança
Cadastro de crianças vinculadas a um responsável, incluindo idade, nível de suporte e informações básicas para acompanhamento.

RF03 — Cadastro de perfil sensorial
Registro de informações sensoriais e preferências da criança, como hiperfocos, sensibilidades e seletividades.

RF04 — Cadastro de rotina fixa
Permite definir uma rotina composta por diferentes itens de atividades.

RF05 — Definição de itens de rotina
Os itens da rotina podem incluir informações como nome, horário, categoria e observações.

RF06 — Registro de rotina executada
Permite registrar, por data, a execução das atividades planejadas.

RF07 — Identificação de mudanças na rotina
Possibilita comparar atividades planejadas com atividades realizadas.

RF08 — Consulta de registros por período
Permite listar registros dentro de um intervalo de datas.

RF09 — Geração de relatórios
Permite gerar relatórios a partir dos dados registrados.

RF10 — Análise de rotina
Relatórios podem incluir informações sobre estabilidade da rotina e atividades realizadas.

---

## ⚙️ Requisitos Não Funcionais (RNF)
RNF01 — Confiabilidade dos registros
O sistema garante armazenamento e recuperação consistente das informações registradas.

RNF02 — Validação de dados
Entradas do sistema são validadas para evitar inconsistências ou dados inválidos.

RNF03 — Manutenibilidade
O código é organizado de forma modular, facilitando manutenção e evolução do sistema.

RNF04 — Legibilidade e organização do código
O projeto segue padrões de organização e nomenclatura para facilitar o trabalho em equipe.

## 📁 Estrutura de arquivos

```
README.md
requirements.txt
teapoio_data.json
teapoio/
├── application/
│   └── services/
│       ├── servico_cadastro.py
│       ├── servico_monitoramento.py
│       ├── servico_perfil.py
│       ├── servico_relatorios.py
│       └── servico_rotinas.py
│
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
│
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
│
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

## 🚀 Backend Flask (API)
O projeto pode ser executado como um *backend HTTP utilizando Flask*, reutilizando as regras de negócio implementadas no domínio e os serviços da aplicação.
Como executar:

### 1. Clone o repositório:

```bash
git clone https://github.com/graziellybn/Te-Apoio.git
cd Te-Apoio
```
### 2. Instale as dependências do projeto:
```
pip install -r requirements.txt
```
### 3. Instalar o Flask:
```
pip install Flask
```
### 4. Execute a aplicação:
```
python -m teapoio.infrastructure.main
```
Após iniciar, a API estará disponível em:
```
http://127.0.0.1:5000
