# PetCare

## Gerenciador de Cuidados do Pet

O PetCare é uma aplicação web desenvolvida para auxiliar tutores na organização dos principais cuidados relacionados aos seus animais de estimação.

O sistema permite registrar vacinas, consultas, medicamentos e outros cuidados, mantendo as informações organizadas em uma agenda.

## Funcionalidades

- Cadastro do nome do pet
- Cadastro do tipo de cuidado
- Registro da descrição do cuidado
- Registro da data
- Visualização dos cuidados na agenda
- Identificação do status do cuidado
- Marcação do cuidado como concluído
- Exclusão de registros
- Armazenamento das informações em banco de dados

## Tecnologias utilizadas

- Python
- Flask
- HTML
- SQLite

## Estrutura do projeto

PetCare/
│
├── app.py
├── petcare.db
├── templates/
│   └── index.html
├── README.md
├── requirements.txt
└── .gitignore

## Como executar o projeto

### 1. Instalar o Python

É necessário possuir o Python instalado no computador.

### 2. Instalar as dependências

No terminal, dentro da pasta do projeto, execute:

pip install -r requirements.txt

### 3. Executar a aplicação

Execute:

python app.py

### 4. Acessar o sistema

Abra o navegador e acesse:

http://127.0.0.1:5000

## Banco de dados

O projeto utiliza SQLite para armazenamento dos dados.

O banco utilizado é:

petcare.db

A tabela principal é chamada:

cuidados

Ela armazena:

- ID
- Nome do pet
- Tipo de cuidado
- Descrição
- Data
- Status

## Situação atual

O projeto encontra-se em sua primeira versão funcional.

Esta versão será utilizada como base para a avaliação inicial da qualidade do software na disciplina de Qualidade de Software.

## Versão

v1.0.0-baseline