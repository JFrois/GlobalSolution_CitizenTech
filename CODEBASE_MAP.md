# CODEBASE_MAP
Mapa curto do repositório (atualizar ao criar ou mover módulos).
| Caminho | Papel | Estado (07/11/2026) |
|---|---|---|
| `src/sistema.py` | Terminal (padrão), `--avaliar`, `--validar-entrega`; `--servidor` chama `servidor.py` | Pronto |
| `src/base.py` | Carga e validação de `data/base.json`; pendências de entrega | Pronto |
| `src/busca.py` | Normalização, pontuação, índice × linear, decisão C·A·B, correção de digitação (só em SEM_BASE), grafo, Dijkstra | Pronto |
| `src/respostas.py` | Modelos A e B, aviso de limitação, mensagens de entrada inválida | Pronto |
| `src/avaliacao.py` | Taxa de acerto, tempos, escala, rubrica A × B, CSVs | Pronto |
| `data/base.json` | 17 registros, 3 temas, sinônimos (vazio) | Orientações em rascunho (sem revisão humana) |
| `testes/perguntas.json` | 19 perguntas do conjunto `equipe` | Congelado; conjunto `publico` pendente |
| `testes/test_*.py` | 147 testes (`python -m unittest discover -s testes -t .`) | Passando (CI em Python 3.9) |
| `testes/usabilidade.md` | Modelo do teste de usabilidade (T1 a T5, clareza, SUS) | Modelo vazio; teste pendente |
| `testes/resultados.csv`, `comparacao_modelos.csv` | Saída de `--avaliar` (versionados com `git add -f`) | Gerados em 07/11 |
| `scripts/testar_gemini.py` | Testa a chave do Gemini do `.env` e lista os modelos que ela enxerga | Pronto; rodar com o ambiente do servidor |
| `scripts/verificacoes_antigas.py` | Lista registros com verificação > 90 dias | Pronto |
| `cspell.json`, `.vscode/extensions.json` | Corretor ortográfico em pt-BR e extensões recomendadas do VS Code (sem o dicionário português, o cSpell marca todo texto em português) | Pronto |
| `docs/` | Spec (fonte de verdade), planejamento, arquitetura, UX, `uso_ia.md` | Atualizados em 07/11 |
| `src/ponte.py` | Liga o servidor ao núcleo (preparar, buscar, formatar, UF) | Pronto, testado |
| `src/transcricao.py` | Voz -> texto com Whisper local (import tardio, precisa de ffmpeg) | Testado com Whisper falso e com áudio real no Telegram (07/11); falta testar na VM |
| `src/roteador.py`, `telegram_bot.py`, `painel.py`, `armazenamento.py`, `servidor.py` | Servidor base: roteador Gemini + regras, bot, API do painel, SQLite, `--servidor` | Bot, UF, voz e roteador **testados no Telegram real** (07/11); painel (`/painel`), Supabase e VM ainda não |
| `deploy/`, `.github/workflows/deploy.yml`, `requirements.txt` | Caddy, systemd e deploy por SSH | Não testados em VM |
| `src/criptografia.py`, `src/cofre.py`, `src/classificador.py` | PBKDF2 + AES-GCM, cofre por `user_id`, tipo do documento via Gemini (lista fechada) | Testados (unitários); Gemini real e Telegram ainda não |
| `painel/` (`index.html`, `painel.js`, `painel.css`, `tokens.css`) + rotas em `src/painel.py` | Front estático: Perguntar (cena da verificação), Cofre, Ajustes; API do cofre e config | Testado no navegador local e por testes; Mini App no Telegram real não |
| `src/tarefas.py`, `src/agendador.py` | Tarefas e lembretes (data lida por regras, fuso Brasília), tick do APScheduler que cumpre lembretes e exclusões vencidas (estado no SQLite) | Testados (unitários + APScheduler real); Telegram real ainda não |
| `src/briefing.py`, `data/feeds.json` | Resumo da manhã: tarefas do dia + até 3 manchetes/tema (rotuladas "não oficial"), feed com erro é pulado; horário por usuário (painel ou chat) | Testado com coletor falso; **feeds por tema vazios (EM ABERTO, equipe escolhe)**; feed real e Telegram não testados |
| Onda 2 restante (foto/PDF no bot) | Não existe ainda | Pendente |
