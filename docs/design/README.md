# Design do Citizen Assist AI

Identidade visual **Estreia clara**, aprovada pela equipe em 07/11/2026.
Conceito: **cinema a serviço da confiança**. A leitura do dia a dia acontece em claro e arejado. Os momentos-chave (abertura, desbloqueio do cofre, cena da verificação, vídeo) acontecem em escuro, com luz âmbar.

> Regras completas de interface, textos, acessibilidade e roteiro de usabilidade: [`docs/ux.md`](../ux.md) (identidade na §9). Decisões que valem para o código: spec §5.4, §10.5 e §19.

## O que tem nesta pasta

| Arquivo | Para quê | Quem usa |
|---|---|---|
| [`tokens.css`](tokens.css) | Variáveis CSS (cores claro e cinema, fontes, espaços, cantos, movimento, "reduzir movimento") | Pedro, no `painel/` |
| [`tokens.json`](tokens.json) | Os mesmos valores em JSON, mais as cores do terminal e as regras do símbolo | Juan (cores ANSI do terminal) e quem gerar gráficos do relatório |
| `imagens/` | Imagens exportadas do manual de marca e das telas (PNG), para o README, o relatório e o vídeo | Todos |

## Foto de perfil do bot

`imagens/avatar-bot.png` (1024 × 1024) e `imagens/avatar-bot.svg` (vetor). Segue a regra do símbolo: fundo âmbar `#F5B544` e símbolo `#0B0D12` (anel da lente com o sinal de conferido), sem o arco de luz. O símbolo fica dentro do círculo central, então o recorte redondo do Telegram não corta nada.

Para usar: no @BotFather, `/setuserpic`, escolha o bot e envie o `avatar-bot.png`.

## Resumo da identidade

| | Claro (dia a dia) | Cinema (escuro) |
|---|---|---|
| Fundo | `#F5F6F8` | `#0B0D12` |
| Texto | `#0B0D12` | `#F2EEE6` |
| Âmbar (ação, números, selo) | `#8A5300` · botão `#F5B544` | `#F5B544` |
| Ciano (links, fonte) | `#0E6E7A` | `#6FD3E0` |
| Atenção | `#B0391B` | `#FF8A6B` |

- **Fontes** (gratuitas, licença OFL): títulos em **Archivo** condensada, peso 800, caixa alta só em títulos curtos; texto em **Atkinson Hyperlegible**, feita para leitura com baixa visão.
- **Símbolo:** uma lente com sinal de conferido, que representa a fonte conferida.
- **Movimento:** só opacidade e posição, 150/300/450 ms. Com "reduzir movimento", nada se mexe.
- **Contraste:** todos os textos passam no WCAG AA; as bordas de campos passam no mínimo de 3:1.

## Canvas de design (claude.ai, privados)

Os arquivos editáveis estão em canvas do claude.ai. **Só abre quem recebeu acesso** pelo menu Share do dono. Por isso as imagens exportadas ficam em `imagens/`, que qualquer pessoa vê no GitHub.

| Canvas | Conteúdo |
|---|---|
| [Manual de marca](https://claude.ai/artifact/5jG18T8avoxzQ2YhSUd8zm) | 8 pranchas: conceito, símbolo, cores, tipografia, ícones, voz, movimento e aplicações |
| [Telas](https://claude.ai/artifact/TiNyp7dFzrcgfsrriizCxo) | Protótipos clicáveis: painel (P0 a P7, com a cena da verificação), Telegram (6 cenas) e terminal |
| [Wireframes](https://claude.ai/artifact/T3RUAHaEZy8zYef4SVgW85) | Estrutura do terminal (modo simples) e as primeiras direções de identidade |
| [Pesquisa](https://claude.ai/artifact/AcRYZX7E9wbCfoJ17WjSGW) | Achados da direção cinematográfica e matriz de pontos de contato |

## Como exportar as imagens

1. Abra o canvas e use **Share › Export**.
2. Salve em PNG com nomes curtos, sem espaços:
   - `manual-01-conceito.png` … `manual-08-aplicacoes.png`;
   - `tela-painel-perguntar.png`, `tela-painel-cena.png`, `tela-painel-documentos.png`;
   - `tela-telegram-resposta.png`;
   - `tela-terminal-identidade.png`.
3. Coloque os arquivos em `docs/design/imagens/` e faça o commit.

Imagens e protótipos usam **texto de exemplo** nas orientações (`[texto da equipe]`) e documentos fictícios. O conteúdo real vem do `data/base.json`.

## Referências

Usadas só como inspiração, sem copiar layouts, imagens ou marcas: templates Therapist, Pediatrician e Study Planner (lovable.dev/templates) e manuais Brand Manual Landscape e Brand Strategy Guide (Adobe Stock). Registro em [`docs/uso_ia.md`](../uso_ia.md).
