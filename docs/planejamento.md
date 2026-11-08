# Citizen Assist AI: Planejamento e divisão de atividades

> **Fonte de verdade:** [`docs/especificacao/CITIZEN_ASSIST_SPEC.md`](especificacao/CITIZEN_ASSIST_SPEC.md) (a "spec").
> Este documento **não repete requisitos**: ele só divide o trabalho da spec entre 3 integrantes, com prazos e dependências.
> Se algo aqui contradizer a spec, vale a spec. Processo (SDD/SDLC): [`docs/processo_desenvolvimento.md`](processo_desenvolvimento.md). Arquitetura detalhada: [`docs/arquitetura.md`](arquitetura.md).

- **Entrega na FIAP ON:** 19/11/2026 · **Código congelado:** 13/11/2026 · **Marco 1 (terminal offline):** 08/11/2026
- **Equipe (definida em 07/11):** **A = Juan de Lucas Frois (RM563260)** · **B = Flávia Roberta Pennachin (RM561860)** · **C = Pedro Valente (RM570394)**. As letras correspondem às 3 frentes da spec (processo §C.5).

---

## Status em 08/11/2026 (`main` até o PR #38)

| Código | Situação | Observação |
|---|---|---|
| A1 a A11 | **Concluído** | Base, validação, busca (índice × linear, C·A·B, digitação, sinônimos), grafo/Dijkstra, modelos A e B, terminal, `--avaliar` (19/19), 231 testes, `scripts/verificacoes_antigas.py`. Falta só conferir numa máquina limpa e no Windows |
| B1 | Concluído | `testes/perguntas.json` (19 perguntas, conjunto `equipe`), congelado antes das palavras-chave |
| E1 (redigir as 17 orientações) | **Rascunho feito pela IA** | Todas com `data_verificacao` 2026-11-07; falta revisão humana (E2) |
| E2 (revisão cruzada da base) | **Pendente** | Inclui `referencias_estaduais` de DOC-001 (hoje vazio) |
| B4, B5, B6, B10 (voz) | **Concluído e testado no Telegram real** (07/11) | Bot, `/localizacao`, `/apagar_meus_dados`, roteador com cascata do Gemini, UF e voz (Whisper local) |
| B7, B8, B9, B10 (foto/PDF) | Código pronto e testado por testes; **falta teste no Telegram real** | Tarefas, agendador, autodestruição, resumo da manhã, foto/PDF no cofre |
| C5 a C8, C10 | Código pronto e testado por testes e no navegador local; **falta teste real** | Criptografia, cofre, classificador, painel (abas Perguntar, **Tarefas**, Cofre e Ajustes) |
| C2 | Parcial | SQLite atrás de `armazenamento.py`; Supabase **não** adotado (decisão EM ABERTO) |
| C1, C3, C4 | **Pendente** | DuckDNS/Caddy, VM e deploy nunca testados; deploy só liga com `DEPLOY_ATIVO=true` |
| C9 | Parcial | Testes de isolamento, senha errada, expiração e `initData` existem; falta revisão humana de segurança |
| B2, B3, B11, B12 | **Pendente** | Faturamento do Gemini, nota de clareza A × B (coluna `clareza_1a5` vazia), usabilidade (`testes/usabilidade.md` vazio), perguntas do público (nenhuma ainda) |
| E6 a E10 | **Pendente** | README (seções 1, 2, 8, 9, 10 e "Participação na Competição"), relatório PDF, `uso_ia.md` (consolidar), vídeo, `link_video.txt`, envio |
| E12 (novo) | Planejado, opcional | Números de contexto da Base dos Dados para o relatório (seção 5) |

### Branches no GitHub

- `main`: única branch de integração. Cada tarefa vira uma branch curta (`feat/…`, `fix/…`, `docs/…`) e entra por PR com revisão de outro integrante (E3). **Depois do merge, apague a branch.**
- `feat/painel-tarefas-aba` (PR #38): complemento da aba Tarefas; revisado, na `main` desde 08/11 e branch apagada.
- `arquivo/servidor-implementacao-paralela`: implementação paralela **arquivada de propósito**. **Não fazer merge**: conflita com o núcleo da `main`; o que servia dela já entrou pelo PR #5. Pode ficar como arquivo ou virar uma tag.
- `main` não está protegida no GitHub. Recomendado: em Settings > Branches, exigir PR e o teste `testes` passando antes do merge.

### Onde parou e o que cada um faz agora

**Como retomar:** `git pull origin main`; crie o ambiente do README §6 ("Rodar o bot") e instale também `httpx` para os testes do painel; rode `python -m unittest discover -s testes -t .` (231 testes) e `python src/sistema.py --avaliar` (19/19). Uma branch por tarefa a partir da `main`; PR citando a seção da spec; commits sem segredos.

**Já feito que vale conhecer antes de mexer:**
- A IA só entra no texto livre quando a base não resolve (`roteador.resposta_direta_basta`) e a escolha do Gemini é conferida com as regras (`roteador.reconciliar`). Botões nunca chamam IA.
- O bot usa `parse_mode` HTML; todo texto da base passa por `html.escape` (`ponte.formatar_telegram`).
- Chat e painel criam tarefas pela mesma função (`tarefas.tentar_criar`); a data é lida por regras, não pela IA. Concluir duas vezes a mesma tarefa não dá erro (de propósito).
- A voz é transcrita localmente com a dica de vocabulário `transcricao.VOCABULARIO`. Trocar para `small` é só `WHISPER_MODELO=small` no `.env`.
- `painel.py` **não** pode usar `from __future__ import annotations` (o FastAPI precisa das anotações em tempo de execução).

**Integrante A (Juan), até 13/11:**
1. E2: revisar as orientações de `direitos`; consolidar o README (§3, 4, 6 e 8) e o bloco "Estado do projeto".
2. Conferir `python src/sistema.py` numa máquina limpa e no Windows; rodar `--validar-entrega` antes de congelar (E5).
3. ~~Atualizar `cryptography`~~ feito em 08/11: `cryptography==49.0.0` (fecha os 5 alertas do Dependabot; 231 testes passando). Reinstale no ambiente do servidor: `pip install -r requirements.txt`.
4. Decidir o formato padrão A ou B depois das notas de clareza (B3); antes da VM, gerar novo token do bot e nova chave do Gemini.

**Integrante B (Flávia):**
1. B12 (até 14/11): coletar ≥ 10 perguntas do público, anônimas, no conjunto `publico`, e medir **antes** de ajustar a busca. B11 (até 15/11): teste de usabilidade (`docs/ux.md` §8 e SUS). B3: notas de clareza 1 a 5 (rótulos X/Y).
2. B2: confirmar faturamento do Gemini. Escolher os feeds RSS por tema (`data/feeds.json`).
3. Testar no Telegram real: foto/PDF, cofre pelo chat, lembrete, resumo da manhã e "Sim, apagar tudo".
4. E2: revisar `documentacao`, incluindo os links por estado do DOC-001. E8: consolidar `docs/uso_ia.md`.

**Integrante C (Pedro):**
1. C1, C3, C4 (prioridade): teste DuckDNS + Caddy, VM, `ffmpeg` e Whisper na VM, secrets e `DEPLOY_ATIVO=true`.
2. Testar o Mini App no Telegram real (todas as abas, incluindo Tarefas) com `PAINEL_URL` em https.
3. C9: revisão humana de segurança (cripto, `initData`, isolamento por `user_id`, `.env`).
4. E2: revisar `servicos`. E7: consolidar o relatório PDF; se der tempo, E12 (Base dos Dados).

**Melhorias conhecidas (não bloqueiam a entrega):** respostas do Gemini podem chegar fora de ordem; `pyright` não está no `.venv`; Windows não testado.

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

| Código | Atividade | Spec | Prazo | Critério de aceite |
|---|---|---|---|---|
| A1 | Esqueleto de `data/base.json` com os 17 registros (`orientacao: "PREENCHER"`, `data_verificacao` vazia) e `sinonimos` vazio | §7.1, §7.2 | 07/11 | 17 ids, 3 temas, `relacionados` e `referencia` preenchidos; grafo conexo |
| A2 | `base.py`: carga e validação | §6.2, §7.1 | 07/11 | Arquivo ausente, vazio, JSON inválido, campo faltando, id duplicado e relacionado inexistente geram mensagem clara, sem traceback |
| A3 | `--validar-entrega`: recusa registros com `PREENCHER` ou sem data | §7.2 | 07/11 | Teste com registro incompleto falha |
| A4 | `busca.py`: normalização, stopwords, sinônimos, bônus de expressão, índice invertido, busca linear, pontuação e filtros com De Morgan | §7.3 (1–5) | 08/11 | Mesma pergunta dá o mesmo resultado nos dois métodos |
| A5 | `busca.py`: regra de decisão C·A·B (limiar e margem em constantes) | §7.3 (6) | 08/11 | As 4 saídas cobertas por teste |
| A6 | `busca.py`: grafo não direcionado e Dijkstra, incluindo "sem caminho" | §7.3 (7–9) | 08/11 | Teste de caminho, de sem caminho e de relacionados |
| A7 | `respostas.py`: modelos A e B (os dois com relacionados), aviso de limitação e pedido de escolha | §8 | 08/11 | Toda resposta tem fonte, data e relacionados; aviso quando `confirmar_antes` |
| A8 | `sistema.py` (terminal): modo identidade (cores ANSI e molduras) com texto puro como reserva (`--simples`, `NO_COLOR`, saída sem terminal), pergunta direto no menu, menu `1`–`3`/`?`/`0`, navegação, tratamento de entradas, compatível com Python 3.9; telas e textos de `docs/ux.md` §3 | §5.4, §6, §19 | 08/11 | **Marco 1**: roda offline; nunca encerra por erro de entrada |
| A9 | `sistema.py --avaliar`: gera `testes/resultados.csv` (taxa da busca por tipo e por conjunto; tempo linear × índice com repetições) e `testes/comparacao_modelos.csv` (rubrica A × B) | §8, §14.2 | 09/11 | CSVs gerados e resumo impresso |
| A10 | Testes automatizados do núcleo (`testes/test_*.py`, `unittest`) | §14.2 | 09/11 | Suíte passa com `python -m unittest discover -s testes -t .` |
| A11 | `scripts/`: lista registros com data de verificação acima de 90 dias | §7.1 | 12/11 | Lista corretamente um registro antigo de exemplo |

## 3. Integrante B (Flávia): Bot e roteador

| Código | Atividade | Spec | Prazo | Critério de aceite |
|---|---|---|---|---|
| B1 | `testes/perguntas.json`: 14 perguntas (conjunto `equipe`), limites L1–L3 e extras (opção inexistente, `"???"`, texto longo). **Commit antes de A preencher `palavras_chave` e `sinonimos`** | §14.1 | 08/11 (cedo) | Formato `{id, conjunto, tipo, pergunta, esperado}`; tudo fictício; commit anterior ao das palavras-chave |
| B2 | Confirmar faturamento ativo do projeto da chave Gemini (AI Studio) | §12, §17 | 07/11 | Print/registro da confirmação para a equipe |
| B3 | Comparação A × B pela rubrica da spec §8: critérios automáticos + nota de clareza 1–5 (3 integrantes e a pessoa do teste de usabilidade, sem saber qual é o modelo) | §8 | 10/11 (notas até 15/11) | Tabela comparativa e modelo padrão escolhido (fecha item EM ABERTO) |
| B4 | `telegram_bot.py`: interface, `user_id`, `/localizacao`, `/painel`, `/apagar_meus_dados` | §9, §11 | 10/11 | Bot responde na VM |
| B5 | `roteador.py`: Gemini com function calling (4 ferramentas), validação estrita dos argumentos e fallback por regras | §9 | 10/11 | Com o Gemini desligado, o bot continua respondendo pelo fallback |
| B6 | UF: usa `referencias_estaduais[UF]`, senão gov.br com aviso; pergunta a UF uma vez | §11 | 10/11 | Teste com UF com e sem link estadual |
| B7 ✔ código pronto (08/11), falta teste real | `tarefas.py` e `agendador.py` (APScheduler persistente; executa jobs vencidos na subida) | §11 | 12/11 | Lembrete dispara após reiniciar o servidor |
| B8 ✔ código pronto (08/11), falta teste real | Autodestruição das mensagens com documento em 5 min (só < 48 h) | §11 | 12/11 | Mensagem apagada após 5 min, inclusive depois de reiniciar |
| B9 ✔ código pronto (08/11), falta teste real | `briefing.py`: até 3 manchetes RSS por tema, rótulo "não oficial"; feed com falha não derruba o briefing | §11 | 12/11 | Feeds por tema: **EM ABERTO** (decidir com a equipe) |
| B10 ✔ código pronto (08/11), falta teste real | Voz (transcrição), foto e PDF: oferecer "guardar no cofre?" | §9 | 12/11 | Conteúdo do arquivo nunca vira instrução |
| B11 | Teste de usabilidade com pessoa de fora da equipe, pelo roteiro de `docs/ux.md` §8 (+ SUS) | §14.2 | 15/11 | `testes/usabilidade.md` com tarefas, tempo, sucesso, dificuldades e nota SUS |
| B12 | Coletar perguntas do público (meta ≥ 10), **anônimas**, definir o `esperado` de cada uma e rodar **antes** de qualquer ajuste da busca | §14.1 | 14/11 | Perguntas no conjunto `publico` de `testes/perguntas.json`, sem dado pessoal; taxa "antes do ajuste" registrada |

## 4. Integrante C (Pedro): Cofre, painel e infraestrutura

| Código | Atividade | Spec | Prazo | Critério de aceite |
|---|---|---|---|---|
| C1 | **Teste de 15 min** DuckDNS + Caddy e leitura dos termos do DuckDNS | §12, §17 | 07/11 | Certificado emitido, ou plano B escolhido (Cloudflare quick tunnel ou máquina de um integrante) |
| C2 | Confirmar armazenamento (Supabase ou equivalente) e criar a interface de armazenamento | §5.2, §17 | 08/11 | Decisão registrada na spec; interface trocável |
| C3 | VM (Oracle Always Free), serviço `systemd` e `.env` somente na VM | §12 | 09/11 | Serviço reinicia sozinho após falha |
| C4 | GitHub Actions: deploy por SSH com chave dedicada e Secrets `HOST`, `USER`, `KEY` | §12 | 10/11 | Push na `main` atualiza a VM (Action verde) |
| C5 ✔ código pronto (08/11), falta teste real | `criptografia.py`: derivação da chave, AES-256-GCM e verificador de senha | §10.2 | 11/11 | Round-trip funciona; senha errada falha |
| C6 ✔ código pronto (08/11), falta teste real | `cofre.py`: salvar, listar e abrir filtrando por `user_id`; chave em memória com TTL | §10 | 11/11 | Usuário A não lê dados do B (teste) |
| C7 ✔ código pronto (08/11), falta teste real | `classificador.py`: Gemini sugere tipo e nome, com consentimento; em caso de falha usa `documento-AAAAMMDD` | §4.4, §10.3 | 11/11 | Funciona com a API desligada |
| C8 ✔ código pronto (08/11), falta teste real | `painel.py` e `painel/`: validação de `initData`, link de uso único, telas, apagar de verdade, cabeçalhos, CORS e rate limit | §10.4 | 12/11 | `initData` inválido é recusado (teste) |
| C9 | Testes de segurança: isolamento, criptografia, `initData`, expiração do desbloqueio | §14.2, §13 | 12/11 | Suíte de segurança passando |
| C10 ✔ código pronto (08/11), falta teste real | Aba "Perguntar" com a cena da verificação: `POST /api/perguntar` usando o núcleo (A4–A7), 4 saídas da decisão, "reduzir movimento", pergunta não gravada | §10.5 | 12/11 | Mesma pergunta dá a mesma resposta no terminal e no painel; com "reduzir movimento" não há animação |

## 5. Atividades da equipe toda

| Código | Atividade | Divisão sugerida | Prazo |
|---|---|---|---|
| E1 | **Redigir as 17 orientações** a partir das páginas oficiais, com data de verificação (spec §7.1: texto próprio, sem copiar) | A: `documentacao` (DOC-001 a 005) · B: `servicos` (SRV-001 a 006) · C: `direitos` (DIR-001 a 006) | 08/11 |
| E2 | Revisão cruzada da base: cada um revisa o tema de outro. Atenção a DOC-001, DOC-004, DIR-004, DIR-005 e DIR-006, e às justificativas das arestas novas DOC-001–DOC-003 e SRV-001–SRV-006 | A revisa `direitos`, B revisa `documentacao`, C revisa `servicos` | 09/11 |
| E3 | Revisar PRs: todo PR com 1 aprovação de outro integrante; revisão humana obrigatória do que toca segurança | Todos | contínuo |
| E4 | Reunião de 15 min a cada 2 dias até 13/11 | Todos | contínuo |
| E5 | Congelamento: rodar toda a suíte, revisar privacidade (§13), conferir que não há segredos no histórico do Git e criar a tag de versão | Todos | 13/11 |
| E6 | README (10 seções, §15.1) | A: 3, 4, 6 · B: 2, 5, 7 · C: 8 · Todos: 1, 9, 10 · **A consolida** | 16/11 |
| E7 | `docs/relatorio.pdf` (4–8 páginas, §15.2) | Cada um escreve a parte do seu módulo · **C consolida** | 17/11 |
| E8 | `docs/uso_ia.md` (§15.3) | Cada um registra o próprio uso de IA durante o trabalho · **B consolida** | 17/11 |
| E9 | Vídeo: cada integrante apresenta e explica o seu módulo; publicar como "Não Listado" e criar `docs/link_video.txt` | Todos | 18/11 |
| E10 | Enviar o `.txt` na FIAP ON com os 2 links e conferir o checklist da spec §18 | Todos | 19/11 |
| E11 | Revisar a UI ([`docs/ux.md`](ux.md) e wireframes) antes de implementar cada interface · **feito: design aprovado pela equipe em 07/11** | A: terminal · B: Telegram · C: painel | 08/11 |
| E12 | **Roadmap planejado (opcional, baixa prioridade):** consultar **uma única vez** na [Base dos Dados](https://basedosdados.org) alguns números públicos que justifiquem o problema e o impacto social no relatório (ex.: famílias inscritas no CadÚnico, eleitores por UF). O resultado entra só no relatório, com a fonte e a data da consulta citadas; **não entra no código** nem em `data/base.json` (spec §5.3 e §15.2) | C (com apoio de quem estiver livre) | Depois de 13/11, se sobrar tempo; até 17/11 |

---

## 6. Linha do tempo e dependências

```
06–07/11  A1 A2 A3 · B2 · C1 C2                     (esqueleto + decisões urgentes)
07–08/11  A4 A5 A6 A7 A8 · B1 · E1                  ► Marco 1: terminal offline com base preenchida (08/11)
08–09/11  A9 A10 · E2 · C3                           (testes do núcleo)
          (B1 precisa de commit ANTES das palavras-chave de E1)
09–10/11  B3 B4 B5 B6 · C4                           ► bot na VM com deploy automático (10/11)
10–11/11  C5 C6 C7                                    (cofre)
11–12/11  B7 B8 B9 B10 · C8 C9 · A11                 ► cofre e rotinas (12/11)
13/11     E5                                          ► código congelado
14–17/11  B11 B12 · E6 E7 E8                          ► indicadores e relatório (17/11)
18–19/11  E9 E10                                      ► entrega (19/11)
```

**Dependências principais:**
- A9 (`--avaliar`) depende de B1 (perguntas de teste) e de E1 (base preenchida).
- **E1 (palavras-chave e sinônimos) só começa depois do commit de B1** (protocolo contra viés, spec §14.1).
- B3 (comparação A × B) depende de A7 e A9.
- B4 e B5 dependem de C3 (VM) e de B2 (Gemini com faturamento).
- B8 (autodestruição) depende de C6 (cofre enviando documentos).
- C6 a C8 dependem de C2 (armazenamento decidido).
- **Regra de corte (13/11):** o que não estiver testado vira roadmap.

---

## 7. Como levar para o GitHub Projects (kanban)

- **Uma issue por código** (A1, B4, E1…), com título `[A4] busca.py: normalização, índice e pontuação` e, na descrição, a seção da spec e o critério de aceite.
- **Colunas:** Backlog → A fazer → Em andamento → Em revisão → Concluído.
- **Etiquetas:** `onda-1`, `onda-2`, `núcleo`, `bot`, `cofre-infra`, `dados`, `docs`, `segurança`, `em-aberto`.
- **Marcos (milestones):** Marco 1 (08/11), Bot na VM (10/11), Cofre e rotinas (12/11), Congelamento (13/11), Entrega (19/11).
- **Branches** por tarefa a partir da `main` (`feat/A4-busca`, `docs/E6-readme`); o PR cita a seção da spec e leva `Closes #<issue>`.

---

## 8. Itens EM ABERTO que bloqueiam tarefas

Estes itens são decisões humanas, não da IA (spec §17).

| Item | Bloqueia | Quem conduz |
|---|---|---|
| ~~Quem é A, B e C~~ (resolvido em 07/11) · suplentes | — | Equipe |
| Teste DuckDNS + Caddy | C3, C4, C8 | C |
| Armazenamento (Supabase ou equivalente) | C6, C7, C8, B7 | C |
| Faturamento do Gemini | B5, C7, B10 | B |
| Feeds RSS por tema e fuso horário padrão | B9, B7 | B |
| Modelo de resposta padrão (A ou B) | Default do produto | B, após os testes |
| Ferramenta para coletar perguntas do público de forma anônima | B12 | B |
| ~~Aprovar a aba "Perguntar"~~ (aprovada em 07/11) | — | — |
