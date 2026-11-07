# CODEBASE_MAP
Mapa curto do repositório (atualizar ao criar ou mover módulos).
| Caminho | Papel | Estado (07/11/2026) |
|---|---|---|
| `src/sistema.py` | Terminal (padrão), `--avaliar`, `--validar-entrega`; `--servidor` chama `servidor.py` | Pronto |
| `src/base.py` | Carga e validação de `data/base.json`; pendências de entrega | Pronto |
| `src/busca.py` | Normalização, pontuação, índice × linear, decisão C·A·B, grafo, Dijkstra | Pronto |
| `src/respostas.py` | Modelos A e B, aviso de limitação, mensagens de entrada inválida | Pronto |
| `src/avaliacao.py` | Taxa de acerto, tempos, escala, rubrica A × B, CSVs | Pronto |
| `data/base.json` | 17 registros, 3 temas, sinônimos (vazio) | Orientações em rascunho (sem revisão humana) |
| `testes/perguntas.json` | 19 perguntas do conjunto `equipe` | Congelado; conjunto `publico` pendente |
| `testes/test_*.py` | 127 testes (`python -m unittest discover -s testes -t .`) | Passando |
| `testes/usabilidade.md` | Modelo do teste de usabilidade (T1 a T5, clareza, SUS) | Modelo vazio; teste pendente |
| `testes/resultados.csv`, `comparacao_modelos.csv` | Saída de `--avaliar` (versionados com `git add -f`) | Gerados em 07/11 |
| `scripts/testar_gemini.py` | Testa a chave do Gemini do `.env` e lista os modelos que ela enxerga | Pronto; rodar com o ambiente do servidor |
| `scripts/verificacoes_antigas.py` | Lista registros com verificação > 90 dias | Pronto |
| `cspell.json`, `.vscode/extensions.json` | Corretor ortográfico em pt-BR e extensões recomendadas do VS Code (sem o dicionário português, o cSpell marca todo texto em português) | Pronto |
| `docs/` | Spec (fonte de verdade), planejamento, arquitetura, UX, `uso_ia.md` | Atualizados em 07/11 |
| `src/ponte.py` | Liga o servidor ao núcleo (preparar, buscar, formatar, UF) | Pronto, testado |
| `src/roteador.py`, `telegram_bot.py`, `painel.py`, `armazenamento.py`, `servidor.py` | Servidor base: roteador Gemini + regras, bot, API do painel, SQLite, `--servidor` | Escritos; testados só sem Telegram/Gemini/VM reais (as bibliotecas não estão instaladas aqui) |
| `deploy/`, `.github/workflows/deploy.yml`, `requirements.txt` | Caddy, systemd e deploy por SSH | Não testados em VM |
| Onda 2 restante (`cofre`, `criptografia`, `classificador`, `tarefas`, `agendador`, `briefing`, front do painel) | Não existem ainda | Pendente |
