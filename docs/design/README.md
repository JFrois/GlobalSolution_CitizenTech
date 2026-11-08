# Design do Citizen Assist AI

Identidade visual **Azul Telegram**, aprovada em 08/11/2026 (substitui a "Estreia clara" de 07/11).
Conceito: **calma e confiança**. Faixa azul com o título, folha clara com o conteúdo, cartões arredondados, botões em pílula e animação de entrada. O azul é o mesmo do Telegram, para painel, bot e terminal parecerem um produto só.

> Regras completas de interface, textos, acessibilidade e roteiro de usabilidade: [`docs/ux.md`](../ux.md) (identidade na §9). Decisões que valem para o código: spec §5.4, §10.5 e §19.

## O que tem nesta pasta

| Arquivo | Para quê | Quem usa |
|---|---|---|
| [`tokens.css`](tokens.css) | Variáveis CSS (cores claro e cinema, fontes, espaços, cantos, movimento, "reduzir movimento") | Pedro, no `painel/` |
| [`tokens.json`](tokens.json) | Os mesmos valores em JSON, mais as cores do terminal e as regras do símbolo | Juan (cores ANSI do terminal) e quem gerar gráficos do relatório |
| `imagens/` | Avatar do bot e, depois, imagens exportadas das telas (PNG), para o README, o relatório e o vídeo | Todos |
| `prototipo/` | Código das telas animadas (referência para o `painel/`) | Pedro, no `painel/` |

## Foto de perfil do bot

`imagens/avatar-bot.png` (1024 × 1024) e `imagens/avatar-bot.svg` (vetor): degradê azul do Telegram (`#2AABEE` para `#1A86C2`) e símbolo branco (lente com sinal de conferido), sem arco. O símbolo fica dentro do círculo central, então o recorte redondo do Telegram não corta nada.

Para usar: no @BotFather, `/setuserpic`, escolha o bot e envie o `avatar-bot.png`.

## Resumo da identidade

| | Valor |
|---|---|
| Azul da marca (decoração e degradê) | `#229ED9` |
| Ação (botão, item ativo) | `#12689E` |
| Folha clara / texto | `#F2F8FC` / `#0E2233` |
| Selo "Fonte conferida" | `#0F7A5A` |
| Atenção | texto `#5E1F0B` sobre `#FDE7DF` |

- **Fonte** (gratuita, licença OFL): **Plus Jakarta Sans** em tudo; **JetBrains Mono** no terminal.
- **Movimento:** só opacidade e escala; com "reduzir movimento", nada se mexe.
- **Contraste:** textos passam no WCAG AA; o azul da marca não é usado em texto pequeno.

## Protótipo (`prototipo/`)

Código-fonte das 6 telas animadas da identidade (painel: Perguntar, Cena da verificação, Resposta, Cofre e Ajustes; mais o Terminal), no formato do canvas de revisão de UI do claude.ai: https://claude.ai/artifact/VLaxzKY5pHx7NYm9utVwLc (privado; o dono compartilha pelo menu Share).

- Cada `*.dc.html` é uma tela com HTML e CSS inline, animações em CSS e fonte do Google Fonts. Servem de **referência** para o `painel/`: copie estrutura, medidas e animações, trocando os valores fixos pelos tokens de `tokens.css`.
- `canvas.json` guarda a posição das telas no canvas.
- Os textos são de exemplo (`[texto da equipe]`) e os documentos são fictícios. O conteúdo real vem do `data/base.json`.

## Referências

Usadas só como inspiração, sem copiar layouts, imagens ou marcas: templates do Lovable (To-Do List, Study Planner, Debt Payoff Planner, Pomodoro Timer, Meeting Booker, Project Management Board, Flashcard App e outros), vistos rodando em 08/11/2026. Registro em [`docs/uso_ia.md`](../uso_ia.md).
