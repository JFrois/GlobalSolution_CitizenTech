# Uso de Inteligência Artificial

> Exigido pelo enunciado ("registrar no arquivo `docs/uso_ia.md` o uso de IA e a validação crítica realizada") e pela spec §15.3.
> Regra do processo (§B.3, regra 7): **registrar enquanto acontece**, não só no final.
> Responsável pela consolidação: **Integrante B** (atividade E8 do [planejamento](planejamento.md)). Cada integrante registra o próprio uso.

---

## 1. Ferramentas de IA utilizadas

| Ferramenta | Onde foi usada | Para quê |
|---|---|---|
| Claude (chat) | Planejamento | _A confirmar pela equipe_: elaboração da spec e do documento de processo |
| Claude Code (app desktop) | Desenvolvimento | Leitura do enunciado, documentação de planejamento e arquitetura, esqueletos de documentos; depois, implementação guiada pela spec (uma tarefa por vez) |
| Google Gemini (API, plano pago) | **Dentro do produto** (Onda 2) | Escolher a ferramenta (function calling), transcrever voz e sugerir o nome de documentos do cofre. **Não gera** o texto das orientações (spec §1) |

<!-- Acrescentar outras ferramentas se forem usadas (ex.: revisão de texto, geração de testes). -->

---

## 2. Como a IA é usada no desenvolvimento

A equipe segue **Spec-Driven Development** ([processo](processo_desenvolvimento.md), Parte B):

1. A equipe escreve e aprova a [especificação](especificacao/CITIZEN_ASSIST_SPEC.md) **antes** do código.
2. O Claude Code lê a spec (via `CLAUDE.md`) e executa **uma tarefa por vez**, citando a seção da spec atendida.
3. Itens marcados **(EM ABERTO)** na spec não são decididos pela IA: viram `TODO` para a equipe.
4. Todo resultado passa por **revisão humana** antes do merge. Segurança e textos da base têm revisão obrigatória.
5. **Nunca** colocamos segredos, dados pessoais ou documentos reais em prompts.

**O que a IA não faz neste projeto:**
- Não redige as orientações da base: a equipe lê a página oficial e escreve com as próprias palavras (spec §7.1). A IA pode apenas sugerir melhorias de linguagem.
- Não decide requisitos nem itens em aberto.
- Não gera a resposta final ao cidadão: o texto vem sempre de `data/base.json`.

---

## 3. Registro de uso

Uma linha por uso relevante. **Resultado**: aceito, aceito com ajustes ou rejeitado. **Validação**: como a equipe conferiu.

| Data | Integrante | Ferramenta | O que foi pedido | Resultado | Validação crítica |
|---|---|---|---|---|---|
| _até 06/11_ | _A preencher_ | Claude (chat) | _A confirmar_: apoio na escrita de `CITIZEN_ASSIST_SPEC.md` e `processo_desenvolvimento.md` | _A preencher_ | _A preencher_ (ex.: decisões aprovadas em reunião; itens não verificados marcados como EM ABERTO) |
| 06/11 | Juan | Claude Code | Ler o enunciado (incluindo as 2 tabelas, que estavam como imagens) e resumir os requisitos | Aceito | Resumo conferido com o enunciado original |
| 06/11 | Juan | Claude Code | Criar um documento de planejamento com as atividades divididas entre 3 integrantes | **Rejeitado na 1ª versão**, refeito | A 1ª versão foi escrita **sem ler a spec** e contradizia o formato da base, a pasta `testes/` e as frentes da equipe. Refeita para seguir a spec, que é a fonte de verdade |
| 06/11 | Juan | Claude Code | Criar o documento de arquitetura (`docs/arquitetura.md`) a partir da spec §5 | Aceito, aguardando revisão da equipe | A IA apontou uma questão para a equipe: pelos `relacionados` da spec, DOC-003/004/005 e SRV-005/006 ficam isolados no grafo (marcado como EM ABERTO). Falta revisão humana de cada seção |
| 06/11 | Juan | Claude Code | Comparar o repositório com o modelo da coordenação e criar o esqueleto do README e este arquivo | Aceito, aguardando revisão da equipe | README conferido com o modelo GLOBAL-SOLUTION do repositório da coordenação e com as 10 seções do enunciado |

<!-- Modelo para novas linhas:
| DD/MM | Nome | Ferramenta | Pedido resumido (sem dados pessoais) | Aceito / Ajustado / Rejeitado | Como foi conferido |
-->

---

## 4. Prompts testados

### 4.1 Prompts de desenvolvimento (Claude Code)

<!-- Registrar os prompts mais importantes, principalmente os que deram errado e foram reformulados.
     Exemplo de padrão adotado: "Implemente a tarefa A4 da spec §7.3 (1–5). Critério de aceite: ..." -->

| # | Prompt (resumo) | O que funcionou ou não | Ajuste feito |
|---|---|---|---|
| 1 | "Crie um documento para alinhar o projeto e separe as atividades para 3 integrantes" | A IA não conhecia a spec, porque ela estava em outra pasta, e criou um plano incompatível | Passar a spec como contexto (via `CLAUDE.md`) antes de pedir documentos de planejamento |

### 4.2 Modelos de resposta do assistente (A e B)

Os dois modelos de resposta exigidos pela GS são **templates de texto** (spec §8), não prompts de LLM, no modo terminal. A comparação entre eles fica na seção 4 do README e em `testes/resultados.csv`.

<!-- Responsável: Integrante B, após a atividade B3 (10/11). -->

### 4.3 Prompt do roteador (Gemini, modo servidor)

<!-- Responsável: Integrante B, após a atividade B5 (10/11).
     Registrar: instrução de sistema, as 4 ferramentas declaradas, testes de injeção de prompt
     (ex.: PDF com "ignore as instruções") e o comportamento do fallback. -->

_A preencher_

---

## 5. Validação crítica

<!-- Responsável: Integrante B consolida · Prazo: 17/11 -->

| O que validar | Como | Resultado |
|---|---|---|
| Cada orientação da base contra a fonte oficial | Integrante revisor abre a página e confere (atividade E2) | _A preencher_ |
| Código gerado contra a spec | Revisão do PR por outro integrante, citando a seção da spec | _A preencher_ |
| Respostas do assistente contra a base | `--avaliar`: a resposta obtida precisa ser o registro esperado | _A preencher_ |
| Saída do Gemini no modo servidor | A resposta precisa conter a `referencia` da base e nenhuma URL fora dela (spec §8) | _A preencher_ |
| Segurança (cripto, `initData`, isolamento) | Testes automatizados + revisão humana obrigatória | _A preencher_ |

---

## 6. Limitações e cuidados

- A IA pode produzir texto convincente e errado. Por isso, nenhum conteúdo de orientação é aceito sem conferência na fonte oficial.
- Respostas de IA mudam entre execuções. Por isso, a resposta ao cidadão é determinística (vem da base) e o LLM só escolhe a ferramenta.
- No produto, documentos do cofre passam pelo Gemini **com consentimento do usuário** e em plano pago (spec §12). Logs de abuso podem ser mantidos por tempo limitado pelo Google.
