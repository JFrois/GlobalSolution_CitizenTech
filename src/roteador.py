"""Roteador: escolhe UMA de 4 ferramentas (LLM com function calling + regras).

Princípio (spec §1 e §9): o LLM só ESCOLHE a ferramenta. O conteúdo da
orientação vem sempre de busca.py + ponte.py. Os argumentos devolvidos pelo
LLM passam por validação estrita; se algo falhar, o fallback por regras assume,
então o bot nunca fica mudo. Texto de documentos é dado, nunca instrução.

Este módulo só usa a biblioteca padrão; o Gemini é importado dentro de
`chamar_gemini` (import tardio).
"""
from __future__ import annotations

import logging
import re

import ponte

# Cascata de modelos Gemini: tenta na ordem; se um falhar, passa ao próximo.
# O primeiro é o padrão. TODO (EM ABERTO): confirmar os nomes no plano pago (spec §12).
MODELOS_GEMINI = ("gemini-4-argon", "gemini-3.1-pro-preview", "gemini-3.8-flash")
MODELO_GEMINI = MODELOS_GEMINI[0]
log = logging.getLogger("citizen.llm")
TEMPO_LIMITE_LLM = 15  # segundos no total; usado por quem chama (telegram_bot)
# Cada tentativa tem o próprio limite. Erro 429 volta em menos de 1 s, então só o modelo
# lento gasta esse tempo; 6 s bastam para o function calling de um modelo flash.
TEMPO_POR_MODELO_MS = 6000

FERRAMENTAS = ("buscar_orientacao", "cofre_documento", "gerenciar_tarefas", "briefing_matinal")

# Esquema estrito de cada ferramenta: nome do argumento -> (tipo, obrigatório, opções)
ESQUEMAS = {
    "buscar_orientacao": {"pergunta": (str, True, None)},
    "cofre_documento": {"acao": (str, True, ("enviar", "listar", "abrir")),
                        "nome": (str, False, None)},
    "gerenciar_tarefas": {"acao": (str, True, ("criar", "listar", "concluir")),
                          "titulo": (str, False, None), "quando": (str, False, None)},
    "briefing_matinal": {"acao": (str, True, ("agora", "configurar")),
                         "temas": (list, False, None), "hora": (str, False, None)},
}
TAMANHO_MAX_TEXTO = 300

MSG_EM_BREVE = ("Essa função ainda não está disponível nesta versão. "
                "Por enquanto posso orientar sobre documentos, serviços e direitos.")


def validar_chamada(nome, args):
    """Valida nome e argumentos. Devolve a chamada limpa ou None se inválida."""
    esquema = ESQUEMAS.get(nome)
    if esquema is None or not isinstance(args, dict):
        return None
    if set(args) - set(esquema):
        return None  # argumento desconhecido
    limpo = {}
    for campo, (tipo, obrigatorio, opcoes) in esquema.items():
        if campo not in args or args[campo] is None:
            if obrigatorio:
                return None
            continue
        valor = args[campo]
        if not isinstance(valor, tipo):
            return None
        if tipo is str:
            valor = valor.strip()
            if not valor or len(valor) > TAMANHO_MAX_TEXTO:
                return None
            if opcoes and valor not in opcoes:
                return None
        if tipo is list:
            if len(valor) > 10 or not all(isinstance(v, str) and 0 < len(v) <= 50 for v in valor):
                return None
        if campo == "hora" and not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", valor):
            return None
        limpo[campo] = valor
    return {"ferramenta": nome, "args": limpo}


def fallback_por_regras(texto):
    """Escolha determinística por palavras-chave simples. Padrão: buscar."""
    palavras = " ".join(ponte.tokenizar(texto))
    if re.search(r"\b(cofre|guardar|guarde|me envie|meus documentos)\b", palavras):
        return {"ferramenta": "cofre_documento", "args": {"acao": "listar"}}
    if re.search(r"\b(lembrete|lembre|tarefa|tarefas)\b", palavras):
        return {"ferramenta": "gerenciar_tarefas", "args": {"acao": "listar"}}
    if re.search(r"\b(briefing|manchetes|noticias|resumo do dia)\b", palavras):
        return {"ferramenta": "briefing_matinal", "args": {"acao": "agora"}}
    return {"ferramenta": "buscar_orientacao", "args": {"pergunta": texto.strip()[:TAMANHO_MAX_TEXTO]}}


def rotear(texto, llm=None):
    """Decide a ferramenta. `llm(texto) -> (nome, args)` é opcional e injetável.

    Qualquer falha do LLM (exceção, tempo, resposta inválida) cai no fallback.
    """
    if llm is not None:
        try:
            nome, args = llm(texto)
            chamada = validar_chamada(nome, args)
            if chamada is not None:
                return chamada
        except Exception:  # LLM fora do ar, tempo esgotado, saída malformada...
            pass
    return fallback_por_regras(texto)


def chamar_gemini(texto, api_key, modelos=None):
    """Pede ao Gemini (function calling) a ferramenta, percorrendo a cascata de modelos.

    `modelos` (opcional) substitui a cascata; o .env pode trazer GEMINI_MODELO,
    que vira o primeiro da lista. Import tardio da biblioteca.
    """
    from google import genai
    from google.genai import types

    def declarar(nome, descricao, props, obrigatorios):
        return types.FunctionDeclaration(
            name=nome, description=descricao,
            parameters=types.Schema(type=types.Type.OBJECT, properties=props, required=obrigatorios))

    texto_s = types.Schema(type=types.Type.STRING)
    declaracoes = [
        declarar("buscar_orientacao", "Dúvida sobre documentos, serviços públicos ou direitos.",
                 {"pergunta": texto_s}, ["pergunta"]),
        declarar("cofre_documento", "Guardar, listar ou pedir de volta um documento do cofre.",
                 {"acao": types.Schema(type=types.Type.STRING, enum=["enviar", "listar", "abrir"]),
                  "nome": texto_s}, ["acao"]),
        declarar("gerenciar_tarefas", "Criar, listar ou concluir tarefas e lembretes.",
                 {"acao": types.Schema(type=types.Type.STRING, enum=["criar", "listar", "concluir"]),
                  "titulo": texto_s, "quando": texto_s}, ["acao"]),
        declarar("briefing_matinal", "Ver ou configurar o resumo matinal.",
                 {"acao": types.Schema(type=types.Type.STRING, enum=["agora", "configurar"]),
                  "temas": types.Schema(type=types.Type.ARRAY, items=texto_s), "hora": texto_s}, ["acao"]),
    ]
    cliente = genai.Client(api_key=api_key,
                           http_options=types.HttpOptions(timeout=TEMPO_POR_MODELO_MS))
    config = types.GenerateContentConfig(
        tools=[types.Tool(function_declarations=declaracoes)],
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode=types.FunctionCallingConfigMode.ANY)),
        # Só queremos saber qual ferramenta escolher; não deixar o SDK executar nada sozinho.
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True, maximum_remote_calls=None))
    ultimo_erro = None
    for modelo in (modelos or MODELOS_GEMINI):
        try:
            log.info("Gemini: tentando o modelo %s", modelo)
            resposta = cliente.models.generate_content(model=modelo, contents=texto, config=config)
            candidatos = resposta.candidates or []
            conteudo = candidatos[0].content if candidatos else None
            partes = (conteudo.parts if conteudo else None) or []
            chamada = partes[0].function_call if partes else None
            if chamada is None or not chamada.name:
                raise ValueError("resposta sem chamada de função")
            # Log sem o texto da mensagem (spec §13): só o modelo e a ferramenta escolhida.
            log.info("Gemini: o modelo %s respondeu (ferramenta %s)", modelo, chamada.name)
            return chamada.name, dict(chamada.args or {})
        except Exception as erro:  # modelo indisponível ou resposta vazia: tenta o próximo
            ultimo_erro = erro
            log.warning("Gemini: o modelo %s falhou (%s %s)", modelo, type(erro).__name__,
                        getattr(erro, "code", ""))
    # Todos falharam: quem chama cai no fallback por regras.
    raise ultimo_erro or RuntimeError("nenhum modelo Gemini configurado")


def executar(chamada, base, uf=None):
    """Executa a ferramenta escolhida. Devolve {"texto", "opcoes", "decisao"}.

    `opcoes` é a lista de ids de assuntos que a interface pode oferecer como botões.
    """
    if chamada["ferramenta"] != "buscar_orientacao":
        # Cofre, tarefas e briefing entram na próxima rodada (roadmap).
        return {"texto": MSG_EM_BREVE, "opcoes": [], "decisao": "EM_BREVE"}

    ponte.preparar(base)
    pergunta = chamada["args"]["pergunta"]
    r = ponte.buscar(pergunta, base)
    por_id = base["registros_por_id"]
    if r["decisao"] == "INVALIDA":
        return {"texto": ponte.MSG_SEM_PALAVRA, "opcoes": [], "decisao": "INVALIDA"}
    if r["decisao"] == "SEM_BASE":
        return {"texto": ponte.aviso_sem_base(base["temas"]), "opcoes": [],
                "decisao": "SEM_BASE"}
    if r["decisao"] == "PEDIR_ESCOLHA":
        ids = [c[0] for c in r["candidatos"]]
        return {"texto": ponte.pedir_escolha([por_id[i] for i in ids]),
                "opcoes": ids, "decisao": "PEDIR_ESCOLHA"}
    return resposta_do_assunto(base, r["candidatos"][0][0], uf)


def resposta_do_assunto(base, rid, uf=None, modelo="B"):
    """Resposta completa de um assunto (modelo B por padrão no bot)."""
    ponte.preparar(base)
    ids = ponte.relacionados(base, rid)
    regs = [base["registros_por_id"][i] for i in ids]
    reg = base["registros_por_id"][rid]
    texto = ponte.formatar(reg, modelo, regs, uf=uf)
    # "html" é a versão para o Telegram (negrito, link); "texto" serve ao terminal e aos testes.
    return {"texto": texto, "html": ponte.formatar_telegram(reg, uf=uf), "opcoes": ids,
            "decisao": "RESPONDER", "registro": rid}
