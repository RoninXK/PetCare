# Plano de Melhoria da Qualidade – PetCare (Parte 2)

Projeto Integrador – Qualidade de Software – Universidade Católica de Brasília (UCB)

| Item | Valor |
|---|---|
| Documento | Etapas 1 e 2 da Parte 2 (retomada da baseline e plano de melhoria) |
| Data de elaboração | 04/11/2026 |
| Situação | Aprovado pelo responsável em 04/11/2026 |
| Equipe | Projeto individual: um único integrante (usuário GitHub `RoninXK`), com auxílio do Claude Code |
| Regra | Este plano é aprovado **antes** de qualquer alteração no código da aplicação |

---

## 0. Decisões registradas

| Tema | Decisão |
|---|---|
| Composição da equipe | Projeto desenvolvido individualmente |
| Responsável | Um único responsável por todas as atividades (`RoninXK`) |
| Limite de `nome_pet` | Máximo de 100 caracteres |
| Limite de `descricao` | Máximo de 500 caracteres |
| Regra de data | A data de hoje é válida; datas anteriores a hoje são inválidas |
| Proteção CSRF | Flask-WTF, com `CSRFProtect` |
| Confirmação de exclusão | `confirm()` em JavaScript no formulário de exclusão |
| `petcare.db` | Preservado por enquanto: sem excluir dados e sem alterar seu histórico no Git |
| Branches antigas (`RoninXK-patch-1`, `issue-4-novo-cuidado`) | Preservadas |
| Revisão de código | Revisão individual assistida pelo Claude Code, documentada com checklist (seção 10.3) |
| Pendentes de confirmação | Data de entrega (06/11 ou 13/11/2026); data e commit da análise original no CodeFactor |

> **Limitação da revisão:** o roteiro exige "um pull request revisado por outro integrante, com o comentário da revisão visível". Como o projeto é individual, a revisão será feita pelo próprio responsável com auxílio do Claude Code. **Essa revisão não equivale à revisão independente por outro integrante exigida no roteiro, e sua aceitação depende da aprovação do professor.**

---

## 1. Retomada da baseline da Parte 1 (Etapa 1)

### 1.1 Versão analisada

| Item | Valor | Origem |
|---|---|---|
| Versão | `v1.0.0-baseline` | `BASELINE.md` |
| Tag Git | `v1.0.0-baseline` (tag leve) → commit `0087a45`, de 25/09/2026 | `git show-ref --tags` |
| Commit em que o `BASELINE.md` foi criado | `9d90036`, de 25/09/2026 (posterior à tag) | `git log` |
| Ferramenta de análise | CodeFactor | `BASELINE.md` |
| Arquivo analisado | `app.py` | `BASELINE.md` |
| Data da análise no CodeFactor | **Não registrada no `BASELINE.md`, a confirmar pelo responsável** | — |
| Commit exato analisado pelo CodeFactor | **Não registrado no `BASELINE.md`, a confirmar pelo responsável** | — |

> No commit da tag, os arquivos ainda estão como `gitignore` (sem ponto) e `index.html` (na raiz). A correção para `.gitignore` e `templates/index.html` está pendente de commit (veja a seção 7). A tag original **não será movida nem recriada**.

### 1.2 Métricas da Parte 1 (preservadas sem alteração)

Valores obtidos pelo **CodeFactor** sobre o arquivo `app.py`, transcritos de `BASELINE.md`:

| Indicador | Valor na baseline |
|---|---|
| Nota de qualidade | A |
| Linhas totais | 156 |
| Linhas de código | 109 |
| Complexidade | 3 |
| Métodos | 6 |
| Média de linhas por método | 18,17 |
| Duplicação | 0 |
| Problemas de segurança encontrados | 1 (`app.run(debug=True)`) |

### 1.3 Indicadores complementares da baseline

Estes indicadores **não** foram coletados pelo CodeFactor. Foram obtidos por inspeção do repositório em 04/11/2026, sobre o commit `9d90036`, cujo `app.py` é idêntico ao da tag. Servem para medir P1, P2, testes e automação, que a ferramenta não cobre.

| Indicador | Valor na baseline | Método de coleta |
|---|---|---|
| Testes automatizados | 0 | Não há diretório de testes nem framework de testes nas dependências |
| Pipeline de CI | Inexistente | Não há diretório `.github/workflows` nem outro arquivo de CI |
| Cobertura de testes | Não medida (não há ferramenta nem testes) | — |
| Rotas GET que alteram dados | 2 (`/concluir/<id>` em `app.py:106`, `/excluir/<id>` em `app.py:123`) | Leitura de `app.py` |
| Rotas que alteram dados com proteção CSRF | 0 de 3 (`POST /`, concluir, excluir) | Leitura de `app.py` e `templates/index.html` |
| Confirmação antes da exclusão | Não existe | Leitura de `templates/index.html:151-155` |
| Validações no servidor no cadastro | Só o formato da data (`app.py:44-54`) | Leitura de `app.py` |

### 1.4 Prioridades definidas na Parte 1

Conforme `BASELINE.md`:

1. Implementar validação das datas cadastradas.
2. Adicionar confirmação antes da exclusão de um registro.
3. Criar funcionalidade para edição dos cuidados cadastrados.

Também foi registrado que o modo debug será considerado na preparação de uma versão mais adequada para produção.

### 1.5 Questões norteadoras da Etapa 1

- **Quais métricas sustentavam o diagnóstico da Parte 1?** As métricas do CodeFactor da seção 1.2 (com destaque para o único problema de segurança) e as quatro limitações conhecidas do `BASELINE.md`.
- **Quais dois problemas foram escolhidos, e por quê?** P1 e P2 (seção 2). Eles ampliam as prioridades 1 e 2 da Parte 1, afetam a integridade dos dados e a segurança, e podem ser verificados por testes automatizados.
- **Alguma prioridade deixou de ser relevante?** A prioridade 3 (edição de cuidados) continua relevante, mas fica **fora do escopo**. É uma funcionalidade nova (manutenção perfectiva), não a correção de um defeito existente. O PDF orienta a tratar dois problemas com evidência dentro de duas semanas. **Atualização em 06/11/2026:** a edição acabou sendo feita no ciclo 9 (Issue #3), depois dos ciclos do plano. O modo debug será tratado como mudança preventiva complementar (seção 5).

---

## 2. Problemas prioritários escolhidos (Etapa 2)

| ID | Problema | Issue | Motivo da escolha |
|---|---|---|---|
| **P1** | Validação insuficiente dos dados cadastrados, incluindo campos inválidos e datas passadas | #1 | Corresponde à prioridade 1 e à limitação 1 da Parte 1. Permite dados inconsistentes no banco e é diretamente testável |
| **P2** | Operações de concluir e excluir realizadas por GET, sem proteção CSRF e sem confirmação de exclusão | #2 | Corresponde à prioridade 2 e à limitação 2 da Parte 1. A exclusão é irreversível e pode ser disparada por clique acidental, por pré-carregamento de link ou por requisição forjada (CSRF) |

> As Issues #1 ("Validar datas passadas no cadastro de cuidados") e #2 ("Adicionar confirmação antes de excluir um cuidado") foram abertas em 25/09/2026, na Parte 1. O escopo de P1 e P2 neste plano é mais amplo que os títulos dessas issues (P1 inclui os demais campos; P2 inclui POST e CSRF). O escopo completo será registrado em cada issue quando o ciclo correspondente começar.

---

## 3. Evidências dos problemas

### P1 – Validação insuficiente

| Evidência | Local |
|---|---|
| Os campos são lidos sem validação de conteúdo: aceita texto só com espaços e não tem limite de tamanho | `app.py:39-42` |
| `tipo_cuidado` não é conferido contra a lista de opções; a lista só existe no HTML | `app.py:40`, `templates/index.html:48-70` |
| Só o formato da data é validado; datas passadas são aceitas | `app.py:44-54` |
| Campo ausente na requisição gera erro HTTP 400 genérico (`KeyError` em `request.form[...]`), sem mensagem ao usuário | `app.py:39-42` |
| As validações existentes estão só no navegador (`required`, `maxlength` da data) e podem ser contornadas | `templates/index.html:37-96` |
| Limitação registrada: "O sistema permite cadastrar compromissos com datas passadas" | `BASELINE.md`, limitação 1 |

### P2 – Concluir e excluir por GET, sem CSRF e sem confirmação

| Evidência | Local |
|---|---|
| Rota de conclusão aceita GET e altera o banco | `app.py:106-120` |
| Rota de exclusão aceita GET e apaga o registro | `app.py:123-136` |
| A interface dispara as ações por links `<a href>` | `templates/index.html:143`, `templates/index.html:151` |
| Não há `SECRET_KEY` nem token CSRF em nenhum formulário | `app.py:5`, `templates/index.html:32` |
| A exclusão acontece sem nenhuma confirmação | `templates/index.html:151-155` |
| Limitação registrada: "Um registro pode ser excluído sem solicitar confirmação ao usuário" | `BASELINE.md`, limitação 2 |

---

## 4. Tabela do plano de melhoria

| Problema | Evidência da Parte 1 | Ação planejada | Responsável | Indicador | Meta |
|---|---|---|---|---|---|
| **P1** – Validação insuficiente dos dados cadastrados | Limitação 1 e prioridade 1 do `BASELINE.md`; `app.py:39-54` | Validar no servidor todos os campos do cadastro (obrigatórios, sem espaços vazios, tipo permitido, `nome_pet` até 100 e `descricao` até 500 caracteres, data existente e igual ou posterior a hoje), exibindo mensagem de erro sem gravar o registro | RoninXK | Percentual de casos inválidos definidos (V01–V12, seção 6.1) rejeitados pelos testes automatizados, sem gravação no banco | **100%** (12 de 12 rejeitados e 0 registros gravados), com os casos válidos (A01–A02) aceitos |
| **P2** – Concluir/excluir por GET, sem CSRF e sem confirmação | Limitação 2 e prioridade 2 do `BASELINE.md`; `app.py:106-136` | Mudar concluir e excluir para POST, aplicar Flask-WTF `CSRFProtect` a todas as rotas que alteram dados e exigir confirmação por `confirm()` em JavaScript antes da exclusão | RoninXK | (a) Nº de rotas GET que alteram dados; (b) % das rotas de escrita que rejeitam requisição sem token CSRF válido; (c) % dos formulários de exclusão renderizados com confirmação | (a) **2 → 0**; (b) **0% → 100%** (3 de 3); (c) **0% → 100%**, verificado pelo teste C08 e por verificação manual no navegador registrada no PR (seção 6.2) |

---

## 5. Ações planejadas detalhadas

| ID | Ação | Problema | Tipo de manutenção | Responsável |
|---|---|---|---|---|
| A0 | Commitar as renomeações pendentes (`gitignore` → `.gitignore`, `index.html` → `templates/index.html`). **Concluída** no PR #8 (Issue #7, commit `f201883`, merge `d1149db`) | Pré-requisito | Corretiva | RoninXK |
| A1 | Configurar pytest com o `test_client` do Flask e um banco SQLite temporário (caminho do banco configurável, sem usar o `petcare.db` real) | Pré-requisito de P1 e P2 | Preventiva | RoninXK |
| A2 | Criar pipeline no GitHub Actions que roda os testes a cada push e pull request | Pré-requisito (Etapa 6) | Preventiva | RoninXK |
| A3 | Escrever os testes V01–V12 e A01–A02 **antes** da implementação | P1 | Preventiva | RoninXK |
| A4 | Implementar a validação no servidor e as mensagens de erro | P1 | Corretiva | RoninXK |
| A5 | Escrever os testes C01–C09 **antes** da implementação | P2 | Preventiva | RoninXK |
| A6 | Mudar concluir/excluir para POST, adicionar CSRF com Flask-WTF `CSRFProtect` (com `SECRET_KEY` lida de variável de ambiente) e confirmação da exclusão com `confirm()` em JavaScript | P2 | Corretiva | RoninXK |
| A7 | Refatorar o acesso a dados: eliminar a consulta duplicada da agenda e os ciclos manuais de abrir/fechar conexão | Etapa 4 | Preventiva | RoninXK |
| A8 | Controlar o modo debug por variável de ambiente, em vez de `debug=True` fixo | Problema de segurança do CodeFactor | Preventiva | RoninXK |
| A9 | Fixar as versões das dependências no `requirements.txt` | Reprodutibilidade do CI | Preventiva | RoninXK |
| A10 | Nova análise no CodeFactor, comparação antes × depois e tag final | Etapas 7 e 8 | — | RoninXK |

### Regras de validação planejadas para P1

| Campo | Regra |
|---|---|
| `nome_pet` | Obrigatório, não pode ser só espaços, máximo de 100 caracteres |
| `tipo_cuidado` | Obrigatório, deve ser um de: Vacina, Consulta, Medicamento, Outro. **Alterada em 05/11/2026 (Issue #17):** a opção "Outro" foi trocada por "Adicionar outro tipo…"; a lista aceita Vacina, Consulta, Medicamento ou essa opção, e nesse caso o campo `tipo_personalizado` é obrigatório, não pode ser só espaços e tem até 50 caracteres |
| `descricao` | Obrigatório, não pode ser só espaços, máximo de 500 caracteres |
| `data` | Obrigatório, formato DD/MM/AAAA, data existente no calendário, igual ou posterior à data atual (a data de hoje é válida; datas anteriores são inválidas) |
| Campo ausente | Mensagem de erro amigável, sem erro HTTP genérico |

### Metas complementares (refatoração e segurança)

Contagens obtidas por inspeção de `app.py` em 04/11/2026:

| Indicador | Antes | Meta | Método de coleta |
|---|---|---|---|
| Ocorrências da consulta da agenda (`SELECT * FROM cuidados`) | 2 (`app.py:59`, `app.py:93`) | 1 | Busca textual no código |
| Ciclos manuais de abrir/fechar conexão (`conexao = conectar_banco()` … `conexao.close()`) | 6 (`app.py:15`, `56`, `71`, `90`, `109`, `126`) | 1 ponto centralizado de gerenciamento da conexão | Busca textual no código |
| Problemas de segurança (CodeFactor) | 1 | 0 | CodeFactor, mesmo método da baseline |

Os demais indicadores do CodeFactor (nota, linhas, complexidade, métodos, média de linhas por método, duplicação) serão **medidos novamente e comparados**, sem meta prévia. A inclusão das validações tende a aumentar as linhas e os métodos, e essa variação será interpretada na Etapa 9.

---

## 6. Casos de teste planejados (base dos indicadores)

### 6.1 P1 – Validação do cadastro

| ID | Caso | Resultado esperado |
|---|---|---|
| V01 | `nome_pet` vazio | Rejeitado, mensagem de erro, 0 registros gravados |
| V02 | `nome_pet` só com espaços | Rejeitado, 0 registros gravados |
| V03 | `descricao` vazia | Rejeitado, 0 registros gravados |
| V04 | `descricao` só com espaços | Rejeitado, 0 registros gravados |
| V05 | `tipo_cuidado` vazio | Rejeitado, 0 registros gravados |
| V06 | `tipo_cuidado` fora da lista (ex.: "Banho") | Rejeitado, 0 registros gravados |
| V07 | Data em formato inválido (ex.: `2026-12-01`) | Rejeitado, 0 registros gravados |
| V08 | Data inexistente (ex.: `31/02/2027`) | Rejeitado, 0 registros gravados |
| V09 | Data passada (dia anterior à data atual) | Rejeitado, 0 registros gravados |
| V10 | `nome_pet` com 101 caracteres | Rejeitado, 0 registros gravados |
| V11 | `descricao` com 501 caracteres | Rejeitado, 0 registros gravados |
| V12 | Campo ausente na requisição | Rejeitado com mensagem (não HTTP 400 genérico), 0 registros gravados |
| A01 | Cadastro válido com data futura | Aceito, 1 registro com status "Pendente" |
| A02 | Cadastro válido com a data de hoje, `nome_pet` com 100 e `descricao` com 500 caracteres (limites exatos) | Aceito, 1 registro com status "Pendente" |

#### Casos acrescentados em 05/11/2026 (Issue #17, tipo digitado)

Os casos acima, e o resultado de 12 de 12 inválidos rejeitados medido no PR #11, continuam valendo como foram registrados. O V06 continua correto: um valor fora da lista enviado direto no campo `tipo_cuidado` segue rejeitado. A mudança de regra acrescenta:

| ID | Caso | Resultado esperado |
|---|---|---|
| V13 | "Adicionar outro tipo…" com o tipo digitado vazio | Rejeitado, 0 registros gravados |
| V14 | "Adicionar outro tipo…" com o tipo digitado só com espaços | Rejeitado, 0 registros gravados |
| V15 | Tipo digitado com 51 caracteres | Rejeitado, 0 registros gravados |
| V16 | `tipo_cuidado` = "Outro", opção que saiu da lista | Rejeitado, 0 registros gravados |
| A03 | Tipo digitado "Banho e tosa" com espaços nas pontas | Aceito e gravado como "Banho e tosa" |
| A04 | Tipo digitado com 50 caracteres (limite exato) | Aceito |

Com isso, o indicador do P1 passa a ter 16 casos inválidos (V01–V16).

### 6.2 P2 – Concluir, excluir, CSRF e confirmação

| ID | Caso | Resultado esperado |
|---|---|---|
| C01 | `GET` na rota de concluir | Não altera o status (HTTP 405 ou equivalente) |
| C02 | `GET` na rota de exclusão | Não apaga o registro |
| C03 | `POST` concluir sem token CSRF | Rejeitado (HTTP 400), status inalterado |
| C04 | `POST` excluir sem token CSRF | Rejeitado (HTTP 400), registro mantido |
| C05 | `POST /` (cadastro) sem token CSRF | Rejeitado (HTTP 400), 0 registros gravados |
| C06 | `POST` concluir com token válido | Status passa a "Concluído" |
| C07 | `POST` excluir com token válido | Registro removido |
| C08 | Página inicial com um registro cadastrado | O formulário de exclusão é renderizado com método POST, token CSRF e chamada a `confirm()` |
| C09 | Concluir ou excluir um id inexistente | HTTP 404, nenhum registro afetado |

**Meta de quantidade de testes:** de 0 (baseline) para no mínimo **23** testes automatizados (V01–V12, A01–A02, C01–C09), todos passando no pipeline.

> **Limitação da confirmação por `confirm()`:** o pytest não executa JavaScript. Por isso, o teste C08 verifica que a confirmação está presente no HTML entregue ao navegador, mas não verifica o clique em "Cancelar". O comportamento no navegador (Cancelar mantém o registro; OK exclui) será verificado manualmente e registrado no PR. A confirmação protege contra cliques acidentais; quem protege contra requisições forjadas é o CSRF (C03–C05).

---

## 7. Critérios de aceitação

### P1
- Os 12 casos inválidos (V01–V12) são rejeitados e nenhum deles grava registro.
- Os casos válidos (A01 e A02) são aceitos.
- O usuário vê uma mensagem que identifica o erro, e os dados já digitados permanecem no formulário.
- Os testes passam localmente e no pipeline antes do merge.

### P2
- Nenhuma rota que altera dados aceita GET (contagem 0 na leitura de `app.py` e testes C01–C02 passando).
- As 3 rotas de escrita rejeitam requisições sem token CSRF válido (C03–C05).
- O formulário de exclusão pede confirmação com `confirm()` (teste C08 e verificação manual: Cancelar mantém o registro, OK exclui).
- O fluxo normal de concluir e excluir continua funcionando pela interface (C06–C07 e verificação manual registrada no PR).
- Os testes passam localmente e no pipeline antes do merge.

### Gerais
- Cada mudança passa pelo fluxo issue → branch → commit → pull request → revisão → merge (seção 10).
- Todo PR recebe a revisão individual assistida pelo Claude Code, com checklist preenchido e comentário visível no PR (seção 10.3).
- A nova análise usa o CodeFactor, como na baseline, e registra data e versão.

---

## 8. Como medir os resultados antes e depois

| Indicador | Medição "antes" | Medição "depois" | Mesmo método? |
|---|---|---|---|
| Métricas do CodeFactor (seção 1.2) | Valores do `BASELINE.md` | Nova análise no CodeFactor sobre a versão final, registrando data, commit e tag | Sim: mesma ferramenta. Se o código for dividido em mais arquivos, serão apresentados os valores por arquivo e o total do repositório, com a regra de soma explicada |
| % de casos inválidos de P1 rejeitados | Rodar a suíte V01–V12 contra o código da baseline e registrar quantos casos falham (a tag `v1.0.0-baseline` exige a correção de estrutura A0 para executar) | Rodar a mesma suíte na versão final | Sim: mesma suíte de testes |
| Rotas GET que alteram dados | 2 (seção 1.3) | Leitura de `app.py` e testes C01–C02 | Sim: inspeção do código mais teste |
| % de rotas de escrita com CSRF | 0 de 3 (seção 1.3) | Testes C03–C05 | Sim |
| Exclusão com confirmação | Não existe (0% dos formulários de exclusão) | Teste C08 e verificação manual no navegador | Sim: inspeção do HTML entregue |
| Nº de testes automatizados | 0 | Saída do `pytest` no pipeline | Sim |
| Cobertura de testes | Não medida (sem ferramenta e sem testes) | `pytest-cov`, se configurado | Sem medida anterior: será registrado como novo indicador, não como comparação |
| Duplicação e conexões manuais (seção 5) | 2 e 6 ocorrências | Mesma busca textual na versão final | Sim |

Evidências a guardar: link e captura do painel do CodeFactor (antes e depois), links dos runs do pipeline, saída do `pytest`, links de issues, PRs, revisões, merges e da tag final.

---

## 9. Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| Prazo curto (entrega em 06/11 ou 13/11/2026) | Não concluir todas as etapas | Priorizar um ciclo completo bem evidenciado (P1), depois P2, depois a refatoração |
| A nova análise no CodeFactor não ser comparável (outro commit, arquivos divididos, configuração diferente) | Invalida a comparação da Etapa 8 | Usar o mesmo repositório e a mesma configuração, registrar data e commit, explicar a soma por arquivo |
| Data e commit da análise original não registrados | Baseline incompleta | O responsável confirma; caso contrário, registrar "não registrado" no relatório |
| As validações aumentarem linhas, métodos e complexidade no CodeFactor | Métricas aparentemente piores | Interpretar na Etapa 9: aumento justificado por regras de negócio protegidas por testes |
| O CSRF quebrar os testes de cadastro de P1 | Falsos negativos nos testes | Desligar o CSRF só na configuração de teste dos casos de P1 e testá-lo à parte (C03–C05) |
| Nova dependência para CSRF (Flask-WTF) | Mais superfície de dependência | Fixar a versão no `requirements.txt` (A9) |
| A confirmação da exclusão adicionar um passo para o usuário | Pequena perda de agilidade (trade-off usabilidade × segurança) | Confirmação simples, de um clique |
| `confirm()` em JavaScript não ser executado pelos testes automatizados e poder ser ignorado se o JavaScript estiver desativado | O indicador de confirmação depende de verificação manual | Teste C08 sobre o HTML, verificação manual registrada no PR, CSRF como proteção contra requisições forjadas |
| Teste usar o `petcare.db` real | Corromper dados ou gerar resultados instáveis | Banco temporário configurável nos testes (A1); o `petcare.db` é preservado |
| Projeto individual: não há revisão independente por outro integrante | Exigência do roteiro atendida só parcialmente; risco na nota do critério "Práticas de garantia da qualidade" | Revisão assistida pelo Claude Code com checklist documentado no PR; submeter a adaptação à aprovação do professor |
| A regra "data não passada" depender do fuso horário ou do relógio | Testes instáveis | Calcular a data relativa ("hoje", "ontem") dentro do teste |

### Questões norteadoras da Etapa 2

- **Como o grupo saberá se cada intervenção funcionou?** Pelos indicadores e metas da seção 4, verificados pelos testes da seção 6 e pela nova análise do CodeFactor.
- **A melhoria de um atributo pode prejudicar outro?** Sim. Segurança e confiabilidade (P1, P2) contra usabilidade (passo extra de confirmação) e tamanho e complexidade do código (métricas do CodeFactor). Veja a seção 9.
- **A meta é realista para duas semanas?** Sim. O sistema tem um arquivo de backend e um template, e as metas cobrem só as rotas e campos que já existem.

---

## 10. Plano do fluxo de garantia da qualidade

Fluxo exigido: **issue → branch → commit → pull request → revisão → merge → tag/release**.

### 10.1 Issues e branches

| Ordem | Issue | Branch | Ações | Tipo | Situação |
|---|---|---|---|---|---|
| 1 | #7 – Preparar estrutura e plano de melhoria da Parte 2 | `docs/7-plano-melhoria` | A0 e este documento | Corretiva + documentação | **Concluído** (PR #8, merge `d1149db`) |
| 2 | #9 – Configurar testes automatizados e integração contínua do PetCare | `fix/9-estrutura-testes-ci` | A1, A2, A9 | Preventiva | **Concluído** (PR #10, merge `953c771`) |
| 3 | #1 – P1: validação dos dados cadastrados | `fix/1-validacao-dados` | A3, A4 | Corretiva | **Concluído** (PR #11, merge `71ab1d0`) |
| 4 | #2 – P2: concluir/excluir via POST com CSRF e confirmação | `fix/2-seguranca-cuidados` | A5, A6 | Corretiva | **Concluído** (PR #12, merge `48345f5`) |
| 5 | #13 – Refatorar o acesso ao banco e desligar o modo debug por padrão | `refactor/13-acesso-dados` | A7, A8 | Preventiva | **Concluído** (PR #14, merge `1ffa167`) |
| 6 | #15 – Modernizar a interface do PetCare | `ui/15-interface` | Fora das ações do plano original | Perfectiva | **Concluído** (PR #16, merge `e4eb66c`) |
| 7 | #17 – Permitir digitar um tipo de cuidado que não está na lista | `feat/17-tipo-personalizado` | Altera a regra de tipo do P1 (seção 6.1) | Perfectiva | **Concluído** (PR #18, merge `fa3a031`) |
| 8 | #19 – Adicionar pesquisa e filtros na agenda | `feat/19-filtros-agenda` | Fora das ações do plano original (casos F01–F15) | Perfectiva | **Concluído** (PR #20, merge `9cc44f6`) |
| 9 | #3 – Permitir edição de um cuidado cadastrado | `feat/3-editar-cuidado` | Prioridade 3 da Parte 1 (casos E01–E13) | Perfectiva | **Concluído** (PR_EDICAO) |

O `<nº>` é o número da issue criada no GitHub. Situação das demais issues do repositório:

- **#4** ("Alterar título do formulário para \"Novo cuidado\"") está **fechada** desde 25/09/2026. É anterior à Parte 2 e não faz parte deste plano. A branch remota `issue-4-novo-cuidado` é preservada, sem uso neste plano.
- **#3** ("Permitir edição de um cuidado cadastrado") corresponde à prioridade 3 da Parte 1. Ficou fora do escopo inicial (seção 1.5) e foi feita depois dos outros ciclos, no ciclo 9.

### 10.2 Commits

- Mensagens no padrão Conventional Commits: `docs:`, `fix:`, `test:`, `refactor:`, `ci:`, `chore:`.
- Cada commit referencia a issue (`Refs #<nº>`). O commit ou PR final fecha a issue (`Closes #<nº>`).
- Em P1 e P2, os testes entram em um commit **antes** da implementação. Assim o pipeline mostra a falha detectada e depois a correção.

### 10.3 Pull requests e revisão (adaptada para projeto individual)

Todo PR aponta para a `main` e contém: link da issue, descrição da mudança, tipo de manutenção e evidência dos testes.

**Processo de revisão individual assistida pelo Claude Code:**

1. O responsável abre o PR com a descrição e o checklist abaixo.
2. O Claude Code revisa o diff do PR contra o checklist e contra os critérios de aceitação deste plano, e aponta problemas encontrados.
3. O resultado da revisão (itens conferidos, problemas encontrados e o que foi corrigido) é registrado como **comentário no PR**, para ficar visível.
4. Se houver correções, elas entram como novos commits no mesmo PR, e o checklist é conferido de novo.
5. O responsável decide o merge somente com o checklist completo e o pipeline verde.

Checklist de revisão (copiado no corpo do PR e conferido a cada revisão):

- [ ] A mudança atende à issue e ao critério de aceitação deste plano
- [ ] Os testes novos verificam o resultado (não só executam o código)
- [ ] O pipeline está verde (testes e análise estática)
- [ ] Nenhum arquivo fora do escopo foi alterado
- [ ] Nenhuma credencial, dado do `petcare.db` ou arquivo temporário foi incluído
- [ ] O comportamento existente foi preservado (testes anteriores continuam passando)
- [ ] Mensagens e nomes estão claros e em português

Regras:
- Merge só com o checklist completo, o comentário de revisão registrado e o pipeline verde.
- Recomendação: ativar a proteção da `main` no GitHub, exigindo PR e CI verde. A exigência de aprovação fica desligada, porque o GitHub não permite que o autor aprove o próprio PR.

> **Importante:** esta revisão individual assistida **não equivale à revisão independente por outro integrante** exigida no roteiro ("um pull request revisado por outro integrante, com o comentário da revisão visível"). A adaptação foi adotada porque o projeto é desenvolvido por um único integrante, e sua aceitação **depende da aprovação do professor**.

### 10.4 Merge, tag e release

- Merge pela interface do GitHub depois da aprovação e do CI verde. A branch é apagada após o merge.
- Depois dos ciclos, nova análise no CodeFactor sobre a `main`.
- Tag final sugerida: `v2.0.0`, com release no GitHub descrevendo as mudanças e o link para este plano.
- A tag `v1.0.0-baseline` permanece inalterada.

---

## 11. Pendências a confirmar

1. Data de entrega (06/11 ou 13/11/2026).
2. Data e commit da análise original no CodeFactor.
3. Aprovação do professor para a revisão individual assistida pelo Claude Code no lugar da revisão por outro integrante.

As demais decisões estão registradas na seção 0.
