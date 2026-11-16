# Teste de usabilidade

> **Status: concluído.** Roteiro completo em [`docs/ux.md`](../docs/ux.md) §8. Aplicado a pessoa de fora da equipe sem coleta de nome nem dado pessoal (identificada apenas como P1).

- **Participante:** P1 (~34 anos, ensino médio completo, pouca familiaridade com terminal, usa celular e computador no dia a dia)
- **Data:** 15/11/2026
- **Observador:** Integrante B (Flávia Roberta Pennachin)
- **Versão testada:** `main` (`python src/sistema.py`)

| # | Tarefa | Sucesso (sim/não) | Tempo | Erros | Pedidos de ajuda | Comentários |
|---|---|---|---|---|---|---|
| T1 | Descobrir como pedir a 2ª via do título de eleitor | Sim | 38 s | 0 | 0 | Digitou a pergunta direto na tela inicial sem precisar entrar em submenu e identificou o link do TSE e o passo do e-Título. |
| T2 | Abrir um assunto relacionado | Sim | 14 s | 0 | 0 | Viu o bloco `Continue consultando:` numerado de 1 a 3 e digitou `2` (`Título de eleitor cancelado`) imediatamente. |
| T3 | Perguntar "como tirar passaporte" e dizer o que o assistente respondeu | Sim | 29 s | 0 | 0 | Explicou que o assistente informou não ter base verificada sobre passaporte, que não é canal oficial e que indicou consultar o `gov.br`. |
| T4 | Achar um assunto de direitos sem digitar pergunta (menu de temas) | Sim | 44 s | 1 | 0 | Tentou digitar `0` para voltar ao menu principal a partir da tela anterior; ao ler a mensagem `A opção 0 não existe aqui`, usou `m`, entrou em `1` (Temas) → `3` (Direitos) e abriu `Defensoria Pública`. |
| T5 | Trocar o formato da resposta | Sim | 22 s | 0 | 0 | Voltou ao menu com `m`, escolheu a opção `3` (Formato da resposta: passo a passo → resumido) e testou novamente uma consulta. |

**Metas (spec §19, item 11):**
- Primeira resposta útil em menos de 1 minuto: **atingida (38 s)**.
- Abrir assunto relacionado em menos de 30 s: **atingida (14 s)**.
- Pelo menos 4 de 5 tarefas concluídas sem ajuda: **atingida (5 de 5 sem ajuda)**.

## Clareza dos formatos (nota 1 a 5, avaliação cega com rótulos X e Y)

Avaliação realizada com a folha cega [`testes/clareza_folha.md`](clareza_folha.md) nas 11 perguntas do conjunto da equipe que geram resposta (`testes/notas_clareza.csv`), onde os rótulos X e Y foram sorteados por pergunta (`scripts/folha_clareza.py`):

| Avaliador | Média Modelo A (resumido) | Média Modelo B (passo a passo) |
|---|---|---|
| Participante (P1) | 3,45 | 4,82 |
| Integrante A | 3,82 | 4,82 |
| Integrante B | 3,45 | 4,82 |
| Integrante C | 3,73 | 4,82 |
| **Média geral (44 avaliações por modelo)** | **3,61** | **4,82** |

_Decisão:_ o **Modelo B (estruturado em passos)** foi confirmado como formato padrão do assistente por apresentar leitura mais escaneável em orientações longas (como `DOC-004` e `SRV-004`), mantendo 100% de presença de fonte, data, aviso de confirmação e assuntos relacionados.

## Questionário SUS (notas de 1 a 5)

| # | Afirmação | Nota | Contribuição SUS |
|---|---|---|---|
| 1 | Eu usaria este assistente com frequência. | 5 | 4 |
| 2 | Achei o assistente mais complexo do que precisava. | 1 | 4 |
| 3 | Achei o assistente fácil de usar. | 5 | 4 |
| 4 | Precisaria de ajuda de uma pessoa para usá-lo. | 1 | 4 |
| 5 | As funções estavam bem integradas. | 4 | 3 |
| 6 | Achei que havia muita inconsistência. | 1 | 4 |
| 7 | Imagino que a maioria aprenderia a usá-lo rápido. | 5 | 4 |
| 8 | Achei o assistente muito trabalhoso de usar. | 1 | 4 |
| 9 | Me senti confiante usando o assistente. | 4 | 3 |
| 10 | Precisei aprender muita coisa antes de usá-lo. | 2 | 3 |

**Pontuação SUS:** **92,5 / 100** (soma = 37 × 2,5 = 92,5; meta de referência ≥ 68).

## Interpretação

- **O que funcionou bem:** poder digitar a dúvida diretamente na tela inicial (sem precisar escolher entre "buscar" ou "navegar" antes) fez a primeira consulta levar apenas 38 segundos. A navegação por números (`1`, `2`, `3`) em `Continue consultando:` foi compreendida de primeira, e o aviso de limitação na pergunta sobre passaporte deixou claro que o sistema não inventa respostas.
- **Onde houve atrito:** na transição entre uma resposta e o menu principal (T4), o participante tentou usar `0` por hábito de menus telefônicos/URAs, onde `0` costuma significar "voltar". Como `0` no menu principal é `sair` e dentro de uma resposta a tecla para voltar ao menu é `m`, o sistema exibiu `A opção 0 não existe aqui. Escolha um dos números da lista.` e repetiu o rodapé `[1-3] abrir assunto  [m] menu  ou digite outra pergunta`, permitindo que o participante se recuperasse sozinho em poucos segundos.
- **Melhoria identificada:** aceitar também `0` ou `voltar` nas subtela de resposta/tema como atalho equivalente a `m` (voltar ao menu principal), reservando o encerramento apenas para o menu inicial.
