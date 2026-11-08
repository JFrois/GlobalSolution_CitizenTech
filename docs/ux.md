# Citizen Assist AI: Interface e experiência do usuário

> **Fonte de verdade:** [`docs/especificacao/CITIZEN_ASSIST_SPEC.md`](especificacao/CITIZEN_ASSIST_SPEC.md) (a "spec"), §19. Este documento **detalha** as telas, os textos e as regras de uso das três interfaces. Se houver conflito, vale a spec.
>
> Decisões aprovadas em 07/11/2026: definir as 3 interfaces (terminal, Telegram, painel); o menu do terminal aceita a pergunta digitada direto; a troca de modelo A/B aparece para o cidadão como **"Formato da resposta"**.
>
> Os exemplos de resposta abaixo usam **texto de exemplo**. O conteúdo real de cada orientação vem do `data/base.json`, redigido pela equipe a partir da fonte oficial.

| Interface | Quem implementa | Onda | Avaliada pela GS? |
|---|---|---|---|
| Terminal (`python src/sistema.py`) | A — Juan | 1 | **Sim** (inclui o teste de usabilidade) |
| Bot no Telegram | B — Flávia | 2 | Não |
| Painel web / Mini App | C — Pedro | 2 | Não |

---

## 1. Princípios

1. **Uma ação por tela.** Cada tela diz, na última linha, o que dá para fazer a seguir.
2. **Pergunta primeiro.** O caminho mais curto é digitar a dúvida; menus existem para quem não sabe o que perguntar.
3. **Transparência sempre visível.** Toda resposta mostra `Fonte:` com a data e lembra que o assistente **não é canal oficial**.
4. **Nunca um beco sem saída.** Erro, "sem base" ou ambiguidade sempre oferecem o próximo passo (outra pergunta, temas, assuntos parecidos).
5. **Linguagem simples.** Frases curtas, "você", sem jargão técnico (ver vocabulário, seção 2).
6. **Mesma lógica nas três interfaces.** Os mesmos nomes, a mesma ordem (resposta → atenção → fonte → continuar) e os mesmos textos de erro, adaptados ao meio.

---

## 2. Vocabulário (usar sempre as mesmas palavras)

| Na interface dizemos | Nunca dizemos ao usuário | Observação |
|---|---|---|
| assunto | registro, id, DOC-001 | Os ids ficam só nos testes e logs |
| tema | categoria, cluster | Documentação pessoal · Serviços públicos · Direitos e orientações comunitárias |
| fonte · verificado em | referência, data_verificacao | Data no formato `10/11/2026` |
| formato resumido · formato passo a passo | modelo A, modelo B | Os nomes A e B só aparecem no README e no relatório |
| cofre | storage, banco | |
| desbloquear · bloquear | descriptografar, chave, TTL | |
| senha do cofre | chave, hash | |
| documento | arquivo, blob | |
| não é um canal oficial | — | Frase fixa, sempre igual |

---

## 3. Terminal (Onda 1, avaliado)

### 3.1 Regras gerais
- Linhas com **até 80 colunas**; sem emoji; acentos permitidos (o Python 3 escreve UTF-8 no console do Windows).
- **Dois modos de exibição (spec §5.4):** *identidade* (cores ANSI e molduras: títulos e números em azul, selo de fonte em verde, `Atenção:` em coral, cartela de abertura estática) e *simples* (texto puro, como nos exemplos abaixo). O modo simples entra sozinho quando a saída não é um terminal ou quando existe `NO_COLOR`, e pode ser forçado com `--simples`. Os exemplos desta seção mostram o modo simples; o modo identidade está no canvas de pesquisa (seção 10).
- **Na entrada:** só dígitos = opção da tela atual; `m` = menu; `?` ou `ajuda` = ajuda; `0` = sair (só no menu principal); qualquer outro texto = **pergunta**.
- Respostas e listas usam a mesma numeração da tela em que aparecem; a última linha sempre lembra as teclas válidas.
- `Ctrl+C` e fim de entrada (`Ctrl+D`/`Ctrl+Z`) encerram com a mensagem de despedida, **sem traceback**.
- Perguntas com mais de 300 caracteres: pedir uma versão curta (não cortar sem avisar).

### 3.2 Menu principal (spec §6.2)

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

>
```

> O formato padrão (resumido ou passo a passo) é **EM ABERTO** até a comparação A × B (spec §8). O exemplo acima mostra "passo a passo" só como ilustração.

### 3.3 Resposta: formato passo a passo (modelo B)

```text
----------------------------------------------------------------
2ª via da carteira de identidade (CIN/RG)
----------------------------------------------------------------
1. [Passo 1 da orientação, texto da equipe]
2. [Passo 2 da orientação, texto da equipe]
3. [Passo 3 da orientação, texto da equipe]

Atenção: o procedimento e a taxa mudam de estado para estado.
Confirme no site oficial antes de ir.
Fonte: https://www.gov.br/... (verificado em 10/11/2026)

Continue consultando:
  1  CIN digital no app gov.br
  2  2ª via do título de eleitor
  3  Inscrição no CadÚnico

Este assistente não é um canal oficial.
[1-3] abrir assunto  [m] menu  ou digite outra pergunta
>
```

### 3.4 Resposta: formato resumido (modelo A)

```text
2ª via da carteira de identidade (CIN/RG): [parágrafo curto da
orientação, texto da equipe].
Atenção: confirme no site oficial antes de ir.
Fonte: https://www.gov.br/... (verificado em 10/11/2026)
Veja também: 1) CIN digital  2) Título de eleitor  3) CadÚnico

[1-3] abrir assunto  [m] menu  ou digite outra pergunta
>
```

### 3.5 Pergunta ambígua (decisão C·A·¬B)

```text
Encontrei mais de um assunto parecido. Qual deles você procura?

  1  2ª via da carteira de identidade (CIN/RG)
  2  CIN digital no app gov.br
  3  Certidão de nascimento gratuita

[1-3] escolher  [m] menu  ou reescreva a pergunta
>
```

### 3.6 Sem base (decisão C·¬A)

```text
Não encontrei orientação verificada sobre isso na minha base.
Não sou um canal oficial e não vou inventar instruções.

Você pode consultar o portal oficial: https://www.gov.br
ou escolher um destes temas:

  1  Documentação pessoal
  2  Serviços públicos
  3  Direitos e orientações comunitárias

[1-3] ver tema  [m] menu  ou tente outra pergunta
>
```

### 3.7 Mensagens de entrada inválida (decisão ¬C e erros de menu)

| Situação | Mensagem |
|---|---|
| Entrada vazia | `Você não digitou nada. Escreva sua dúvida com palavras ou escolha um número.` |
| Só símbolos (`???`) ou nenhuma palavra útil | `Não entendi. Tente com palavras, por exemplo: como consultar minha situação eleitoral.` |
| Opção que não existe na tela | `A opção 7 não existe aqui. Escolha um dos números da lista.` |
| Texto muito longo | `Sua pergunta ficou longa. Tente resumir em uma frase curta.` |
| Base com problema (na abertura) | `Não consegui abrir a base de orientações: <motivo>. Avise a equipe.` (sai com código 1, sem traceback) |

Depois de cada mensagem, a tela atual é mostrada de novo; o programa **nunca** encerra por erro de entrada.

### 3.8 Ver assuntos por tema (menu 1)

```text
Temas disponíveis:
  1  Documentação pessoal (5 assuntos)
  2  Serviços públicos (6 assuntos)
  3  Direitos e orientações comunitárias (6 assuntos)
[1-3] escolher tema  [m] menu
>
```
Depois de escolher o tema, aparece a lista numerada dos assuntos daquele tema. O usuário pode **digitar um número** (abre o assunto) **ou uma pergunta**, que é buscada **só dentro do tema** (filtro com De Morgan, spec §7.3, item 4). A última linha diz: `[número] abrir assunto  [m] menu  ou digite uma pergunta sobre este tema`.

### 3.9 Caminho entre dois assuntos (menu 2)

O usuário **escolhe pela lista** (nunca digita ids). Primeiro a origem, depois o destino, com os 17 assuntos agrupados por tema e numerados de 1 a 17.

```text
Caminho de "CIN digital no app gov.br" até "Tarifa Social de Energia":

  CIN digital no app gov.br
   -> 2ª via da carteira de identidade (CIN/RG)
   -> Inscrição no CadÚnico
   -> Tarifa Social de Energia Elétrica

3 passos. Assuntos de temas diferentes contam como passos mais longos.
[1-4] abrir um assunto do caminho  [m] menu
>
```
Sem caminho (para bases futuras): `Esses dois assuntos não estão ligados na base. Escolha outro par.`

### 3.10 Formato da resposta (menu 3)

```text
Como você prefere ler as respostas?
  1  Resumido: um parágrafo curto e a fonte
  2  Passo a passo: lista de passos, avisos e assuntos relacionados
Agora: passo a passo.
[1-2] escolher  [m] menu
>
```

### 3.11 Ajuda e saída
- **Ajuda (`?`):** 3 exemplos de pergunta, as teclas (`m`, `?`, `0`) e a frase de não-oficialidade.
- **Sair (`0`):** `Até logo. Lembre-se de confirmar as informações no site oficial.`

---

## 4. Bot no Telegram (Onda 2)

### 4.1 Regras gerais
- Mensagens curtas (até ~4 linhas antes dos passos); negrito só no título (HTML do Telegram); **pré-visualização de links desligada**, para a fonte não virar um cartão grande.
- Escolhas são **botões** (inline keyboard), não comandos para decorar. Comandos existem como atalho.
- O bot **nunca fica mudo**: se algo falhar, `Tive um problema agora. Tente de novo em instantes.`
- Não pedir a UF no `/start`: perguntar **na primeira vez** que uma resposta depender do estado (spec §11).

### 4.2 Primeiro uso (`/start`)
```text
Olá! Eu sou o Citizen Assist AI.
Ajudo com dúvidas sobre documentos, serviços públicos e
direitos, sempre com a fonte oficial. Não sou um canal oficial.

Pergunte do seu jeito, por texto ou áudio. Por exemplo:
[Como tirar a 2ª via do RG?] [Como acessar o Meu INSS?]
[Ver temas]
```

### 4.3 Comandos (menu do BotFather)
| Comando | Faz |
|---|---|
| `/start` | Apresentação e exemplos |
| `/temas` | Botões dos 3 temas |
| `/painel` | Abre o painel (Mini App) ou gera um link de uso único |
| `/localizacao` | Escolher ou trocar a UF |
| `/ajuda` | O que o bot faz, exemplos e limites |
| `/apagar_meus_dados` | Pede confirmação e apaga tudo do usuário |

Tarefas, lembretes e briefing são pedidos em linguagem natural ("me lembra amanhã às 9h de levar o RG"); o roteador decide (spec §9).

### 4.4 Respostas
- **Orientação:** formato passo a passo (spec §9) + botões com os 3 relacionados + `[Nova pergunta]`.
- **Ambígua:** `Encontrei mais de um assunto parecido. Qual deles?` + 3 botões.
- **Sem base:** o mesmo aviso do terminal + botões dos temas + link gov.br.
- **Áudio:** primeiro `Entendi: "<transcrição>"`, depois a resposta. Assim o usuário percebe se a transcrição errou.
- **Resposta estadual sem UF:** `Esse procedimento muda por estado. Em qual estado você está?` + teclado de UFs (pergunta **uma vez**).

### 4.5 Fotos, PDFs e cofre
```text
Recebi um documento. Quer guardar no seu cofre?
[Guardar no cofre] [Não, obrigado]
```
- **Cofre bloqueado:** `Seu cofre está bloqueado. Desbloqueie no painel e envie de novo.` + botão `[Desbloquear no painel]` (abre o Mini App).
- **Primeiro envio (consentimento):** explica em 3 linhas que o arquivo vai ao Gemini para sugerir um nome, que o Google guarda registros por um tempo limitado e pode processar em outros países, com `[Concordo]` `[Cancelar]`.
- **Nome sugerido:** `Salvar como "RG - frente"?` `[Salvar]` `[Mudar o nome]`.
- **Ao enviar um documento do cofre:** `Esta mensagem será apagada do chat em 5 minutos. Isso não apaga cópias salvas no seu aparelho. Conversas com bots do Telegram não são criptografadas de ponta a ponta.`

### 4.6 Briefing matinal
```text
Bom dia! Seu resumo de hoje:

Suas tarefas
- 09:00 Levar o RG ao cartório

Notícias - fonte não oficial
Serviços públicos
- [manchete] (veículo)
```
As notícias ficam **sempre** depois das tarefas e com o rótulo "fonte não oficial" (spec §4.7).

---

## 5. Painel web / Mini App (Onda 2)

### 5.1 Regras visuais
- **Celular primeiro:** uma coluna, largura máxima de 480 px, centralizada no navegador.
- **No Mini App**, usar as cores do tema do Telegram (variáveis `--tg-theme-*`) e os botões nativos (`MainButton` para a ação principal, `BackButton` para voltar). **No navegador**, paleta própria com modo claro e escuro.
- Fonte **Plus Jakarta Sans** (§9), corpo de **16 px**, botões e áreas de toque com **pelo menos 44 px** de altura.
- Sem scripts de terceiros além do script oficial do Telegram Web App (spec §10.4).

### 5.2 Telas

| # | Tela | Conteúdo principal | Ação principal |
|---|---|---|---|
| P0 | **Perguntar (spec §10.5)** | Campo "Sua pergunta", três exemplos tocáveis; ao enviar, a cena: consulta → título e passos em sequência → selo "Fonte conferida" → próximos assuntos. Também as telas de pedir escolha, sem base e entrada inválida | Perguntar |
| P1 | Criar cofre (primeiro acesso) | 3 frases: só você abre com a sua senha; nem a equipe consegue abrir; **se esquecer a senha, perde os documentos**. Campo de senha (mín. 10 caracteres, com botão mostrar/ocultar e medidor), confirmação, caixa "Entendi que não dá para recuperar a senha" | Criar cofre |
| P2 | Desbloquear | Campo de senha | Desbloquear |
| P3 | Documentos (início) | Faixa "Cofre aberto · bloqueia em 9:42" + `Bloquear agora`; lista de cartões (tipo, nome, data); barra inferior Documentos · Configurações | — |
| P4 | Ver documento | Pré-visualização, nome, tipo, data | Apagar (secundária, em vermelho) |
| P5 | Confirmar exclusão | `Apagar "RG - frente"? O arquivo e os dados dele somem para sempre.` | Apagar de vez / Cancelar |
| P6 | Configurações | Estado (UF), temas do briefing, horário do briefing, área "Apagar todos os meus dados" | Salvar |
| P7 | Link expirado | `Este link já foi usado ou expirou. Peça um novo com /painel no bot.` | — |

### 5.3 Estados e mensagens
- **Barra inferior:** Perguntar · Documentos · Configurações. A aba Perguntar é a primeira e funciona sem o cofre.
- **Lista vazia (P3):** `Seu cofre está vazio. Mande a foto de um documento para o bot e ela aparece aqui.`
- **Senha errada (P2):** `Senha incorreta.` (mensagem genérica). Depois de várias tentativas: `Muitas tentativas. Espere 1 minuto e tente de novo.` (rate limit, spec §10.4).
- **Cofre bloqueou sozinho:** volta para P2 com `Seu cofre foi bloqueado por segurança. Digite a senha para abrir de novo.`
- **Apagar todos os dados (P6):** dois passos; no segundo, o usuário digita `APAGAR` para confirmar.

---

## 6. Acessibilidade (checklist para as 3 interfaces)

- [ ] Contraste de texto de pelo menos 4,5:1 (WCAG AA) no painel, nos modos claro e escuro.
- [ ] Nenhuma informação só por cor (erros têm texto; o botão de apagar diz "Apagar").
- [ ] Todo campo do painel tem rótulo visível; imagens e ícones têm texto alternativo.
- [ ] Painel navegável só com teclado e com foco visível.
- [ ] Áreas de toque com pelo menos 44 px; corpo de texto de 16 px; zoom do navegador não quebra o layout.
- [ ] Terminal: linhas de até 80 colunas, sem cores obrigatórias nem arte ASCII que confunda leitores de tela.
- [ ] Linguagem simples: frases de até ~20 palavras, sem siglas sem explicação na primeira vez (ex.: "CadÚnico (Cadastro Único)").
- [ ] Datas no formato brasileiro (`10/11/2026`) e horários com 24 h.

---

## 7. Curva de aprendizado

**Como reduzimos:**
- Exemplos de pergunta no menu, no `/start` e na ajuda: o usuário aprende copiando.
- A última linha de cada tela diz o que dá para fazer, sem precisar memorizar comandos.
- Telas vazias e erros ensinam o próximo passo.
- O mesmo vocabulário e a mesma ordem da resposta nas 3 interfaces.

**Metas (medidas no teste de usabilidade):**

| Meta | Valor |
|---|---|
| Primeira resposta útil sem ajuda | < 1 min |
| Abrir um assunto relacionado a partir de uma resposta | < 30 s |
| Tarefas concluídas sem ajuda da equipe | ≥ 4 de 5 |
| Nota SUS (System Usability Scale, 0 a 100) **(sugestão)** | ≥ 68 (média de mercado) |

---

## 8. Roteiro do teste de usabilidade (terminal; spec §14.2)

Pessoa de fora da equipe, sem explicação prévia além de "este é um assistente de orientação cidadã". Um integrante observa, cronometra e **não ajuda** (se a pessoa travar por 2 min, conta como falha e a equipe explica).

| # | Tarefa dita ao participante | Sucesso quando |
|---|---|---|
| T1 | "Descubra como pedir a segunda via do título de eleitor." | Chega à resposta com fonte |
| T2 | "A partir dessa resposta, veja outro assunto ligado a ela." | Abre um relacionado |
| T3 | "Pergunte como tirar passaporte e me diga o que o assistente respondeu." | Entende que não há base e vê a sugestão do gov.br |
| T4 | "Encontre um assunto sobre direitos sem digitar uma pergunta." | Usa o menu de temas |
| T5 | "Mude o jeito como as respostas aparecem." | Troca o formato |

Registrar em `testes/usabilidade.md`, para cada tarefa: sucesso (sim/não), tempo, erros, pedidos de ajuda e comentários. No fim, aplicar o questionário SUS (10 afirmações, notas de 1 a 5) **(sugestão)** e pedir a nota de clareza 1–5 dos dois formatos sem dizer qual é qual (rubrica A × B, spec §8).

---

## 9. Identidade visual: **Azul Telegram** (aprovada em 08/11/2026; substitui a "Estreia clara" de 07/11)

Protótipo animado (6 telas: painel em 5, mais o terminal) no canvas de revisão de UI. Tokens prontos para o código: [`docs/design/`](design/README.md) (`tokens.css`, `tokens.json`).

**Por quê:** a "Estreia clara" parecia engessada e rústica. A nova direção segue o que os templates do Lovable fazem (fundo cheio de cor, painéis arredondados, botões em pílula, animação de entrada) e usa o **mesmo azul do Telegram** em painel, bot e terminal, para as três interfaces parecerem um produto só.

**Conceito:** calma e confiança. Toda tela do painel tem uma **faixa azul** (hero, com o título) e uma **folha clara** com cantos de 34 px que sobe por baixo com o conteúdo.

### 9.1 Tokens

| Token | Valor | Papel | Contraste |
|---|---|---|---|
| `--cor-azul` | `#229ED9` | Azul do Telegram: marca, brilho e degradê. **Só decoração** | branco 3,0 (não usar em texto pequeno) |
| `--degrade-hero` | `#229ED9` → `#1676B0` → `#0F5C93` (170°) | Faixa azul do topo | — |
| `--cor-acao` | `#12689E` | Botão principal, item ativo, número do passo | branco 6,0 |
| `--cor-link` | `#0B5E94` | Links e "Abrir →" | 6,9 no branco |
| `--cor-fundo` | `#F2F8FC` | Folha clara | — |
| `--cor-superficie` | `#FFFFFF` | Cartões | — |
| `--cor-texto` | `#0E2233` | Títulos e texto | 16,5 |
| `--cor-apoio` | `#4A6176` | Legendas e rótulos | 5,9 |
| `--cor-noite` | `#0E2233` | Barra de navegação flutuante e terminal | — |
| `--cor-verde` | `#0F7A5A` | Selo "Fonte conferida" (fundo `#DDF3EA`) | branco 5,5 |
| `--cor-teal` / `--cor-coral` | `#0A7C73` / `#B8431F` | Tinta dos temas Serviços e Direitos (Documentos usa o azul) | ícone sobre fundo suave ≥ 4,5 |
| `--cor-atencao-texto` | `#5E1F0B` | "Atenção:" sobre `#FDE7DF` | 9,5 |
| `--cor-borda` | `#6F8CA2` | Bordas de campos e botões secundários | ≥ 3,3 |

- **Vidro:** fundo `rgba(8,40,70,.38)`, borda `rgba(255,255,255,.4)`, blur de 14 px (chips e cartões sobre o azul). Texto branco só sobre vidro ou sobre a parte escura do degradê.
- **Tipografia:** **Plus Jakarta Sans** em tudo (400 a 800; títulos em 800, 36 px no hero e 32 px na resposta, espaçamento -0,03 em); texto de no mínimo 16 px, entrelinha 1,5; **JetBrains Mono** no terminal. Fontes gratuitas (Google Fonts, licença OFL).
- **Formas:** cartões 22 px, ícones 14 px, folha 34 px nos cantos de cima, botões, chips e barra de navegação em pílula; sombras suaves, sem borda dura.
- **Navegação do painel:** barra escura flutuante em pílula (Perguntar · Cofre · Ajustes). O item ativo vira uma pílula branca com ícone e **rótulo** (nunca só a cor), com `aria-current="page"`.
- **Símbolo:** lente (anel) com sinal de conferido, em branco sobre azul. Mínimos: símbolo 24 px, avatar 40 px, logotipo 140 px. **Avatar do bot:** degradê azul e símbolo branco (`docs/design/imagens/`).
- **Ícones:** grade 24 px, traço 2 px, pontas redondas, sempre com texto ao lado (ou `aria-label`).
- **Grafismos:** selo "Fonte conferida" (cartão verde com check), números de passo em círculo, rótulo "Não oficial" em vidro.
- **Movimento:** blocos entram subindo 14 px com fade em 550 ms, em sequência de ~150 ms; a folha sobe 60 px em 600 ms; o selo "Fonte conferida" faz *pop* e o check é desenhado; toque reduz a escala a 0,96 em 150 ms. Só `opacity` e `transform`. **Cena da verificação** (aba Perguntar, spec §10.5): contagem até 17 com barra de progresso, título, 3 passos, selo e próximos assuntos, em ~3 s, com botão "Repetir cena" no protótipo. Com "reduzir movimento", tudo aparece pronto.
- **Estado ativo nunca só pela cor:** aba e chip selecionados levam também rótulo e marca de check.
- **Títulos no Telegram:** em negrito e com a primeira letra maiúscula (a fonte do chat não é a Plus Jakarta Sans).
- **Terminal (identidade):** fundo sugerido `#0B1622`; destaque (marca, números, teclas) em `#2AABEE` (16 cores: `94`); "Fonte:" em `#5BD68F` (`32`); "Atenção:" em `#FF9B7A` (`91`); apoio `#8FA9BD`. Moldura com caracteres de caixa e a cartela `C I T I Z E N   A S S I S T   A I` em azul. Modo `--simples`, `NO_COLOR` e saída sem terminal continuam em texto puro.
- **Nunca:** o azul e o amarelo do gov.br, brasão ou bandeira; tirar o "não oficial". O azul do Telegram é permitido e deve ser diferente o bastante do azul institucional do gov.br (`#1351B4`): a base é `#229ED9`, mais claro e mais ciano.

Onde a identidade aparece: avatar e nome do bot, painel no navegador (no Mini App valem as cores do Telegram, com a primária como destaque), README, relatório, vídeo e o cabeçalho do terminal (só o nome, em texto). As telas do Telegram e do painel já foram desenhadas na Estreia clara (seção 10).

## 10. Protótipo e wireframes

- **Protótipo animado da identidade Azul Telegram** (painel em 5 telas, cena da verificação e terminal): código em [`docs/design/prototipo/`](design/prototipo/) e canvas de revisão de UI: https://claude.ai/artifact/VLaxzKY5pHx7NYm9utVwLc
- Wireframes do terminal em modo simples (estrutura das telas da §3): https://claude.ai/artifact/T3RUAHaEZy8zYef4SVgW85

Os links são privados; o dono precisa compartilhar pelo menu Share para a equipe abrir. Os protótipos usam **texto de exemplo** nas orientações; não são fonte de conteúdo.
