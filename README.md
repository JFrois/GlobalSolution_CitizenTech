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

_A preencher_

### Público beneficiado

_A preencher_

### Temas abordados

| Tema | Assuntos | Registros |
|---|---|---|
| Documentação pessoal | _A preencher_ | DOC-001 a DOC-005 |
| Serviços públicos | _A preencher_ | SRV-001 a SRV-006 |
| Direitos e orientações comunitárias | _A preencher_ | DIR-001 a DIR-006 |

---

## 3. Base de conhecimento, estruturas e estratégia de busca

<!-- Responsável: Integrante A · Prazo: 16/11
     Escrever: formato de data/base.json e campos obrigatórios; como acrescentar/corrigir registros
     sem mexer no código; listas e dicionários usados; grafo de temas (relacionados) e Dijkstra;
     normalização, pesos, índice invertido × busca linear; De Morgan nos filtros; o que acontece com
     várias correspondências (desempate e pedido de escolha).
     Base: spec §7 e docs/arquitetura.md §5. -->

### Organização da base

_A preencher_

### Estruturas de dados utilizadas

_A preencher_

### Estratégia de busca

_A preencher_

### Grafo de temas e navegação

_A preencher_

### Fontes consultadas

<!-- Lista das fontes oficiais usadas na base, com a data de verificação. Pode ser gerada a partir do base.json. -->

| Registro | Fonte | Verificado em |
|---|---|---|
| _A preencher_ | _A preencher_ | _A preencher_ |

---

## 4. Regras de resposta, modelos de prompt e tratamento de limitações

<!-- Responsável: Integrante A (com B, que faz a comparação) · Prazo: 16/11
     Escrever: regra de decisão C·A·B (4 saídas); modelos A e B (papel, formato, obrigações e limites);
     resultado da comparação A × B e o modelo escolhido; aviso de limitação; o que o assistente nunca faz.
     Base: spec §7.3 e §8, docs/arquitetura.md §5.4. -->

### Regra de decisão

_A preencher_

### Modelo A: direto e compacto

_A preencher_

### Modelo B: estruturado em passos

_A preencher_

### Comparação entre os modelos

_A preencher_

### Tratamento de limitações

_A preencher_

---

## 5. Plano de testes, indicadores e resultados

<!-- Responsável: Integrante B · Prazo: 16/11 (indicadores fechados em 17/11)
     Escrever: as 14 perguntas + limites L1–L3 e o protocolo contra viés (perguntas congeladas antes
     das palavras-chave; conjunto do público coletado depois, anônimo); taxa de acerto da busca
     (geral, por tipo e por conjunto); tempo médio (linear × índice); rubrica A × B; teste de
     usabilidade; interpretação; pelo menos 2 melhorias; limitações da avaliação.
     Base: spec §8 e §14, testes/resultados.csv, testes/comparacao_modelos.csv, testes/usabilidade.md. -->

### Plano de testes

_A preencher_

### Indicadores da busca

<!-- A taxa de acerto e o tempo medem a busca, que é a mesma para os modelos A e B (spec §8).
     Por isso não há coluna por modelo aqui; a comparação A × B fica na tabela seguinte. -->

| Indicador | Perguntas da equipe | Perguntas do público |
|---|---|---|
| Taxa de acerto | _%_ | _%_ (antes de ajustes) |
| Tempo médio (índice invertido) | _ms_ | _ms_ |
| Tempo médio (busca linear) | _ms_ | _ms_ |

### Comparação dos modelos A e B

| Critério (spec §8) | Modelo A | Modelo B |
|---|---|---|
| Respostas com fonte e data | _x/y_ | _x/y_ |
| Aviso presente quando necessário | _x/y_ | _x/y_ |
| Tamanho médio (palavras) | _n_ | _n_ |
| Nota média de clareza (1–5) | _n_ | _n_ |

### Teste de usabilidade

_A preencher_

### Interpretação dos resultados

_A preencher_

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
| `python src/sistema.py --servidor` | Sobe o bot do Telegram, o painel e o agendador (precisa de `.env`; ver `.env.example`) |
| `python -m unittest discover -s testes -t .` | Roda os testes automatizados |

<!-- TODO: ajustar se algum modo mudar durante a implementação (spec §6.1). -->

---

## 7. Exemplos de uso

<!-- Responsável: Integrante B · Prazo: 16/11
     Copiar saídas reais do terminal (não inventar). Incluir: pergunta direta, reformulada,
     ambígua (pedir escolha), fora da base (aviso de limitação), entrada vazia e opção inexistente. -->

### Pergunta com resposta e fonte

```text
A preencher com uma saída real do terminal
```

### Pergunta ambígua

```text
A preencher
```

### Pergunta fora da base

```text
A preencher
```

### Entradas inválidas

```text
A preencher
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

_A preencher_

### Limitações

_A preencher_

### Melhorias e roadmap

_A preencher_

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
