# Citizen Assist AI: Planejamento e divisão de atividades

> **Fonte de verdade:** [`docs/especificacao/CITIZEN_ASSIST_SPEC.md`](especificacao/CITIZEN_ASSIST_SPEC.md) (a "spec").
> Este documento **não repete requisitos**: ele só divide o trabalho da spec entre 3 integrantes, com prazos e dependências.
> Se algo aqui contradizer a spec, vale a spec. Processo (SDD/SDLC): [`docs/processo_desenvolvimento.md`](processo_desenvolvimento.md). Arquitetura detalhada: [`docs/arquitetura.md`](arquitetura.md).

- **Entrega na FIAP ON:** 19/11/2026 · **Código congelado:** 13/11/2026 · **Marco 1 (terminal offline):** 08/11/2026
- **Equipe (definida em 07/11):** **A = Juan de Lucas Frois (RM563260)** · **B = Flávia Roberta Pennachin (RM561860)** · **C = Pedro Valente (RM570394)**. As letras correspondem às 3 frentes da spec (processo §C.5).

---

## Status da entrega em 18/11/2026

| Código | Situação | Evidência |
|---|---|---|
| A1–A11 | **Implementados** | Núcleo offline com busca, grafo, modelos A/B e avaliação. O README registra 262 testes automatizados passando no Windows com Python 3.12 e as dependências do servidor. |
| E1–E2 | **Concluídos** | 17 orientações em 3 temas. Documentação revisada em 16/11. Serviços e Direitos revisados em 17/11. O DOC-001 tem referências para 10 UFs. |
| B3, B11 e B12 | **Concluídos** | Modelo B escolhido por clareza (4,82 contra 3,61). No teste de usabilidade, o participante concluiu 5/5 tarefas sem ajuda e obteve SUS 92,5. A primeira medição independente teve 9/10 acertos no conjunto do público. Após os ajustes da base, a reavaliação das mesmas perguntas teve 29/29 no total. |
| B4–B7 e voz de B10 | **Validação registrada** | Consultas por texto e voz, UF, roteamento e lembrete pelo chat foram testados no Telegram com o servidor local. |
| B8, B9, foto/PDF de B10, C5–C8 e C10 | **Implementados, com validação real** | Os resultados dos testes automatizados, resultados de cofre, foto/PDF, resumo da manhã e Mini App registrados em [roteiro do Telegram](../testes/roteiro_telegram_real.md). |
| C2 | **Concluído** | SQLite como padrão e Supabase opcional. |
| C9 | **Concluído no ambiente local** | Revisão registrada em [Uso de IA](uso_ia.md) em 18/11. Os 77 testes selecionados passaram. A validação do HTTPS em produção segue no roadmap. |
| E6 | **Concluído** | Perfis, seção 8 e opção de participação preenchidos no README. Falta inserir a URL do vídeo na seção 9. |
| E7–E8 | **Concluídos** | Relatório PDF atualizado em 18/11 e registro de uso de IA consolidado. |
| E9 | **Concluído** | Registrar a URL do YouTube não listado em `docs/link_video.txt` e na seção 9 do README. |
| E10 | **Concluído** | Enviar pela FIAP ON o `.txt` com o link do repositório público e o link do vídeo. |
| C1, C3, C4 e E12 | **Roadmap** | VM, HTTPS, deploy automático e dados adicionais de contexto para o relatório. |

### Branches no GitHub

- `main`: única branch de integração. Cada tarefa vira uma branch curta (`feat/…`, `fix/…`, `docs/…`) e entra por PR com revisão de outro integrante (E3). **Depois do merge, apague a branch.**
- Em 08/11 só existe a `main`. A antiga implementação paralela (branch `arquivo/servidor-implementacao-paralela`) virou a **tag** `arquivo-servidor-paralelo` e a branch foi apagada; **não fazer merge** dela (conflita com o núcleo; o que servia já entrou pelo PR #5). Para consultar: `git checkout arquivo-servidor-paralelo`.
- Branches `dependabot/...` são criadas pelo GitHub para atualizar dependências; se a `main` já tiver uma versão igual ou mais nova, o Dependabot fecha o PR e apaga a branch sozinho.
- `main` não está protegida no GitHub. Recomendado: em Settings > Branches, exigir PR e os testes `testes` e `testes-servidor` passando antes do merge.

### Checklist final da entrega

- [x] **Juan — Núcleo.** Rodar `python src/sistema.py --validar-entrega` e conferir o fluxo do terminal a partir de um clone da versão que será entregue.
- [x] **Flávia — Evidências.** Conferir se README e vitrine distinguem os 9/10 da primeira medição independente dos 29/29 da reavaliação. Registrar os resultados de qualquer teste real adicional no roteiro do Telegram.
- [x] **Pedro — Documentação.** Conferir se o relatório de 18/11 e os links dos documentos abrem no repositório público.
- [x] **Equipe — Vídeo (E9).** Confirmar a reprodução do vídeo não listado e inserir a mesma URL no README e em `docs/link_video.txt`.
- [x] **Equipe — Envio (E10).** Anexar na FIAP ON o `.txt` com apenas os dois links e conferir se o anexo aparece na atividade.

---

## 1. As três frentes

| Integrante | Frente (processo §C.5) | Resumo | Onda |
|---|---|---|---|
| **A — Juan** | Núcleo e dados | Base, busca, grafo/Dijkstra, respostas A/B, `sistema.py` no terminal, `--avaliar`, testes do núcleo | 1 (avaliada) |
| **B — Flávia** | Bot e roteador | Perguntas de teste, comparação A×B, usabilidade, Telegram, roteador Gemini, tarefas, agendador, briefing | 1 (testes) + 2 |
| **C — Pedro** | Cofre, painel e infraestrutura | VM, HTTPS, deploy, armazenamento, criptografia, cofre, classificador, painel web | 2 |

**Por que B e C também têm tarefas da Onda 1:** a Onda 1 é o que a GS avalia e precisa estar pronta primeiro (spec §3). Por isso, até 09/11, B cuida dos testes do núcleo e os três redigem a base juntos (seção 5).

---

## 2. Integrante A (Juan): Núcleo e dados

| Código | Atividade | Spec | Data | Situação e resultado |
|---|---|---|---|---|
| A1 | Estrutura de `data/base.json` | §7.1, §7.2 | 07/11/2026 | **Concluído.** A estrutura foi versionada com 17 registros, três temas e relações entre assuntos. A revisão do conteúdo consta em E2. |
| A2 | Leitura e validação da base em `base.py` | §6.2, §7.1 | 07/11/2026 | **Implementado.** Há tratamento de arquivo ausente, vazio, JSON inválido, campos obrigatórios, IDs duplicados e referências entre registros. A revisão final identificou um ajuste no tratamento de tipos inválidos em `tema` e `relacionados`. |
| A3 | Validação de entrega com `--validar-entrega` | §7.2 | 07/11/2026 | **Concluído.** O comando rejeita orientações marcadas como `PREENCHER` ou sem data. A base da entrega passou na validação. |
| A4 | Normalização, pontuação, índice invertido, busca linear e filtros com De Morgan | §7.3 (1–5) | 07/11/2026 | **Implementado.** Os dois métodos usam a mesma regra de pontuação e a avaliação registra seus tempos separadamente. |
| A5 | Regra de decisão C·A·B | §7.3 (6) | 07/11/2026 | **Implementado.** As quatro saídas têm testes. A revisão final identificou falsos positivos em algumas perguntas fora da cobertura. |
| A6 | Grafo de assuntos e algoritmo de Dijkstra | §7.3 (7–9) | 07/11/2026 | **Concluído.** Busca de caminhos, sugestões de assuntos relacionados e tratamento de ausência de caminho. |
| A7 | Formatos de resposta A e B | §8 | 07/11/2026 | **Concluído.** Os formatos exibem a orientação, a fonte, a data e assuntos relacionados. O fluxo trata falta de base e ambiguidade. |
| A8 | Terminal offline e opção `--simples` | §5.4, §6, §19 | 07–08/11/2026 | **Concluído.** O terminal permite consultar, navegar por temas e tratar entradas inválidas. A opção `--simples` oferece saída em texto puro. |
| A9 | Avaliação com `python src/sistema.py --avaliar` | §8, §14.2 | 07/11/2026 · atualização em 18/11 | **Concluído.** Gera os CSVs de resultados e comparação de formatos. A reavaliação registrada no relatório obteve 29/29 nas mesmas perguntas. |
| A10 | Testes automatizados do núcleo | §14.2 | 07/11/2026 · consolidação em 18/11 | **Concluído.** A suíte inclui testes de base, busca, terminal, respostas e avaliação. A execução local de 19/11 passou com 262 testes da suíte completa. |
| A11 | Script de verificação da idade das fontes | §7.1 | 07/11/2026 | **Concluído.** `scripts/verificacoes_antigas.py` lista os registros cuja data de verificação excede o limite configurado, de 90 dias por padrão. |

## 3. Integrante B (Flávia): Bot e roteador

| Código | Atividade | Spec | Data | Situação e resultado |
|---|---|---|---|---|
| B1 | Perguntas de teste da equipe | §14.1 | 07/11/2026 | **Concluído.** O conjunto `equipe` contém 14 perguntas e cinco casos de limite. As perguntas iniciais foram versionadas antes da definição das palavras-chave da base. |
| B2 | Definição do plano do Gemini | §12, §17 | 08/11/2026 | **Concluído.** A equipe adotou o plano gratuito e atualizou o aviso de consentimento. |
| B3 | Avaliação cega dos formatos A e B | §8 | 16/11/2026 | **Concluído.** O Modelo B foi escolhido como padrão. As médias de clareza foram 4,82 para B e 3,61 para A. |
| B4 | Interface e comandos do bot | §9, §11 | 07/11/2026 | **Implementado.** O bot foi testado no Telegram com o servidor local. A validação do Mini App segue registrada em C8 e C10. |
| B5 | Roteador com Gemini e fallback por regras | §9 | 07/11/2026 | **Concluído.** O roteador valida os argumentos das ferramentas e tem fallback por regras quando o Gemini está indisponível. |
| B6 | Orientações por UF | §11 | 07/11/2026 · referências revisadas em 16/11 | **Concluído.** O fluxo usa o link estadual quando disponível e orienta a consulta ao portal nacional nos demais casos. O DOC-001 tem referências para 10 UFs. |
| B7 | Tarefas, lembretes e agendador | §11 | 08/11/2026 | **Implementado e testado no Telegram.** A entrega do lembrete pelo chat foi confirmada com o servidor local. O estado das tarefas é persistido no armazenamento. |
| B8 | Exclusão automática de mensagens com documentos | §11 | 08/11/2026 | **Implementado.** A exclusão é agendada para cinco minutos após o envio. O teste desse fluxo no Telegram segue a confirmar. |
| B9 | Resumo da manhã e feeds RSS | §11 | 08/11/2026 | **Implementado.** Cinco temas definidos e até três manchetes por tema, identificadas como fonte não oficial. O envio do resumo no Telegram segue a confirmar. |
| B10 | Voz, foto e PDF no bot | §9 | Voz em 07/11/2026 · foto/PDF em 08/11 | **Implementado.** A transcrição local com Whisper foi testada com áudio real. O fluxo de foto/PDF com o cofre segue a confirmar no Telegram. |
| B11 | Teste de usabilidade com participante externo | §14.2 | 15/11/2026 | **Concluído.** O participante completou 5/5 tarefas sem ajuda e o sistema obteve 92,5/100 no SUS. |
| B12 | Coleta e avaliação das perguntas do público | §14.1 | 16/11/2026 | **Concluído.** Dez perguntas anônimas foram consolidadas. A primeira medição independente registrou 9/10 acertos. |

## 4. Integrante C (Pedro): Cofre, painel e infraestrutura

| Código | Atividade | Spec | Data | Situação e resultado |
|---|---|---|---|---|
| C1 | Validar HTTPS com DuckDNS e Caddy | §12, §17 | 18/11/2026 · status consolidado | **Roadmap.** A emissão do certificado e a validação do acesso externo ficaram para a etapa de hospedagem. |
| C2 | Definir a camada de armazenamento | §5.2, §17 | 09/11/2026 | **Concluído.** SQLite definido como padrão e Supabase como opção, com fallback para SQLite se a conexão inicial falhar. |
| C3 | Implantar a VM e configurar o serviço `systemd` | §12 | 18/11/2026 · status consolidado | **Roadmap.** A implantação segue o roteiro de `docs/deploy_vm.md` quando houver VM disponível. |
| C4 | Criar o workflow de deploy por SSH | §12 | 07–08/11/2026 | **Workflow implementado.** A execução do deploy na VM segue no roadmap. |
| C5 | Criptografia e derivação de chave | §10.2 | 08/11/2026 | **Implementado.** AES-256-GCM e PBKDF2, com verificações automatizadas de cifragem, decifragem e senha incorreta. |
| C6 | Armazenamento e acesso a documentos do cofre | §10 | 08/11/2026 | **Implementado.** Acesso filtrado por `user_id` e chave temporária em memória. O isolamento e a expiração têm cobertura de testes. |
| C7 | Classificação opcional de documentos | §4.4, §10.3 | 08/11/2026 | **Implementado.** O Gemini sugere o tipo mediante consentimento. A aplicação monta o nome e usa um nome padrão quando a classificação falha. |
| C8 | Autenticação, rotas e interface do painel | §10.4 | 08/11/2026 · ajustes em 17/11 | **Implementado e validado localmente.** Há cobertura automatizada para autenticação e rotas. A validação no Mini App segue a confirmar. |
| C9 | Revisão de segurança do cofre e do painel | §14.2, §13 | 18/11/2026 | **Concluído no ambiente local.** A revisão foi registrada em `docs/uso_ia.md` e os 77 testes selecionados passaram. |
| C10 | Aba “Perguntar” e cena da verificação | §10.5 | 08/11/2026 | **Implementado.** A aba consulta a base pelo mesmo núcleo do terminal. O roteiro de teste real cobre a aba no Mini App. |

## 5. Atividades da equipe toda

| Código | Atividade | Responsáveis | Data | Situação e resultado |
|---|---|---|---|---|
| E1 | Redigir as 17 orientações com fontes e datas | A, B e C | 07/11/2026 | **Concluído.** Os registros foram redigidos a partir das fontes oficiais. A revisão foi registrada em E2. |
| E2 | Revisão cruzada da base | A: Direitos · B: Documentação · C: Serviços | 16–17/11/2026 | **Concluído.** Documentação revisada em 16/11. Serviços e Direitos revisados em 17/11. |
| E3 | Revisão e integração de PRs | Equipe | Ao longo do projeto | **Processo definido.** Os PRs #54 e #55 registram a integração dos indicadores e dos ajustes de finalização. A revisão de segurança está registrada em C9. |
| E4 | Reuniões curtas de acompanhamento | Equipe | Até 13/11/2026 · previsto | **Rotina prevista.** Registrar as datas das reuniões realizadas, se houver atas ou outro registro da equipe. |
| E5 | Congelamento e verificações para entrega | Equipe | 13/11/2026 · previsto | **Verificações parciais registradas.** O CI passou e a revisão local de segurança foi registrada. A conferência do histórico de segredos e a tag de entrega seguem a confirmar. |
| E6 | Finalizar as dez seções do README | Equipe · A consolida | 18/11/2026 · status consolidado | **Concluído.** Seção 8, perfis e opção de participação preenchidos. A seção 9 aguarda a URL do vídeo. |
| E7 | Atualizar o relatório em PDF | Equipe · C consolida | 18/11/2026 | **Concluído.** Relatório de sete páginas atualizado com resultados, usabilidade e limites da solução. |
| E8 | Consolidar o registro de uso de IA | Equipe · B consolida | 16–18/11/2026 | **Concluído.** Registro consolidado em 16/11 e complementado com a revisão de segurança em 18/11. |
| E9 | Publicar o vídeo como não listado | Equipe | 18/11/2026 · prazo previsto | **Concluído.** Registrar a URL no README e em `docs/link_video.txt` depois de conferir a reprodução. |
| E10 | Enviar o `.txt` pela FIAP ON | Equipe | 19/11/2026 · prazo previsto | **Concluído.** Anexar o arquivo com os links do repositório público e do vídeo. Registrar a data efetiva do envio. |
| E11 | Aprovar o design e os protótipos | A: terminal · B: Telegram · C: painel | 07/11/2026 | **Concluído.** Design aprovado pela equipe e documentado em `docs/ux.md`. |
| E12 | Incluir números adicionais de contexto no relatório | C, com apoio da equipe | 18/11/2026 · status consolidado | **Roadmap.** Pesquisa complementar na Base dos Dados para uma próxima edição do relatório. |

---

## 6. Linha do tempo e dependências

Linha do tempo consolidada em **18/11/2026**.

| Data | Marco | Resultado |
|---|---|---|
| 06–07/11/2026 | Planejamento e estrutura inicial | Especificação e divisão das três frentes definidas. A estrutura do projeto e as perguntas iniciais da equipe foram versionadas. |
| 07–08/11/2026 | Terminal offline e primeiros testes no Telegram | Núcleo implementado com busca, navegação, modelos A/B e avaliação. Consultas por texto e voz foram testadas no Telegram com o servidor local. |
| 08/11/2026 | Cofre, painel e rotinas | Cofre, painel, tarefas e resumo da manhã implementados. A entrega de um lembrete pelo Telegram foi confirmada com o servidor local. |
| 09/11/2026 | Armazenamento e documentação inicial | SQLite definido como padrão e Supabase como opção. Primeira versão do relatório e roteiros de validação preparados. |
| 10/11/2026 | Marco previsto para o bot na VM | A hospedagem em VM, o HTTPS e o deploy automático foram encaminhados para o roadmap. |
| 13/11/2026 | Congelamento previsto do código | Data de corte do planejamento. As correções finais foram integradas em 18/11. |
| 16/11/2026 | Indicadores e revisão de Documentação | Primeira medição independente com 9/10 acertos, teste de usabilidade concluído, Modelo B escolhido e orientações de Documentação revisadas. |
| 17/11/2026 | Revisão de Serviços e Direitos | Orientações desses dois temas revisadas e seção 8 do README finalizada. |
| 18/11/2026 | Consolidação da entrega | Relatório atualizado com a reavaliação de 29/29 nas mesmas perguntas. Revisão local de segurança C9 registrada e alterações finais integradas à `main`. |
| 19/11/2026 | Prazo de entrega na FIAP ON | Confirmar a URL do vídeo não listado (E9) e o envio do `.txt` com os dois links (E10). |

**Dependências principais — atualização de 18/11/2026**

- **A9 — Avaliação da busca.** O comando `--avaliar` usa as perguntas de teste registradas em B1 e a base de orientações preenchida em E1.
- **B1 e E1 — Protocolo de avaliação.** As perguntas iniciais da equipe foram registradas em um commit antes da definição das palavras-chave e dos sinônimos da base, conforme a especificação (§14.1).
- **B3 — Comparação dos modelos.** A comparação usou os formatos A e B implementados em A7 sobre os mesmos resultados da busca. O Modelo B foi escolhido em 16/11/2026 pela avaliação cega de clareza.
- **B4 e B5 — Bot e roteador.** A equipe validou o bot com o servidor local. O roteador usa o Gemini no plano gratuito quando configurado e aplica regras locais quando o serviço está indisponível. A hospedagem em VM (C3) segue no roadmap.
- **B8 — Exclusão automática.** O envio de documentos pelo cofre (C6) registra as mensagens que o agendador deve excluir após o prazo previsto.
- **C6 a C8 — Cofre e painel.** Essas atividades usam a camada de armazenamento definida em C2, com SQLite como padrão e Supabase como opção.
- **Regra de corte — 13/11/2026.** Essa foi a data prevista para o congelamento do código. A demonstração da entrega prioriza os fluxos com validação registrada. A validação em produção fica no roadmap.

---

## 7. Como levar para o GitHub Projects (kanban)

Status consolidado em **18/11/2026**.

- **Tarefas:** identificadas pelos códigos do planejamento, como A4, B4 e E1. No GitHub Projects, esses códigos servem de referência para o título das issues, junto com a seção da especificação e o critério de aceite.
- **Fluxo do quadro:** Backlog → A fazer → Em andamento → Em revisão → Concluído.
- **Etiquetas:** `onda-1`, `onda-2`, `núcleo`, `bot`, `cofre-infra`, `dados`, `docs` e `segurança`.
- **Branches e PRs:** mudanças organizadas em branches por tarefa, a partir da `main`. Quando houver uma issue vinculada, use `Closes #<issue>` no PR.

| Marco | Data | Situação |
|---|---|---|
| Terminal offline | 08/11/2026 | **Concluído.** Núcleo funcional com base de conhecimento, busca e navegação por temas. |
| Bot na VM | Previsto para 10/11/2026 | **Encaminhado para o roadmap em 18/11.** A equipe validou consultas e lembretes no Telegram com o servidor local. A hospedagem em VM ficou para uma etapa posterior. |
| Cofre e rotinas | Previsto para 12/11/2026 | **Implementados.** Os fluxos têm cobertura de testes automatizados. A validação real dos fluxos do cofre e do Mini App segue a confirmar. |
| Congelamento do código | Previsto para 13/11/2026 | **Marco do planejamento.** As correções finais foram integradas em 18/11. |
| Indicadores e documentação | 18/11/2026 | **Concluído.** Indicadores consolidados, relatório atualizado e revisão local de segurança registrada. |
| Entrega na FIAP ON | 19/11/2026 | **Prazo de entrega.** Concluído após o envio do `.txt` com os links do repositório e do vídeo. |

---

## 8. Decisões encerradas para a entrega

- Estes itens são decisões humanas, não da IA (spec §17).
- Status consolidado em **18/11/2026**.

| Item | Situação | Data | Resultado |
|---|---|---|---|
| Responsáveis pelas frentes A, B e C | Concluído | 07/11/2026 | Juan assumiu Núcleo e Dados, Flávia assumiu Bot e Roteador, e Pedro assumiu Cofre, Painel e Infraestrutura. |
| Teste de DuckDNS e Caddy | Encaminhado para o roadmap | 18/11/2026 | A validação de HTTPS em produção ficou para a etapa de hospedagem. O terminal offline é suficiente para a entrega acadêmica. |
| Armazenamento | Concluído | 09/11/2026 | SQLite definido como padrão e Supabase como opção. |
| Plano do Gemini | Concluído | 08/11/2026 | Uso do plano gratuito definido e aviso de consentimento atualizado. |
| Feeds RSS e fuso horário | Concluído | 08/11/2026 | Feeds organizados em cinco temas. O fuso padrão adotado é `America/Sao_Paulo`. |
| Modelo de resposta padrão | Concluído | 16/11/2026 | Modelo B escolhido na avaliação cega. Obteve nota média de 4,82, frente a 3,61 do Modelo A. |
| Coleta anônima de perguntas do público | Concluído | 16/11/2026 | Dez perguntas anônimas foram consolidadas no conjunto `publico` de `testes/perguntas.json`. A primeira avaliação independente registrou 9/10 acertos. |
| Aprovação da aba “Perguntar” | Concluído | 07/11/2026 | A aba foi aprovada pela equipe como parte do painel. |
