# CODEBASE_MAP

Mapa curto do repositório (atualizar ao criar ou mover módulos).

| Caminho | Papel | Estado (07/11/2026) |
|---|---|---|
| `src/sistema.py` | Terminal (padrão), `--avaliar`, `--validar-entrega`; `--servidor` ainda não existe | Pronto |
| `src/base.py` | Carga e validação de `data/base.json`; pendências de entrega | Pronto |
| `src/busca.py` | Normalização, pontuação, índice × linear, decisão C·A·B, grafo, Dijkstra | Pronto |
| `src/respostas.py` | Modelos A e B, aviso de limitação, mensagens de entrada inválida | Pronto |
| `src/avaliacao.py` | Taxa de acerto, tempos, escala, rubrica A × B, CSVs | Pronto |
| `data/base.json` | 17 registros, 3 temas, sinônimos (vazio) | Orientações em rascunho (sem revisão humana) |
| `testes/perguntas.json` | 19 perguntas do conjunto `equipe` | Congelado; conjunto `publico` pendente |
| `testes/test_*.py` | 94 testes (`python -m unittest discover -s testes -t .`) | Passando |
| `testes/resultados.csv`, `comparacao_modelos.csv` | Saída de `--avaliar` (versionados com `git add -f`) | Gerados em 07/11 |
| `scripts/verificacoes_antigas.py` | Lista registros com verificação > 90 dias | Pronto |
| `docs/` | Spec (fonte de verdade), planejamento, arquitetura, UX, `uso_ia.md` | Atualizados em 07/11 |
| Onda 2 (`telegram_bot`, `roteador`, `cofre`, `painel`, ...) | Não existem nesta branch | Pendente |
