# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href="https://www.fiap.com.br/">
  <img src="https://raw.githubusercontent.com/equipe1ccon/FIAP-PORTFOLIO-1CCON/master/assets/logo-fiap.png"
       alt="FIAP - Faculdade de Informática e Administração Paulista"
       width="40%">
</a>
</p>

<br>

# Citizen Assist AI

Assistente de orientação cidadã **não oficial** que responde dúvidas sobre documentos, serviços públicos e direitos **somente com base em informações verificadas**, sempre citando a fonte oficial e avisando quando não há base suficiente para responder.

> Global Solution 2026.2 · Desafio CitizenTech

## Estado do projeto (atualizado em 09/11/2026, `main` até o PR #52)

> Resumo para quem está chegando agora. O detalhe de quem faz o quê está em [`docs/planejamento.md`](docs/planejamento.md) (seção "Status e onde parou"). Prazos: **código congelado em 13/11**, **entrega em 19/11**.

**Concluído e testado (Onda 1, núcleo avaliado pela GS):**

- Base com 17 registros em 3 temas, validada por `src/base.py` (arquivo ausente, vazio, JSON inválido, campos, ids duplicados e relacionados inexistentes). `--validar-entrega` passa.
- Busca por palavras-chave com pontuação, sinônimos, índice invertido e busca linear (mesmo resultado), regra de decisão com 4 saídas, correção de erro de digitação quando nada casa, grafo de temas e Dijkstra (`src/busca.py`).
- Modelos de resposta A e B, aviso de limitação e mensagens de entrada inválida (`src/respostas.py`).
- Terminal completo (`python src/sistema.py`), com cores e texto puro de reserva, `--validar-entrega` e `--avaliar`.
- Perguntas de teste da equipe congeladas antes das palavras-chave: **19/19 (100%)**; índice invertido cerca de 100 vezes mais rápido que a busca linear. Resultados em `testes/resultados.csv` e `testes/comparacao_modelos.csv`.
- **259 testes automatizados** (`python -m unittest discover -s testes -t .`), todos passando. O CI roda a suíte duas vezes: no Python 3.9 só com a biblioteca padrão (o que o avaliador usa) e no 3.12 com as bibliotecas do servidor, sem pular os testes do painel, cofre e bot.

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

**Armazenamento (09/11):** SQLite é o padrão. O Supabase (`src/armazenamento_supabase.py`) liga sozinho quando `SUPABASE_URL` e uma chave `sb_secret_` estão no `.env`; foi testado no projeto real (grava e lê) e, se falhar, o sistema volta para o SQLite. Schema: `deploy/supabase_schema.sql`.

**Página pública do projeto:** `docs/index.html`, servida pelo GitHub Pages (Settings > Pages > Branch `main`, pasta `/docs`); o endereço fica em `https://jfrois.github.io/GlobalSolution_CitizenTech/`. Ao mudar o estado do projeto, atualize também essa página.

**Páginas e materiais (09/11):** relatório em `docs/relatorio.pdf`; folha cega de clareza `testes/clareza_folha.md`; roteiro de teste real `testes/roteiro_telegram_real.md`; roteiro de VM `docs/deploy_vm.md`; página pública do projeto em `docs/index.html` (GitHub Pages).

**Rascunho, precisa de revisão humana:**

- As 17 orientações de `data/base.json` foram redigidas pela IA a partir das páginas oficiais lidas em 07/11/2026 (todas com `data_verificacao` 2026-11-07). Cada orientação precisa ser conferida por um integrante (atividade E2 do planejamento). Pontos de atenção em `docs/uso_ia.md`.

**Pendente, por prioridade:**

1. **Antes do congelamento (13/11), Onda 1:** revisão humana das 17 orientações (E2) e links por estado da 2ª via da CIN (`referencias_estaduais` de DOC-001 está vazio; todos os estados caem no `gov.br`); conferir `python src/sistema.py` numa máquina limpa e no Windows.
2. **Indicadores (até 15/11):** perguntas do público (≥ 10, anônimas; hoje só existe o conjunto `equipe`) medidas **antes** de ajustar a busca; teste de usabilidade com pessoa de fora (`testes/usabilidade.md` está vazio); nota de clareza A × B (coluna `clareza_1a5` vazia). Só depois se escolhe o formato padrão (hoje o passo a passo é provisório).
3. **Onda 2, teste real:** no Telegram real (com documentos fictícios): foto/PDF, cofre pelo chat, resumo da manhã, Mini App (incluindo a aba Tarefas) e o botão "Sim, apagar tudo". O lembrete pelo chat já foi testado (08/11). `/painel` precisa de `PAINEL_URL` com https.
4. **Infraestrutura (bloqueio principal):** não há VM. O subdomínio DuckDNS existe, mas aponta para um IP residencial e as portas 80/443 não respondem; a conta Oracle não foi criada. Alternativas: GitHub Student Pack + DigitalOcean, Google Cloud e2-micro ou computador + Cloudflare Tunnel (só demonstração). Passo a passo em `docs/deploy_vm.md`; o deploy só liga com `DEPLOY_ATIVO=true`; `ffmpeg` e Whisper na VM.
5. **Segurança:** `cryptography` atualizada para 50.0.2 em 08/11 (fecha os 6 alertas do Dependabot). Para atualizar um ambiente já criado: `.venv/bin/python -m pip install cryptography==50.0.2` (não use `pip install -r requirements.txt` fora do `.venv` nem antes do passo do Whisper, ver §6). Antes da VM, gerar **novo** token do bot e **nova** chave do Gemini (os de teste foram compartilhados fora do `.env`) e conferir o histórico do Git (busca feita em 08/11 não achou tokens).
6. **Decisões EM ABERTO:** fuso por usuário (hoje todos em America/Sao_Paulo). Armazenamento: SQLite padrão e Supabase opcional (testado em 09/11 contra o projeto real com a chave secret: grava e lê; volta sozinho para o SQLite se falhar). Gemini no plano gratuito (decidido em 08/11; ver spec §12).
7. **Documentação e entrega:** seções 2, 8 e 10 escritas em 09/11 (revisar). Faltam o nome do grupo e os perfis da seção 1, o link da seção 9, "Participação na Competição", conferir o `docs/relatorio.pdf` (rascunho gerado em 09/11 por `scripts/gerar_relatorio.py`), o vídeo e `docs/link_video.txt`, e o `.txt` na FIAP ON.
8. **Roadmap planejado (opcional, baixa prioridade):** números de contexto da Base dos Dados para o relatório (ver seção 10, "Melhorias e roadmap").

Melhorias conhecidas que não bloqueiam a entrega:

- Sem `httpx` no `.venv`, 18 testes do painel e do cofre são pulados localmente (o CI roda todos). Para rodar tudo: `.venv/bin/python -m pip install httpx`.

---

## 1. Equipe

<!-- Responsável: todos (A consolida) · Prazo: 16/11 · Exigência do enunciado: nome da equipe e RMs -->

### Nome do grupo

#### _Citizen Assist AI_

### 👨‍🎓 Integrantes

| Nome | RM | Frente no projeto | Perfil |
|---|---|---|---|
| Juan de Lucas Frois | RM563260 | Núcleo e dados (Integrante A) | [GitHub](https://github.com/JFrois) · [LinkedIn](https://www.linkedin.com/in/jfrois/) |
| Flávia Roberta Pennachin | RM561860 | Bot e roteador (Integrante B) | [GitHub](https://github.com/flaviapennachin) · [LinkedIn](https://www.linkedin.com/in/flavia-pennachin/) |
| Pedro Valente | RM570394 | Cofre, painel e infraestrutura (Integrante C) | [GitHub](https://github.com/P3dr0vt) · [LinkedIn](https://www.linkedin.com/in/pedro-valente-toledo/) |

### 👩‍🏫 Professores

**Tutor(a)**
- <a href="https://www.linkedin.com/in/lucas-gon%C3%A7alez/">Lucas Gomes Jorge Gonçalez</a> 

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
| DOC-001 (2ª via da identidade (CIN/RG)) | https://www.gov.br/secom/pt-br/acompanhe-a-secom/noticias/2026/02/saiba-como-solicitar-a-2a-via-da-cin-apos-caso-de-perda | 16/11/2026 |
| DOC-002 (CIN digital no app gov.br) | https://www.gov.br/gestao/pt-br/assuntos/noticias/2026/junho/governo-do-brasil-envia-notificacoes-personalizadas-sobre-o-uso-da-versao-digital-da-cin-saiba-como-usar, https://www.gov.br/governodigital/pt-br/identidade/carteira-de-documentos-digitais, https://www.gov.br/governodigital/pt-br/acessibilidade-e-usuario/atendimento-gov.br/duvidas-na-conta-gov.br/duvidas-para-aumentar-o-nivel-da-conta-gov.br/duvidas-para-aumentar-o-nivel-com-a-cin/duvidas-para-aumentar-o-nivel-com-a-cin | 16/11/2026 |
| DOC-003 (2ª via do título de eleitor) | https://www.tse.jus.br/comunicacao/noticias/2024/Janeiro/precisa-da-2a-via-do-seu-titulo-confira-como-emitir-em-apenas-3-passos | 16/11/2026 |
| DOC-004 (Título de eleitor cancelado) | https://www.tse.jus.br/comunicacao/noticias/2025/Dezembro/eleitor-em-dia-veja-como-regularizar-o-titulo-cancelado, https://www.tse.jus.br/servicos-eleitorais/titulo-eleitoral/quitacao-de-multas, https://www.tse.jus.br/legislacao/compilada/res/2026/resolucao-no-23-750-de-26-de-fevereiro-de-2026 | 16/11/2026 |
| DOC-005 (Situação eleitoral) | https://www.tse.jus.br/comunicacao/noticias/2026/Abril/eleitor-em-dia-saiba-como-verificar-se-seu-titulo-esta-regular-1, https://www.tse.jus.br/institucional/corregedoria-geral-eleitoral/sistemas-e-servicos-1/consulta-situacao-eleitoral, https://www.tse.jus.br/servicos-eleitorais/certidoes | 16/11/2026 |
| SRV-001 (Meu INSS e telefone 135) | https://www.gov.br/inss/pt-br/canais_atendimento/meu-inss/meu-inss | 17/11/2026 |
| SRV-002 (Perícia médica do INSS) | https://www.gov.br/inss/pt-br/noticias/precisa-fazer-pericia-medica-confira-o-passo-a-passo-do-atestmed | 17/11/2026 |
| SRV-003 (Extrato CNIS e aposentadoria) | https://www.gov.br/pt-br/servicos/emitir-extrato-de-contribuicao-cnis, https://www.gov.br/pt-br/servicos/simular-aposentadoria | 17/11/2026 |
| SRV-004 (Inscrição no CadÚnico) | https://www.gov.br/pt-br/servicos/inscrever-se-no-cadastro-unico-para-programas-sociais-do-governo-federal | 17/11/2026 |
| SRV-005 (Cartão Nacional de Saúde) | https://www.gov.br/saude/pt-br/composicao/seidigi/meususdigital/perguntas-e-respostas/cidadao/9-como-faco-o-cartao | 17/11/2026 |
| SRV-006 (Meu SUS Digital) | https://www.gov.br/saude/pt-br/composicao/seidigi/meususdigital/perguntas-e-respostas/cidadao | 17/11/2026 |
| DIR-001 (Reclamar no Consumidor.gov.br) | https://www.consumidor.gov.br/pages/conteudo/publico/1 | 17/11/2026 |
| DIR-002 (Defensoria Pública) | https://www.dpu.def.br/noticias-institucional/233-slideshow/66949-saiba-como-a-defensoria-publica-da-uniao-pode-ajudar-voce | 17/11/2026 |
| DIR-003 (Disque 100 e Ligue 180) | https://www.gov.br/mdh/pt-br/ondh, https://www.gov.br/mulheres/pt-br/ligue180 | 07/11/2026 |
| DIR-004 (Certidão de nascimento gratuita) | https://www.planalto.gov.br/ccivil_03/leis/l9534.htm, https://www2.camara.leg.br/legin/fed/lei/1970-1979/lei-6015-31-dezembro-1973-357511-normaatualizada-pl.html | 17/11/2026 |
| DIR-005 (Juizado Especial Cível) | https://www.cnj.jus.br/cnj-servico-para-que-servem-os-juizados-especiais/, https://www2.camara.leg.br/legin/fed/lei/1995/lei-9099-26-setembro-1995-348608-normaatualizada-pl.html | 17/11/2026 |
| DIR-006 (Tarifa Social de Energia Elétrica) | https://www.gov.br/aneel/pt-br/assuntos/tarifas/tarifa-social | 17/11/2026 |

---

## 4. Regras de resposta, modelos de prompt e tratamento de limitações

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

Os dois modelos formatam o **mesmo** resultado da busca; por isso taxa de acerto e tempo não servem para compará-los. Critérios objetivos medidos por `--avaliar` nas 11 perguntas que geram resposta (`testes/comparacao_modelos.csv`) e avaliação cega de clareza (`testes/notas_clareza.csv`):

- Fonte com link e data: A 11/11, B 11/11.
- Aviso de confirmação quando exigido (`confirmar_antes` ou estadual): A 5/5, B 5/5 (`n/a` nas outras 6).
- Relacionados para continuar: A 11/11, B 11/11.
- Tamanho médio: A 235,2 palavras, B 242,9 palavras. Passos numerados: A 0, B 5,7.
- **Nota média de clareza (1 a 5, avaliação cega X/Y com os 3 integrantes + participante do teste de usabilidade):** **Modelo A = 3,61** · **Modelo B = 4,82**.

**Modelo escolhido:** **Modelo B (passo a passo)** foi confirmado como padrão do assistente por apresentar leitura mais escaneável em orientações com várias etapas (como regularização eleitoral e inscrição no CadÚnico), sem aumentar significativamente o número de palavras (3,3% em média).

### Tratamento de limitações

Sem base suficiente, o assistente diz que não encontrou orientação verificada, que não é um canal oficial e que não vai inventar instruções, e aponta o portal https://www.gov.br e os temas disponíveis. Entrada vazia, só símbolos, opção inexistente e pergunta longa têm mensagem própria e o programa nunca encerra por erro de entrada. Toda resposta mostra fonte e data, e o aviso de confirmação quando aplicável.

---

## 5. Plano de testes, indicadores e resultados

### Plano de testes

A avaliação usa **29 perguntas** em [`testes/perguntas.json`](testes/perguntas.json), divididas em dois conjuntos conforme o protocolo da especificação (§14.1).

- **Conjunto `equipe` (19 perguntas).** Inclui 8 diretas, 3 reformuladas, 3 fora da base e 5 casos de limite: entrada vazia, consulta ambígua (`documento`), assunto fora da base (`como tirar passaporte?`), entrada só com símbolos (`???`) e texto longo. As perguntas foram registradas em um commit antes da definição das palavras-chave da base.

- **Conjunto `publico` (10 perguntas, `P01` a `P10`).** Inclui 5 diretas, 4 reformuladas e 1 fora da base. As perguntas foram coletadas de forma anônima. A primeira medição foi feita com os pesos e as palavras-chave já definidos.

Todas as perguntas são fictícias ou anônimas, sem nenhum dado pessoal. Testes automatizados: `python -m unittest discover -s testes -t .` (259 testes cobrindo base, busca, decisão, De Morgan, Dijkstra, respostas, sessões do terminal, avaliação e módulos do servidor).

### Indicadores da busca

A taxa de acerto e o tempo medem a busca, que é a mesma para os modelos A e B (spec §8). Por isso não há coluna por modelo aqui; a comparação A × B fica na tabela seguinte. [Resultados por pergunta](testes/resultados.csv)

| Indicador | Conjunto `equipe` (19) | Conjunto `publico` (10) | Geral (29) |
|---|---|---|---|
| **Taxa de acerto** | **100,0% (19/19)** | **100,0% (10/10)** | **100,0% (29/29)** |
| Perguntas diretas | 100,0% (8/8) | 100,0% (5/5) | 100,0% (13/13) |
| Perguntas reformuladas | 100,0% (3/3) | 100,0% (4/4) | 100,0% (7/7) |
| Perguntas fora da base | 100,0% (3/3) | 100,0% (1/1) | 100,0% (4/4) |
| Casos de limite | 100,0% (5/5) | — | 100,0% (5/5) |
| **Tempo médio com índice invertido** | 1,0155 ms | 0,3172 ms | **0,7747 ms** |
| **Tempo médio com busca linear** | 4,2268 ms | 3,4833 ms | **3,9704 ms** |

### Comparação dos modelos A e B

A comparação abrange 11 respostas por modelo. [Resultados da comparação](testes/comparacao_modelos.csv)

| Critério (spec §8) | Modelo A (resumido) | Modelo B (passo a passo) |
|---|---|---|
| Respostas com fonte e data | 11/11 (100%) | 11/11 (100%) |
| Aviso presente quando necessário | 5/5 (100%, 6 não aplicáveis) | 5/5 (100%, 6 não aplicáveis) |
| Assuntos relacionados para continuar | 11/11 (100%) | 11/11 (100%) |
| Tamanho médio (palavras) | 235,2 | 242,9 |
| Passos numerados (média) | 0,0 | 5,7 |
| **Nota média de clareza (1 a 5)** | **3,61** | **4,82** |

### Teste de usabilidade

Aplicado a participante externo (`P1`, sem coleta de dados pessoais) seguindo o roteiro de 5 tarefas de `docs/ux.md` §8, com registro completo em [`testes/usabilidade.md`](testes/usabilidade.md):

- **Taxa de sucesso nas tarefas:** **5 de 5 (100%)** concluídas sem ajuda (meta: ≥ 4 de 5).
- **Tempo até a primeira resposta útil (T1):** **38 s** (meta: < 1 min).
- **Tempo para abrir assunto relacionado (T2):** **14 s** (meta: < 30 s).
- **Pontuação SUS (System Usability Scale):** **92,5 / 100** (meta de referência: ≥ 68).
- **Dificuldade observada:** na T4, o participante tentou usar `0` para voltar ao menu a partir de uma resposta (hábito de URAs telefônicas); a mensagem de opção inexistente e o rodapé `[m] menu` permitiram que ele se corrigisse sozinho.

### Interpretação dos resultados

Na primeira medição do conjunto da equipe, **antes de ajustes**, a busca acertou 17 de 19 perguntas (erros em `E02` e `E14`, corrigidos nas palavras-chave de `DOC-002` e `DIR-006`). Como esse ajuste foi feito olhando as perguntas da equipe, os 100% (19/19) não são uma medida independente. A medida independente veio com o **conjunto do público (`P01` a `P10`)**, em que a busca obteve **90,0% (9/10)** sem mexer na base. O único erro foi `P10` (*"Quero pedir auxílio-doença pelo aplicativo, como funciona?"*): `SRV-002` somou 5 pontos (`auxilio` + `doenca`) e `DOC-002` somou 4 pontos (porque `aplicativo` é palavra-chave de `DOC-002`), deixando a diferença em 1 ponto (`< MARGEM = 2`) e acionando `PEDIR_ESCOLHA` (com `SRV-002` em 1º lugar na lista de escolha) em vez de responder direto.

Após a revisão da orientação de `SRV-002`, o termo `aplicativo` passou a pontuar nesse registro, que chegou a 6 pontos. A diferença de 2 pontos permitiu responder diretamente com o registro esperado. A reavaliação chegou a **10/10 no conjunto do público** e **29/29 no total**. Esse resultado se refere às mesmas perguntas já usadas na primeira medição. [Resultados da reavaliação](testes/resultados.csv)

Na execução no Windows, o índice invertido levou em média **0,7747 ms** por pergunta, ante **3,9704 ms** da busca linear. A comparação usa as mesmas 29 perguntas e inclui os casos de limite e fora da base.


### Limitações e melhorias

**Melhorias propostas (≥ 2):**
1. **Ampliar sinônimos e palavras-chave compostas** (ex.: adicionar `"auxilio doenca"` como palavra-chave composta em `SRV-002` para dar o bônus de expressão +2 e evitar ambiguidade com termos genéricos como `"aplicativo"`).
2. **Aceitar `0` ou `voltar` nas subtelas do terminal** como atalho equivalente a `m` (menu principal), resolvendo o único atrito observado no teste de usabilidade.
3. **Ampliar a base verificada** com temas frequentes que hoje caem em `SEM_BASE` (como CNH, CPF e passaporte).

**Limitações da avaliação:** amostra ainda reduzida (29 perguntas no total e 1 participante externo no teste de usabilidade), base enxuta (17 registros) e medição de escala feita com cópias sintéticas dos registros reais.

---

## 6. 🔧 Como executar

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
================================================================
  CITIZEN ASSIST AI  -  orientação cidadã NÃO OFICIAL
================================================================
Respondo só com informações verificadas em fontes oficiais.
Não sou um canal oficial do governo.

Digite sua pergunta (ex.: como tirar a segunda via do RG)
ou escolha uma opção:

  1  Ver assuntos por tema
  2  Ver o caminho entre dois assuntos
  3  Formato da resposta (agora: passo a passo)
  ?  Ajuda
  0  Sair
> 1
Temas disponíveis:
  1  Documentação pessoal (5 assuntos)
  2  Serviços públicos (6 assuntos)
  3  Direitos e orientações comunitárias (6 assuntos)

[1-3] escolher tema  [m] menu
> 1
Documentação pessoal
  1  2ª via da identidade (CIN/RG)
  2  CIN digital no app gov.br
  3  2ª via do título de eleitor
  4  Título de eleitor cancelado
  5  Situação eleitoral

[número] abrir assunto  [m] menu  ou digite uma pergunta sobre este tema
> 5
--------------------------------------------------------------------------------
Situação eleitoral
--------------------------------------------------------------------------------
1. Para consultar sua situação eleitoral gratuitamente, acesse
   https://www.tse.jus.br, entre em 'Autoatendimento Eleitoral', abra o menu
   'Consultas' e selecione 'Situação do título'.
2. Informe o número do título de eleitor, CPF ou nome completo e a data de
   nascimento, conforme solicitado. A consulta permite verificar se a inscrição
   eleitoral está regular, cancelada ou suspensa e obter orientações sobre
   possíveis providências.
3. Também é possível consultar a situação eleitoral pela página inicial do TSE,
   selecionando 'Situação eleitoral' no menu de serviços, ou pelo aplicativo
   e-Título.
4. Atenção: estar com o título regular significa que a inscrição está habilitada
   para votar, mas não garante que todas as obrigações eleitorais estejam
   quitadas. Para verificar multas por ausências injustificadas, acesse
   'Consultas' e 'Débitos Eleitorais' no Autoatendimento Eleitoral.
5. Para comprovar que está em dia com a Justiça Eleitoral, emita gratuitamente a
   Certidão de Quitação Eleitoral. No Autoatendimento Eleitoral, selecione
   'Certidões' e depois 'Certidão de Quitação Eleitoral', preenchendo os dados
   solicitados. Também é possível emitir a certidão pelo aplicativo e-Título, em
   'Mais opções'.
6. Se o título estiver cancelado ou suspenso, ou se houver pendências, consulte
   as orientações do TSE ou procure a zona eleitoral responsável para verificar
   como regularizar a situação.

Fonte:
  https://www.tse.jus.br/comunicacao/noticias/2026/Abril/eleitor-em-dia-saiba-como-verificar-se-seu-titulo-esta-regular-1
  (verificado em 16/11/2026)
Fonte:
  https://www.tse.jus.br/institucional/corregedoria-geral-eleitoral/sistemas-e-servicos-1/consulta-situacao-eleitoral
  (verificado em 16/11/2026)
Fonte: https://www.tse.jus.br/servicos-eleitorais/certidoes (verificado em
  16/11/2026)

Continue consultando:
  1  2ª via do título de eleitor
  2  Título de eleitor cancelado
  3  2ª via da identidade (CIN/RG)

Este assistente não é um canal oficial.

[1-3] abrir assunto  [m] menu  ou digite outra pergunta
>
--------------------------------------------------------------------------------
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

O assistente usa linguagem simples, instruções diretas e rótulos como **Atenção** e **Fonte**, que continuam legíveis sem cor. 
No terminal, as orientações são quebradas em até 80 colunas, preservando links inteiros. O modo `--simples` ou a variável `NO_COLOR` habilita a saída em texto puro, sem cores nem molduras. 
No painel, o critério de contraste para texto comum é de pelo menos 4,5:1, conforme o nível AA da WCAG.

### Privacidade

O núcleo em terminal roda localmente e não coleta nem armazena dados pessoais. Na camada extra, o cofre é opcional. O nome e o conteúdo dos documentos são cifrados antes do armazenamento com AES-256-GCM. A chave é derivada da senha com PBKDF2-HMAC-SHA-256, 600 mil iterações e um sal aleatório por cofre. As operações são filtradas por `user_id`. Após confirmação, o comando `/apagar_meus_dados` remove os dados da pessoa armazenados pelo aplicativo, inclusive os documentos do cofre.

Quando o painel é publicado com HTTPS, a senha digitada no painel trafega por uma conexão cifrada até o servidor. Durante o desbloqueio, o servidor mantém a chave temporariamente em memória e decifra os documentos para visualização. O cofre oferece criptografia em repouso, e o HTTPS protege o tráfego do painel. A criptografia de ponta a ponta fica como melhoria futura.

Quando o Gemini gratuito está habilitado para sugerir nomes, o envio do documento ao serviço exige consentimento prévio. A pessoa pode escolher o nome manualmente e evitar esse envio. Os testes, as demonstrações e o vídeo usam somente documentos fictícios.

### Informação não oficial

O Citizen Assist AI é um projeto acadêmico independente e não representa nenhum órgão público. Cada orientação da base exibe o link oficial e a data de verificação. O assistente apresenta apenas os passos cadastrados na base. Se faltar informação, ele avisa que a pergunta está fora da base ou pede que a pessoa escolha entre os assuntos encontrados. Confirme os requisitos e prazos no canal oficial indicado.

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

O Citizen Assist AI roda localmente com Python no terminal, sem dependências externas. O assistente consulta a base de conhecimento, apresenta orientações com fonte oficial e data de verificação e avisa quando a pergunta está fora da cobertura. A resposta ao cidadão nunca é gerada livremente pela IA: o conteúdo vem sempre da base, com fonte e data. Sobre a camada de produto, o bot no Telegram, os lembretes e o roteador foram testados no Telegram real; cofre, foto/PDF, resumo da manhã e Mini App têm testes automatizados, mas ainda faltam testes reais (ver "Estado do projeto").

Na primeira avaliação independente, o assistente acertou **9 de 10 perguntas do público**. Após a revisão da base, a reavaliação com as mesmas perguntas chegou a **29 acertos em 29 consultas**. Na execução no Windows, o índice invertido levou em média **0,7747 ms** por consulta, ante **3,9704 ms** da busca linear no mesmo conjunto. No teste de usabilidade, o participante externo concluiu **5 de 5 tarefas sem ajuda** e atribuiu ao sistema uma pontuação SUS de **92,5/100**.

### Limitações

- **Cobertura da base.** A base tem 17 orientações em três temas. A busca depende das palavras presentes na pergunta e nos registros. Regras, prazos e valores podem mudar, por isso cada orientação indica quando a informação foi verificada e onde confirmá-la.

- **Amostra da avaliação.** O conjunto tem 29 perguntas, e o teste de usabilidade teve um participante externo. A reavaliação reutilizou as perguntas anteriores, e os testes de escala usaram cópias sintéticas dos registros.

- **Privacidade do cofre.** Os documentos são cifrados em repouso e decifrados no servidor durante o desbloqueio. A sugestão de nomes pelo Gemini gratuito depende de consentimento. A pessoa também pode dar um nome ao arquivo sem enviá-lo ao serviço.

- **Validação da camada extra.** A VM, o HTTPS e o deploy automático ainda aguardam validação em produção. As demonstrações e os testes do cofre usam documentos fictícios.


### Melhorias e roadmap


- **Ampliar sinônimos e palavras-chave** na base (hoje o `base.json` não tem sinônimos), medindo antes e depois com o conjunto do público.
- **Ampliar a base de orientações** com temas como CNH, CPF e passaporte, conferindo os procedimentos nas fontes oficiais.
- **Ampliar a cobertura estadual** da segunda via da CIN. O `DOC-001` já tem referências específicas para 10 UFs.
- **Avaliar um classificador local** para sugerir nomes de documentos no próprio dispositivo ou servidor do projeto.

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
│   ├── base.json                  orientações, fontes e datas de verificação
│   └── feeds.json                 fontes de notícias do resumo da manhã
├── docs/
│   ├── Solicitação GS.md          enunciado e checklist da entrega
│   ├── arquitetura.md             arquitetura e decisões técnicas
│   ├── deploy_vm.md               instruções de implantação
│   ├── design/                    identidade visual e protótipos
│   ├── especificacao/
│   │   └── CITIZEN_ASSIST_SPEC.md  especificação do projeto
│   ├── index.html                 página pública no GitHub Pages
│   ├── link_video.txt             URL do vídeo de apresentação
│   ├── planejamento.md           divisão de atividades e prazos
│   ├── processo_desenvolvimento.md
│   ├── relatorio.pdf              relatório da Global Solution
│   ├── uso_ia.md                  registro de uso de IA e validação crítica
│   └── ux.md                      interfaces e avaliação de usabilidade
├── painel/
│   ├── index.html                 interface do painel web
│   ├── painel.css                 estilos do painel
│   ├── painel.js                  interação e chamadas à API
│   ├── tokens.css                 cores e estilos compartilhados
│   └── icone.svg                  ícone do painel
├── scripts/
│   ├── folha_clareza.py            folha e cálculo da avaliação cega
│   ├── gerar_relatorio.py         gerador do relatório PDF
│   ├── testar_gemini.py            verificação da configuração do Gemini
│   └── verificacoes_antigas.py     identificação de fontes a rever
├── src/
│   ├── sistema.py                 ponto de entrada do terminal
│   ├── base.py                    leitura e validação da base
│   ├── busca.py                   busca, pontuação e grafo de assuntos
│   ├── respostas.py               modelos de resposta A e B
│   ├── avaliacao.py               execução das avaliações e cálculo dos indicadores
│   ├── servidor.py                inicialização do bot, da API e do agendador
│   ├── telegram_bot.py            interface do bot
│   ├── painel.py                  rotas e autenticação do painel
│   ├── cofre.py                   operações do cofre
│   └── criptografia.py            derivação de chaves e cifragem
└── testes/
    ├── perguntas.json             consultas e resultados esperados
    ├── resultados.csv             resultados e tempos de busca
    ├── comparacao_modelos.csv      indicadores dos modelos A e B
    ├── notas_clareza.csv           notas individuais da avaliação cega
    ├── usabilidade.md             registro do teste de usabilidade
    └── test_*.py                  suíte de testes automatizados
```

---

## 🧠 Decisões técnicas

As principais decisões e suas justificativas estão em [`docs/arquitetura.md`](docs/arquitetura.md) (seção 11) e na [especificação](docs/especificacao/CITIZEN_ASSIST_SPEC.md).

<!-- Opcional: resumir aqui as 3 ou 4 decisões mais importantes (ex.: resposta sempre vem da base;
     núcleo sem dependências; senha do cofre só no painel). -->

---

## 📢 Observações gerais

<!-- OBRIGATÓRIO pelo modelo da coordenação: a equipe precisa marcar uma das opções abaixo. -->

* **Participação na Competição:** [x] Sim, aceitamos participar / [ ] Não vamos participar.
* **Uso de IA:** registrado em [`docs/uso_ia.md`](docs/uso_ia.md).
* **Aviso:** o Citizen Assist AI **não é um canal oficial** de nenhum órgão público. Confirme sempre as informações no site oficial indicado em cada resposta.

---

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/fiap-tutoria/FIAP-PORTFOLIO-AI">TEMPLATE - FIAP PORTFÓLIO AI</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">FIAP</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
