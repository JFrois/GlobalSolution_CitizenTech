"""Busca por palavras-chave com pontuação, regra de decisão, grafo e Dijkstra.

Núcleo da Onda 1: só biblioteca padrão (spec §7.3). Este módulo NÃO formata
texto para o usuário; isso é papel de respostas.py.

Pontuação (documentada, spec §7.3 item 3)
-----------------------------------------
Para cada palavra da pergunta (já normalizada e expandida por sinônimos):
  * está em `palavras_chave` do registro .... peso 3
  * está em `pergunta` do registro .......... peso 2
  * está em `orientacao` do registro ........ peso 1
Os pesos de um mesmo registro somam. Uma palavra e suas variações (sinônimos)
contam UMA vez: vale a maior pontuação entre elas. Bônus de expressão: se todas
as palavras de uma palavra-chave composta (ex.: "segunda via") aparecem na
pergunta, o registro ganha +2.
"""
from __future__ import annotations

import heapq
import re
import unicodedata

# ---- Constantes ajustáveis (calibradas com --avaliar) ----------------------
PESO_PALAVRA_CHAVE = 3
PESO_PERGUNTA = 2
PESO_ORIENTACAO = 1
BONUS_EXPRESSAO = 2
LIMIAR_MINIMO = 3   # A: melhor pontuação precisa chegar a este valor
MARGEM = 2          # B: diferença mínima entre a 1ª e a 2ª pontuação
MAX_CANDIDATOS = 3
CUSTO_MESMO_TEMA = 1
CUSTO_TEMAS_DIFERENTES = 2

# Palavras de função e verbos genéricos que aparecem em qualquer pergunta.
STOPWORDS = frozenset("""
a o as os um uma uns umas de da do das dos em na no nas nos para pra por com sem
e ou que como quero quer preciso precisa fazer faco faca tirar onde meu minha
meus minhas me eu se ao aos qual quais posso pode ter tenho foi ser sao ja mais
mas nao isso esse essa este esta ela ele quando porque qual
""".split())


# ---- Normalização ----------------------------------------------------------
def tokenizar(texto):
    """Minúsculas, sem acentos e sem pontuação, dividido em palavras."""
    texto = unicodedata.normalize("NFKD", str(texto).lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", texto)


def normalizar(texto):
    """Tokeniza e remove stopwords. Mesma regra para pergunta e registros."""
    return [t for t in tokenizar(texto) if t not in STOPWORDS]


def montar_expansao(sinonimos):
    """Monta palavra -> conjunto de variações (em dois sentidos).

    `sinonimos` vem do base.json: {"identidade": ["rg", "cin"]}. Assim "rg"
    também conta como "identidade" e vice-versa.
    """
    exp = {}
    for termo, variacoes in (sinonimos or {}).items():
        grupo = set()
        for texto in [termo] + list(variacoes):
            grupo.update(tokenizar(texto))
        for palavra in grupo:
            exp.setdefault(palavra, set()).update(grupo)
    return exp


def expandir(token, expansao):
    """Devolve a palavra mais as suas variações."""
    return expansao.get(token, set()) | {token}


# ---- Índice invertido e busca linear ---------------------------------------
def _pesos_registro(reg):
    """Palavra -> peso total dentro de um registro (soma dos três campos)."""
    pesos = {}
    campos = (
        (" ".join(reg["palavras_chave"]), PESO_PALAVRA_CHAVE),
        (reg["pergunta"], PESO_PERGUNTA),
        (reg["orientacao"], PESO_ORIENTACAO),
    )
    for texto, peso in campos:
        if texto.strip() == "PREENCHER":
            continue  # orientação ainda não redigida não entra na busca
        for palavra in set(normalizar(texto)):
            pesos[palavra] = pesos.get(palavra, 0) + peso
    return pesos


def construir_indice(registros):
    """Índice invertido: palavra -> {id: peso}. Montado uma vez na carga."""
    indice = {}
    for reg in registros:
        for palavra, peso in _pesos_registro(reg).items():
            indice.setdefault(palavra, {})[reg["id"]] = peso
    return indice


def _bonus_expressoes(registros_por_id, ids, tokens_expandidos):
    """Bônus por palavra-chave composta cujas palavras estão todas na pergunta."""
    bonus = {}
    for rid in ids:
        for chave in registros_por_id[rid]["palavras_chave"]:
            partes = normalizar(chave)
            if len(partes) > 1 and all(p in tokens_expandidos for p in partes):
                bonus[rid] = bonus.get(rid, 0) + BONUS_EXPRESSAO
    return bonus


def preparar(base):
    """Adiciona à base os índices e o grafo (idempotente)."""
    if "indice" not in base:
        base["indice"] = construir_indice(base["registros"])
        base["expansao"] = montar_expansao(base.get("sinonimos"))
        base["grafo"] = montar_grafo(base)
    return base


def _pontuar(tokens, base, metodo):
    """Soma as pontuações por registro. Devolve {id: pontuação}."""
    expansao = base["expansao"]
    # Variações de cada palavra da pergunta (cada grupo conta uma vez).
    grupos = [expandir(t, expansao) for t in dict.fromkeys(tokens)]
    todas = set().union(*grupos) if grupos else set()
    pontos = {}

    if metodo == "linear":
        # Varredura de todos os registros (comparação de desempenho, Fase 6).
        for reg in base["registros"]:
            pesos = _pesos_registro(reg)
            for grupo in grupos:
                melhor = max((pesos.get(p, 0) for p in grupo), default=0)
                if melhor:
                    pontos[reg["id"]] = pontos.get(reg["id"], 0) + melhor
    else:
        # Consulta ao índice invertido: só visita registros com a palavra.
        indice = base["indice"]
        for grupo in grupos:
            melhor_por_id = {}
            for palavra in grupo:
                for rid, peso in indice.get(palavra, {}).items():
                    if peso > melhor_por_id.get(rid, 0):
                        melhor_por_id[rid] = peso
            for rid, peso in melhor_por_id.items():
                pontos[rid] = pontos.get(rid, 0) + peso

    for rid, extra in _bonus_expressoes(base["registros_por_id"], list(pontos), todas).items():
        pontos[rid] += extra
    return pontos


# ---- Busca com decisão -----------------------------------------------------
def buscar(pergunta, base, metodo="indice", temas_excluidos=None,
           ids_excluidos=None, apenas_tema=None):
    """Busca e decide o que fazer (regra C, A, B da spec §7.3 item 6).

    Retorna {"decisao", "candidatos": [(id, pontuacao)], "melhor", "segundo"}.
    `apenas_tema` restringe a busca a um tema (menu 1 do terminal);
    `ids_excluidos` tira registros já exibidos de "Continue consultando".
    """
    preparar(base)
    temas_excluidos = temas_excluidos or set()
    ids_excluidos = ids_excluidos or set()
    tokens = normalizar(pergunta) if isinstance(pergunta, str) else []

    # C = entrada válida (pelo menos 1 palavra útil)
    C = len(tokens) >= 1
    if not C:
        return {"decisao": "INVALIDA", "candidatos": [], "melhor": 0, "segundo": 0}

    pontos = _pontuar(tokens, base, metodo)
    ordenados = []
    for rid, pont in pontos.items():
        tema = base["registros_por_id"][rid]["tema"]
        fora_do_tema = (apenas_tema is not None and tema != apenas_tema) or tema in temas_excluidos
        ja_exibido = rid in ids_excluidos
        # De Morgan: not (fora_do_tema or ja_exibido) == (not fora_do_tema) and (not ja_exibido)
        incluir = not (fora_do_tema or ja_exibido)
        assert incluir == ((not fora_do_tema) and (not ja_exibido))
        if incluir:
            ordenados.append((rid, pont))
    # Pontuação decrescente; empate pelo menor id.
    ordenados.sort(key=lambda par: (-par[1], par[0]))

    melhor = ordenados[0][1] if ordenados else 0
    segundo = ordenados[1][1] if len(ordenados) > 1 else 0
    A = melhor >= LIMIAR_MINIMO
    B = (melhor - segundo) >= MARGEM
    if not A:
        decisao = "SEM_BASE"
    elif B:
        decisao = "RESPONDER"
    else:
        decisao = "PEDIR_ESCOLHA"
    return {
        "decisao": decisao,
        "candidatos": ordenados[:MAX_CANDIDATOS] if A else [],
        "melhor": melhor,
        "segundo": segundo,
    }


# ---- Grafo e Dijkstra ------------------------------------------------------
def montar_grafo(base):
    """Lista de adjacência não direcionada: id -> [(vizinho, custo)]."""
    por_id = base["registros_por_id"]
    vizinhos = {rid: set() for rid in por_id}
    for reg in base["registros"]:
        for outro in reg["relacionados"]:
            vizinhos[reg["id"]].add(outro)
            vizinhos[outro].add(reg["id"])  # trata como não direcionado
    grafo = {}
    for rid, outros in vizinhos.items():
        grafo[rid] = []
        for outro in sorted(outros):
            mesmo = por_id[rid]["tema"] == por_id[outro]["tema"]
            custo = CUSTO_MESMO_TEMA if mesmo else CUSTO_TEMAS_DIFERENTES
            grafo[rid].append((outro, custo))
    return grafo


def _dijkstra_completo(grafo, origem):
    """Distâncias mínimas da origem a todos os alcançáveis (e predecessores)."""
    dist = {origem: 0}
    anterior = {}
    fila = [(0, origem)]
    while fila:
        d, atual = heapq.heappop(fila)
        if d > dist.get(atual, float("inf")):
            continue  # entrada antiga da fila
        for viz, custo in grafo.get(atual, []):
            nd = d + custo
            if nd < dist.get(viz, float("inf")):
                dist[viz] = nd
                anterior[viz] = atual
                heapq.heappush(fila, (nd, viz))
    return dist, anterior


def dijkstra(grafo, origem, destino):
    """Menor caminho: (custo_total, [ids]) ou None se não houver caminho."""
    if origem not in grafo or destino not in grafo:
        return None
    dist, anterior = _dijkstra_completo(grafo, origem)
    if destino not in dist:
        return None
    caminho = [destino]
    while caminho[-1] != origem:
        caminho.append(anterior[caminho[-1]])
    caminho.reverse()
    return dist[destino], caminho


def relacionados_ordenados(grafo, origem, limite=3, excluir=None):
    """Os `limite` registros mais próximos da origem (vizinhos diretos primeiro).

    Completa com os seguintes mais próximos quando há poucos vizinhos diretos.
    """
    excluir = set(excluir or ()) | {origem}
    dist, _ = _dijkstra_completo(grafo, origem)
    candidatos = sorted((d, rid) for rid, d in dist.items() if rid not in excluir)
    return [rid for _, rid in candidatos[:limite]]
