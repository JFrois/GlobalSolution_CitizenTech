"""Avaliação do sistema: taxa de acerto, tempos e comparação dos modelos A e B.

Usado por 'python src/sistema.py --avaliar' (spec 8 e 14.2). Só biblioteca
padrão, Python 3.9+.

O que cada medida significa:
  - Taxa de acerto e tempo de consulta medem a BUSCA e são iguais para os
    modelos A e B por construção (os dois formatam o mesmo resultado).
  - A comparação A x B mede só o FORMATO da resposta, pela rubrica de
    critérios objetivos; a nota de clareza (1 a 5) é preenchida à mão.
"""
from __future__ import annotations

import copy
import csv
import json
import re
import time
from pathlib import Path

import busca
import respostas

PASTA_TESTES = Path(__file__).resolve().parent.parent / "testes"

# Repetições por consulta: muitas na base real (para reduzir ruído) e menos
# nas bases sintéticas ampliadas, que são mais lentas.
REPETICOES = 1000
REPETICOES_AMPLIADA = 3
# Nas bases ampliadas usamos só algumas perguntas (a medição já é lenta).
PERGUNTAS_NA_ESCALA = 5
TAMANHOS_AMPLIADOS = (1700, 17000)

CAB_RESULTADOS = ["conjunto", "id", "tipo", "pergunta", "esperado", "obtido",
                  "resultado", "tempo_indice_ms", "tempo_linear_ms"]
CAB_COMPARACAO = ["id", "pergunta", "registro", "modelo", "tem_fonte_com_data",
                  "tem_aviso", "tem_relacionados", "palavras", "passos",
                  "clareza_1a5"]


def carregar_perguntas(caminho=None) -> list:
    caminho = Path(caminho) if caminho else PASTA_TESTES / "perguntas.json"
    return json.loads(caminho.read_text(encoding="utf-8"))["perguntas"]


def obtido_de(resultado) -> str:
    """Rótulo comparável com 'esperado': o id quando responde, senão a decisão."""
    if resultado.decisao == busca.RESPONDER:
        return resultado.candidatos[0]
    return resultado.decisao


def _tempo_medio_ms(buscador, pergunta: str, metodo: str, repeticoes: int) -> float:
    inicio = time.perf_counter()
    for _ in range(repeticoes):
        buscador.buscar(pergunta, metodo=metodo)
    return (time.perf_counter() - inicio) * 1000 / repeticoes


def avaliar_busca(buscador, perguntas: list, repeticoes: int = REPETICOES) -> list:
    """Uma linha por pergunta: esperado x obtido, acerto e tempo dos dois métodos."""
    linhas = []
    for p in perguntas:
        resultado = buscador.buscar(p["pergunta"])
        obtido = obtido_de(resultado)
        linhas.append({
            "conjunto": p["conjunto"], "id": p["id"], "tipo": p["tipo"],
            "pergunta": p["pergunta"], "esperado": p["esperado"], "obtido": obtido,
            "resultado": "acerto" if obtido == p["esperado"] else "erro",
            "tempo_indice_ms": _tempo_medio_ms(buscador, p["pergunta"], "indice", repeticoes),
            "tempo_linear_ms": _tempo_medio_ms(buscador, p["pergunta"], "linear", repeticoes),
        })
    return linhas


def taxa(linhas: list) -> tuple:
    """(acertos, total, percentual) de uma lista de linhas de resultado."""
    total = len(linhas)
    acertos = sum(1 for l in linhas if l["resultado"] == "acerto")
    return acertos, total, (100.0 * acertos / total if total else 0.0)


def agrupar(linhas: list, chave: str) -> dict:
    grupos = {}
    for l in linhas:
        grupos.setdefault(l[chave], []).append(l)
    return grupos


# --------------------------------------------------------------------------
# Comparação linear x índice em bases maiores
# --------------------------------------------------------------------------

def ampliar_base(dados: dict, tamanho: int) -> dict:
    """Base sintética: copia os registros reais até chegar em 'tamanho'.
    Os ids novos não seguem o formato AAA-000 porque a base ampliada só
    alimenta a medição de tempo (não passa pela validação)."""
    originais = dados["registros"]
    registros = []
    for i in range(tamanho):
        copia = copy.deepcopy(originais[i % len(originais)])
        if i >= len(originais):
            copia["id"] = "%s-X%d" % (copia["id"], i)
            copia["relacionados"] = []
        registros.append(copia)
    return {"temas": dados["temas"], "sinonimos": dados.get("sinonimos", {}),
            "registros": registros}


def medir_escala(dados: dict, perguntas: list, tamanhos=TAMANHOS_AMPLIADOS,
                 repeticoes: int = REPETICOES_AMPLIADA,
                 repeticoes_base: int = 200) -> list:
    """Tempo médio por consulta (ms) de cada método em bases de vários tamanhos."""
    medidas = []
    textos = [p["pergunta"] for p in perguntas if p["pergunta"].strip()][:PERGUNTAS_NA_ESCALA]
    for tamanho in (len(dados["registros"]),) + tuple(tamanhos):
        base_n = dados if tamanho == len(dados["registros"]) else ampliar_base(dados, tamanho)
        buscador = busca.Buscador(base_n)
        reps = repeticoes_base if tamanho == len(dados["registros"]) else repeticoes
        indice = sum(_tempo_medio_ms(buscador, t, "indice", reps) for t in textos) / len(textos)
        linear = sum(_tempo_medio_ms(buscador, t, "linear", reps) for t in textos) / len(textos)
        medidas.append({"registros": tamanho, "indice_ms": indice, "linear_ms": linear})
    return medidas


# --------------------------------------------------------------------------
# Rubrica A x B (spec 8)
# --------------------------------------------------------------------------

_DATA = re.compile(r"\d{2}/\d{2}/\d{4}")
# A URL longa pode ir para a linha de baixo, então aceitamos "Fonte:" e espaço ou quebra.
_FONTE = re.compile(r"Fonte:\s+http")


def criterios_do_formato(texto: str, reg: dict) -> dict:
    """Critérios objetivos da rubrica para um texto de resposta pronto."""
    exige_aviso = bool(reg.get("confirmar_antes")) or reg.get("abrangencia") == "estadual"
    return {
        "tem_fonte_com_data": "sim" if (_FONTE.search(texto) and _DATA.search(texto)) else "nao",
        "tem_aviso": ("sim" if "Atenção:" in texto else "nao") if exige_aviso else "n/a",
        "tem_relacionados": "sim" if ("Veja também:" in texto or "Continue consultando:" in texto) else "nao",
        "palavras": len(texto.split()),
        "passos": len(re.findall(r"(?m)^\d+\. ", texto)),
    }


def comparar_modelos(buscador, perguntas: list) -> list:
    """Aplica A e B ao MESMO resultado de cada pergunta que gera resposta."""
    linhas = []
    for p in perguntas:
        r = buscador.buscar(p["pergunta"])
        if r.decisao != busca.RESPONDER:
            continue
        rid = r.candidatos[0]
        reg = buscador.por_id[rid]
        sugestoes = buscador.sugestoes(rid, 3, excluir=(rid,))
        for modelo in ("A", "B"):
            texto = respostas.montar_resposta(modelo, reg, sugestoes, buscador.por_id)
            linha = {"id": p["id"], "pergunta": p["pergunta"], "registro": rid,
                     "modelo": modelo, "clareza_1a5": ""}
            linha.update(criterios_do_formato(texto, reg))
            linhas.append(linha)
    return linhas


# --------------------------------------------------------------------------
# Arquivos e resumo
# --------------------------------------------------------------------------

def gravar_csv(caminho: Path, cabecalho: list, linhas: list) -> None:
    with open(caminho, "w", encoding="utf-8", newline="") as arq:
        escritor = csv.DictWriter(arq, fieldnames=cabecalho, extrasaction="ignore")
        escritor.writeheader()
        for l in linhas:
            l = dict(l)
            for chave in ("tempo_indice_ms", "tempo_linear_ms"):
                if chave in l:
                    l[chave] = "%.4f" % l[chave]
            escritor.writerow(l)


def resumo(linhas: list, comparacao: list, escala: list) -> str:
    """Texto do resumo impresso no terminal (ASCII, até 80 colunas)."""
    out = []
    ac, tot, pct = taxa(linhas)
    out.append("TAXA DE ACERTO DA BUSCA")
    out.append("  geral: %d/%d = %.1f%%" % (ac, tot, pct))
    for rotulo, chave in (("por conjunto", "conjunto"), ("por tipo", "tipo")):
        out.append("  " + rotulo + ":")
        for nome, grupo in sorted(agrupar(linhas, chave).items()):
            a, t, p = taxa(grupo)
            out.append("    %-14s %d/%d = %.1f%%" % (nome, a, t, p))
    erros = [l for l in linhas if l["resultado"] == "erro"]
    if erros:
        out.append("  erros:")
        for l in erros:
            out.append("    %s: esperado %s, obtido %s" % (l["id"], l["esperado"], l["obtido"]))
    ti = [l["tempo_indice_ms"] for l in linhas]
    tl = [l["tempo_linear_ms"] for l in linhas]
    out.append("")
    out.append("TEMPO DE CONSULTA (ms, media de %d repeticoes por pergunta)" % REPETICOES)
    out.append("  indice invertido: media %.4f  max %.4f" % (sum(ti) / len(ti), max(ti)))
    out.append("  busca linear:     media %.4f  max %.4f" % (sum(tl) / len(tl), max(tl)))
    if escala:
        out.append("  por tamanho da base (media por consulta):")
        for m in escala:
            razao = m["linear_ms"] / m["indice_ms"] if m["indice_ms"] else 0
            out.append("    %6d registros: indice %.4f  linear %.4f  (linear %.1fx)"
                       % (m["registros"], m["indice_ms"], m["linear_ms"], razao))
    out.append("")
    out.append("MODELOS A x B (criterios objetivos; clareza preenchida a mao)")
    for modelo in ("A", "B"):
        grupo = [c for c in comparacao if c["modelo"] == modelo]
        if not grupo:
            continue
        n = len(grupo)
        fonte = sum(1 for c in grupo if c["tem_fonte_com_data"] == "sim")
        rel = sum(1 for c in grupo if c["tem_relacionados"] == "sim")
        palavras = sum(c["palavras"] for c in grupo) / n
        passos = sum(c["passos"] for c in grupo) / n
        out.append("  modelo %s: fonte+data %d/%d  relacionados %d/%d  %.1f palavras  %.1f passos"
                   % (modelo, fonte, n, rel, n, palavras, passos))
    return "\n".join(out)


def avaliar(dados: dict, pasta=None, perguntas_arq=None, escala: bool = True,
            repeticoes: int = REPETICOES) -> str:
    """Roda tudo, grava os dois CSVs e devolve o resumo."""
    pasta = Path(pasta) if pasta else PASTA_TESTES
    perguntas = carregar_perguntas(perguntas_arq)
    buscador = busca.Buscador(dados)
    linhas = avaliar_busca(buscador, perguntas, repeticoes)
    comparacao = comparar_modelos(buscador, perguntas)
    medidas = medir_escala(dados, perguntas) if escala else []
    gravar_csv(pasta / "resultados.csv", CAB_RESULTADOS, linhas)
    gravar_csv(pasta / "comparacao_modelos.csv", CAB_COMPARACAO, comparacao)
    return resumo(linhas, comparacao, medidas)
