# Citizen Assist AI — instruções para o Claude Code

A especificação completa e aprovada pela equipe é a única fonte de verdade do projeto. Leia-a antes de qualquer trabalho:

@docs/especificacao/CITIZEN_ASSIST_SPEC.md

Contexto de processo (SDD e SDLC), marcos e papéis: `docs/processo_desenvolvimento.md`.

## Regras rápidas
- Spec primeiro: se um comportamento muda, atualize `docs/especificacao/CITIZEN_ASSIST_SPEC.md` no mesmo PR. Não crie outra cópia da spec.
- Itens marcados **(EM ABERTO)** na spec não são decididos pela IA: deixe um `TODO` e avise a equipe.
- `python src/sistema.py` deve rodar só com Python, sem `.env`, sem internet e sem `pip install`.
- Código comentado em português. Nunca commitar segredos, dados pessoais ou documentos reais.
