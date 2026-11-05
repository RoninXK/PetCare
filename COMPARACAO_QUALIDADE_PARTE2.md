# Comparação de qualidade – PetCare, Parte 1 × Parte 2

Projeto Integrador – Qualidade de Software – Universidade Católica de Brasília (UCB)

Este documento reúne as Etapas 7 (nova análise de qualidade) e 8 (comparação antes × depois) do roteiro da Parte 2. Ele compara a versão da Parte 1 (tag `v1.0.0-baseline`, commit `0087a45`) com a versão atual da `main` (commit `15117f7`).

**Situação:** os indicadores do CodeFactor da Parte 2 foram coletados, com exceção do número de problemas de segurança do `app.py`, que ainda precisa ser confirmado no detalhe do arquivo. A data exata e o commit da nova análise também estão pendentes de confirmação. Os demais indicadores foram medidos no repositório entre 04/11 e 05/11/2026, com os métodos descritos em cada seção.

---

## 1. Indicadores do CodeFactor

A Parte 1 analisou o arquivo `app.py` com o CodeFactor. Os valores abaixo são os registrados no `BASELINE.md`, sem alteração. A data da análise original e o commit exato analisado não foram registrados na baseline.

A nova medição usou a mesma ferramenta (CodeFactor) e o mesmo arquivo (`app.py`). As variações percentuais foram calculadas sobre o valor da Parte 1 e arredondadas para uma casa decimal.

| Indicador | Parte 1 | Parte 2 | Variação | Interpretação |
|---|---|---|---|---|
| Nota de qualidade | A | A | Mantida | O arquivo manteve a nota A, mesmo tendo quase dobrado de tamanho. |
| Linhas totais | 156 | 289 | +133 (+85,3%) | O crescimento vem das correções (validação, CSRF, tratamento de erros) e das funcionalidades novas (tipo digitado, pesquisa e filtros). |
| Linhas de código | 109 | 216 | +107 (+98,2%) | O código efetivo praticamente dobrou, pelos mesmos motivos. Todo esse código é exercitado pelos 70 testes, com 97% de cobertura. |
| Complexidade | 3 | 20 | +17 (+566,7%) | Aumento esperado, já que a aplicação passou a tomar mais decisões. Ver a análise abaixo. |
| Métodos | 6 | 18 | +12 (+200,0%) | A lógica foi dividida em funções com uma responsabilidade cada, como validar, converter a data, consultar e alterar o banco. |
| Média de linhas por método | 18,17 | 12 | −6,17 (−34,0%) | As funções ficaram menores e mais fáceis de ler e testar, mesmo com o arquivo maior. |
| Duplicação | 0 | 0 | Mantida | O código novo não introduziu trechos duplicados. |
| Problemas de segurança encontrados | 1 (`app.run(debug=True)`) | _a confirmar_ | _a confirmar_ | O número ainda não foi confirmado no detalhe do arquivo no CodeFactor. |

Conferência dos valores: nas duas medições, a média de linhas por método é igual às linhas de código divididas pelo número de métodos (109 ÷ 6 = 18,17 e 216 ÷ 18 = 12). As 289 linhas totais coincidem com o tamanho do `app.py` no commit `15117f7`. Isso indica que a análise foi feita sobre a versão atual da `main`, mas o commit ainda precisa ser confirmado no painel.

### 1.1 Aumento da complexidade

A complexidade passou de 3 para 20. É a maior variação percentual da tabela e precisa ser lida junto com o crescimento do aplicativo. Na Parte 1, o `app.py` fazia pouco mais do que gravar, listar, concluir e excluir registros, quase sem verificações. A complexidade baixa refletia essa ausência de verificações, e não um código mais bem resolvido: um dos problemas da baseline (P1) era justamente o sistema aceitar dados inválidos sem conferir nada.

Na Parte 2, cada correção e cada funcionalidade acrescentou decisões ao código:

- **Validação do cadastro (P1):** campos vazios, limites de tamanho, tipo de cuidado válido, formato da data, data existente e data anterior a hoje.
- **Tipo digitado:** escolha entre o tipo da lista e o texto digitado, com sua própria validação.
- **Rotas de escrita (P2):** resposta 404 quando o cuidado não existe e tratamento do erro de CSRF.
- **Banco de dados:** `commit` ou `rollback` conforme o resultado da operação.
- **Pesquisa e filtros:** valores desconhecidos substituídos pelo padrão, filtro por status, ordenação e pesquisa por texto.
- **Configuração:** chave secreta e modo debug lidos de variáveis de ambiente.

O aumento, portanto, corresponde a regras que o sistema não tinha. Em média, a complexidade passou de 0,5 para cerca de 1,1 por método (3 ÷ 6 e 20 ÷ 18). O valor continua baixo, e as decisões ficaram distribuídas entre funções pequenas em vez de concentradas em uma só. Além disso, cada caminho novo tem testes: a cobertura de 97% indica que quase todos os ramos são executados pela suíte.

### 1.2 Redução da média de linhas por método

A média caiu de 18,17 para 12 linhas por método (−34,0%), enquanto as linhas de código quase dobraram. Isso mostra que o código novo não foi acumulado nas funções que já existiam. Ele foi organizado em funções menores. O principal fator foi a refatoração do PR #14: a função `inicio()`, que concentrava leitura do formulário, gravação e listagem, foi reduzida de 68 para 21 linhas, e a lógica foi dividida em funções como `listar_cuidados`, `inserir_cuidado`, `alterar_cuidado` e `conectar_banco`. Funções menores são mais fáceis de entender, de revisar e de testar isoladamente.

### 1.3 Duplicação

A duplicação continuou em zero. O código cresceu 98,2% sem criar trechos repetidos. A refatoração contribuiu para isso: a consulta da agenda, que aparecia duas vezes, passou a existir em um só lugar, e as seis chamadas manuais de `conexao.close()` foram reduzidas a uma, dentro do gerenciador de contexto `conectar_banco()` (ver seção 2).

### 1.4 Problemas de segurança

O número de problemas de segurança do `app.py` na Parte 2 **ainda não foi confirmado** e não foi preenchido. A meta do plano é **1 → 0**. O único problema apontado na baseline (`app.run(debug=True)`) foi removido no PR #14, e o debug agora só é ligado quando a variável `PETCARE_DEBUG` vale `1`. Duas evidências apontam nessa direção, mas não substituem a leitura do detalhe do arquivo:

- O Ruff, com a regra S201 (equivalente ao `debug=True`), não encontra mais o problema no `app.py` atual (seção 2).
- O painel geral da branch `main` no CodeFactor mostra 0 issues.

### 1.5 Indicadores gerais da branch (complementares)

No painel geral, a branch `main` aparece com nota **A+** e **0 issues**. Esses valores se referem ao repositório inteiro, que agora inclui testes, CSS e o workflow de CI, e não apenas ao `app.py`. Por isso, eles não entram na comparação da tabela acima, que usa somente os indicadores do arquivo, como na baseline. A Parte 1 também não registrou a nota geral da branch, então não há valor anterior para comparar.

---

## 2. Métricas novas da Parte 2

Estes indicadores não existiam na análise do CodeFactor. Eles foram definidos no `PLANO_MELHORIA_PARTE2.md` para medir os problemas tratados. Em cada linha, o valor da Parte 1 foi obtido no código da baseline e o da Parte 2 no código atual, pelo mesmo método.

| Indicador | Parte 1 | Parte 2 | Variação | Método de coleta |
|---|---|---|---|---|
| Testes automatizados | 0 | 70 | +70 | Contagem do pytest; a baseline não tem pasta nem arquivo de teste |
| Cobertura de testes do `app.py` | Não medida | 97% | Indicador novo | `pytest --cov` (pytest-cov), na `main` e no CI |
| Casos inválidos do P1 rejeitados | 2 de 12 (16,7%) | 12 de 12 (100%) | +83,3 p.p. | Suíte V01–V12 executada antes (commit `b32d706`) e depois (PR #11) da correção |
| Rotas GET que alteram dados | 2 | 0 | −2 (−100%) | Leitura das rotas do `app.py` e testes C01–C02 |
| Formulários de escrita com proteção CSRF | 0 de 3 | 3 de 3 | +100 p.p. | Leitura do `app.py` e testes C03–C05 (sem token e com token inválido) |
| Ocorrências da consulta da agenda (`SELECT * FROM cuidados`) | 2 | 1 | −1 (−50%) | Busca textual no `app.py` |
| Chamadas manuais de fechamento de conexão (`conexao.close()`) | 6 | 1 | −5 (−83,3%) | Busca textual no `app.py` |
| Achados do Ruff no `app.py` (regras E, W, F, I, B, UP, A, S) | 5 | 0 | −5 (−100%) | Ruff 0.17.3 com a configuração atual do `pyproject.toml`, aplicado ao `app.py` da tag e da `main` |

Observações sobre a tabela:

- **Casos inválidos do P1.** O valor 12 de 12 é o resultado medido no PR #11. No ciclo 7 (PR #18), a regra do tipo de cuidado mudou, e o plano acrescentou os casos V13 a V16. Na versão atual, os 16 casos inválidos são rejeitados (16 de 16). O valor original fica registrado como histórico.
- **Testes.** A quantidade cresceu a cada ciclo: 5 (PR #10), 20 (PR #11), 32 (PR #12), 38 (PR #14), 43 (PR #16), 55 (PR #18) e 70 (PR #20).
- **Cobertura.** A cobertura foi medida pela primeira vez no PR #10 (65%), passou para 84% no PR #11 e para 96% no PR #12, e está em 97% desde o PR #18. As linhas não cobertas são o `except` do filtro de data e o bloco que inicia o servidor.
- **Ruff.** Os 5 achados na baseline são: dois A002 (parâmetro `id` nas rotas), um S201 (`debug=True`), um W292 (falta de quebra de linha no final) e um I001 (ordem dos imports). O S201 corresponde ao mesmo problema que o CodeFactor apontou na Parte 1.

---

## 3. Evidências

Todos os ciclos seguiram o fluxo issue → branch → commits → pull request → revisão → merge. As revisões foram individuais, feitas pelo próprio desenvolvedor com apoio do Claude Code, e não são revisões independentes.

| Ciclo | Issue | Pull request e revisão | Merge | CI na `main` após o merge |
|---|---|---|---|---|
| 1. Estrutura e plano | [#7](https://github.com/RoninXK/PetCare/issues/7) | [PR #8](https://github.com/RoninXK/PetCare/pull/8) · [revisão](https://github.com/RoninXK/PetCare/pull/8#issuecomment-6647050688) | `d1149db` | Ainda não havia CI |
| 2. Testes e CI | [#9](https://github.com/RoninXK/PetCare/issues/9) | [PR #10](https://github.com/RoninXK/PetCare/pull/10) · [revisão](https://github.com/RoninXK/PetCare/pull/10#issuecomment-6647346451) | `953c771` | [run 41950957789](https://github.com/RoninXK/PetCare/actions/runs/41950957789) |
| 3. P1 – validação | [#1](https://github.com/RoninXK/PetCare/issues/1) | [PR #11](https://github.com/RoninXK/PetCare/pull/11) · [revisão](https://github.com/RoninXK/PetCare/pull/11#issuecomment-6647566201) | `71ab1d0` | [run 41952625976](https://github.com/RoninXK/PetCare/actions/runs/41952625976) |
| 4. P2 – POST, CSRF e confirmação | [#2](https://github.com/RoninXK/PetCare/issues/2) | [PR #12](https://github.com/RoninXK/PetCare/pull/12) · [revisão](https://github.com/RoninXK/PetCare/pull/12#issuecomment-6647897291) | `48345f5` | [run 41954797201](https://github.com/RoninXK/PetCare/actions/runs/41954797201) |
| 5. Refatoração A7/A8 | [#13](https://github.com/RoninXK/PetCare/issues/13) | [PR #14](https://github.com/RoninXK/PetCare/pull/14) · [revisão](https://github.com/RoninXK/PetCare/pull/14#issuecomment-6648177023) | `1ffa167` | [run 41956781678](https://github.com/RoninXK/PetCare/actions/runs/41956781678) |
| 6. Interface | [#15](https://github.com/RoninXK/PetCare/issues/15) | [PR #16](https://github.com/RoninXK/PetCare/pull/16) · [revisão](https://github.com/RoninXK/PetCare/pull/16#issuecomment-6648534802) | `e4eb66c` | [run 41959225092](https://github.com/RoninXK/PetCare/actions/runs/41959225092) |
| 7. Tipo digitado | [#17](https://github.com/RoninXK/PetCare/issues/17) | [PR #18](https://github.com/RoninXK/PetCare/pull/18) · [revisão](https://github.com/RoninXK/PetCare/pull/18#issuecomment-6648744408) | `fa3a031` | [run 41960806920](https://github.com/RoninXK/PetCare/actions/runs/41960806920) |
| 8. Pesquisa e filtros | [#19](https://github.com/RoninXK/PetCare/issues/19) | [PR #20](https://github.com/RoninXK/PetCare/pull/20) · [revisão](https://github.com/RoninXK/PetCare/pull/20#issuecomment-6648760113) | `9cc44f6` | [run 41960923492](https://github.com/RoninXK/PetCare/actions/runs/41960923492) |
| Documentação final | [#21](https://github.com/RoninXK/PetCare/issues/21) | [PR #22](https://github.com/RoninXK/PetCare/pull/22) · [revisão](https://github.com/RoninXK/PetCare/pull/22#issuecomment-6648815113) | `15117f7` | [run 41961355817](https://github.com/RoninXK/PetCare/actions/runs/41961355817) |

Falhas detectadas pelo pipeline: nos ciclos 3, 4, 7 e 8, os testes foram publicados antes da correção, e o CI registrou a falha esperada.

- P1: [run 41951433499](https://github.com/RoninXK/PetCare/actions/runs/41951433499), 11 falhas e 9 aprovações
- P2: [run 41953578819](https://github.com/RoninXK/PetCare/actions/runs/41953578819), 12 falhas e 20 aprovações
- Tipo digitado: [run 41959414384](https://github.com/RoninXK/PetCare/actions/runs/41959414384), 9 falhas e 46 aprovações
- Pesquisa e filtros: [run 41959943300](https://github.com/RoninXK/PetCare/actions/runs/41959943300), 13 falhas e 57 aprovações

---

## 4. Pendências de confirmação

Já foram coletados no CodeFactor sete dos oito indicadores do `app.py`, além da nota e das issues gerais da branch `main`. Ainda falta confirmar:

1. **Problemas de segurança do `app.py`:** o número e a descrição de cada problema, no detalhe do arquivo, para confirmar se o `debug=True` deixou de aparecer e se surgiu algum problema novo.
2. **Commit analisado:** o hash mostrado no painel do CodeFactor. A expectativa é `15117f7`, pelo tamanho do arquivo, mas isso precisa ser lido no painel.
3. **Data exata da análise.**
4. **Capturas de tela** do painel da branch e da página do `app.py`, com a data visível, como evidência.

---

## 5. Limitações

- A data e o commit exato da análise do CodeFactor da Parte 1 não foram registrados. A comparação assume que os valores do `BASELINE.md` correspondem à versão da tag `v1.0.0-baseline`.
- As métricas da seção 2 foram definidas na Parte 2. Os valores "Parte 1" dessas linhas foram medidos agora sobre o código da baseline, e não fazem parte da análise original.
- A data e o commit exato da nova análise do CodeFactor ainda não foram confirmados no painel.
- O `app.py` cresceu com funcionalidades que não existiam na Parte 1 (tipos digitados, filtros). Parte da variação de linhas, métodos e complexidade vem dessas funcionalidades, e não só da correção dos problemas. A comparação não separa as duas origens.
- A forma exata como o CodeFactor calcula a complexidade não foi verificada. A relação de complexidade por método é uma conta feita a partir dos valores do painel, não um indicador fornecido pela ferramenta.
- As revisões de código foram individuais e assistidas por IA, sem revisor independente.
