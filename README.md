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

## Estado do projeto

Atualizado em **18/11/2026**, com referência à `main` após o merge do [PR #55]


### Histórico de entregas

A tabela usa a data de integração na `main` ou, quando indicado, a data do commit na branch.

| Data | O que foi entregue | PR ou commit |
|---|---|---|
| 06/11/2026 | Especificação inicial, processo de desenvolvimento, planejamento e arquitetura. Primeira versão do README e do registro de uso de IA. | [#1](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/1), [#2](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/2) |
| 07/11/2026 | Núcleo em Python com base de 17 orientações, busca, grafo de assuntos, modelos A e B, terminal e avaliação automatizada. | [#4](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/4) |
| 07/11/2026 | Integração do servidor ao núcleo, com bot do Telegram, roteador, painel inicial e armazenamento. Ajustes de robustez do painel e do workflow. | [#5](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/5), [#6](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/6) |
| 07/11/2026 | Ajustes na cascata do Gemini, transcrição local de voz com Whisper e tolerância a erros de digitação na busca. | [#16](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/16), [#17](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/17), [#19](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/19), [#20](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/20), [#23](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/23) |
| 08/11/2026 | Implementação da criptografia, do cofre, do classificador de documentos, do painel e dos fluxos de tarefas, resumo da manhã e recebimento de foto/PDF. | [#25](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/25), [#26](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/26), [#27](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/27), [#28](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/28), [#29](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/29), [#30](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/30), [#31](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/31) |
| 08/11/2026 | Aba Tarefas do painel, ajustes no agendador, atualização de `cryptography` para 50.0.2, encerramento conjunto com Ctrl+C e correção do roteamento de lembretes. O teste de entrega de um lembrete no Telegram foi registrado nessa data. | [#37](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/37), [#38](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/38), [#42](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/42), [#43](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/43), [#44](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/44), [#47](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/47) |
| 08/11/2026 | Respostas do bot em ordem por usuário, distinção entre lembretes pendentes e já avisados, definição dos cinco temas do resumo e aviso sobre o Gemini gratuito. | [#48](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/48) |
| 09/11/2026 | Primeira versão do relatório, folha de avaliação cega e roteiros de deploy e testes. Supabase opcional com SQLite como padrão. Publicação da vitrine para GitHub Pages. | [#49](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/49), [#50](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/50), [#51](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/51), [#52](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/52) |
| 16/11/2026 | Indicadores da Frente B, com as primeiras medidas no conjunto do público, avaliação cega dos modelos, teste de usabilidade e referências de 10 UFs para a segunda via da CIN. | [#54](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/54) |
| 16/11/2026 | Atualização do status na vitrine e no planejamento e correção do layout do terminal ilustrado em telas pequenas. | [`13fb4ca`](https://github.com/JFrois/GlobalSolution_CitizenTech/commit/13fb4ca), [`13e452a`](https://github.com/JFrois/GlobalSolution_CitizenTech/commit/13e452a) |
| 17/11/2026 | Revisão das orientações de Serviços e Direitos (E2), seção 8 do README (E6), suporte a múltiplas fontes por registro e ajuste das rotas do cofre e das tarefas. Commits da branch integrados no dia seguinte. | [#55](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/55), commits `235dd14`, `1eb2fac`, `dea767a` e `6b2f605` |
| 18/11/2026 | Registro da revisão de segurança do cofre e do painel (C9), geração do relatório atualizado (E7), atualização dos perfis e das fontes no README e alinhamento da especificação sobre o cofre. | [#55](https://github.com/JFrois/GlobalSolution_CitizenTech/pull/55), commits `d7e1629`, `51348f9` e `040903b` |

### Situação atual

- **Núcleo.** O terminal roda offline com a biblioteca padrão do Python. A base reúne 17 orientações em três temas. A revisão de Documentação integra os resultados da Frente B, e a revisão de Serviços e Direitos foi registrada na atividade E2.
- **Indicadores.** Na primeira avaliação independente, o assistente acertou **9 de 10 perguntas do público**. A reavaliação após os ajustes da base reutilizou as perguntas e obteve **29/29**. O Modelo B foi escolhido na avaliação cega (**4,82**, ante **3,61** do Modelo A). No teste de usabilidade, o participante concluiu **5/5 tarefas sem ajuda** e o sistema obteve **92,5/100 no SUS**.
- **Testes e documentação.** Os **262 testes automatizados** passaram em uma execução local com Python 3.12 e as dependências do servidor. O [relatório da GS](docs/relatorio.pdf) foi regenerado em 19/11 e a revisão de segurança está registrada em [`docs/uso_ia.md`](docs/uso_ia.md).
- **Camada extra.** A equipe registrou testes no Telegram com consultas por texto, voz, localização e roteamento em 07/11, e com lembretes em 08/11. O painel foi conferido no navegador local. O cofre cifra os arquivos em repouso e a decifragem ocorre no servidor


A divisão de atividades está em [`docs/planejamento.md`](docs/planejamento.md).

---

## 1. Equipe

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

### Organização da base

Toda a base fica em `data/base.json`: `versao`, `temas`, `sinonimos` e `registros`. Cada registro tem `id`, `titulo` (opcional), `tema`, `palavras_chave`, `pergunta`, `orientacao`, `referencia`, `data_verificacao` e `relacionados`; os campos opcionais são `confirmar_antes`, `abrangencia` e `referencias_estaduais`. O campo `referencia` aceita uma URL ou uma lista de URLs. São 17 registros em 3 temas.

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

Todas as perguntas são fictícias ou anônimas, sem nenhum dado pessoal. Testes automatizados: `python -m unittest discover -s testes -t .` (262 testes cobrindo base, busca, decisão, De Morgan, Dijkstra, respostas, sessões do terminal, avaliação e módulos do servidor).


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


### Rodar no terminal

```bash
git clone https://github.com/JFrois/GlobalSolution_CitizenTech.git
cd GlobalSolution_CitizenTech
python src/sistema.py
```

### Outros modos

| Comando | O que faz |
|---|---|
| `python src/sistema.py --avaliar` | Avalia a busca e os modelos A e B. O comando atualiza `testes/resultados.csv` e `testes/comparacao_modelos.csv`. |
| `python src/sistema.py --validar-entrega` | Confere se os registros da base estão completos para a entrega. |
| `python src/sistema.py --simples` | Exibe texto puro, sem cores nem molduras. Também é usado com `NO_COLOR` preenchida ou com a saída redirecionada. |
| `python src/sistema.py --base caminho.json` | Usa outro arquivo JSON como base. |
| `python src/sistema.py --servidor` | Inicia o bot do Telegram, a API do painel e o agendador. |
| `python -m unittest discover -s testes -t .` | Executa a suíte. Os testes da camada extra dependem das bibliotecas do servidor e do `httpx`. |


### Rodar o bot e o painel

Crie e ative um ambiente virtual. No Windows, com PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

No macOS ou Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Com o ambiente ativo, instale as dependências nesta ordem. Para transcrever mensagens de voz, instale também o FFmpeg e confira se `ffmpeg -version` funciona.

```text
python -m pip install "setuptools<81" wheel
python -m pip install --no-build-isolation openai-whisper==20240930
python -m pip install -r requirements.txt
```

Para rodar os testes das rotas do painel, instale também `httpx` com `python -m pip install httpx`.

Crie o arquivo `.env` a partir de [`.env.example`](.env.example) e preencha as variáveis obrigatórias. Mantenha o `.env` fora do Git.

| Variável | Para quê |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Obrigatória. Token do bot fornecido pelo BotFather. |
| `SESSAO_SEGREDO` | Obrigatória. Segredo aleatório para assinar as sessões do painel. Use `python -c "import secrets; print(secrets.token_urlsafe(32))"` para gerar um valor. |
| `GEMINI_API_KEY` | Opcional. Sem a chave, o bot usa as regras locais. |
| `GEMINI_MODELO` | Opcional. Define o primeiro modelo que o roteador tentará usar. |
| `WHISPER_MODELO` | Opcional. Define o modelo de transcrição (`tiny`, `base`, `small` ou `medium`). O padrão é `base`. |
| `PAINEL_URL` | Endereço do painel. Para abrir o painel pelo Telegram, configure uma URL HTTPS acessível. |
| `PAINEL_PORTA` | Porta local da API. O padrão é `8000`. |

`python scripts/testar_gemini.py` confere a chave e lista os modelos. Se a porta 8000 estiver ocupada, o servidor avisa e sai (`lsof -i :8000` mostra o processo).

Inicie o servidor e envie `/start` ao bot correspondente ao token configurado.

```text
python src/sistema.py --servidor
```

Para encerrar o bot, o painel e o agendador, pressione **Ctrl+C**. Se a porta estiver ocupada, identifique o processo que a está usando ou ajuste `PAINEL_PORTA`. O comando `python scripts/testar_gemini.py` confere a configuração do Gemini e lista os modelos disponíveis.

---

## 7. Exemplos de uso

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


* **[Vídeo de apresentação no YouTube (Não Listado)](http://url-aqui)**: 

---

## 10. Conclusões, limitações e melhorias

### Conclusões

O Citizen Assist AI roda localmente com Python no terminal, sem dependências externas. O assistente consulta a base de conhecimento, apresenta orientações com fonte oficial e data de verificação e avisa quando a pergunta está fora da cobertura. A camada extra inclui bot no Telegram, painel, cofre e lembretes. A cobertura dos testes está no [estado do projeto](#estado-do-projeto).

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

- **Orientações com fonte verificável.** As respostas sobre documentos, serviços e direitos vêm de `data/base.json` e incluem a fonte oficial e a data de verificação. Quando a busca encontra assuntos próximos, pede que a pessoa escolha. Quando a base é insuficiente, informa a limitação.

- **Terminal leve e offline.** O núcleo usa apenas a biblioteca padrão do Python. Isso facilita a execução em outras máquinas, sem instalar dependências ou configurar chaves de API. O Telegram e o painel são extensões opcionais.

- **Busca por índice invertido.** O índice identifica os registros que contêm termos da pergunta e reduz o trabalho da busca. A busca linear serve de referência para comparar os tempos, usando as mesmas regras de pontuação.

- **Cofre opcional.** O nome e o conteúdo dos documentos são cifrados antes de serem armazenados. A senha é digitada no painel, e o servidor decifra os arquivos durante o desbloqueio. O acesso aos documentos é filtrado por `user_id`.

As justificativas completas estão na [seção 11 da arquitetura](docs/arquitetura.md) e na [especificação do projeto](docs/especificacao/CITIZEN_ASSIST_SPEC.md).

---

## 📢 Observações gerais

<!-- OBRIGATÓRIO pelo modelo da coordenação: a equipe precisa marcar uma das opções abaixo. -->

* **Participação na Competição:** [x] Sim, aceitamos participar / [ ] Não vamos participar.
* **Uso de IA:** registrado em [`docs/uso_ia.md`](docs/uso_ia.md).
* **Aviso:** o Citizen Assist AI **não é um canal oficial** de nenhum órgão público. Confirme sempre as informações no site oficial indicado em cada resposta.

---

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/fiap-tutoria/FIAP-PORTFOLIO-AI">TEMPLATE - FIAP PORTFÓLIO AI</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">FIAP</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
