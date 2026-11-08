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
| Google Gemini (API, plano gratuito) | **Dentro do produto** (Onda 2) | Escolher a ferramenta (function calling) e sugerir o nome de documentos do cofre. A voz **não** usa mais o Gemini (decisão de 07/11: Whisper local). **Não gera** o texto das orientações (spec §1) |

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

| 07/11 | Juan | Claude Code | Auditar o repositório contra o enunciado da GS (checklist, inconsistências, correções) | Aceito | Achados conferidos com o enunciado e com o estado real do repositório (sem código ainda; `python src/sistema.py` falhava) |
| 07/11 | Juan | Claude Code | Aplicar as decisões da equipe na spec e nos documentos: responsáveis A/B/C, comparação A × B por rubrica, navegação nos dois modelos, Python 3.9 no núcleo, sinônimos e expressões, grafo conexo, protocolo das perguntas de teste | Aceito, aguardando revisão da equipe | As decisões (responsáveis, ligar as ilhas, criar perguntas antes e coletar do público depois) vieram da equipe; a IA propôs as arestas DOC-001–DOC-003 e SRV-001–SRV-006, que precisam ser conferidas nas fontes oficiais (atividade E2) |

| 07/11 | Juan | Claude Code | Definir a UI das 3 interfaces (terminal, Telegram, painel) em `docs/ux.md` e spec §19, e montar wireframes clicáveis | Aceito; aprovado pela equipe em 07/11 | Decisões de escopo tomadas pela equipe (3 interfaces, pergunta direto no menu, "Formato da resposta"); a IA propôs telas e textos, que cada responsável revisa na atividade E11. Exemplos de orientação no protótipo são texto de exemplo, não conteúdo da base |

| 07/11 | Juan | Claude Code | Pesquisar identidades visuais a partir de templates do Lovable e manuais de marca do Adobe Stock, propor direções e montar o manual de marca | Aceito; aprovado pela equipe em 07/11 | A equipe escolheu a base (híbrida), as referências e a direção final (Estreia clara). Rejeitado: comprar template pago ou usar app React do Lovable (conflita com a spec). Contraste de todas as cores conferido por script (WCAG AA); referências usadas só como inspiração, sem copiar layouts, imagens ou marcas |

| 07/11 | Juan | Claude Code | Desenhar as telas na Estreia clara, fazer a crítica de design e corrigir os problemas encontrados | Aceito; aprovado pela equipe em 07/11 | Contraste medido por script (bordas de campos falhavam em 3:1 e foram corrigidas); aba ativa ganhou marcação além da cor; alvos de toque ajustados para 44 px |
| 08/11 | Juan | Claude Code | Revisar a identidade visual: abrir 11 templates do Lovable rodando, trocar âmbar por azul do Telegram, desenhar o canvas animado (painel, cena, terminal) e atualizar tokens, ux.md §9, spec e cores do terminal | Aceito: degradê azul, folha clara, vidro fosco, pílulas e animação de entrada. Ajustado: azul de ação escurecido (`#12689E`) para passar no contraste AA com texto branco |
| 07/11 | Juan | Claude Code | Propor na spec a aba "Perguntar" no Mini App com a cena da verificação (§10.5) | Aceito; aprovado pela equipe em 07/11 | A ideia veio da crítica de design e foi aceita pelo Juan; a proposta mantém as regras da spec (resposta só da base, sem LLM nessa rota, pergunta não gravada, "reduzir movimento") |

| 07/11 | Juan | Claude Code | Implementar o núcleo: `base.py`, `busca.py`, `respostas.py`, `sistema.py`, `avaliacao.py` e testes, seguindo a spec | Aceito, aguardando revisão por outro integrante | 94 testes automatizados (`unittest`) passam em Python 3.14 e 3.9. Limiar e margem da decisão foram ajustados olhando as perguntas de teste da equipe; o conjunto do público ainda não foi medido |
| 07/11 | Juan | Claude Code | Redigir **rascunhos** das 17 orientações lendo as páginas oficiais (gov.br, TSE, ANEEL, CNJ, DPU, Planalto) | Aceito como rascunho; **precisa de revisão humana de cada orientação** (atividade E2) | A IA abriu cada página e escreveu com palavras próprias, com a data em que leu (07/11/2026). Pontos que a equipe deve conferir: DOC-001 (estados da equipe ainda sem link estadual), DOC-004 (situação do TSE após a reabertura de 03/11), DIR-004 (a lei diz "demais certidões"; a equipe deve confirmar com um cartório se vale para a 2ª via), DIR-005 (página do CNJ é de 2016; limites vêm da Lei 9.099), DIR-006 (a ANEEL diz que a inclusão é automática; confirmar o conflito de fontes da spec). O TSE bloqueia leitura automática (403) e foi lido pelo navegador |
| 07/11 | Juan | Claude Code | Implementar o servidor base (roteador com Gemini e fallback por regras, bot do Telegram, esqueleto do painel, armazenamento, deploy) a partir da spec, em sessão paralela, e trazer para a `main` por `cherry-pick` | Aceito, aguardando revisão da equipe | Testes do servidor (`testes/test_servidor.py`) rodados contra o núcleo da `main`. Não testado com Telegram, Gemini ou VM reais. Nomes dos modelos Gemini seguem em aberto (spec §12) |
| 07/11 | Juan | Claude Code | Subir o bot no Telegram, corrigir erros dos testes reais (anotações do FastAPI, voz sem texto, botões cortados, porta em uso), cascata de modelos do Gemini com IA só quando a base não resolve | Aceito | Cada erro foi reproduzido no Telegram real, corrigido e coberto por teste; 133 testes. O Juan rodou o servidor e colou os logs |
| 07/11 | Juan | Claude Code | Voz no Telegram com Whisper local (`transcricao.py`), aviso "Recebi seu áudio…", dica de vocabulário | Aceito | Áudio real do Juan: o modelo `base` ouviu "segundo aviado do RG"; com a dica de vocabulário acertou "segunda via do RG" (amostra de 1 áudio, não prova geral). 7 testes com Whisper falso |
| 07/11 | Juan | Claude Code (controle do app Telegram no desktop) | Testar a interface pelo Telegram real: comandos, 17 assuntos, ambíguas, inválidas, fora da base, UF, menu, HTML no texto | Aceito | Bug achado: "???", "documento" e "Como pagar o IPVA?" iam ao Gemini e voltavam "função não disponível". Corrigido (`reconciliar`, `resposta_direta_basta`) e retestado. Melhorias de UX (lista duplicada, botão voltar) feitas e retestadas |
| 07/11 | Juan | Claude Code | Correção de digitação na busca (só em SEM_BASE) | Aceito | Conjunto da equipe 19/19 antes e depois; fora da base (IPVA, MEI, imposto de renda, passaporte) continua sem base; 5 testes novos. Spec §7.3, item 5b |
| 08/11 | Juan | Claude Code | Implementar criptografia, cofre, classificador, painel com abas Perguntar/Cofre/Ajustes, tarefas, agendador, briefing e foto/PDF no bot, em uma branch por etapa (PRs #25 a #31) | Aceito, aguardando revisão humana de segurança por outro integrante | 214 testes automatizados (senha errada, adulteração, expiração, isolamento por usuário, injeção no classificador, limite de tentativas); painel conferido no navegador local; **não testado** no Telegram real nem na VM. Decisões da IA para a equipe confirmar: PBKDF2 no lugar de Argon2id e estado do agendador no banco em vez de jobstore |
| 08/11 | Juan | Claude Code | Complementar a aba Tarefas do painel (já entregue no PR #37): proteção contra envio duplo no botão "Anotar" e testes de `tentar_criar` e `lista_para_painel` | Aceito, aguardando revisão de outro integrante | 231 testes passando (venv do servidor + httpx e Python do sistema); conferido no navegador local: clique duplo cria 1 tarefa, data inválida mostra mensagem e mantém o texto. A IA errou um teste ("ontem" não é entendido pelo leitor de datas) e corrigiu |
| 08/11 | Juan | Claude Code | Revisar o projeto inteiro, identificar o que falta e atualizar README (estado e roadmap), planejamento (status, branches, tarefas por integrante, E12), spec e mapa; avaliar a Base dos Dados | Aceito pelo Juan | Fatos conferidos rodando o projeto (231 testes, `--validar-entrega`, `--avaliar` 19/19), lendo `data/base.json`, `data/feeds.json`, `testes/` e os alertas do Dependabot (todos em `cryptography` 43.0.1). Base dos Dados **rejeitada para o código** (exige `pip install`, BigQuery e internet, contra a spec §5.3, e traz estatísticas, não orientações); aceita só como números de contexto do relatório (E12, opcional) |
| 08/11 | Juan | Claude Code | Corrigir o lembrete que chegou 39 min atrasado e "tarefa - trabalho às 18:10" que listava em vez de criar; atualizar `cryptography`; revisão completa do projeto (núcleo, bot e segurança) com 3 agentes de revisão | Aceito pelo Juan | Atraso confirmado no log do macOS (`pmset`): o Mac dormiu de 18:03 a 18:48 e o bot roda nele; o código cumpriu o vencido ao acordar. Correções com 4 testes novos (235 passando). Dos achados dos agentes, 1 comentário desatualizado foi corrigido; os demais (CORS, link de uso único, tipo de arquivo, fuso do agendador, SQLite) foram conferidos no código e **rejeitados** por não serem problemas reais |
| 08/11 | Juan | Claude Code | `/code-review` do projeto inteiro (10 achados) e correção dos 6 de código e documentação: usuário que bloqueou o bot não recebe novas tentativas a cada 30 s; resumo da manhã com mais de 3 h de atraso é pulado; erro de digitação em "tarefa"/"lembrete"; ordem de instalação no README; README desatualizado; job de CI em Python 3.12 com as bibliotecas do servidor | Aceito pelo Juan | 239 testes passando (8 novos), inclusive num ambiente limpo igual ao do CI novo. Cuidado conferido: "tarifa" (Tarifa Social de Energia) **não** é corrigida para "tarefa". Os 4 achados restantes dependem da equipe (VM, `referencias_estaduais`, feeds RSS, revisão humana da base) |
| 08/11 | Juan | Claude Code | Teste de ponta a ponta (terminal, bot no Telegram e painel) e correção do que ele achou: "me lembra de pagar a luz amanhã às 9h" ia para a busca e respondia a Tarifa Social de Energia; o teste do `--servidor` sem `.env` falhava em quem já tem `.env` | Aceito pelo Juan | 242 testes passando (1 novo, com 11 casos). Conferido: "não lembro a senha do gov.br" continua indo para a busca |
| 08/11 | Juan | Claude Code | Investigar por que o Ctrl+C não desligava o `--servidor` (porta 8000 presa) e corrigir; organizar as branches do GitHub | Aceito pelo Juan | Causa: o aiogram toma o sinal só para si e encerra o polling, mas o uvicorn e o agendador seguiam vivos. Bug **reproduzido** num processo de simulação (uvicorn real + handler de sinal igual ao do aiogram): antes o processo seguia rodando, depois terminou. 2 testes novos. Branch antiga de implementação paralela virou a tag `arquivo-servidor-paralelo` antes de ser apagada |
| 08/11 | Juan | Claude Code | Levantar pontas soltas depois do PR #44 e atualizar README, planejamento e mapa com o que está pronto e o que falta | Aceito, aguardando revisão da equipe | Conferido rodando: 242 testes passando, servidor novo na porta 8000, nenhum PR ou alerta do Dependabot aberto. Achado: "tarifa de ônibus" responde a Tarifa Social de Energia (reproduzido no terminal); ficou registrado como pendência, sem mexer na busca |
| 08/11 | Juan | Claude Code | Corrigir "tarifa de ônibus" respondendo a Tarifa Social de Energia (DIR-006) | Aceito pelo Juan | Regra nova na busca: se a pergunta tem palavra que a base não conhece e o melhor registro só bate por pedaço de palavra-chave composta, não responde (SEM_BASE). Conferido: `--avaliar` segue 19/19; "tarifa social", "tarifa de luz" e "segunda via rg urgente" continuam respondendo; 243 testes passando (1 novo) |
| 08/11 | Juan | Claude Code | Conferir a chegada de um lembrete no Telegram real: tarefa criada para as 20:10 no banco do servidor local | Aceito pelo Juan | Mensagem "Lembrete: …" chegou às 20:10 (print do Juan); banco marcou como avisada. Um `/start` saiu da conta do Juan 1 s depois sem ele ter enviado; registrado no log do bot, origem não identificada |

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
- No produto, documentos do cofre passam pelo Gemini **com consentimento do usuário** e em plano gratuito (spec §12): o Google pode usar o conteúdo para melhorar produtos e permitir revisão humana, e o aviso de consentimento diz isso. Demonstração e testes usam só documentos fictícios.
