"""Roteador: escolhe UMA de 4 ferramentas (LLM com function calling + regras).

Princípio (spec §1 e §9): o LLM só ESCOLHE a ferramenta. O conteúdo da
orientação vem sempre de busca.py + ponte.py. Os argumentos devolvidos pelo
LLM passam por validação estrita; se algo falhar, o fallback por regras assume,
então o bot nunca fica mudo. Texto de documentos é dado, nunca instrução.

Este módulo só usa a biblioteca padrão; o Gemini é importado dentro de
`chamar_gemini` (import tardio).
"""
from __future__ import annotations

import difflib
import logging
import re
import time

import ponte

# Cascata de modelos Gemini: o bot percorre TODOS os modelos de texto que a chave enxerga, do
# mais leve ao mais pesado, até um responder. A tarefa é só escolher 1 de 4 ferramentas, então
# os modelos "lite" e "flash" vêm primeiro; os "pro" por último. Se um falha (cota 429,
# sobrecarga 503, tempo esgotado, nome sem function calling), ele fica de fora por um tempo e o
# próximo é tentado. GEMINI_MODELO (no .env) vira o primeiro da fila.
#
# MODELOS_GEMINI é só a lista de reserva, usada se a descoberta pela chave falhar.
MODELOS_GEMINI = ("gemini-flash-lite-latest", "gemini-flash-latest",
                  "gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro")
log = logging.getLogger("citizen.llm")
PRAZO_TOTAL_S = 25  # segundos para tentar modelos numa mesma mensagem (o bot espera este tempo)
TEMPO_LIMITE_LLM = PRAZO_TOTAL_S + 5  # limite externo de quem chama (telegram_bot)
TEMPO_POR_MODELO_MS = 6000  # cada tentativa tem o próprio limite; 429 volta em menos de 1 s
VALIDADE_DA_LISTA_S = 3600  # a lista de modelos da chave é consultada de hora em hora

# Modelos que não servem para escolher ferramenta (imagem, voz, agente de tela, robótica...).
EXCLUIR_NO_NOME = ("image", "tts", "transcribe", "computer-use", "robotics", "customtools",
                   "nano-banana", "embedding", "live", "audio", "omni")

# Modelos em "geladeira": nome -> instante (time.time) até quando ficam de fora.
_de_fora = {}
_lista_em_cache = {"valida_ate": 0.0, "nomes": []}


def ordenar_modelos(nomes):
    """Filtra e ordena os nomes de modelo: lite, depois flash, depois pro, depois o resto.
    Dentro de cada grupo, "-latest" primeiro, versões estáveis antes das "preview"."""
    uteis = sorted({n.replace("models/", "") for n in nomes
                    if "gemini" in n and not any(x in n for x in EXCLUIR_NO_NOME)})

    def chave(nome):
        flash, leve, pro = "flash" in nome, "lite" in nome, "pro" in nome
        grupo = 0 if (flash and leve) else 1 if flash else 2 if pro else 3
        return (grupo, 0 if "latest" in nome else 1, 1 if "preview" in nome else 0, nome)

    return sorted(uteis, key=chave)


def pausa_depois_de_falhar(erro):
    """Quantos segundos o modelo fica de fora depois de um erro."""
    codigo = getattr(erro, "code", None)
    if codigo == 429:  # sem cota: demora a voltar
        return 600
    if codigo == 404:  # nome que não existe para esta chave
        return 3600
    if codigo in (400, 403):  # pedido ou chave recusados
        return 600
    return 120  # 503, tempo esgotado, resposta vazia: costuma passar logo


def percorrer(modelos, tentar, agora=time.time, prazo_s=PRAZO_TOTAL_S):
    """Chama tentar(modelo) em cada modelo, na ordem, até um devolver resultado.

    Pula os que estão em pausa e para ao estourar o prazo. Se nenhum responder, levanta o
    último erro (quem chama usa o fallback por regras, então o bot nunca fica mudo)."""
    inicio, ultimo_erro = agora(), None
    for modelo in modelos:
        if agora() - inicio > prazo_s:
            log.warning("Gemini: prazo de %ss esgotado", prazo_s)
            break
        if _de_fora.get(modelo, 0) > agora():
            continue
        try:
            log.info("Gemini: tentando o modelo %s", modelo)
            resultado = tentar(modelo)
            _de_fora.pop(modelo, None)
            return resultado
        except Exception as erro:
            ultimo_erro = erro
            _de_fora[modelo] = agora() + pausa_depois_de_falhar(erro)
            log.warning("Gemini: o modelo %s falhou (%s %s)", modelo, type(erro).__name__,
                        getattr(erro, "code", ""))
    raise ultimo_erro or RuntimeError("nenhum modelo Gemini disponível agora")


def modelos_da_chave(cliente, agora=time.time):
    """Lista de modelos de texto que a chave enxerga, já ordenada (com cache de 1 hora)."""
    if _lista_em_cache["nomes"] and _lista_em_cache["valida_ate"] > agora():
        return _lista_em_cache["nomes"]
    try:
        nomes = [m.name or "" for m in cliente.models.list()
                 if "generateContent" in (getattr(m, "supported_actions", None) or [])]
        ordenados = ordenar_modelos(nomes)
    except Exception as erro:
        log.warning("Gemini: não consegui listar os modelos (%s); usando a lista de reserva",
                    type(erro).__name__)
        ordenados = []
    if not ordenados:
        ordenados = list(MODELOS_GEMINI)
    _lista_em_cache.update(valida_ate=agora() + VALIDADE_DA_LISTA_S, nomes=ordenados)
    log.info("Gemini: %d modelos na cascata (o primeiro é %s)", len(ordenados), ordenados[0])
    return ordenados


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

# Mensagem por função ainda sem implementação (diz QUAL função, em vez de uma frase genérica).
MSG_EM_BREVE_POR_FERRAMENTA = {
    "gerenciar_tarefas": "As tarefas e lembretes não estão disponíveis agora.",
}
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


# Palavras (já normalizadas) que, sozinhas junto de "tarefa"/"lembrete", pedem a lista de pendentes.
PALAVRAS_DE_LISTAGEM = {"lembrete", "lembretes", "tarefa", "tarefas", "minhas", "minha", "meus", "meu",
                        "ver", "listar", "lista", "mostrar", "mostre", "quais", "qual", "pendentes",
                        "pendente", "tenho", "hoje", "amanha", "semana", "todas", "todos"}


PALAVRAS_DE_TAREFA = ("tarefa", "tarefas", "lembrete", "lembretes")
# Palavras reais parecidas com "tarefa" que NÃO podem virar tarefa ("Tarifa Social de Energia").
NAO_CORRIGIR = {"tarifa", "tarifas"}


def corrigir_digitacao_de_tarefa(tokens):
    """"tareda" -> "tarefa", "lembrte" -> "lembrete": o roteamento de tarefas exige a palavra certa."""
    saida = []
    for t in tokens:
        if len(t) >= 5 and t not in NAO_CORRIGIR and t not in PALAVRAS_DE_TAREFA:
            parecida = difflib.get_close_matches(t, PALAVRAS_DE_TAREFA, n=1, cutoff=0.8)
            if parecida:
                t = parecida[0]
        saida.append(t)
    return saida


def fallback_por_regras(texto):
    """Escolha determinística por palavras-chave simples. Padrão: buscar."""
    palavras = " ".join(corrigir_digitacao_de_tarefa(ponte.tokenizar(texto)))
    # "me" e "meu" são stopwords e somem em `palavras`: o pedido de envio usa o texto cru.
    cru = " ".join(re.findall(r"\w+", texto.lower()))
    if re.search(r"\b(guardar|guarde|salvar|salve)\b", palavras):
        return {"ferramenta": "cofre_documento", "args": {"acao": "enviar"}}
    if re.search(r"\b(briefing|manchetes|noticias|resumo do dia)\b", palavras):
        return {"ferramenta": "briefing_matinal", "args": {"acao": "agora"}}
    if re.search(r"\bme (envie|mande|mostre|manda)\b", cru):
        nome = " ".join(p for p in palavras.split()
                        if p not in ("envie", "mande", "mostre", "manda", "cofre", "documento", "documentos"))
        args = {"acao": "abrir"}
        if nome:
            args["nome"] = nome[:TAMANHO_MAX_TEXTO]
        return {"ferramenta": "cofre_documento", "args": args}
    if re.search(r"\b(cofre|meus documentos)\b", palavras) or "meus documentos" in cru:
        return {"ferramenta": "cofre_documento", "args": {"acao": "listar"}}
    if re.search(r"\b(lembrete|lembretes|lembre|tarefa|tarefas)\b", palavras):
        resto = texto.strip()[:TAMANHO_MAX_TEXTO]
        if re.search(r"\b(conclui|concluir|concluida|concluido|feita|feito)\b", palavras):
            return {"ferramenta": "gerenciar_tarefas", "args": {"acao": "concluir", "titulo": resto}}
        verbos = r"\b(lembre|lembrar|criar|crie|cria|nova|novo|anotar|anote|adicionar|adicione|agendar|marcar)\b"
        if re.search(verbos, palavras):
            # Só o pedido, sem o que anotar ("crie esta tareda"): título vazio faz a tarefa perguntar qual é.
            if not [p for p in re.sub(verbos, " ", palavras).split() if p not in PALAVRAS_DE_LISTAGEM]:
                resto = ""
            return {"ferramenta": "gerenciar_tarefas", "args": {"acao": "criar", "titulo": resto}}
        # Sem verbo: se sobrar conteúdo além das palavras de consulta ("tarefa - trabalho às 18:10"),
        # é um pedido de criação; só "minhas tarefas", "quais lembretes" etc. viram listagem.
        if [p for p in palavras.split() if p not in PALAVRAS_DE_LISTAGEM]:
            return {"ferramenta": "gerenciar_tarefas", "args": {"acao": "criar", "titulo": resto}}
        return {"ferramenta": "gerenciar_tarefas", "args": {"acao": "listar"}}
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


def chamar_gemini(texto, api_key, preferido=None):
    """Pede ao Gemini (function calling) a ferramenta, percorrendo a cascata de modelos.

    `preferido` (GEMINI_MODELO do .env) vai para o início da fila; os demais vêm da lista
    de modelos que a chave enxerga. Import tardio da biblioteca.
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
    def tentar(modelo):
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

    fila = modelos_da_chave(cliente)
    if preferido:
        fila = [preferido] + [m for m in fila if m != preferido]
    return percorrer(fila, tentar)


def resposta_direta_basta(texto, base):
    """True quando a base decide sozinha, sem precisar do Gemini.

    Vale se as regras simples mandam para a busca (nada de cofre, tarefa ou briefing) e a
    busca determinística já tem uma saída útil: responder, pedir a escolha entre candidatos
    ("documento") ou recusar entrada sem palavras ("???"). Nesses casos a IA não acrescenta
    nada e só atrasa. O Gemini fica para o que não casou com a base (SEM_BASE)."""
    if fallback_por_regras(texto)["ferramenta"] != "buscar_orientacao":
        return False
    return ponte.buscar(texto, base)["decisao"] in ("RESPONDER", "PEDIR_ESCOLHA", "INVALIDA")


def reconciliar(chamada_llm, texto):
    """Confere a escolha do Gemini com as regras simples.

    Se o Gemini escolheu uma ferramenta que ainda não existe (cofre, tarefas, briefing) mas
    nada no texto indica isso (as regras mandam para a busca), vale a busca. Senão a pessoa
    que perguntou "Como pagar o IPVA?" recebia "função não disponível"."""
    regras = fallback_por_regras(texto)
    if chamada_llm is None:
        return regras
    if chamada_llm["ferramenta"] != "buscar_orientacao" and regras["ferramenta"] == "buscar_orientacao":
        return regras
    # O texto traz uma tarefa para anotar, mas o Gemini escolheu só listar: vale a criação,
    # senão "tarefa - trabalho às 18:10" respondia "Você não tem tarefas pendentes".
    if (chamada_llm["ferramenta"] == regras["ferramenta"] == "gerenciar_tarefas"
            and regras["args"].get("acao") == "criar" and chamada_llm["args"].get("acao") == "listar"):
        return regras
    return chamada_llm


def executar(chamada, base, uf=None):
    """Executa a ferramenta escolhida. Devolve {"texto", "opcoes", "decisao"}.

    `opcoes` é a lista de ids de assuntos que a interface pode oferecer como botões.
    """
    if chamada["ferramenta"] != "buscar_orientacao":
        # Cofre, tarefas e briefing são tratados pelo telegram_bot antes de chegar aqui;
        # esta mensagem é só reserva para quem chamar executar() com outra ferramenta.
        texto = MSG_EM_BREVE_POR_FERRAMENTA.get(chamada["ferramenta"], MSG_EM_BREVE)
        return {"texto": texto, "opcoes": [], "decisao": "EM_BREVE"}

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
