# Roteiro de teste no Telegram real (item 9)

Use **só documentos fictícios** (spec §10.1). Marque cada linha e anote data, quem testou e o que viu. Rode com o servidor local (`python src/sistema.py --servidor`) ou na VM.

| # | O que fazer | Resultado esperado | OK? | Obs. |
|---|---|---|---|---|
| 1 | Mandar uma foto de documento **fictício** com o cofre fechado | O bot não guarda; mostra botão "Desbloquear no painel" | | |
| 2 | Abrir `/painel`, criar o cofre (senha ≥ 10 caracteres) e desbloquear | Cofre desbloqueado com contador | | |
| 3 | Reenviar a foto | Aviso de consentimento do Gemini (plano gratuito) na primeira vez | | |
| 4 | Aceitar e confirmar o nome sugerido | Documento salvo com o nome confirmado | | |
| 5 | Repetir com um PDF e editando o nome | Salvo com o nome digitado | | |
| 6 | Escolher nome próprio sem usar a sugestão | Arquivo **não** é enviado ao Gemini | | |
| 7 | Escrever "me envie meu RG" | Documento chega e a mensagem some em 5 min | | |
| 8 | Esperar o desbloqueio expirar (10 min) e pedir o documento | Bot pede novo desbloqueio | | |
| 9 | Painel: listar, visualizar e apagar um documento (2 passos) | Some da lista e do armazenamento | | |
| 10 | Criar lembrete pelo chat e pelo painel (aba Tarefas) | Aviso chega na hora; lembrete avisado vai para "Já avisadas" | | |
| 11 | Painel → Ajustes: escolher temas (Música, Filmes...) e horário | Resumo da manhã chega com até 3 manchetes por tema, rotuladas "não oficial" | | |
| 12 | Abrir o painel como Mini App dentro do Telegram | Login pelo `initData`, 4 abas funcionando | | |
| 13 | Enviar 2 perguntas seguidas, a primeira caindo no Gemini | Respostas chegam na ordem | | |
| 14 | `/apagar_meus_dados` → "Sim, apagar tudo" | Cofre, tarefas, UF e temas somem | | |

Falhou algo? Abra uma issue com o número da linha, sem anexar documento real nem token.
