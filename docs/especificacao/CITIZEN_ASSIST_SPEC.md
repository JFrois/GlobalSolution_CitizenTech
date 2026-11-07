# Citizen Assist AI — Especificação final (GS 2026.2 · CitizenTech)

> **Para o Claude Code:** este arquivo é a **única fonte de verdade** do projeto (o `CLAUDE.md` da raiz apenas o importa; edite sempre este arquivo). Leia-o inteiro antes de escrever código. Tudo o que está aqui foi **aprovado pela equipe**. Onde aparecer **(sugestão)**, é detalhe de implementação que você pode ajustar sem perguntar; onde aparecer **(EM ABERTO)**, não decida sozinho: registre no código como `TODO` e avise o Juan.

- **Equipe:** grupo de 3 alunos da FIAP (definido em 07/11/2026):
  - **Integrante A — Juan de Lucas Frois (RM563260):** núcleo e dados.
  - **Integrante B — Flávia Roberta Pennachin (RM561860):** bot e roteador; testes e comparação A × B.
  - **Integrante C — Pedro Valente (RM570394):** cofre, painel e infraestrutura.
  - Mantenedor da VM em último caso: Juan.
- **Prazo de entrega na FIAP ON:** 19/11/2026. **Código completo até 13/11/2026.** De 14 a 19/11: testes finais, README, relatório PDF, vídeo e envio.
- **Regra de corte:** o que não estiver testado em 13/11 vira *roadmap* no README/relatório, não entra na demonstração.

---

## 1. Resumo do produto

**Citizen Assist AI** é um assistente de orientação cidadã que responde dúvidas sobre documentos, serviços públicos e direitos **somente com base em registros verificados** (`data/base.json`), sempre citando a fonte oficial e avisando quando não há base suficiente.

Ele existe em duas camadas:

1. **Núcleo (Onda 1 — é o que a GS avalia):** base de conhecimento, busca por palavras-chave com pontuação, grafo de temas com navegação e Dijkstra, modelos de resposta A e B, tratamento de entradas inválidas, testes e métricas. Roda **no terminal, offline, sem chaves**: `python src/sistema.py`.
2. **Camada de produto (Onda 2 — diferencial, a GS não avalia):** bot no Telegram multimodal (texto, voz, foto, PDF), roteador com LLM (Gemini, function calling), cofre de documentos criptografado, tarefas e lembretes, briefing matinal e painel web (Telegram Mini App ou navegador).

> **Princípio de projeto:** a resposta ao cidadão **nunca** é gerada livremente pelo LLM. O LLM só (a) decide qual ferramenta chamar e (b) sugere nome/tipo de documento do cofre. A voz é transcrita localmente pelo Whisper, sem LLM. O conteúdo da orientação vem sempre do `base.json`. Isso mantém a taxa de acerto mensurável e evita informação inventada.

---

## 2. Requisitos da Global Solution (o que não pode faltar)

Fonte: [`docs/Solicitação GS.md`](../Solicitação%20GS.md) (enunciado oficial). Fases 4, 5 e 6 são o foco; fases 1–3 apoiam.

### 2.1 Dados obrigatórios
- ≥ **15 registros** em ≥ **3 temas**. Cada registro: identificador, tema, pergunta/palavras-chave, orientação resumida, referência consultada, data de verificação. (Planejado: **17 registros, 3 temas**.)
- ≥ **12 perguntas de teste** (diretas, reformuladas, fora da base). (Planejado: **14**.)
- ≥ **3 situações-limite** (entrada vazia, consulta ambígua, ausência de resposta confiável).
- **Registro de resultados** dos testes: esperada × obtida × acerto/erro × tempo.

### 2.2 Requisitos técnicos
- Carregar a base de JSON em Python, listar temas, permitir **acrescentar/corrigir registros sem mexer nas regras do programa**, **validar campos** e tratar arquivo ausente/vazio/inconsistente.
- Listas e dicionários para recuperar por id, tema ou palavra-chave; busca por pergunta **ou** seleção de assunto por menu.
- Temas em **grafo simples**; navegação entre **≥ 3 assuntos relacionados** com opções de continuidade; explicar a estratégia de busca e o comportamento com várias correspondências.
- Condicionais e lógica para: pergunta válida, correspondência, ausência de orientação.
- **≥ 2 modelos de prompt/resposta** documentados e **comparados** nas perguntas de teste, justificando o melhor.
- Aviso de limitação quando não houver base; **nunca** inventar instrução nem se apresentar como canal oficial.
- Exibir resposta + fonte + aviso de "confirmar antes" quando aplicável; tratar entrada vazia, opção inexistente, sem correspondência; sugerir alternativas/assuntos relacionados.
- Calcular **taxa de acerto** e **tempo médio**; **teste de usabilidade** com ≥ 1 usuário ou roteiro de tarefas; interpretar indicadores; **≥ 2 melhorias**; limitações da avaliação.
- Não coletar dados pessoais desnecessários; não prometer integração com órgãos públicos.
- Uso de IA registrado em `docs/uso_ia.md` com validação crítica.

### 2.3 Arquivos obrigatórios no repositório (Tabela 2)
| Arquivo | Conteúdo |
|---|---|
| `README.md` | Estrutura de 10 seções (ver §15.1) |
| `src/sistema.py` | Funcional e **comentado**: consulta, exibição de referências, navegação, tratamento de entradas inválidas |
| `data/base.json` | ≥ 15 orientações, perguntas/palavras-chave, fontes, datas de verificação |
| `docs/relatorio.pdf` | 4–8 páginas (ver §15.2) |
| `docs/link_video.txt` | URL do YouTube ("Não Listado") |
| `docs/uso_ia.md` | Ferramentas de IA usadas, prompts testados, validação crítica |

O repositório deve seguir o **modelo da coordenação**: https://github.com/equipe1ccon/FIAP-PORTFOLIO-1CCON/tree/master — conferir a estrutura de pastas ao criar o repo.

### 2.4 Entrega na FIAP ON
Um `.txt` contendo **apenas** dois links: (1) repositório GitHub **público**; (2) vídeo no YouTube **Não Listado**.

### 2.5 Mapeamento dos conteúdos das fases (para o README e o relatório)
- **Fases 1–3:** listas, dicionários, booleanos, funções.
- **Fase 4:** grafos e **Dijkstra** (caminho mais curto entre assuntos no grafo `relacionados`). Regressão, limites e derivadas **não** são usados — não forçar.
- **Fase 5:** JSON/TXT, prompts e encadeamento, saídas estruturadas (function calling em JSON), **De Morgan** nos filtros de busca.
- **Fase 6:** métricas (taxa de acerto, tempo médio), comparação **busca linear × índice invertido de palavras-chave**, **mapa de Karnaugh** da regra de decisão (§7.3) no relatório, recursos.

---

## 3. Escopo por onda

| Onda | Módulos | Observação |
|---|---|---|
| **1 (core, avaliada)** | base, busca, grafo/Dijkstra, respostas A/B, `sistema.py` terminal, testes/métricas, docs | Prioridade absoluta. Deve estar 100% pronta e testada primeiro. |
| **2 (produto)** | bot Telegram, roteador Gemini, cofre + criptografia, classificador Gemini, painel/Mini App, tarefas/lembretes, briefing, autodestruição de mensagens, voz/foto/PDF | Todo o código entra até 13/11 (decisão da equipe). O que não for testado vira roadmap. |

**Fora do escopo (roadmap, não implementar):** ferramenta `consultar_site_oficial`; classificador de documentos local (sem enviar ao Gemini); CNH e CPF na base (entram na ampliação); integração com órgãos públicos; qualquer pagamento.

---

## 4. Decisões aprovadas (resumo)

1. **Interface:** Telegram + painel web. O painel abre como **Telegram Mini App** (login pelo `initData` assinado pelo Telegram) e também no **navegador** (link de uso único gerado pelo comando `/painel`).
2. **Senha do cofre:** criada e digitada **somente no painel web**. **Nunca** no chat do Telegram. O servidor não armazena a senha.
3. **Cofre:** arquivos **criptografados antes de armazenar**, com chave derivada da senha do usuário. Desbloqueio **temporário**: o servidor mantém a chave só em memória por tempo curto.
4. **Classificador de documentos:** os documentos do cofre **são enviados ao Gemini** (plano pago, com consentimento no upload) para reconhecer o tipo e sugerir o nome; o usuário confirma. Se a API falhar, usa nome padrão. Classificador local = roadmap.
5. **Autodestruição:** o bot apaga as mensagens com documentos após **5 minutos** (só mensagens com menos de 48 h).
6. **Localização:** o usuário informa apenas a **UF**; muda a qualquer hora com `/localizacao` ou no painel.
7. **Briefing matinal:** tarefas/lembretes do dia + até **3 manchetes por tema** escolhido pelo usuário, vindas de feeds RSS, **rotuladas "não oficial"** e **separadas** da base verificada.
8. **Base — tema 3:** Consumidor.gov.br, Defensoria Pública, Disque 100/Ligue 180, certidão de nascimento gratuita, Juizado Especial Cível e Tarifa Social de Energia.
9. **Hospedagem:** VM sempre ligada + **deploy automático** via GitHub Actions. HTTPS gratuito com DuckDNS + Caddy (depende de um teste de 15 min — §12).
10. **Cronograma:** tudo vai até 13/11; responsáveis das 3 frentes definidos em 07/11 (ver cabeçalho): A = Juan, B = Flávia, C = Pedro.
11. **(Aprovada pela equipe em 07/11) Aba "Perguntar" no painel/Mini App** com a **cena da verificação** (§10.5). Motivo: a crítica de design mostrou que o momento que mais encanta (ver a fonte sendo conferida) só existia no vídeo; o chat do Telegram não permite animação nem visual próprio.

---

## 5. Arquitetura

```
Usuário ──► Telegram ──► telegram_bot.py ──► roteador.py (Gemini + function calling; fallback por regras)
              │                                   │
              │                    ┌──────────────┼───────────────┬────────────────┐
              ▼                    ▼              ▼               ▼                ▼
        painel (Mini App)   buscar_orientacao  cofre_documento  gerenciar_tarefas  briefing_matinal
        painel.py (API)     busca.py+base.py   cofre.py         tarefas.py         briefing.py
                                   │              │
                                   ▼              ▼
                            data/base.json   storage (DB/arquivos)  ◄── toda consulta filtrada por user_id
                                               criptografia.py

agendador.py (APScheduler persistente): lembretes, briefing, exclusão de mensagens (na subida, executa as vencidas)
```

### 5.1 Estrutura do repositório
```
README.md
CLAUDE.md                   instruções do Claude Code; importa docs/especificacao/CITIZEN_ASSIST_SPEC.md
requirements.txt            dependências fixadas do modo --servidor (o terminal não precisa) (extra)
src/
  sistema.py                consulta no terminal (padrão); --servidor inicia bot, painel e agendador
  base.py                   carrega e valida data/base.json
  busca.py                  palavras-chave, pontuação, grafo de temas e Dijkstra
  respostas.py              modelos de prompt/resposta A e B e avisos de limitação
  roteador.py               LLM com function calling e regras de reserva           (extra)
  telegram_bot.py           interface, autorização e user_id                       (extra)
  painel.py                 API do painel web: listar, desbloquear, apagar, config (extra)
  cofre.py                  armazenamento criptografado, nome sugerido, envio      (extra)
  criptografia.py           chave derivada da senha do usuário e cifra de arquivos (extra)
  classificador.py          tipo do documento, via Gemini                          (extra)
  tarefas.py                lembretes e alertas                                    (extra)
  briefing.py               manchetes por tema e resumo matinal                    (extra)
  agendador.py              alertas, briefing e exclusão de mensagens              (extra)
  avaliacao.py              --avaliar: acerto, tempo, CSVs e comparação A x B
  servidor.py               modo --servidor: lê .env e sobe bot e painel           (extra)
  ponte.py                  liga o servidor ao núcleo (busca.py e respostas.py)    (extra)
  armazenamento.py          interface de armazenamento (SQLite local; Supabase = EM ABERTO) (extra)
data/
  base.json
docs/
  relatorio.pdf  link_video.txt  uso_ia.md          entregáveis da GS (Tabela 2)
  Solicitação GS.md                                  enunciado oficial
  especificacao/CITIZEN_ASSIST_SPEC.md               esta spec (fonte de verdade)
  processo_desenvolvimento.md  planejamento.md  arquitetura.md  ux.md
  design/                                            tokens.css, tokens.json e imagens da identidade (§19)
painel/                     front-end do painel web (HTML/JS estático)             (extra)
testes/                     perguntas (equipe e público), resultados.csv, comparacao_modelos.csv, usabilidade.md, test_*.py
scripts/                    lista registros com data de verificação antiga         (extra)
.env.example                só nomes das variáveis, sem valores                    (extra)
.github/workflows/deploy.yml
```

### 5.2 Stack
- **Python:** o **núcleo** (`base`, `busca`, `respostas`, `sistema` no modo terminal e `--avaliar`) precisa rodar em **Python 3.9 ou superior**, porque não sabemos qual versão o avaliador tem. A **Onda 2** usa **Python 3.11+** (só na VM). Núcleo usa **só biblioteca padrão** (`json`, `unicodedata`, `heapq`, `time`, `re`, `argparse`).
- **aiogram 3.x** (bot), **APScheduler** com jobstore persistente, **FastAPI/uvicorn** ou equivalente leve para o painel **(sugestão)**, `cryptography` para AES-GCM, `google-genai` para o Gemini, `feedparser` para RSS.
- **Armazenamento:** Supabase (DB + Storage) **ou equivalente** **(EM ABERTO: confirmar no início)**. Isole atrás de uma interface em `cofre.py`/`tarefas.py` para trocar sem reescrever.

### 5.3 Regra de import (crítica)
Bibliotecas de Telegram, servidor, Gemini, Supabase e `cryptography` são importadas **somente dentro do modo `--servidor`** (import tardio). `python src/sistema.py` precisa rodar numa máquina limpa, só com Python, **sem `pip install`, sem `.env`, sem internet**. É isso que o avaliador executa.

### 5.4 Portabilidade do núcleo
- Compatível com Python 3.9: usar `from __future__ import annotations` nos módulos que anotam tipos com `X | None` ou `list[str]`; não usar `match`/`case`.
- Se a versão for menor que 3.9, `sistema.py` mostra uma mensagem clara e sai (sem traceback).
- Caminhos (`data/base.json`, `testes/`) resolvidos a partir de `Path(__file__)`, nunca da pasta atual do terminal.
- Saída do terminal sem emoji e com linhas de até 80 colunas, para funcionar no console do Windows.
- **Identidade visual no terminal (decisão de 07/11):** cores ANSI e molduras com caracteres de caixa, **só com a biblioteca padrão**. Cores de 24 bits quando o terminal suporta (`COLORTERM=truecolor`), senão 16 cores aproximadas; no Windows 10+, ativar o modo de cores do console com `ctypes`. **Texto puro automático** quando a saída não é um terminal (`sys.stdout.isatty()` falso: `--avaliar`, testes, arquivo) ou quando existe a variável `NO_COLOR`; opção `--simples` força texto puro, sem cor e sem molduras (leitores de tela). A cor nunca é a única pista: `Atenção:` e `Fonte:` continuam escritos. Cartela de abertura **estática** (sem animação).

---

## 6. `src/sistema.py`

### 6.1 Modos
- `python src/sistema.py` → **modo terminal** (padrão). Menu interativo + pergunta livre, lendo `data/base.json`. Sem chaves, sem rede.
- `python src/sistema.py --servidor` → sobe bot, painel e agendador com variáveis do `.env`.
- `python src/sistema.py --avaliar` → roda as perguntas de `testes/` e imprime taxa de acerto e tempo médio **(sugestão)**.

### 6.2 Fluxo do terminal
1. Carrega e **valida** a base (campos obrigatórios; arquivo ausente, vazio, JSON inválido, ids duplicados, `relacionados` apontando para id inexistente → mensagem clara, sem traceback).
2. Menu (decisão de 07/11): o usuário **digita a pergunta direto** no menu principal (só dígitos = opção; qualquer outro texto = pergunta). Opções: `1` ver assuntos por tema · `2` ver o caminho entre dois assuntos · `3` formato da resposta (resumido = modelo A; passo a passo = modelo B) · `?` ajuda · `0` sair. Telas, textos e mensagens de erro em [`docs/ux.md`](../ux.md) §3.
3. Pergunta → busca (§7) → decisão (§7.3) → resposta no modelo A ou B (§8) com **fonte**, **data de verificação**, **aviso de confirmação** (se `confirmar_antes`) e **assuntos relacionados** como próximos passos numerados.
4. Tratamento: entrada vazia, opção inexistente, texto só com símbolos, pergunta sem correspondência, pergunta ambígua. Mensagens compreensíveis; o programa **nunca** encerra por erro de entrada.
5. Todo código **comentado em português** (a GS exige).

---

## 7. Base de conhecimento e busca

### 7.1 Esquema do registro (`data/base.json`)
```json
{
  "id": "DOC-001",
  "titulo": "2ª via da identidade (CIN/RG)",
  "tema": "documentacao",
  "palavras_chave": ["segunda via", "rg", "identidade", "cin", "perdi"],
  "pergunta": "Como solicitar a 2ª via da carteira de identidade (CIN/RG)?",
  "orientacao": "texto curto e claro, redigido pela equipe a partir da fonte oficial",
  "confirmar_antes": true,
  "abrangencia": "estadual",
  "referencia": "https://URL-oficial-consultada",
  "referencias_estaduais": { "SP": "https://portal-do-estado" },
  "data_verificacao": "2026-11-10",
  "relacionados": ["DOC-002", "SRV-004", "DIR-004"]
}
```
- Obrigatórios: `id`, `tema`, `palavras_chave`, `pergunta`, `orientacao`, `referencia`, `data_verificacao`, `relacionados` (pode ser lista vazia). Opcionais: `titulo` (nome curto do assunto, usado nas listas, nos botões do Telegram e como título da resposta; **até 36 caracteres**, para o botão não ficar cortado; se faltar, vale a `pergunta`), `confirmar_antes` (padrão `false`), `abrangencia` (`"nacional"`/`"estadual"`), `referencias_estaduais`.
- Estrutura do arquivo: `{ "versao": 1, "temas": {"documentacao": "Documentação pessoal", ...}, "sinonimos": { ... }, "registros": [ ... ] }`.
- `sinonimos` (opcional): dicionário `termo → [variações]`, por exemplo `{"identidade": ["rg", "cin"], "segunda": ["2a"]}`. Fica nos **dados**, não no código, para que a equipe melhore a busca sem mexer nas regras do programa (requisito da GS).
- **Passos da orientação:** `respostas.py` monta a lista de passos do Modelo B a partir da `orientacao`: se o texto tiver várias linhas (`\n`), cada linha é um passo; se for uma linha só, cada frase é um passo. Nunca se cria passo que não esteja no texto.
- **Regras de redação:** a orientação é escrita **pelas palavras da equipe**, após abrir e ler a página oficial (não copiar trechos). Sem valores de taxa fixos quando variam. Sempre com `data_verificacao` real.
- `scripts/` deve listar registros com `data_verificacao` antiga (> 90 dias).

### 7.2 Os 17 registros
Temas: `documentacao` (Documentação pessoal), `servicos` (Serviços públicos), `direitos` (Direitos e orientações comunitárias).

| ID | Assunto | Fonte (domínio) | Relacionados | Atenção |
|---|---|---|---|---|
| DOC-001 | 2ª via da CIN/RG, **por estado** | portal do estado + gov.br | DOC-002, DOC-003, SRV-004, DIR-004 | `abrangencia: estadual`; taxa varia por UF → **não fixar valor**; detalhar os estados da equipe, demais → link gov.br |
| DOC-002 | CIN digital no app gov.br | gov.br | DOC-001 | |
| DOC-003 | 2ª via do título de eleitor | tse.jus.br | DOC-001, DOC-004, DOC-005 | Aresta com DOC-001: o atendimento eleitoral pede documento oficial de identidade (**conferir no TSE ao redigir**) |
| DOC-004 | Título cancelado: como regularizar | tse.jus.br | DOC-003, DOC-005 | Serviços suspensos de 07/05/2026 a 02/11/2026 — a suspensão já terminou; **reconferir a situação atual no TSE antes de redigir** |
| DOC-005 | Consultar situação eleitoral | tse.jus.br | DOC-003, DOC-004 | |
| SRV-001 | Meu INSS e telefone 135 | gov.br/inss | SRV-002, SRV-003, SRV-004, SRV-006 | |
| SRV-002 | Agendar perícia médica | gov.br/inss | SRV-001 | |
| SRV-003 | Extrato CNIS e simulação de aposentadoria | gov.br/inss | SRV-001 | |
| SRV-004 | Inscrição no CadÚnico | gov.br/mds | DOC-001, SRV-001, DIR-006 | |
| SRV-005 | Cartão Nacional de Saúde | gov.br/saude | SRV-006 | |
| SRV-006 | Meu SUS Digital | gov.br/saude | SRV-005, SRV-001 | Aresta com SRV-001: os dois serviços digitais usam a mesma conta gov.br (**conferir ao redigir**) |
| DIR-001 | Reclamar de produto/serviço — Consumidor.gov.br | consumidor.gov.br | DIR-002, DIR-005 | A empresa tem 10 dias para responder |
| DIR-002 | Defensoria Pública | dpu.def.br + defensorias estaduais | DIR-001, DIR-003, DIR-004, DIR-005 | |
| DIR-003 | Disque 100 e Ligue 180 | gov.br/mdh e gov.br/mulheres | DIR-002 | **São serviços diferentes**; não misturar |
| DIR-004 | Certidão de nascimento gratuita | cnj.jus.br e gov.br/mdh | DIR-002, DOC-001 | 1ª via sempre gratuita; **2ª via só para quem não pode pagar** (Lei 9.534/97) |
| DIR-005 | Juizado Especial Cível | cnj.jus.br | DIR-001, DIR-002 | Até 40 salários mínimos; até 20 sem advogado |
| DIR-006 | Tarifa Social de Energia Elétrica | aneel.gov.br | SRV-004 | **Conflito de fontes:** inclusão via CadÚnico é automática ou exige pedido à distribuidora? Confirmar na ANEEL antes de redigir |

> **Grafo conexo (decisão de 07/11):** com as arestas DOC-001–DOC-003 e SRV-001–SRV-006, os 17 registros ficam num único componente; não existe mais par de assuntos "sem caminho" na base atual (o caso continua tratado no código, para bases futuras). Ao redigir, a equipe confirma se a justificativa de cada aresta nova está correta na fonte oficial; se não estiver, troca a aresta por outra que faça sentido, mantendo o grafo conexo.

> **Importante:** até aqui só foram lidos *snippets* de busca. A equipe precisa **abrir cada página oficial, ler e escrever a orientação** com a data de verificação. Gere `data/base.json` já com os 17 registros (ids, tema, palavras-chave, pergunta, `relacionados`, `referencia` com o domínio) e o campo `orientacao` marcado `"PREENCHER"` e `data_verificacao` vazia; o `base.py` deve **recusar** registros ainda não preenchidos ao validar em modo de entrega (`--validar-entrega`).

### 7.3 Algoritmo de busca (`busca.py`)
1. **Normalização:** minúsculas, remoção de acentos (`unicodedata`), remoção de pontuação, remoção de *stopwords* pt-BR (lista curta própria), tokenização. **A mesma normalização** é aplicada à pergunta do usuário e aos campos dos registros (`palavras_chave`, `pergunta`, `orientacao`).
   - *Stopwords* incluem palavras de função e **verbos genéricos** que aparecem em qualquer pergunta (ex.: `como`, `quero`, `preciso`, `fazer`, `tirar`, `onde`, `meu`, `minha`) **(sugestão; documentar a lista final)**.
   - **Sinônimos:** depois de normalizar, cada token do usuário é expandido com `sinonimos` do `base.json` (ex.: `rg` → também conta como `identidade`). Um token expandido pontua no máximo uma vez por campo.
   - **Palavras-chave com mais de uma palavra** (ex.: `"segunda via"`): cada token pontua normalmente; se **todos** os tokens da expressão aparecem na pergunta, o registro ganha um **bônus de expressão** (+2) **(sugestão de valor; documentar o usado)**.
2. **Índice invertido** `palavra → {id: peso}` construído na carga. Também manter a **busca linear** (varredura de todos os registros) para a comparação de desempenho do relatório (Fase 6).
3. **Pontuação** por registro: soma de pesos dos tokens da pergunta do usuário encontrados em `palavras_chave` (**3**), em `pergunta` (**2**) e em `orientacao` (**1**) **(sugestão de pesos; documentar os usados)**.
4. **Filtros com De Morgan:** os filtros de tema/exclusão são escritos na forma `not (A or B)` e equivalente `(not A) and (not B)`; mostrar a equivalência no código comentado e no relatório. **Onde o usuário vê o filtro:** (a) no menu `1`, depois de escolher um tema, a pergunta é buscada **só dentro desse tema**; (b) ao montar "Continue consultando", o registro que acabou de ser exibido é excluído. Exemplo: `incluir = not (fora_do_tema or ja_exibido)` ≡ `(not fora_do_tema) and (not ja_exibido)`.
5. **Várias correspondências:** ordenar por pontuação desc.; desempate por menor `id`.
6. **Regra de decisão** (variáveis booleanas):
   - `C` = entrada válida (não vazia, ≥ 1 token útil)
   - `A` = melhor pontuação ≥ limiar mínimo
   - `B` = (1ª pontuação − 2ª pontuação) ≥ margem
   - Resultado: **¬C → entrada inválida** · **C·A·B → responder** · **C·A·¬B → pedir escolha entre os candidatos** (top 3) · **C·¬A → sem base** (aviso de limitação + link do portal gov.br + temas disponíveis).
   - Esta tabela vira o **mapa de Karnaugh** do relatório. Limiar e margem ficam em constantes no topo do módulo.
7. **Grafo:** lista de adjacência montada de `relacionados` (tratar como **não direcionado** ao montar, para consistência).
8. **Dijkstra** (`heapq`): menor caminho entre dois ids; custo da aresta 1 (mesmo tema) ou 2 (temas diferentes) **(sugestão)**. Usado em "ver caminho entre dois assuntos" e para ordenar sugestões de continuidade. Retornar também o caso "sem caminho".
9. **Navegação:** após cada resposta, listar 3 relacionados como opções numeradas, **nos dois modelos** (A e B): os **3 registros mais próximos** pela distância de Dijkstra a partir do registro exibido (vizinhos diretos primeiro; se houver menos de 3, completa com os seguintes mais próximos, porque 6 registros têm só 1 vizinho direto). Quem monta a lista é `busca.py` (ordem) e quem a formata é `respostas.py` (texto), para que a comparação A × B meça só o formato.

---

## 8. Modelos de resposta/prompt (A e B)

Dois modelos documentados, comparados nos testes (clareza, consistência, presença de fonte/aviso). No modo terminal são **templates de texto**; no modo `--servidor` o LLM pode reescrever **apenas a forma**, sem alterar fatos, e a saída é validada (precisa conter a `referencia` e não conter URLs fora da base).

**Modelo A — direto/compacto:** papel: "assistente de orientação cidadã não oficial". Formato: 1 parágrafo curto + `Fonte: <url> (verificado em <data>)` + uma linha `Veja também: 1) … 2) … 3) …` com os relacionados (§7.3, item 9). Limite: se `confirmar_antes`, adicionar uma linha de aviso.

**Modelo B — estruturado em passos:** papel igual + obrigações: (1) título do assunto, (2) lista numerada de passos, (3) `Fonte:` com data, (4) `Atenção:` quando exigir confirmação, (5) `Continue consultando:` com os relacionados, (6) frase fixa de não-oficialidade. Limite: nunca inventar passo que não esteja na `orientacao`.

**Aviso de limitação (sem base):** "Não encontrei orientação verificada sobre isso na minha base. Não sou um canal oficial e não vou inventar instruções. Você pode consultar o portal oficial (https://www.gov.br) ou tentar um destes assuntos: …".

**Comparação (o que mede e o que não mede):** A e B são aplicados ao **mesmo** resultado da busca. Por isso a **taxa de acerto e o tempo de consulta são iguais nos dois modelos por construção** e não servem para compará-los; eles medem a **busca** (§14.2). A comparação A × B mede o **formato da resposta**, com uma rubrica aplicada às perguntas que geram resposta:

| Critério | Tipo | Como medir |
|---|---|---|
| Tem `Fonte:` com URL e data | objetivo (sim/não) | automático no `--avaliar` |
| Tem aviso quando `confirmar_antes` | objetivo (sim/não/não se aplica) | automático |
| Tem relacionados para continuar | objetivo (sim/não) | automático |
| Tamanho | objetivo (nº de palavras) | automático |
| Nº de passos | objetivo | automático |
| Clareza | nota 1–5 | leitura dos 3 integrantes **e** da pessoa do teste de usabilidade, sem saber qual é o modelo (rótulos trocados por X/Y) **(sugestão)** |

`--avaliar` grava os critérios automáticos em `testes/comparacao_modelos.csv` **(sugestão de nome)**; as notas de clareza entram numa coluna preenchida à mão. Justificar o modelo escolhido no relatório. **Default do produto:** o vencedor da comparação **(EM ABERTO até rodar os testes)**.

---

## 9. Roteador (modo `--servidor`)

- Gemini (plano **pago**) com **function calling**. O modelo recebe a mensagem (texto, ou transcrição de voz) e escolhe **uma** ferramenta:
  - `buscar_orientacao(pergunta: str)` → chama `busca.py` (determinístico) e responde com o Modelo B.
  - `cofre_documento(acao: "enviar"|"listar"|"abrir", nome?: str)` → ver §10.
  - `gerenciar_tarefas(acao, titulo?, quando?)` → criar/listar/concluir tarefas e lembretes.
  - `briefing_matinal(acao: "agora"|"configurar", temas?: list[str], hora?: str)`.
- **Validar** os argumentos retornados com esquema estrito; argumento inválido → ignorar e cair no fallback.
- **Fallback por regras** (palavras-chave simples) se o LLM falhar, estourar tempo ou devolver algo inválido. O bot nunca fica mudo.
- **Segurança contra injeção de prompt:** o LLM não executa nada além de escolher entre as 4 ferramentas; conteúdo de documentos/PDFs/fotos é tratado como **dado**, nunca como instrução.
- **Voz (decisão de 07/11):** transcrever **localmente com Whisper** (`src/transcricao.py`; modelo `base`, configurável por `WHISPER_MODELO`; exige `ffmpeg`) → mostrar "Entendi: …" → tratar como texto, no mesmo caminho do texto digitado (o Gemini só entra se a base não resolver). O áudio não sai da VM, não é gravado e o texto transcrito não é logado. Limite: 2 min / 10 MB. Sem Whisper ou `ffmpeg`, o bot avisa e pede para escrever. **Foto/PDF:** oferecer "guardar no cofre?" (fluxo §10) — não responder perguntas com base no conteúdo do arquivo.

---

## 10. Cofre, criptografia e painel

### 10.1 Princípios
- **Por que o cofre não fere a regra da GS de "não coletar dados pessoais desnecessários":** ele é opcional, só guarda o que o próprio usuário decide enviar, cifra antes de armazenar e permite apagar tudo (`/apagar_meus_dados`). O núcleo avaliado não coleta nada. Isso precisa estar explicado no README §8 e no relatório. **Demonstração, vídeo e testes usam somente documentos fictícios.**
- Dado do cidadão é **sensível**. Toda consulta ao armazenamento é filtrada por `user_id` (id do Telegram validado). Nunca confiar em `user_id` vindo do cliente sem validação do `initData`.
- A **senha nunca** trafega pelo chat do Telegram nem é gravada no servidor. Senha perdida = documentos perdidos (avisar na criação).

### 10.2 Criptografia **(sugestão de parâmetros; documentar os usados)**
- Derivação: **Argon2id** (ou PBKDF2-HMAC-SHA256 com ≥ 600 000 iterações se Argon2 não estiver disponível) com **salt aleatório por usuário** → chave de 256 bits.
- Cifra: **AES-256-GCM**, nonce aleatório de 96 bits por arquivo, nome do arquivo e metadados também cifrados ou, no mínimo, sem dados pessoais em claro.
- **Verificador de senha:** cifrar uma constante conhecida com a chave derivada e guardar; validar a senha decifrando-a. Nunca guardar hash reutilizável da senha em claro.
- Chave do usuário: só na **memória** do servidor, com **TTL curto** (ex.: 10 min) após desbloqueio no painel; expirou → o bot pede novo desbloqueio (botão que abre o painel).

### 10.3 Fluxos
- **Criar cofre:** usuário abre o painel → define senha (≥ 10 caracteres, aviso de irrecuperável) → servidor gera salt e verificador.
- **Enviar documento ("guardar isto"):** usuário manda foto/PDF ao bot → se o cofre está **bloqueado**, o bot **não guarda**: responde com botão "Desbloquear no painel" e pede para reenviar. Se desbloqueado → **aviso de consentimento** (primeira vez: o arquivo é enviado ao Gemini para reconhecer o tipo e sugerir um nome; mencionar retenção de logs de abuso e possível armazenamento em outros países) → Gemini sugere tipo/nome → usuário **confirma ou edita o nome** → arquivo criptografado e salvo. Falha do Gemini → nome padrão `documento-AAAAMMDD`.
- **Pedir documento ("me envie meu RG"):** roteador → `cofre_documento(abrir, "rg")` → se bloqueado, botão de desbloqueio; se desbloqueado, servidor decifra e **envia no chat** e agenda a **autodestruição** da mensagem em 5 min. Avisar que isso apaga do chat, não do aparelho, e que conversas com bots do Telegram **não** são de ponta a ponta.
- **Verdade sobre E2E:** enquanto o cofre está desbloqueado, o servidor vê o arquivo ao enviar. **E2E real existe apenas no painel** (decifrar no navegador com WebCrypto). Dizer isso no README e no relatório, sem exagerar.

### 10.4 Painel web
- Telas: **perguntar** (cena da verificação, §10.5) · criar/desbloquear cofre · listar documentos · visualizar · **apagar de verdade** (confirmação, remove arquivo e metadados) · configurar **UF** e **temas do briefing** · horário do briefing.
- **Login no Mini App:** validar `initData` (HMAC com token do bot, checar `auth_date` recente). **Login no navegador:** link de uso único e curta duração gerado por `/painel`.
- **HTTPS obrigatório** com certificado válido (certificado autoassinado é rejeitado pelo Telegram).
- Cabeçalhos de segurança, CORS restrito ao domínio do painel, sem `eval`, sem scripts de terceiros desnecessários, rate limit nas rotas de desbloqueio.

### 10.5 Aba "Perguntar" e cena da verificação **(aprovada pela equipe em 07/11)**
- **O que é:** primeira aba do painel. O cidadão digita a pergunta e vê a resposta "em cena":
  1. "Consultando 17 orientações verificadas", com os candidatos aparecendo;
  2. título e passos em sequência;
  3. o selo **"Fonte conferida"** com a data;
  4. os próximos assuntos (relacionados, §7.3 item 9).

  Visual e tempos em [`docs/ux.md`](../ux.md) §5 (tela P0) e §9 (movimento).
- **Funciona sem cofre e sem senha.** Exige só o login do painel (`initData` ou link de uso único), como as outras telas.
- **Conteúdo 100% da base:** a rota `POST /api/perguntar` chama `busca.buscar()` e devolve os dados do registro em **JSON estruturado** (título, passos, atenção, fonte, data, relacionados, decisão C·A·B). **Sem LLM** nessa rota. O front só desenha; não gera texto.
- **As 4 saídas da regra de decisão** (§7.3) têm tela própria: resposta (cena completa), pedir escolha (lista dos candidatos), sem base (aviso de limitação + gov.br + temas), entrada inválida (mensagem e exemplos).
- **Privacidade:** a pergunta **não é gravada** nem logada (§13.2 e §13.4). Rate limit na rota.
- **Acessibilidade:** com `prefers-reduced-motion`, a resposta aparece pronta, sem animação. A cena inteira dura no máximo ~3,2 s, e o texto pode ser lido assim que aparece.
- **Regra de corte:** se não estiver testada em 13/11, vira roadmap; a cena continua no vídeo como demonstração.

---

## 11. Tarefas, lembretes, briefing, UF, autodestruição

- **Tarefas/lembretes (`tarefas.py`):** título, data/hora (fuso do usuário **(EM ABERTO: assumir America/Sao_Paulo por padrão)**), status. Alertas via APScheduler **persistente**.
- **Briefing (`briefing.py`):** todo dia no horário configurado, envia (1) tarefas/lembretes do dia e (2) até **3 manchetes por tema** do usuário, de feeds RSS, com rótulo **"Notícias — fonte não oficial"**. Lista curada de feeds por tema **(EM ABERTO: equipe escolher 1–2 feeds por tema; preferir veículos públicos/governamentais)**. Falha de um feed não derruba o briefing.
- **UF:** `/localizacao` (teclado com UFs) ou painel. Ao responder um registro `abrangencia: estadual`, usar `referencias_estaduais[UF]` se existir; senão o link nacional gov.br e um aviso de que o procedimento varia por estado. Se a UF não foi informada, perguntar uma vez.
- **Autodestruição (`agendador.py`):** job por mensagem com documento, em 5 min. Só apaga mensagens com < 48 h (limite do Telegram). **Ao iniciar o servidor, executar exclusões vencidas** (persistência).
- **Privacidade:** coletar o mínimo — `user_id` do Telegram, UF, temas do briefing, tarefas, metadados do cofre. Comando `/apagar_meus_dados` remove tudo do usuário.

---

## 12. Hospedagem, HTTPS e deploy

- **Plano principal:** VM gratuita sempre ligada (**Oracle Cloud Always Free**). Atenção: em 2026 os limites foram reduzidos (~2 OCPU / 12 GB), há risco de **recuperação por ociosidade** (p95 de CPU/rede/memória < 20% por 7 dias) e de falta de capacidade na criação. **Plano B:** rodar na máquina de um integrante com **Cloudflare quick tunnel** (URL muda a cada reinício, sem SLA).
- **HTTPS gratuito:** subdomínio **DuckDNS** + **Caddy** (Let's Encrypt automático).
  - Caminho simples (HTTP-01, portas 80/443 abertas): `Caddyfile` → `seubot.duckdns.org { reverse_proxy localhost:8000 }`.
  - Alternativa DNS-01: build do Caddy com o plugin `duckdns` e `DUCKDNS_TOKEN`.
  - **Teste obrigatório de 15 min (EM ABERTO):** apontar o subdomínio, subir o Caddy e ver se o certificado emite. Também **ler os Termos/Privacidade do DuckDNS** (não verificados) e os limites do serviço.
- **Deploy automático (aprovado):** GitHub Actions em `push` na `main`, `appleboy/ssh-action`, **chave SSH de deploy dedicada**, secrets `HOST`, `USER`, `KEY` no GitHub Secrets; o script na VM faz `git pull` e reinicia o serviço (`systemd`).
- **Segredos:** o `.env` fica **somente na VM** e **nunca** entra no repositório. O repo é público e contém apenas `.env.example`. Variáveis **(sugestão de nomes)**: `TELEGRAM_BOT_TOKEN`, `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, `PAINEL_URL`, `SESSAO_SEGREDO`, `DUCKDNS_TOKEN`.
- **Gemini:** a chave **deve pertencer a um projeto com faturamento ativo** (plano pago). No plano gratuito os dados podem ser usados para melhoria de produto. Conferir no AI Studio. No plano pago, o Google não usa prompts/arquivos/respostas para treinar produtos, mas **mantém logs por período limitado para monitoramento de abuso** (fontes secundárias citam ~55 dias) e pode armazenar em qualquer país. O usuário é avisado antes do primeiro upload.
- Rodar como serviço `systemd` com reinício automático; logs **sem** conteúdo de documentos nem tokens.

---

## 13. Segurança e privacidade — regras que valem para todo o código

1. Nunca commitar segredos. `.gitignore` com `.env`, `*.key`, `__pycache__`, bancos locais.
2. Nunca logar token, chave, senha, conteúdo/nome de documentos nem texto completo de mensagens.
3. Toda leitura/escrita de dados de usuário filtrada por `user_id`; testes cobrindo que o usuário A não lê dados do B.
4. O núcleo não pede nem armazena dado pessoal (CPF, RG, endereço). Se o usuário digitar, **não persistir**.
5. Não se apresentar como canal oficial; toda resposta carrega a fonte e a data; quando aplicável, "confirme no site oficial".
6. Conteúdo de arquivos enviados é dado, nunca instrução (injeção de prompt).
7. Respostas de LLM validadas contra a base antes de ir ao usuário.
8. Dependências fixadas em `requirements.txt` (versões); `requirements.txt` não é necessário para o modo terminal.
9. Mensagens de erro ao usuário são claras e não vazam stack trace.

---

## 14. Testes, métricas e usabilidade

### 14.1 Perguntas de teste
Arquivo `testes/perguntas.json` com `{id, conjunto, tipo, pergunta, esperado}`; `conjunto` = `"equipe"` ou `"publico"`; `esperado` = id do registro ou `"SEM_BASE"` / `"PEDIR_ESCOLHA"` / `"INVALIDA"`. Todas **fictícias**, sem dado pessoal.

**Protocolo contra viés (decisão de 07/11):**
1. **Conjunto da equipe:** as 14 perguntas abaixo + limites são escritas pela equipe e **congeladas num commit antes** de preencher as `palavras_chave` e os `sinonimos` da base. O histórico do Git prova a ordem. Depois de congeladas, não se muda o texto de uma pergunta para ela acertar.
2. **Conjunto do público:** depois, a equipe coleta perguntas de pessoas de fora (meta: ≥ 10) **(sugestão)**, de forma **anônima**: só o texto da pergunta, sem nome, e-mail, telefone ou qualquer dado pessoal. Se alguém escrever um dado pessoal no texto, a pergunta é descartada ou anonimizada antes de entrar no repositório. A equipe define o `esperado` de cada uma **antes** de rodar o sistema.
3. **Medição:** a taxa de acerto do conjunto do público é medida **antes** de qualquer ajuste de pesos, palavras-chave ou sinônimos. Se a equipe ajustar depois, reporta as duas medidas (antes e depois), deixando claro que a segunda já não é independente.
4. Os dois conjuntos são reportados **separadamente** no README e no relatório; a diferença entre eles é discutida nas limitações.

As 14 perguntas do conjunto da equipe **(ajustar só antes do congelamento)**:

| # | Tipo | Pergunta | Esperado |
|---|---|---|---|
| 1 | direta | Como tirar a segunda via do RG? | DOC-001 |
| 2 | direta | Como ter a carteira de identidade no celular? | DOC-002 |
| 3 | direta | Como pedir segunda via do título de eleitor? | DOC-003 |
| 4 | direta | Meu título foi cancelado, o que faço? | DOC-004 |
| 5 | direta | Como consultar minha situação eleitoral? | DOC-005 |
| 6 | direta | Como acessar o Meu INSS? | SRV-001 |
| 7 | direta | Como me inscrever no CadÚnico? | SRV-004 |
| 8 | direta | Como reclamar de uma empresa no Consumidor.gov.br? | DIR-001 |
| 9 | reformulada | Perdi minha identidade, como faço outra? | DOC-001 |
| 10 | reformulada | Quero marcar perícia do INSS | SRV-002 |
| 11 | reformulada | Não tenho dinheiro para advogado, onde busco ajuda? | DIR-002 |
| 12 | fora da base | Como pagar o IPVA? | SEM_BASE |
| 13 | fora da base | Como abrir um MEI? | SEM_BASE |
| 14 | fora da base | Como declarar o imposto de renda? | SEM_BASE |

**Testes de limite (≥ 3):** (L1) entrada vazia `""` → INVALIDA; (L2) consulta ambígua `"documento"` → PEDIR_ESCOLHA com candidatos; (L3) tópico sem base `"como tirar passaporte?"` → SEM_BASE com link gov.br e sem inventar passos. Extras úteis: opção de menu inexistente, só símbolos `"???"`, texto muito longo.

### 14.2 Indicadores
- **Taxa de acerto da busca** = acertos ÷ total × 100 (exemplo da GS: 10/12 = 83,3%). Calcular: geral, por **tipo** (direta/reformulada/fora da base/limite) e por **conjunto** (equipe × público). Não se calcula por modelo (ver §8).
- **Tempo de consulta** = média (e máx.) de `time.perf_counter()` em ms, repetindo cada consulta várias vezes (ex.: 1 000) para reduzir ruído; comparar **busca linear × índice invertido**. Com só 17 registros a diferença tende a ser pequena; para mostrar o efeito do tamanho da base, repetir a medição com uma base sintética ampliada (ex.: registros copiados até 1 700 e 17 000) **(sugestão)**.
- `--avaliar` grava `testes/resultados.csv` (conjunto, id, tipo, pergunta, esperado, obtido, acerto/erro, tempo índice ms, tempo linear ms) e `testes/comparacao_modelos.csv` (§8), e imprime o resumo.
- **Usabilidade:** roteiro de 5 tarefas definido em [`docs/ux.md`](../ux.md) §8 (2ª via do título, abrir relacionado, pergunta sem base, achar assunto pelo menu, trocar o formato) com ≥ 1 pessoa de fora da equipe; registrar sucesso, tempo, erros e pedidos de ajuda em `testes/usabilidade.md`. Ao final, questionário **SUS** (0–100) como indicador de facilidade de uso **(sugestão)**.
- **Interpretar:** o que acertou/errou e por quê; **≥ 2 melhorias** (ex.: sinônimos/ajuste de pesos, correção ortográfica, ampliar a base); **limitações da avaliação** (poucas perguntas, feitas pela própria equipe, base pequena).
- **Testes automatizados** (`testes/test_*.py`, com `unittest`; rodar com `python -m unittest discover -s testes -t .`): validação da base (ausente/vazia/inconsistente), normalização, busca, decisão (4 saídas), Dijkstra, isolamento por `user_id`, cripto (round-trip; senha errada falha), validação do `initData`.

---

## 15. Documentação a entregar

### 15.1 README (10 seções, nesta ordem)
1. Nome da equipe e RMs · 2. Problema, público e temas · 3. Organização da base, estruturas e estratégia de busca · 4. Regras de resposta, modelos de prompt A/B e tratamento de limitações · 5. Plano de testes, indicadores, resultados e interpretação · 6. **Como executar: `python src/sistema.py`** (e como rodar `--servidor`/`--avaliar`) · 7. Exemplos de perguntas, respostas com fontes e entradas inválidas · 8. Clareza, acessibilidade, privacidade e informação não oficial · 9. Link do vídeo · 10. Conclusões, limitações e melhorias.

### 15.2 `docs/relatorio.pdf` (4–8 páginas)
Problema · público · arquitetura (diagrama §5) · fontes · estratégias de prompt (A × B) · resultados dos testes · indicadores · Karnaugh da decisão · comparação linear × índice · limitações · impacto social · privacidade e limites do cofre (honestidade sobre E2E e Gemini).

### 15.3 `docs/uso_ia.md`
Ferramentas usadas (Claude, Claude Code, Gemini no produto), prompts testados, o que foi aceito/rejeitado, **validação crítica** (conferência de cada orientação contra a fonte oficial; testes comparando resposta × base).

### 15.4 Vídeo e envio
Vídeo no YouTube **Não Listado**: demo do terminal (`python src/sistema.py`) + busca, relacionados, entrada inválida, sem base, métricas; depois a camada Telegram/painel. Salvar a URL em `docs/link_video.txt`. `.txt` da FIAP ON com **só os dois links**.

---

## 16. Ordem de implementação (até 13/11)

Faça nesta ordem e **faça commit a cada marco**. Não avance sem os testes do marco passando.

1. **06–07/11 — Esqueleto + base:** estrutura de pastas, `.gitignore`, `.env.example`, `data/base.json` com os 17 registros (esqueleto), `base.py` com validação completa.
2. **07–08/11 — Busca e grafo:** `busca.py` (normalização, índice, pontuação, decisão, grafo, Dijkstra), `respostas.py` (A e B), `sistema.py` terminal completo. **Marco 1: o terminal funciona offline com a base preenchida.**
3. **08–09/11 — Testes do núcleo:** `testes/perguntas.json`, `--avaliar`, resultados CSV, testes automatizados.
4. **09–10/11 — Servidor base:** `telegram_bot.py`, `roteador.py` (+ fallback), `/localizacao`, `/painel`, `/apagar_meus_dados`. Deploy automático na VM funcionando (workflow + `systemd` + Caddy/HTTPS).
5. **10–11/11 — Cofre:** `criptografia.py`, `cofre.py`, `classificador.py`, `painel.py` + front `painel/` (Mini App e navegador), desbloqueio temporário, apagar de verdade. Aba "Perguntar" com a cena da verificação (§10.5).
6. **11–12/11 — Rotinas:** `tarefas.py`, `agendador.py` (lembretes + autodestruição persistente), `briefing.py`, voz/foto/PDF.
7. **13/11 — Congelar:** rodar toda a suíte, revisar privacidade (§13), limpar logs/segredos, tagar versão. Itens não testados → roadmap.

---

## 17. Pendências em aberto (precisam de decisão humana)

- ~~Responsáveis pelas 3 frentes~~ — **resolvido em 07/11** (ver cabeçalho). Suplentes: a definir.
- **Quem mantém a VM no ar:** a definir; Juan assume em último caso.
- **Teste de 15 min do DuckDNS + Caddy** (HTTP-01 com subdomínio DuckDNS) e leitura dos Termos/Privacidade do DuckDNS; se falhar → Cloudflare quick tunnel ou máquina de um integrante.
- **Confirmar faturamento ativo** do projeto da chave do Gemini no AI Studio.
- **Revisar as 17 orientações** (rascunho feito em 07/11 a partir das páginas oficiais, falta conferência humana) — em especial DOC-001 (UFs da equipe), DOC-004 (reconferir suspensões do TSE), DIR-006 (conflito de fontes) e DIR-004/DIR-005 (limites).
- Armazenamento: confirmar Supabase ou equivalente.
- Feeds RSS por tema e fuso horário padrão.
- Modelo de resposta padrão (A ou B), definido pelos testes.
- Ferramenta para coletar as perguntas do público de forma anônima (§14.1).
- ~~Aprovar a aba "Perguntar"~~ — **aprovada pela equipe em 07/11** (§10.5).
- ~~Identidade visual~~ — **resolvido em 07/11:** direção **Estreia clara** ([`docs/ux.md`](../ux.md) §9). Manual de marca e telas aprovados pela equipe em 07/11.

---

## 18. Definição de pronto (checklist final)

- [ ] `python src/sistema.py` roda numa máquina limpa, sem chave e sem internet, sem erros. (07/11: roda em Python 3.9 e 3.14 sem dependências; falta conferir numa máquina limpa e no Windows)
- [ ] 17 registros preenchidos, com fonte e `data_verificacao` reais, 3 temas. (07/11: rascunho escrito pela IA com as páginas oficiais; falta a revisão humana de cada um)
- [ ] ≥ 12 (planejado 14) testes + ≥ 3 limites executados; taxa de acerto e tempo médio da busca calculados (equipe e público); comparação A × B pela rubrica (§8). (07/11: equipe feito, 19/19; faltam o conjunto do público e a nota de clareza)
- [x] Entrada vazia, opção inexistente, sem correspondência e ambiguidade tratadas com mensagem clara. (07/11: testado)
- [x] Navegação por relacionados (≥ 3 assuntos) e Dijkstra funcionando. (07/11: testado)
- [ ] README com as 10 seções; relatório 4–8 páginas; `uso_ia.md`; `link_video.txt`.
- [ ] Repositório público, sem segredos (verificar histórico do Git).
- [ ] Vídeo Não Listado; `.txt` com os dois links enviado na FIAP ON.
- [ ] Onda 2: cofre testado com senha errada, expiração de desbloqueio e isolamento por usuário; ou movida para o roadmap.

---

## 19. Interface e experiência do usuário

Detalhe completo (telas, textos, mensagens, acessibilidade, roteiro de usabilidade) em [`docs/ux.md`](../ux.md). Decisões aprovadas em 07/11:

1. **Três interfaces definidas antes do código:** terminal (Onda 1, avaliado), bot no Telegram e painel web/Mini App (Onda 2).
2. **Terminal:** cores e molduras da identidade com texto puro como reserva (§5.4); pergunta digitada direto no menu; menu `1` temas · `2` caminho · `3` formato · `?` ajuda · `0` sair; escolha de assuntos sempre **por número**, nunca por id; a última linha de cada tela mostra as teclas válidas; `Ctrl+C` e fim de entrada saem sem traceback.
3. **Modelos A e B para o cidadão:** aparecem como **"Formato da resposta: resumido ou passo a passo"**. Os nomes A/B ficam no README, no relatório e nos testes.
4. **Vocabulário único** nas 3 interfaces ("assunto", "tema", "fonte", "verificado em", "cofre", "desbloquear"); ids e termos técnicos nunca aparecem para o usuário.
5. **Ordem fixa da resposta:** conteúdo → `Atenção:` (se houver) → `Fonte:` com data → assuntos para continuar → frase de não-oficialidade.
6. **Telegram:** escolhas por botões; áudio mostra a transcrição antes da resposta; UF perguntada só quando a resposta depende do estado; o bot nunca fica mudo.
7. **Painel:** celular primeiro (uma coluna, até 480 px); no Mini App usa as cores e botões nativos do Telegram; contador visível de bloqueio do cofre; apagar em dois passos.
8. **Acessibilidade mínima:** contraste WCAG AA, toque ≥ 44 px, texto 16 px, nada indicado só por cor, linguagem simples, terminal com até 80 colunas e sem emoji.
9. **Identidade visual "Estreia clara" (decisão de 07/11):** base híbrida (leitura em claro, momentos de cinema em escuro), paleta âmbar e ciano, Archivo condensada nos títulos e Atkinson Hyperlegible no texto. Tokens e regras em [`docs/ux.md`](../ux.md) §9; manual de marca completo no link registrado lá.
10. **Cena da verificação no produto (§10.5):** aba "Perguntar" no painel/Mini App, com o mesmo núcleo do terminal.
11. **Metas de aprendizado** (medidas no teste de usabilidade): primeira resposta útil em < 1 min; ≥ 4 de 5 tarefas sem ajuda.
