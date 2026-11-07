# Citizen Assist AI — Documento do projeto/produto, SDD e SDLC

> Documento de processo da equipe (GS 2026.2 · CitizenTech). Complementa a [especificação](especificacao/CITIZEN_ASSIST_SPEC.md), que é a **fonte de verdade**, e serve de base para as seções de arquitetura e impacto do `relatorio.pdf`.

---

## Parte A — O projeto e o produto

### A.1 O problema
Cidadãos encontram informação dispersa, termos difíceis e instruções incompletas ao buscar orientação sobre documentos, serviços e direitos do dia a dia. A busca fica lenta, confusa e sujeita a interpretações erradas.

### A.2 O produto
**Citizen Assist AI** é um assistente de orientação cidadã **não oficial**. Ele responde apenas com base em registros verificados (`data/base.json`), cita sempre a fonte oficial com a data de verificação e avisa quando não há base suficiente, sem inventar instruções.

| Camada | O que entrega | Quem avalia |
|---|---|---|
| **Núcleo (Onda 1)** | Terminal offline: base, busca com pontuação, grafo de temas + Dijkstra, modelos de resposta A e B, tratamento de entradas inválidas, testes e métricas | **A Global Solution** |
| **Produto (Onda 2)** | Bot no Telegram (texto, voz, foto, PDF), roteador com Gemini, cofre criptografado de documentos, tarefas/lembretes, briefing matinal, painel web (Mini App) | Diferencial da equipe |

### A.3 Público e valor
- **Público:** pessoas que precisam de orientação simples sobre documentação pessoal, serviços públicos e direitos, inclusive quem tem pouca familiaridade com os portais oficiais.
- **Valor:** reduz o tempo de busca, aponta o caminho oficial correto, deixa claros os limites da resposta e organiza documentos e lembretes num só lugar.
- **Temas:** Documentação pessoal · Serviços públicos (INSS, CadÚnico, SUS) · Direitos e orientações comunitárias. Total planejado: 17 registros.

### A.4 Princípios do produto
1. **Resposta vem da base**, nunca de texto livre do LLM. Isso torna a taxa de acerto mensurável.
2. **Transparência:** toda resposta traz fonte, data e, quando preciso, aviso para confirmar no site oficial.
3. **Privacidade por padrão:** coletar o mínimo; senha do cofre só no painel; criptografia antes de armazenar.
4. **Honestidade sobre limites:** não é canal oficial; criptografia ponta a ponta real só no painel; documentos do cofre passam pelo Gemini (plano pago, com consentimento).

### A.5 Fora do escopo
Integração com órgãos públicos, consulta ao site oficial em tempo real (`consultar_site_oficial`, roadmap), classificador de documentos local (roadmap), CNH e CPF na base (ampliação), qualquer pagamento.

---

## Parte B — Spec-Driven Development (SDD)

### B.1 O que é, aplicado aqui
No SDD, a **especificação escrita vem antes do código e governa o código**. Em vez de "pedir código" a uma IA e ajustar depois, a equipe define o *quê* e o *porquê* com precisão, deriva um plano e tarefas pequenas, implementa uma tarefa por vez e **valida o resultado contra a spec**. A spec é um artefato vivo e versionado no Git.

No nosso caso, a spec fica em `docs/especificacao/CITIZEN_ASSIST_SPEC.md` e o `CLAUDE.md` da raiz apenas a **importa** (não há cópia). Assim o Claude Code a lê antes de qualquer trabalho. Isso reduz alucinação de requisito, mantém a IA dentro do escopo aprovado e deixa a decisão de produto com os humanos.

### B.2 O fluxo SDD da equipe

```
Especificar ─► Planejar ─► Quebrar em tarefas ─► Implementar ─► Validar ─► (ajustar spec ou código)
   (spec)       (plano)      (tarefas pequenas)    (1 por vez)   (testes)
```

| Etapa | O que fazemos | Artefato | Onde |
|---|---|---|---|
| **1. Especificar** | Requisitos da GS, decisões aprovadas, esquema da base, regras de busca, segurança | `CITIZEN_ASSIST_SPEC.md` | `docs/especificacao/` (importada pelo `CLAUDE.md`) |
| **2. Planejar** | Arquitetura, stack, ordem de implementação por marco | §5, §12 e §16 da spec | Mesma spec |
| **3. Tarefas** | Cada marco vira tarefas curtas com critério de aceite testável | Issues/Projects do GitHub ou `TASKS.md` | Repositório |
| **4. Implementar** | Claude Code executa **uma tarefa por vez**, citando a seção da spec que atende | Commits pequenos | Git |
| **5. Validar** | Testes automatizados + `--avaliar` + revisão humana contra a spec | `testes/`, `resultados.csv` | Repositório |
| **6. Evoluir** | Mudou requisito? **Atualiza a spec primeiro**, depois o código | Diff da spec no PR | Git |

### B.3 Regras de trabalho com o Claude Code
1. **Spec primeiro.** Nenhuma mudança de comportamento sem alterar a spec no mesmo PR.
2. **Uma tarefa por vez**, com critério de aceite escrito antes (ex.: "validar base: arquivo ausente, vazio e JSON inválido geram mensagem clara, sem traceback").
3. **Itens (EM ABERTO) não são decididos pela IA.** Viram `TODO` e vão para o responsável humano.
4. **Rastreabilidade:** a mensagem do commit ou o PR cita a seção da spec (ex.: `busca: decisão C·A·B (spec §7.3)`).
5. **Revisão humana obrigatória** de tudo que toca segurança (cripto, `initData`, isolamento por `user_id`, `.env`) e de todo texto de orientação da base.
6. **Nunca** colocar segredos, dados pessoais ou documentos reais em prompts, commits ou testes.
7. **Registrar o uso de IA** em `docs/uso_ia.md`: o que foi pedido, o que foi aceito ou rejeitado e como foi validado.

### B.4 Matriz de rastreabilidade (requisito → spec → módulo → teste)

| Requisito da GS | Spec | Módulo | Verificação |
|---|---|---|---|
| ≥ 15 registros, ≥ 3 temas, campos obrigatórios | §7.1–7.2 | `data/base.json`, `base.py` | Teste de validação da base; `--validar-entrega` |
| Ler JSON, listar temas, tratar arquivo ausente/vazio/inconsistente | §6.2, §7.1 | `base.py` | Testes automatizados (3 casos de erro) |
| Busca por pergunta ou menu; várias correspondências | §7.3 | `busca.py` | Perguntas 1–11 |
| Grafo de temas e navegação com ≥ 3 assuntos | §7.3 (7–9) | `busca.py` | Teste de Dijkstra e de relacionados |
| ≥ 2 modelos de prompt, comparados | §8 | `respostas.py` | Rubrica A × B (`comparacao_modelos.csv`) |
| Aviso de limitação, sem inventar | §7.3, §8 | `busca.py`, `respostas.py` | Perguntas 12–14 e limites L1–L3 |
| ≥ 12 perguntas, ≥ 3 limites, taxa de acerto e tempo | §14 | `testes/`, `sistema.py --avaliar` | `resultados.csv` (conjuntos equipe e público) |
| Usabilidade com ≥ 1 usuário | §14.2 | — | `testes/usabilidade.md` |
| Privacidade e não oficialidade | §13 | todos | Checklist de revisão (§13) |
| Uso de IA documentado | §15.3 | — | `docs/uso_ia.md` |
| Entrega: repo público + vídeo + `.txt` | §15.4, §18 | — | Checklist §18 |

### B.5 Definição de pronto de uma tarefa
- Critério de aceite atendido e coberto por teste.
- Comentários em português no código (exigência da GS).
- Spec atualizada se algo mudou.
- Sem segredos, sem log de dado sensível.
- Revisado por outra pessoa da equipe antes do merge.

### B.6 Riscos específicos do SDD com IA e mitigação
| Risco | Mitigação |
|---|---|
| IA implementa algo que a spec não pede | Tarefas pequenas; revisão de diff contra a seção citada |
| Spec desatualizada em relação ao código | Regra "spec antes do código"; PR sem diff da spec quando muda comportamento é recusado |
| Orientação da base escrita por IA sem conferir | Texto escrito pela equipe a partir da página oficial, com data; IA só ajuda a revisar a linguagem |
| Equipe não entende o código gerado | Cada integrante explica no vídeo e no relatório o módulo pelo qual é responsável (a GS exige compreender e justificar) |

---

## Parte C — Ciclo de vida do software (SDLC)

Modelo adotado: **iterativo e incremental, em duas ondas**, com marcos curtos e prazo fixo. Cada fase tem entrada, saída e critério de passagem.

### C.1 Fases, datas e artefatos

| Fase | Período | Atividades | Saída | Critério de passagem |
|---|---|---|---|---|
| **1. Planejamento e requisitos** | até 06/11 | Ler a GS, definir produto, escopo, ondas, riscos | Proposta de produto aprovada pela equipe | Checklist de decisões 100% marcado (feito) |
| **2. Projeto (design)** | até 06/11 | Arquitetura, esquema da base, busca, cripto, hospedagem | `CITIZEN_ASSIST_SPEC.md` | Spec cobre todos os itens da GS (matriz B.4) |
| **3. Implementação** | 06–13/11 | Marcos 1 a 7 da spec §16 | Código no GitHub | Marco 1 (terminal offline) antes de tudo; código completo em 13/11 |
| **4. Teste e verificação** | 08/11 → 17/11 | Testes automatizados, 14 perguntas + limites, usabilidade, revisão de segurança | `resultados.csv`, `usabilidade.md` | Indicadores calculados e interpretados; nada crítico aberto |
| **5. Documentação e entrega** | 14–19/11 | README (10 seções), relatório PDF, `uso_ia.md`, vídeo, `.txt` na FIAP ON | Entregáveis da Tabela 2 | Checklist final da spec §18 |
| **6. Operação e manutenção** | pós-entrega | VM, deploy automático, revisão de datas da base, roadmap | Versão `main` estável | Registros com data de verificação ≤ 90 dias |

> **Regra de corte (13/11):** o que não estiver testado vira roadmap no README e no relatório, não entra na demonstração.

### C.2 Ambientes e fluxo de código
- **Branches:** `main` protegida (sempre demonstrável) + branches curtas por tarefa (`feat/busca`, `feat/cofre`…). Merge por PR com revisão de um colega.
- **Integração e deploy:** push na `main` dispara GitHub Actions → deploy por SSH na VM (chave dedicada em Secrets). `.env` só na VM.
- **Dois modos de execução:** `python src/sistema.py` (terminal, avaliado) e `--servidor` (bot, painel, agendador).

### C.3 Qualidade e testes por camada
| Camada | O que testar | Como |
|---|---|---|
| Base | Campos obrigatórios, ids únicos, relacionados válidos, arquivo ausente/vazio | Testes automatizados |
| Busca | Normalização, pontuação, desempate, 4 saídas da regra de decisão | Testes automatizados + perguntas 1–14 |
| Grafo | Dijkstra, sem caminho, relacionados | Testes automatizados |
| Respostas | Modelos A e B trazem fonte e aviso | `--avaliar` |
| Segurança | Isolamento por `user_id`, cripto round-trip, senha errada, `initData` | Testes automatizados + revisão humana |
| Usabilidade | Roteiro de tarefas com pessoa de fora | `usabilidade.md` |

### C.4 Gestão de riscos do projeto
| Risco | Prob. | Impacto | Resposta |
|---|---|---|---|
| Tempo curto (7 dias de código) | Alta | Alta | Onda 1 primeiro; regra de corte em 13/11 |
| Orientações da base sem conferência | Média | Alta | Equipe lê a fonte oficial e registra a data; DOC-004 e DIR-006 conferidos com atenção |
| HTTPS gratuito não funcionar (DuckDNS + Caddy) | Média | Média | Teste de 15 min já; plano B Cloudflare quick tunnel ou máquina de um integrante |
| Limites da VM gratuita (Oracle) | Média | Média | Monitorar; plano B de hospedagem |
| Vazamento de segredo no repositório público | Baixa | Alta | `.gitignore`, `.env.example`, revisão do histórico antes de enviar |
| Dado sensível no cofre / Gemini | Média | Alta | Plano pago com faturamento ativo, consentimento no upload, texto honesto no README |
| Integrante indisponível | Média | Média | Frentes com responsáveis e suplentes (a definir) |

### C.5 Papéis (definidos em 07/11)
| Frente | Responsável | Suplente |
|---|---|---|
| Núcleo e dados (base, busca, testes, métricas) | A — Juan de Lucas Frois (RM563260) | a definir |
| Bot e roteador (Telegram, Gemini, tarefas, briefing) | B — Flávia Roberta Pennachin (RM561860) | a definir |
| Cofre, painel e infraestrutura (cripto, Mini App, VM, deploy) | C — Pedro Valente (RM570394) | a definir |

Mantenedor da VM em último caso: Juan.

### C.6 Marcos de acompanhamento
| Data | Marco | Evidência |
|---|---|---|
| 08/11 | Terminal offline funcionando (Marco 1) | Demo local de `python src/sistema.py` |
| 10/11 | Bot respondendo na VM com deploy automático | Mensagem no Telegram + Action verde |
| 12/11 | Cofre e rotinas funcionando | Teste de cofre com senha errada e expiração |
| 13/11 | **Código congelado** | Tag de versão; suíte de testes passando |
| 17/11 | Indicadores, usabilidade e relatório fechados | `resultados.csv`, `relatorio.pdf` |
| 19/11 | **Entrega na FIAP ON** | `.txt` com repo público e vídeo Não Listado |

### C.7 Ritual semanal curto
Reunião rápida (15 min) a cada 2 dias até 13/11: o que foi entregue, o que bloqueia, o que vira roadmap. Decisões novas entram na spec no mesmo dia.

---

## Referências internas
- [`docs/especificacao/CITIZEN_ASSIST_SPEC.md`](especificacao/CITIZEN_ASSIST_SPEC.md) — especificação técnica completa.
- [`docs/Solicitação GS.md`](Solicitação%20GS.md) — enunciado oficial.
- Repositório modelo da coordenação: https://github.com/equipe1ccon/FIAP-PORTFOLIO-1CCON/tree/master
