# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href="https://www.fiap.com.br/">
  <img src="https://raw.githubusercontent.com/equipe1ccon/FIAP-PORTFOLIO-1CCON/master/assets/logo-fiap.png"
       alt="FIAP - Faculdade de Informática e Administração Paulista"
       width="40%">
</a>
</p>

<br>

<!--
=====================================================================
  ESQUELETO DO README: COMO PREENCHER (apagar este bloco antes da entrega)
---------------------------------------------------------------------
  - Este README junta o modelo da coordenação (FIAP-PORTFOLIO-1CCON,
    pasta GLOBAL-SOLUTION) com as 10 seções exigidas pelo enunciado,
    na ordem pedida.
  - Cada seção tem um comentário com o responsável, o prazo e o que
    escrever. Os responsáveis seguem docs/planejamento.md (atividade E6).
  - Textos marcados com "_A preencher_" ainda precisam ser escritos.
  - Prazo do README completo: 16/11/2026. Integrante A consolida.
  - Antes de entregar: apagar TODOS os comentários HTML (como este)
    e conferir o checklist da spec §18.
=====================================================================
-->

# Citizen Assist AI

Assistente de orientação cidadã **não oficial** que responde dúvidas sobre documentos, serviços públicos e direitos **somente com base em informações verificadas**, sempre citando a fonte oficial e avisando quando não há base suficiente para responder.

> Global Solution 2026.2 · Desafio CitizenTech

## Estado do projeto (atualizado em 09/11/2026, `main` até o PR #48)

> Resumo para quem está chegando agora. O detalhe de quem faz o quê está em [`docs/planejamento.md`](docs/planejamento.md) (seção "Status e onde parou"). Prazos: **código congelado em 13/11**, **entrega em 19/11**.

**Concluído e testado (Onda 1, núcleo avaliado pela GS):**

- Base com 17 registros em 3 temas, validada por `src/base.py` (arquivo ausente, vazio, JSON inválido, campos, ids duplicados e relacionados inexistentes). `--validar-entrega` passa.
- Busca por palavras-chave com pontuação, sinônimos, índice invertido e busca linear (mesmo resultado), regra de decisão com 4 saídas, correção de erro de digitação quando nada casa, grafo de temas e Dijkstra (`src/busca.py`).
- Modelos de resposta A e B, aviso de limitação e mensagens de entrada inválida (`src/respostas.py`).
- Terminal completo (`python src/sistema.py`), com cores e texto puro de reserva, `--validar-entrega` e `--avaliar`.
- Perguntas de teste da equipe congeladas antes das palavras-chave: **19/19 (100%)**; índice invertido cerca de 100 vezes mais rápido que a busca linear. Resultados em `testes/resultados.csv` e `testes/comparacao_modelos.csv`.
- **248 testes automatizados** (`python -m unittest discover -s testes -t .`), todos passando. O CI roda a suíte duas vezes: no Python 3.9 só com a biblioteca padrão (o que o avaliador usa) e no 3.12 com as bibliotecas do servidor, sem pular os testes do painel, cofre e bot.

**Concluído e testado no Telegram real (Onda 2, camada de produto), em 07/11:**

- Bot `@CitizenAssistAIBot` rodando localmente: `/start`, `/menu` (temas, assuntos e "Voltar aos temas"), perguntas por texto para os 17 assuntos, pergunta ambígua (candidatos em botões), entrada inválida, fora da base, erro de digitação, `/localizacao` (UF), `/apagar_meus_dados` (confirmação), botões de assuntos relacionados.
- **Voz:** o áudio é transcrito localmente pelo Whisper (`src/transcricao.py`), o bot avisa "Recebi seu áudio…" e depois mostra "Entendi: …". Testado com um áudio real em português.
- Roteador com cascata de modelos do Gemini: a IA só entra quando a base não resolve (fora da base) ou há pedido de cofre/tarefa/briefing; botões, perguntas respondidas e ambíguas **nunca** chamam a IA.

**Testado de ponta a ponta com o servidor local em 08/11 (PRs #42 a #44):**

- **Lembrete pelo chat:** "me lembra de pagar a luz amanhã às 9h" cria a tarefa (antes caía na busca e respondia a Tarifa Social de Energia; corrigido no PR #44). O aviso chega no Telegram na hora certa (o atraso de 39 min foi corrigido no PR #42).
- **Lembrete pelo painel local:** "daqui a 1 minuto" foi marcado como avisado pelo agendador no tick seguinte (cerca de 30 s depois). Lembrete criado para as 20:10 chegou no Telegram real às 20:10 e foi marcado como avisado no banco.
- **Desligar o servidor:** Ctrl+C agora encerra bot, painel e agendador juntos (PR #43). Se a porta 8000 estiver ocupada, o `--servidor` avisa e não sobe um segundo bot.
- Painel local: sem sessão ou com link vencido, a API responde 401 e a tela pede um novo link pelo `/painel`.

**Implementado em 08/11 (Onda 2), testado só por testes automatizados e no navegador local; nunca no Telegram real nem na VM:**

- **Criptografia e cofre** (`src/criptografia.py`, `src/cofre.py`): PBKDF2-SHA256 (600 mil iterações, salt por usuário), AES-256-GCM, verificador de senha, chave só na memória com validade de 10 min; nome e conteúdo cifrados; tudo filtrado por `user_id`.
- **Classificador** (`src/classificador.py`): o Gemini escolhe um tipo de uma lista fechada; o nome é montado pelo código, nunca copiado do texto do modelo; falha vira `documento-AAAAMMDD`.
- **Painel** (`painel/` + rotas em `src/painel.py`): abas Perguntar (cena da verificação), Tarefas (anotar, ver pendentes e concluir; o aviso chega pelo bot; botão protegido contra envio duplo), Cofre (criar, desbloquear, ver, apagar em dois passos) e Ajustes (UF, temas e horário do resumo). Conferido no navegador local; Mini App no Telegram real não.
- **Tarefas e agendador** (`src/tarefas.py`, `src/agendador.py`): lembretes com data lida por regras (fuso de Brasília) e autodestruição das mensagens com documento em 5 min. O estado fica no SQLite e o APScheduler só dispara o tick; assim, ao subir, o servidor cumpre o que venceu. Chat e painel usam as mesmas regras (`tarefas.tentar_criar`).
- **Resumo da manhã** (`src/briefing.py`, `data/feeds.json`): tarefas do dia + até 3 manchetes por tema, rotuladas "não oficial". O usuário escolhe entre 5 temas (Cultura, Tecnologia, Saúde e bem-estar, Música, Filmes); os feeds de cada um ficam em `data/feeds.json` e podem ser trocados sem mexer no código. A fonte de Filmes é fraca (reavaliar).
- **Foto/PDF e cofre no chat** (`src/documentos.py`, `src/telegram_bot.py`): cofre fechado não guarda nada (botão para o painel); consentimento do Gemini; nome confirmado ou editado; "me envie meu RG" envia e apaga em 5 min.

**Rascunho, precisa de revisão humana:**

- As 17 orientações de `data/base.json` foram redigidas pela IA a partir das páginas oficiais lidas em 07/11/2026 (todas com `data_verificacao` 2026-11-07). Cada orientação precisa ser conferida por um integrante (atividade E2 do planejamento). Pontos de atenção em `docs/uso_ia.md`.

**Pendente, por prioridade:**

1. **Antes do congelamento (13/11), Onda 1:** revisão humana das 17 orientações (E2) e links por estado da 2ª via da CIN (`referencias_estaduais` de DOC-001 está vazio; todos os estados caem no `gov.br`); conferir `python src/sistema.py` numa máquina limpa e no Windows.
2. **Indicadores (até 15/11):** perguntas do público (≥ 10, anônimas; hoje só existe o conjunto `equipe`) medidas **antes** de ajustar a busca; teste de usabilidade com pessoa de fora (`testes/usabilidade.md` está vazio); nota de clareza A × B (coluna `clareza_1a5` vazia). Só depois se escolhe o formato padrão (hoje o passo a passo é provisório).
3. **Onda 2, teste real:** no Telegram real (com documentos fictícios): foto/PDF, cofre pelo chat, resumo da manhã, Mini App (incluindo a aba Tarefas) e o botão "Sim, apagar tudo". O lembrete pelo chat já foi testado (08/11). `/painel` precisa de `PAINEL_URL` com https.
4. **Infraestrutura:** VM, DuckDNS/Caddy e deploy automático (nunca testados; o deploy só liga com `DEPLOY_ATIVO=true`); `ffmpeg` e Whisper na VM.
5. **Segurança:** `cryptography` atualizada para 50.0.2 em 08/11 (fecha os 6 alertas do Dependabot). Para atualizar um ambiente já criado: `.venv/bin/python -m pip install cryptography==50.0.2` (não use `pip install -r requirements.txt` fora do `.venv` nem antes do passo do Whisper, ver §6). Antes da VM, gerar **novo** token do bot e **nova** chave do Gemini (os de teste foram compartilhados fora do `.env`) e conferir o histórico do Git (busca feita em 08/11 não achou tokens).
6. **Decisões EM ABERTO:** fuso por usuário (hoje todos em America/Sao_Paulo), armazenamento definitivo (hoje SQLite; Supabase não foi adotado). Gemini no plano gratuito (decidido em 08/11; ver spec §12).
7. **Documentação e entrega:** seções 2, 8 e 10 escritas em 09/11 (revisar). Faltam o nome do grupo e os perfis da seção 1, o link da seção 9, "Participação na Competição", conferir o `docs/relatorio.pdf` (rascunho gerado em 09/11 por `scripts/gerar_relatorio.py`), o vídeo e `docs/link_video.txt`, e o `.txt` na FIAP ON.
8. **Roadmap planejado (opcional, baixa prioridade):** números de contexto da Base dos Dados para o relatório (ver seção 10, "Melhorias e roadmap").

Melhorias conhecidas que não bloqueiam a entrega:

- Sem `httpx` no `.venv`, 18 testes do painel e do cofre são pulados localmente (o CI roda todos). Para rodar tudo: `.venv/bin/python -m pip install httpx`.

---

## 1. Equipe

<!-- Responsável: todos (A consolida) · Prazo: 16/11 · Exigência do enunciado: nome da equipe e RMs -->

### Nome do grupo

_A preencher_

### 👨‍🎓 Integrantes

| Nome | RM | Frente no projeto | Perfil |
|---|---|---|---|
| Juan de Lucas Frois | RM563260 | Núcleo e dados (Integrante A) | <a href="">GitHub/LinkedIn</a> |
| Flávia Roberta Pennachin | RM561860 | Bot e roteador (Integrante B) | <a href="">GitHub/LinkedIn</a> |
| Pedro Valente | RM570394 | Cofre, painel e infraestrutura (Integrante C) | <a href="">GitHub/LinkedIn</a> |

### 👩‍🏫 Professores

**Tutor(a)**
- Lucas Gomes Jorge Gonçalez

**Coordenador(a)**
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi Chiovato</a>

---

## 2. Problema, público e temas

<!-- Responsável: Integrante B · Prazo: 16/11
     Escrever: o problema (informação dispersa, termos difíceis, instruções incompletas),
     quem é beneficiado e os 3 temas da base. Base: processo_desenvolvimento.md §A.1–A.3 e spec §1. -->

### O problema

Quem precisa de um documento ou serviço público costuma encontrar a informação espalhada em vários portais, com termos técnicos e instruções incompletas ou desatualizadas. Perguntas simples ("perdi meu RG, o que faço?") exigem abrir vários sites, e há risco de seguir um passo errado ou cair em páginas não oficiais.

O Citizen Assist AI responde **somente com orientações verificadas** (`data/base.json`), sempre com a fonte oficial e a data de verificação. Quando não há base suficiente, avisa e não inventa instrução. Não é um canal oficial de nenhum órgão.

### Público beneficiado

Cidadãos que precisam de orientação básica sobre documentos, serviços e direitos e têm pouca familiaridade com portais públicos: quem perdeu um documento, quem vai pedir um benefício, quem quer reclamar de uma empresa ou buscar ajuda jurídica gratuita. A linguagem é simples, e o assistente funciona no terminal (avaliação), no Telegram e em um painel web.

### Temas abordados

| Tema | Assuntos | Registros |
|---|---|---|
| Documentação pessoal | 2ª via da CIN/RG, CIN digital, 2ª via do título de eleitor, título cancelado, situação eleitoral | DOC-001 a DOC-005 |
| Serviços públicos | Meu INSS e 135, perícia médica, extrato CNIS, CadÚnico, Cartão Nacional de Saúde, Meu SUS Digital | SRV-001 a SRV-006 |
| Direitos e orientações comunitárias | Consumidor.gov.br, Defensoria Pública, Disque 100 e Ligue 180, certidão de nascimento gratuita, Juizado Especial Cível, Tarifa Social de Energia | DIR-001 a DIR-006 |

---

## 3. Base de conhecimento, estruturas e estratégia de busca

<!-- Responsável: Integrante A · Prazo: 16/11
     Escrever: formato de data/base.json e campos obrigatórios; como acrescentar/corrigir registros
     sem mexer no código; listas e dicionários usados; grafo de temas (relacionados) e Dijkstra;
     normalização, pesos, índice invertido × busca linear; De Morgan nos filtros; o que acontece com
     várias correspondências (desempate e pedido de escolha).
     Base: spec §7 e docs/arquitetura.md §5. -->

### Organização da base

Toda a base fica em `data/base.json`: `versao`, `temas`, `sinonimos` e `registros`. Cada registro tem `id`, `titulo` (opcional), `tema`, `palavras_chave`, `pergunta`, `orientacao`, `referencia`, `data_verificacao` e `relacionados`; os campos opcionais são `confirmar_antes`, `abrangencia` e `referencias_estaduais`. São 17 registros em 3 temas.

Para acrescentar ou corrigir um registro basta editar o JSON, sem mexer no código. Ao abrir, `src/base.py` valida tudo e, se algo estiver errado, o programa mostra uma mensagem clara e sai sem traceback. `python src/sistema.py --validar-entrega` confere se nenhum registro ficou como `PREENCHER` ou sem data de verificação. Na `orientacao`, cada linha vira um passo no formato passo a passo.

### Estruturas de dados utilizadas

- **Lista de registros** e **dicionário `por_id`** para recuperar um registro pelo id.
- **Dicionário de temas** (id do tema para nome) e **dicionário de sinônimos**, que vira grupos de equivalência nos dois sentidos.
- **Índice invertido**: palavra para `{id: campos onde aparece}`, montado uma vez na carga.
- **Lista de adjacência** (`id` para conjunto de ids) para o grafo de temas e **fila de prioridade** (`heapq`) para o Dijkstra.

### Estratégia de busca

1. **Normalização** (`normalizar`): minúsculas, sem acentos, sem pontuação e sem *stopwords* (palavras de função e verbos genéricos como "como", "quero", "tirar"). A mesma função vale para a pergunta e para os campos dos registros.
2. **Sinônimos**: cada palavra da pergunta é expandida com os sinônimos da base e pontua no máximo uma vez por campo.
3. **Pontuação**: palavra nas `palavras_chave` vale 3, na `pergunta` 2 e na `orientacao` 1. Se todas as palavras de uma palavra-chave composta (ex.: "segunda via") estão na pergunta, há um bônus de +2.
4. **Índice invertido × busca linear**: os dois dão o mesmo resultado; o índice só visita os registros que contêm alguma palavra da pergunta, e a busca linear varre todos (usada na comparação de desempenho).
5. **Filtros com De Morgan**: `incluir = not (fora_do_tema or ja_exibido)` é equivalente a `(not fora_do_tema) and (not ja_exibido)`. No menu de temas a pergunta é buscada só dentro do tema, e o assunto que acabou de ser exibido não volta em "Continue consultando".
6. **Várias correspondências**: ordena por pontuação, desempata pelo menor `id`; se o primeiro e o segundo ficam muito próximos, o programa pede ao usuário que escolha entre até 3 candidatos.

### Grafo de temas e navegação

O campo `relacionados` forma um grafo **não direcionado** (se A aponta para B, B também enxerga A). A aresta custa 1 entre assuntos do mesmo tema e 2 entre temas diferentes. O **Dijkstra** calcula o menor caminho (menu 2 do terminal) e escolhe os 3 assuntos mais próximos do que acabou de ser exibido, com os vizinhos diretos primeiro. Os 17 registros formam um único componente conexo; o caso "sem caminho" continua tratado no código para bases futuras.

### Fontes consultadas

<!-- Lista das fontes oficiais usadas na base, com a data de verificação. Pode ser gerada a partir do base.json. -->

| Registro | Fonte | Verificado em |
|---|---|---|
| DOC-001 (2ª via da identidade (CIN/RG)) | https://www.gov.br/secom/pt-br/acompanhe-a-secom/noticias/2026/02/saiba-como-solicitar-a-2a-via-da-cin-apos-caso-de-perda | 07/11/2026 |
| DOC-002 (CIN digital no app gov.br) | https://www.gov.br/gestao/pt-br/assuntos/noticias/2026/junho/governo-do-brasil-envia-notificacoes-personalizadas-sobre-o-uso-da-versao-digital-da-cin-saiba-como-usar | 07/11/2026 |
| DOC-003 (2ª via do título de eleitor) | https://www.tse.jus.br/comunicacao/noticias/2024/Janeiro/precisa-da-2a-via-do-seu-titulo-confira-como-emitir-em-apenas-3-passos | 07/11/2026 |
| DOC-004 (Título de eleitor cancelado) | https://www.tse.jus.br/comunicacao/noticias/2025/Dezembro/eleitor-em-dia-veja-como-regularizar-o-titulo-cancelado | 07/11/2026 |
| DOC-005 (Situação eleitoral) | https://www.tse.jus.br/comunicacao/noticias/2026/Abril/eleitor-em-dia-saiba-como-verificar-se-seu-titulo-esta-regular-1 | 07/11/2026 |
| SRV-001 (Meu INSS e telefone 135) | https://www.gov.br/inss/pt-br/canais_atendimento/meu-inss/meu-inss | 07/11/2026 |
| SRV-002 (Perícia médica do INSS) | https://www.gov.br/inss/pt-br/noticias/precisa-fazer-pericia-medica-confira-o-passo-a-passo-do-atestmed | 07/11/2026 |
| SRV-003 (Extrato CNIS e aposentadoria) | https://www.gov.br/pt-br/servicos/emitir-extrato-de-contribuicao-cnis | 07/11/2026 |
| SRV-004 (Inscrição no CadÚnico) | https://www.gov.br/pt-br/servicos/inscrever-se-no-cadastro-unico-para-programas-sociais-do-governo-federal | 07/11/2026 |
| SRV-005 (Cartão Nacional de Saúde) | https://www.gov.br/saude/pt-br/composicao/seidigi/meususdigital/perguntas-e-respostas/cidadao/9-como-faco-o-cartao | 07/11/2026 |
| SRV-006 (Meu SUS Digital) | https://www.gov.br/saude/pt-br/composicao/seidigi/meususdigital/perguntas-e-respostas/cidadao | 07/11/2026 |
| DIR-001 (Reclamar no Consumidor.gov.br) | https://www.consumidor.gov.br/pages/conteudo/publico/1 | 07/11/2026 |
| DIR-002 (Defensoria Pública) | https://www.dpu.def.br/noticias-institucional/233-slideshow/66949-saiba-como-a-defensoria-publica-da-uniao-pode-ajudar-voce | 07/11/2026 |
| DIR-003 (Disque 100 e Ligue 180) | https://www.gov.br/mdh/pt-br/ondh | 07/11/2026 |
| DIR-004 (Certidão de nascimento gratuita) | https://www.planalto.gov.br/ccivil_03/leis/l9534.htm | 07/11/2026 |
| DIR-005 (Juizado Especial Cível) | https://www.cnj.jus.br/cnj-servico-para-que-servem-os-juizados-especiais/ | 07/11/2026 |
| DIR-006 (Tarifa Social de Energia Elétrica) | https://www.gov.br/aneel/pt-br/assuntos/tarifas/tarifa-social | 07/11/2026 |

---

## 4. Regras de resposta, modelos de prompt e tratamento de limitações

<!-- Responsável: Integrante A (com B, que faz a comparação) · Prazo: 16/11
     Escrever: regra de decisão C·A·B (4 saídas); modelos A e B (papel, formato, obrigações e limites);
     resultado da comparação A × B e o modelo escolhido; aviso de limitação; o que o assistente nunca faz.
     Base: spec §7.3 e §8, docs/arquitetura.md §5.4. -->

### Regra de decisão

Variáveis: `C` = entrada válida (não vazia, com pelo menos uma palavra útil); `A` = melhor pontuação ≥ 3 (`LIMIAR_MINIMO`); `B` = diferença entre a 1ª e a 2ª pontuação ≥ 2 (`MARGEM`).

| C | A | B | Saída |
|---|---|---|---|
| 0 | - | - | Entrada inválida |
| 1 | 1 | 1 | Responder |
| 1 | 1 | 0 | Pedir escolha entre até 3 candidatos |
| 1 | 0 | - | Sem base (aviso de limitação) |

Esta tabela é a base do mapa de Karnaugh do relatório.

### Modelo A: direto e compacto

Um parágrafo com o título e a orientação, `Atenção:` quando exige confirmação, `Fonte:` com link e data, uma linha `Veja também:` com 3 assuntos e a frase de não-oficialidade. Papel: assistente de orientação cidadã não oficial. Limite: só o texto da base. Para o cidadão aparece como "resumido".

### Modelo B: estruturado em passos

Título do assunto, lista numerada de passos (cada linha da orientação), `Atenção:` quando exige confirmação, `Fonte:` com link e data, `Continue consultando:` com 3 assuntos e a frase de não-oficialidade. Limite: nunca cria passo que não esteja na orientação. Para o cidadão aparece como "passo a passo".

### Comparação entre os modelos

Os dois modelos formatam o **mesmo** resultado da busca; por isso taxa de acerto e tempo não servem para compará-los. Critérios objetivos medidos por `--avaliar` nas 11 perguntas que geram resposta (`testes/comparacao_modelos.csv`):

- Fonte com link e data: A 11/11, B 11/11.
- Relacionados para continuar: A 11/11, B 11/11.
- Tamanho médio: A 142,9 palavras, B 149,5 palavras. Passos numerados: A 0, B 4,6.

**Pendente:** a nota de clareza (1 a 5), dada pelos 3 integrantes e pela pessoa do teste de usabilidade sem saber qual é o modelo. O modelo padrão só será escolhido depois disso; no código o passo a passo (B) é provisório.

### Tratamento de limitações

Sem base suficiente, o assistente diz que não encontrou orientação verificada, que não é um canal oficial e que não vai inventar instruções, e aponta o portal https://www.gov.br e os temas disponíveis. Entrada vazia, só símbolos, opção inexistente e pergunta longa têm mensagem própria e o programa nunca encerra por erro de entrada. Toda resposta mostra fonte e data, e o aviso de confirmação quando aplicável.

---

## 5. Plano de testes, indicadores e resultados

<!-- Responsável: Integrante B · Prazo: 16/11 (indicadores fechados em 17/11)
     Escrever: as 14 perguntas + limites L1–L3 e o protocolo contra viés (perguntas congeladas antes
     das palavras-chave; conjunto do público coletado depois, anônimo); taxa de acerto da busca
     (geral, por tipo e por conjunto); tempo médio (linear × índice); rubrica A × B; teste de
     usabilidade; interpretação; pelo menos 2 melhorias; limitações da avaliação.
     Base: spec §8 e §14, testes/resultados.csv, testes/comparacao_modelos.csv, testes/usabilidade.md. -->

### Plano de testes

São 19 perguntas em `testes/perguntas.json`: 8 diretas, 3 reformuladas, 3 fora da base e 5 de limite (entrada vazia, consulta ambígua "documento", tópico sem base, só símbolos e texto longo). Todas são fictícias, sem dado pessoal. As perguntas da equipe foram **congeladas num commit antes** de preencher as palavras-chave (histórico do Git). O conjunto do público (≥ 10 perguntas anônimas) será coletado depois e medido **antes** de qualquer ajuste.

Testes automatizados: `python -m unittest discover -s testes -t .` (248 testes: base, busca, decisão, De Morgan, Dijkstra, respostas, sessões do terminal e avaliação, além do servidor, que só rodam com o ambiente do bot).

### Indicadores da busca

<!-- A taxa de acerto e o tempo medem a busca, que é a mesma para os modelos A e B (spec §8).
     Por isso não há coluna por modelo aqui; a comparação A × B fica na tabela seguinte. -->

| Indicador | Perguntas da equipe | Perguntas do público |
|---|---|---|
| Taxa de acerto | 100% (19/19) | pendente |
| Tempo médio (índice invertido) | 0,0069 ms | pendente |
| Tempo médio (busca linear) | 0,79 ms | pendente |

### Comparação dos modelos A e B

| Critério (spec §8) | Modelo A | Modelo B |
|---|---|---|
| Respostas com fonte e data | 11/11 | 11/11 |
| Aviso presente quando necessário | ver `comparacao_modelos.csv` | ver `comparacao_modelos.csv` |
| Tamanho médio (palavras) | 142,9 | 149,5 |
| Nota média de clareza (1–5) | pendente | pendente |

### Teste de usabilidade

**Pendente.** Roteiro de 5 tarefas em `docs/ux.md` §8, a ser aplicado a pelo menos uma pessoa de fora da equipe, com registro em `testes/usabilidade.md` e questionário SUS.

### Interpretação dos resultados

Na primeira medição, **antes de qualquer ajuste**, a busca acertou 17 de 19 perguntas da equipe. Os dois erros foram E02 ("carteira de identidade no celular", que caiu em DOC-001) e E14 ("imposto de renda", que caiu em DIR-006 por causa da palavra "renda" em "baixa renda"). Corrigimos as palavras-chave desses registros e chegamos a 19/19. Como a correção foi feita olhando essas perguntas, **os 100% do conjunto da equipe não são uma medida independente**; a medida honesta é a do conjunto do público, ainda pendente.

O índice invertido é cerca de 110 vezes mais rápido que a busca linear com 17 registros e cerca de 200 vezes com 1.700 e 17.000 registros sintéticos (cópias dos reais). Melhorias possíveis: correção ortográfica, mais sinônimos, ajuste de pesos com um conjunto maior e ampliação da base. Limitações da avaliação: poucas perguntas, escritas pela própria equipe, base pequena e cópias sintéticas na medição de escala.

---

## 6. 🔧 Como executar

<!-- Responsável: Integrante A · Prazo: 16/11
     Conferir os comandos numa máquina limpa antes da entrega. -->

### Pré-requisitos

- Python 3.9 ou superior para o modo terminal (o modo `--servidor` usa Python 3.11+).
- Nenhuma biblioteca externa, chave de API ou conexão com a internet é necessária para o modo terminal.

### Passo a passo

```bash
git clone https://github.com/JFrois/GlobalSolution_CitizenTech.git
cd GlobalSolution_CitizenTech
python src/sistema.py
```

### Outros modos

| Comando | O que faz |
|---|---|
| `python src/sistema.py --avaliar` | Roda as perguntas de teste e mostra taxa de acerto e tempo médio |
| `python src/sistema.py --validar-entrega` | Confere se todos os registros da base estão completos |
| `python src/sistema.py --simples` | Texto puro, sem cor nem molduras (leitores de tela); também automático com `NO_COLOR` ou saída redirecionada |
| `python src/sistema.py --base caminho.json` | Usa outra base JSON (para testes) |
| `python src/sistema.py --servidor` | Sobe o bot do Telegram e a API do painel (precisa de `.env` e do ambiente descrito abaixo), com o agendador de lembretes, autodestruição e resumo da manhã |
| `python -m unittest discover -s testes -t .` | Roda os testes automatizados |

### Rodar o bot (modo `--servidor`)

Use **Python 3.11 a 3.13** (no 3.14 o `pydantic-core` não compila). Exemplo no macOS:

```bash
python3.12 -m venv .venv && source .venv/bin/activate
# Voz (Whisper local): precisa do ffmpeg no sistema e de ser instalado ANTES do requirements.txt
brew install ffmpeg            # Linux: sudo apt install ffmpeg
pip install "setuptools<81" wheel && pip install --no-build-isolation openai-whisper==20240930
pip install -r requirements.txt   # sem o passo acima, falha com "No module named 'pkg_resources'"
pip install httpx                 # opcional: para rodar também os testes do painel
cp .env.example .env           # preencha TELEGRAM_BOT_TOKEN e, se quiser IA, GEMINI_API_KEY
python src/sistema.py --servidor
```

Para parar: **Ctrl+C** no terminal do servidor desliga o bot, o painel e o agendador juntos. Se aparecer "A porta 8000 já está em uso", ainda há um servidor rodando: `lsof -i :8000` mostra o número do processo.

Variáveis do `.env` (nomes em `.env.example`; **nunca** commitar o `.env`):

| Variável | Para quê |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Obrigatória. Token do @BotFather |
| `GEMINI_API_KEY` | Opcional. Sem ela o bot usa só as regras (sem IA) |
| `GEMINI_MODELO` | Opcional. Deixe vazio: o bot percorre os modelos que a chave enxerga |
| `WHISPER_MODELO` | Opcional (`tiny`, `base`, `small`, `medium`). Padrão `base` |
| `PAINEL_URL`, `PAINEL_PORTA` | Painel web. Sem `PAINEL_URL`, `/painel` responde "não está configurado". Porta padrão 8000 |

`python scripts/testar_gemini.py` confere a chave e lista os modelos. Se a porta 8000 estiver ocupada, o servidor avisa e sai (`lsof -i :8000` mostra o processo).

> Estado de cada parte: veja a seção "Estado do projeto" no início deste README.

---

## 7. Exemplos de uso

<!-- Responsável: Integrante B · Prazo: 16/11
     Copiar saídas reais do terminal (não inventar). Incluir: pergunta direta, reformulada,
     ambígua (pedir escolha), fora da base (aviso de limitação), entrada vazia e opção inexistente. -->

### Pergunta com resposta e fonte

```text
--------------------------------------------------------------------------------
Situação eleitoral
--------------------------------------------------------------------------------
1. No Autoatendimento Eleitoral do Portal do TSE, abra o menu "Consultas" e
   clique em "Situação do título".
2. Informe o número do título, o CPF ou o nome, e a data de nascimento. A
   consulta é gratuita e mostra pendências e como regularizar.
3. Também dá para consultar pela página principal do TSE, em "Situação
   eleitoral", no menu de serviços.
4. Para comprovar que está em dia, emita a certidão de quitação eleitoral:
   Portal do TSE, Serviços Eleitorais, Certidões. É gratuita.

Fonte:
  https://www.tse.jus.br/comunicacao/noticias/2026/Abril/eleitor-em-dia-saiba-como-verificar-se-seu-titulo-esta-regular-1
  (verificado em 07/11/2026)

Continue consultando:
  1  2ª via do título de eleitor
  2  Título de eleitor cancelado
  3  2ª via da carteira de identidade (CIN/RG)

Este assistente não é um canal oficial.

[1-3] abrir assunto  [m] menu  ou digite outra pergunta
A opção 0 não existe aqui. Escolha um dos números da lista.

[1-3] abrir assunto  [m] menu  ou digite outra pergunta
```

### Pergunta ambígua

```text
Encontrei mais de um assunto parecido. Qual deles você procura?

  1  2ª via da carteira de identidade (CIN/RG)
  2  2ª via do título de eleitor
  3  Título de eleitor cancelado

[1-3] escolher  [m] menu  ou reescreva a pergunta
A opção 0 não existe aqui. Escolha um dos números da lista.

[1-3] escolher  [m] menu  ou reescreva a pergunta
```

### Pergunta fora da base

```text
Não encontrei orientação verificada sobre isso na minha base.
Não sou um canal oficial e não vou inventar instruções.

Você pode consultar o portal oficial: https://www.gov.br
ou escolher um destes temas:

  1  Documentação pessoal
  2  Serviços públicos
  3  Direitos e orientações comunitárias

[1-3] ver tema  [m] menu  ou tente outra pergunta
A opção 0 não existe aqui. Escolha um dos números da lista.
Temas disponíveis:
  1  Documentação pessoal (5 assuntos)
  2  Serviços públicos (6 assuntos)
  3  Direitos e orientações comunitárias (6 assuntos)

[1-3] escolher tema  [m] menu
```

### Entradas inválidas

Entrada vazia, só símbolos e opção que não existe (o programa mostra a mensagem e continua):

```text
Você não digitou nada. Escreva sua dúvida com palavras ou escolha um número.
Não entendi. Tente com palavras, por exemplo: como consultar minha situação eleitoral.
A opção 7 não existe aqui. Escolha um dos números da lista.
```

---

## 8. Clareza, acessibilidade, privacidade e informação não oficial

<!-- Responsável: Integrante C · Prazo: 16/11
     Escrever: linguagem simples; o que o assistente não coleta; o que o produto (Onda 2) guarda
     e como protege (cofre, senha só no painel, criptografia); limites honestos (E2E só no painel,
     documentos passam pelo Gemini com consentimento); que não é canal oficial.
     Base: spec §10, §13 e docs/arquitetura.md §7. -->

### Clareza e acessibilidade

_A preencher_

### Privacidade

_A preencher_

### Informação não oficial

_A preencher_

---

## 9. 🔗 Vídeo de apresentação

<!-- Responsável: todos · Prazo: 18/11. Mesmo link de docs/link_video.txt. -->

* **[Vídeo de apresentação no YouTube (Não Listado)](http://url-aqui)**: _A preencher_

---

## 10. Conclusões, limitações e melhorias

<!-- Responsável: todos (A consolida) · Prazo: 16/11
     Escrever: o que funcionou; limitações (base pequena, perguntas feitas pela equipe, etc.);
     pelo menos 2 melhorias; itens que viraram roadmap na regra de corte de 13/11. -->

### Conclusões

O núcleo roda só com Python, offline e sem chaves. Acertou 19 de 19 perguntas da equipe (8 diretas, 3 reformuladas, 3 fora da base e 5 de limite), e o índice invertido é de 100 a 200 vezes mais rápido que a busca linear nos tamanhos testados. A resposta ao cidadão nunca é gerada livremente pela IA: o conteúdo vem sempre da base, com fonte e data. Sobre a camada de produto, o bot no Telegram, os lembretes e o roteador foram testados no Telegram real; cofre, foto/PDF, resumo da manhã e Mini App têm testes automatizados, mas ainda faltam testes reais (ver "Estado do projeto").

### Limitações

- **Base pequena:** 17 registros em 3 temas, escritos a partir das fontes oficiais e ainda sem revisão humana completa.
- **Avaliação enviesada:** as 19 perguntas foram escritas pela própria equipe. O conjunto do público (anônimo) e o teste de usabilidade ainda não foram aplicados, então 100% não deve ser lido como taxa de acerto geral.
- **Busca por palavras-chave:** não entende o sentido da frase. Perguntas muito diferentes das palavras-chave caem em "sem base".
- **Informação que muda:** taxas, prazos e regras mudam. Por isso cada resposta mostra a data de verificação e orienta a confirmar no site oficial.
- **Cofre e Gemini:** o Gemini usado é o plano gratuito, em que o Google pode usar o conteúdo enviado para melhorar produtos; o aviso de consentimento explica isso. Só E2E real existe no painel; no chat, o servidor vê o arquivo enquanto o cofre está desbloqueado.
- **Infraestrutura:** VM, HTTPS e deploy automático ainda não foram testados em produção.

### Melhorias e roadmap

<!-- Completar com o que virar roadmap na regra de corte de 13/11. -->

- **Ampliar sinônimos e palavras-chave** na base (hoje o `base.json` não tem sinônimos), medindo antes e depois com o conjunto do público.
- **Ampliar a base** com novos temas e registros (por exemplo CNH e CPF), mantendo a conferência na fonte oficial.
- **Detalhar os estados** em `referencias_estaduais` do DOC-001 e do que mais variar por UF.
- **Classificador de documentos local**, para não enviar arquivos ao Gemini.

- **Números de contexto para o relatório (planejado, opcional, baixa prioridade):** consultar uma única vez na [Base dos Dados](https://basedosdados.org) alguns números públicos que justifiquem o problema e o impacto social (ex.: famílias no CadÚnico, eleitores por UF). O resultado vai só para o relatório, com fonte e data citadas; não entra no código, porque a Base dos Dados exige `pip install`, BigQuery e internet (spec §5.3) e traz estatísticas, não orientações passo a passo.
- Ferramenta `consultar_site_oficial`, classificador de documentos local, CNH e CPF na base, fuso por usuário (spec §3 e §11).


---

## 📁 Estrutura de pastas

```text
GlobalSolution_CitizenTech/
├── README.md                 este arquivo
├── CLAUDE.md                 instruções para o Claude Code (importa a spec)
├── .env.example              nomes das variáveis do modo servidor, sem valores
├── requirements.txt          dependências do modo servidor (o terminal não precisa)
├── data/
│   └── base.json             base de conhecimento verificada
├── docs/
│   ├── especificacao/
│   │   └── CITIZEN_ASSIST_SPEC.md   especificação (fonte de verdade)
│   ├── processo_desenvolvimento.md  processo SDD e ciclo de vida
│   ├── planejamento.md       divisão de atividades e prazos
│   ├── arquitetura.md        arquitetura, fluxos e decisões
│   ├── ux.md                 interfaces, textos, acessibilidade e roteiro de usabilidade
│   ├── design/               identidade visual: tokens.css, tokens.json e imagens das telas
│   ├── uso_ia.md             registro do uso de IA
│   ├── relatorio.pdf         relatório final (4 a 8 páginas)
│   └── link_video.txt        link do vídeo no YouTube
├── src/                      código-fonte (python src/sistema.py)
├── testes/                   perguntas de teste, resultados e usabilidade
└── scripts/                  utilitários (ex.: registros com verificação antiga)
```

<!-- TODO: atualizar quando a estrutura final estiver pronta (painel/, .github/workflows/ etc.). -->

---

## 🧠 Decisões técnicas

As principais decisões e suas justificativas estão em [`docs/arquitetura.md`](docs/arquitetura.md) (seção 11) e na [especificação](docs/especificacao/CITIZEN_ASSIST_SPEC.md).

<!-- Opcional: resumir aqui as 3 ou 4 decisões mais importantes (ex.: resposta sempre vem da base;
     núcleo sem dependências; senha do cofre só no painel). -->

---

## 📢 Observações gerais

<!-- OBRIGATÓRIO pelo modelo da coordenação: a equipe precisa marcar uma das opções abaixo. -->

* **Participação na Competição:** [ ] Sim, aceitamos participar / [ ] Não vamos participar.
* **Uso de IA:** registrado em [`docs/uso_ia.md`](docs/uso_ia.md).
* **Aviso:** o Citizen Assist AI **não é um canal oficial** de nenhum órgão público. Confirme sempre as informações no site oficial indicado em cada resposta.

---

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/fiap-tutoria/FIAP-PORTFOLIO-AI">TEMPLATE - FIAP PORTFÓLIO AI</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">FIAP</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
