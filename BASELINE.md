# Baseline de Qualidade - PetCare

## Versão analisada

v1.0.0-baseline

## Descrição

Esta baseline representa a primeira versão funcional do PetCare - Gerenciador de Cuidados do Pet.

A versão foi utilizada como referência inicial para a avaliação da qualidade do software e servirá como base para comparação com as melhorias realizadas posteriormente.

## Funcionalidades disponíveis

- Cadastro do nome do pet
- Cadastro do tipo de cuidado
- Registro de descrição
- Registro de data
- Armazenamento dos dados em SQLite
- Visualização dos cuidados na Agenda
- Alteração do status para concluído
- Exclusão de registros

## Tecnologias utilizadas

- Python
- Flask
- HTML
- SQLite

## Métricas da versão inicial

A análise automatizada foi realizada utilizando o CodeFactor.

Resultados obtidos no arquivo app.py:

- Nota de qualidade: A
- Linhas totais: 156
- Linhas de código: 109
- Complexidade: 3
- Métodos: 6
- Média de linhas por método: 18,17
- Duplicação: 0
- Problemas de segurança encontrados: 1

## Problema identificado pela ferramenta

O CodeFactor identificou um problema de segurança relacionado à execução da aplicação Flask com o modo de depuração habilitado:

app.run(debug=True)

O modo debug é útil durante o desenvolvimento, porém não deve permanecer habilitado em um ambiente de produção.

## Limitações conhecidas

Nesta versão inicial foram identificadas algumas limitações:

1. O sistema permite cadastrar compromissos com datas passadas.
2. Um registro pode ser excluído sem solicitar confirmação ao usuário.
3. Não existe funcionalidade para editar um cuidado já cadastrado.
4. O modo debug do Flask permanece habilitado.

## Prioridades de melhoria

Para a próxima etapa do projeto foram definidas como principais prioridades:

1. Implementar validação das datas cadastradas.
2. Adicionar confirmação antes da exclusão de um registro.
3. Criar funcionalidade para edição dos cuidados cadastrados.

O problema relacionado ao modo debug também será considerado durante a preparação de uma versão mais adequada para produção.
