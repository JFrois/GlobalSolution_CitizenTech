"""Busca por palavras-chave, regra de decisão, grafo de temas e Dijkstra.

Só biblioteca padrão, compatível com Python 3.9 (spec 5.2 e 5.4).

Visão geral (spec 7.3):
  1. normalizar() limpa o texto (minúsculas, sem acento, sem pontuação,
     sem stopwords). A MESMA função vale para a pergunta e para os registros.
  2. Cada token da pergunta é expandido com os sinônimos da base.
  3. Pontuação por registro: o token vale 3 se está nas palavras_chave,
     2 na pergunta e 1 na orientação (no máximo uma vez por campo), mais um
     bônus de expressão (+2) quando todas as palavras de uma palavra-chave
     composta aparecem na pergunta.
  4. Dois métodos dão o mesmo resultado: índice invertido (rápido) e busca
     linear (varre todos os registros; existe para a comparação da Fase 6).
  5. decidir() aplica a regra C·A·B e escolhe uma das 4 saídas.
  6. Grafo não direcionado de 'relacionados' e Dijkstra (heapq).
"""
from __future__ import annotations

import difflib
import heapq
import re
import unicodedata
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# Constantes de ajuste (spec 7.3: pesos, limiar e margem ficam no topo)
# --------------------------------------------------------------------------

# Bits dos campos onde uma palavra pode aparecer.
CAMPO_PALAVRA_CHAVE = 1
CAMPO_PERGUNTA = 2
CAMPO_ORIENTACAO = 4

# Quanto vale a palavra em cada campo.
PESO_CAMPO = {
    CAMPO_PALAVRA_CHAVE: 3,
    CAMPO_PERGUNTA: 2,
    CAMPO_ORIENTACAO: 1,
}

# Bônus quando todas as palavras de uma palavra-chave composta estão na pergunta.
BONUS_EXPRESSAO = 2

# Regra de decisão: A = melhor pontuação >= LIMIAR_MINIMO;
# B = (1ª pontuação - 2ª pontuação) >= MARGEM.
LIMIAR_MINIMO = 3
MARGEM = 2

# Quantos candidatos mostrar quando a pergunta é ambígua.
MAX_CANDIDATOS = 3

# Correção de digitação (só quando a busca normal não acha nada: SEM_BASE).
# Palavra fora do vocabulário da base, com pelo menos TAM_MIN_CORRECAO letras, é trocada
# pela palavra mais parecida (difflib), se a semelhança for >= LIMIAR_SEMELHANCA.
TAM_MIN_CORRECAO = 5
LIMIAR_SEMELHANCA = 0.8

# Custo da aresta do grafo: mesmo tema ou temas diferentes (spec 7.3, item 8).
CUSTO_MESMO_TEMA = 1
CUSTO_TEMAS_DIFERENTES = 2

# Saídas da regra de decisão (os mesmos rótulos de testes/perguntas.json).
INVALIDA = "INVALIDA"
RESPONDER = "RESPONDER"
PEDIR_ESCOLHA = "PEDIR_ESCOLHA"
SEM_BASE = "SEM_BASE"

# Palavras de função e verbos genéricos que aparecem em qualquer pergunta.
# Sem acento, porque a lista é aplicada depois da normalização.
STOPWORDS = frozenset("""
a ao aos as com como da das de do dos e em entre essa esse esta este eu foi
ha isso la mais mas me meu meus minha minhas muito na nas nao no nos num numa
o os ou para pela pelo por pra pro qual quais quando que quem se sem ser so
sobre sua seu suas seus tem um uma uns umas vai voce ainda tambem onde
quero quer preciso precisa posso consigo fazer faco tirar tiro ter tenho
obter conseguir pedir solicitar buscar busco gostaria saber sei ir vou deve
devo existe pode podem
gov br www http https
""".split())


# --------------------------------------------------------------------------
# Normalização
# --------------------------------------------------------------------------

def normalizar(texto: str) -> list:
    """Devolve os tokens úteis do texto: minúsculas, sem acento, sem pontuação,
    sem stopwords. Ex.: "Como tirar a 2ª via do RG?" -> ["2a", "via", "rg"]."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return [t for t in texto.split() if t not in STOPWORDS]


def _montar_grupos_de_sinonimos(sinonimos: dict) -> dict:
    """Transforma {"identidade": ["rg", "cin"]} em token -> conjunto de
    equivalentes. A relação vale nos dois sentidos (rg também conta como
    identidade). Dica de redação: prefira sinônimos de uma palavra só."""
    grupos = {}
    for termo, variacoes in sinonimos.items():
        membros = set(normalizar(termo))
        for variacao in variacoes:
            membros.update(normalizar(variacao))
        for token in membros:
            grupos.setdefault(token, set()).update(membros)
    return grupos


# --------------------------------------------------------------------------
# Filtros com De Morgan (spec 7.3, item 4)
# --------------------------------------------------------------------------

def incluir_registro(fora_do_tema: bool, ja_exibido: bool) -> bool:
    """Forma 'not (A or B)': fica de fora quem é de outro tema OU já foi exibido."""
    return not (fora_do_tema or ja_exibido)


def incluir_registro_equivalente(fora_do_tema: bool, ja_exibido: bool) -> bool:
    """Lei de De Morgan: not (A or B) == (not A) and (not B).
    Fica quem é do tema E ainda não foi exibido. Os testes conferem que as
    duas formas dão sempre o mesmo valor."""
    return (not fora_do_tema) and (not ja_exibido)


# --------------------------------------------------------------------------
# Regra de decisão (mapa de Karnaugh do relatório)
# --------------------------------------------------------------------------

def decidir(c: bool, a: bool, b: bool) -> str:
    """Tabela de decisão da spec 7.3, item 6.

        C A B | saída
        0 - - | INVALIDA
        1 1 1 | RESPONDER
        1 1 0 | PEDIR_ESCOLHA
        1 0 - | SEM_BASE
    """
    if not c:
        return INVALIDA
    if not a:
        return SEM_BASE
    return RESPONDER if b else PEDIR_ESCOLHA


@dataclass
class Resultado:
    """O que a busca devolve para quem vai mostrar a resposta."""
    decisao: str
    ranking: list = field(default_factory=list)      # [(id, pontos)] do maior ao menor
    candidatos: list = field(default_factory=list)   # ids a mostrar (1 ou até 3)
    tokens: list = field(default_factory=list)       # tokens úteis da pergunta
    corrigidos: dict = field(default_factory=dict)   # {digitado: corrigido}, se houve correção


# --------------------------------------------------------------------------
# Buscador
# --------------------------------------------------------------------------

class Buscador:
    """Guarda a base, o índice invertido e o grafo, e faz as consultas."""

    def __init__(self, base: dict):
        self.registros = base["registros"]
        self.por_id = {r["id"]: r for r in self.registros}
        self.grupos = _montar_grupos_de_sinonimos(base.get("sinonimos", {}))
        self.indice = self._construir_indice()
        self.grafo = montar_grafo(self.registros)

    # ---- índice invertido ------------------------------------------------

    def _tokens_dos_campos(self, reg: dict) -> dict:
        """Tokens de cada campo do registro, já normalizados."""
        return {
            CAMPO_PALAVRA_CHAVE: set(t for p in reg["palavras_chave"] for t in normalizar(p)),
            CAMPO_PERGUNTA: set(normalizar(reg["pergunta"])),
            CAMPO_ORIENTACAO: set(normalizar(reg["orientacao"])),
        }

    def _expressoes(self, reg: dict) -> list:
        """Palavras-chave compostas (2+ tokens) do registro, como conjuntos."""
        exprs = []
        for palavra in reg["palavras_chave"]:
            tokens = set(normalizar(palavra))
            if len(tokens) >= 2:
                exprs.append(tokens)
        return exprs

    def _construir_indice(self) -> dict:
        """palavra -> {id: máscara de campos}. A máscara diz em quais campos a
        palavra aparece; o peso vem de PESO_CAMPO. Construído uma vez na carga."""
        indice = {}
        self._expressoes_por_id = {}
        for reg in self.registros:
            for campo, tokens in self._tokens_dos_campos(reg).items():
                for token in tokens:
                    por_id = indice.setdefault(token, {})
                    por_id[reg["id"]] = por_id.get(reg["id"], 0) | campo
            self._expressoes_por_id[reg["id"]] = self._expressoes(reg)
        return indice

    # ---- pontuação -------------------------------------------------------

    def _equivalentes(self, tokens: list) -> list:
        """Para cada token da pergunta, o conjunto {token + sinônimos}."""
        return [self.grupos.get(t, {t}) for t in tokens]

    @staticmethod
    def _pontos(mascaras: list, expressoes: list, tokens_expandidos: set) -> int:
        """Soma os pesos (um campo conta uma vez por token da pergunta) e o
        bônus de expressão. Compartilhada pelos dois métodos de busca."""
        pontos = 0
        for mascara in mascaras:
            for campo, peso in PESO_CAMPO.items():
                if mascara & campo:
                    pontos += peso
        for expressao in expressoes:
            if expressao <= tokens_expandidos:
                pontos += BONUS_EXPRESSAO
        return pontos

    def _ranking_indice(self, equivalentes: list) -> list:
        """Pontuação usando o índice invertido: só visita registros que
        contêm alguma palavra da pergunta."""
        tokens_expandidos = set().union(*equivalentes) if equivalentes else set()
        mascaras_por_id = {}
        for posicao, equivs in enumerate(equivalentes):
            mascara_do_token = {}
            for palavra in equivs:
                for rid, mascara in self.indice.get(palavra, {}).items():
                    mascara_do_token[rid] = mascara_do_token.get(rid, 0) | mascara
            for rid, mascara in mascara_do_token.items():
                mascaras_por_id.setdefault(rid, []).append(mascara)
        ranking = []
        for rid, mascaras in mascaras_por_id.items():
            pontos = self._pontos(mascaras, self._expressoes_por_id[rid], tokens_expandidos)
            ranking.append((rid, pontos))
        return ranking

    def _ranking_linear(self, equivalentes: list) -> list:
        """Mesma pontuação, mas varrendo TODOS os registros e normalizando os
        campos a cada consulta (sem índice). Serve de comparação de desempenho."""
        tokens_expandidos = set().union(*equivalentes) if equivalentes else set()
        ranking = []
        for reg in self.registros:
            campos = self._tokens_dos_campos(reg)
            mascaras = []
            for equivs in equivalentes:
                mascara = 0
                for campo, tokens in campos.items():
                    if equivs & tokens:
                        mascara |= campo
                if mascara:
                    mascaras.append(mascara)
            if not mascaras:
                continue
            pontos = self._pontos(mascaras, self._expressoes(reg), tokens_expandidos)
            ranking.append((reg["id"], pontos))
        return ranking

    # ---- consulta --------------------------------------------------------

    def buscar(self, pergunta: str, tema=None, excluir=(), metodo: str = "indice") -> Resultado:
        """Busca e decide.

        tema:   se informado, só registros desse tema (menu 1 do terminal).
        excluir: ids já exibidos, que ficam de fora ("Continue consultando").
        metodo: "indice" (padrão) ou "linear"; o resultado é o mesmo.
        """
        tokens = list(dict.fromkeys(normalizar(pergunta or "")))  # sem repetir, mantém a ordem
        if not tokens:
            return Resultado(decisao=decidir(False, False, False), tokens=tokens)

        resultado = self._pontuar(tokens, tema, excluir, metodo)
        if resultado.decisao == SEM_BASE:
            # Última tentativa: talvez a pessoa errou a digitação ("docuumento").
            corrigidos = self._corrigir(tokens)
            if corrigidos:
                novos = [corrigidos.get(t, t) for t in tokens]
                segunda = self._pontuar(novos, tema, excluir, metodo)
                if segunda.decisao != SEM_BASE:
                    segunda.corrigidos = corrigidos
                    return segunda
        return resultado

    def _pontuar(self, tokens: list, tema, excluir, metodo: str) -> Resultado:
        """Pontua, ordena e decide para uma lista de tokens já normalizados."""
        equivalentes = self._equivalentes(tokens)
        if metodo == "linear":
            bruto = self._ranking_linear(equivalentes)
        else:
            bruto = self._ranking_indice(equivalentes)

        # Filtro De Morgan: incluir = not (fora_do_tema or ja_exibido).
        ranking = []
        for rid, pontos in bruto:
            fora_do_tema = tema is not None and self.por_id[rid]["tema"] != tema
            ja_exibido = rid in excluir
            if incluir_registro(fora_do_tema, ja_exibido) and pontos > 0:
                ranking.append((rid, pontos))

        # Várias correspondências: maior pontuação primeiro; empate pelo menor id.
        ranking.sort(key=lambda par: (-par[1], par[0]))

        c = len(tokens) >= 1
        melhor = ranking[0][1] if ranking else 0
        segundo = ranking[1][1] if len(ranking) > 1 else 0
        a = melhor >= LIMIAR_MINIMO
        if a and self._so_pedaco(tokens, equivalentes, ranking[0][0]):
            a = False  # "tarifa de ônibus" não é a "Tarifa Social" de energia
        b = (melhor - segundo) >= MARGEM
        decisao = decidir(c, a, b)

        if decisao == RESPONDER:
            candidatos = [ranking[0][0]]
        elif decisao == PEDIR_ESCOLHA:
            candidatos = [rid for rid, _ in ranking[:MAX_CANDIDATOS]]
        else:
            candidatos = []
        return Resultado(decisao=decisao, ranking=ranking, candidatos=candidatos, tokens=tokens)

    def _so_pedaco(self, tokens: list, equivalentes: list, rid: str) -> bool:
        """True se a pergunta tem palavra que a base não conhece e o registro só
        bate por pedaço de palavra-chave composta (nenhuma palavra-chave inteira).

        Ex.: "tarifa de onibus" casa "tarifa" de "tarifa social", mas "onibus" não
        existe na base: o assunto é outro, então não responde com esse registro."""
        desconhecida = any(t not in self.indice and t not in self.grupos for t in tokens)
        if not desconhecida:
            return False
        expandidos = set().union(*equivalentes)
        for palavra in self.por_id[rid]["palavras_chave"]:
            partes = set(normalizar(palavra))
            if partes and partes <= expandidos:
                return False
        return True

    def _corrigir(self, tokens: list) -> dict:
        """{token digitado: palavra parecida da base} para palavras fora do vocabulário.

        Só corrige palavra com TAM_MIN_CORRECAO letras ou mais e que não seja sinônimo
        conhecido. Palavras curtas (ipva, mei) ficam como estão: errariam demais."""
        vocabulario = [p for p in self.indice if len(p) >= TAM_MIN_CORRECAO]
        trocas = {}
        for t in tokens:
            if len(t) < TAM_MIN_CORRECAO or t in self.indice or t in self.grupos:
                continue
            parecidas = difflib.get_close_matches(t, vocabulario, n=1, cutoff=LIMIAR_SEMELHANCA)
            if parecidas:
                trocas[t] = parecidas[0]
        return trocas

    # ---- grafo -----------------------------------------------------------

    def caminho(self, origem: str, destino: str):
        """Menor caminho entre dois assuntos: (custo, [ids]) ou None se não houver."""
        return caminho_mais_curto(self.grafo, self._temas(), origem, destino)

    def sugestoes(self, origem: str, quantidade: int = 3, excluir=()) -> list:
        """Os registros mais próximos de 'origem' pela distância de Dijkstra,
        para o 'Continue consultando'. Vizinhos diretos vêm primeiro; se
        houver menos que 'quantidade', completa com os seguintes mais próximos."""
        distancias, _ = dijkstra(self.grafo, self._temas(), origem)
        vizinhos = self.grafo[origem]
        candidatos = []
        for rid, dist in distancias.items():
            # Mesmo filtro De Morgan: fora quem é a própria origem ou já foi exibido.
            eh_origem = rid == origem
            ja_exibido = rid in excluir
            if incluir_registro(eh_origem, ja_exibido):
                candidatos.append((dist, 0 if rid in vizinhos else 1, rid))
        candidatos.sort()
        return [rid for _, _, rid in candidatos[:quantidade]]

    def _temas(self) -> dict:
        return {rid: reg["tema"] for rid, reg in self.por_id.items()}


# --------------------------------------------------------------------------
# Grafo e Dijkstra
# --------------------------------------------------------------------------

def montar_grafo(registros: list) -> dict:
    """Lista de adjacência id -> conjunto de ids. 'relacionados' é tratado como
    não direcionado: se A aponta para B, B também enxerga A (spec 7.3, item 7)."""
    grafo = {reg["id"]: set() for reg in registros}
    for reg in registros:
        for alvo in reg["relacionados"]:
            if alvo in grafo and alvo != reg["id"]:
                grafo[reg["id"]].add(alvo)
                grafo[alvo].add(reg["id"])
    return grafo


def _custo_aresta(temas: dict, a: str, b: str) -> int:
    return CUSTO_MESMO_TEMA if temas[a] == temas[b] else CUSTO_TEMAS_DIFERENTES


def dijkstra(grafo: dict, temas: dict, origem: str):
    """Dijkstra com heapq. Devolve (distancias, anterior); só entram nas
    distâncias os nós alcançáveis a partir de 'origem'."""
    if origem not in grafo:
        raise ValueError("assunto desconhecido: %s" % origem)
    distancias = {origem: 0}
    anterior = {}
    fila = [(0, origem)]
    while fila:
        dist, no = heapq.heappop(fila)
        if dist > distancias.get(no, dist):
            continue  # entrada velha da fila
        for vizinho in sorted(grafo[no]):  # ordem fixa deixa o resultado reproduzível
            nova = dist + _custo_aresta(temas, no, vizinho)
            if nova < distancias.get(vizinho, float("inf")):
                distancias[vizinho] = nova
                anterior[vizinho] = no
                heapq.heappush(fila, (nova, vizinho))
    return distancias, anterior


def caminho_mais_curto(grafo: dict, temas: dict, origem: str, destino: str):
    """(custo, [origem, ..., destino]) ou None quando não há caminho."""
    if destino not in grafo:
        raise ValueError("assunto desconhecido: %s" % destino)
    distancias, anterior = dijkstra(grafo, temas, origem)
    if destino not in distancias:
        return None
    caminho = [destino]
    while caminho[-1] != origem:
        caminho.append(anterior[caminho[-1]])
    caminho.reverse()
    return distancias[destino], caminho
