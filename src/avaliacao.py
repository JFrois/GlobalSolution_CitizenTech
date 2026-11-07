"""Avaliação do núcleo: taxa de acerto, tempo de consulta e comparação A x B.

Chamado por `python src/sistema.py --avaliar` (spec §6.1, §8 e §14.2). Só
biblioteca padrão. Grava testes/resultados.csv e testes/comparacao_modelos.csv.

Atenção: A e B recebem o MESMO resultado da busca, então taxa de acerto e tempo
de consulta medem a BUSCA e são iguais nos dois modelos por construção. A
comparação A x B usa a rubrica de formato (colunas de comparacao_modelos.csv).
"""
from __future__ import annotations

import copy
import csv
import json
import time
from pathlib import Path

import busca
import respostas

RAIZ = Path(__file__).resolve().parent.parent
PERGUNTAS = RAIZ / "testes" / "perguntas.json"
SAIDA_RESULTADOS = RAIZ / "testes" / "resultados.csv"
SAIDA_MODELOS = RAIZ / "testes" / "comparacao_modelos.csv"
REPETICOES = 1000  # repete cada consulta para reduzir o ruído do relógio


def obtido_de(resultado):
    """Traduz o resultado da busca para o mesmo vocabulário de `esperado`."""
    if resultado["decisao"] == "RESPONDER":
        return resultado["candidatos"][0][0]
    return resultado["decisao"]


def medir_ms(pergunta, base, metodo, repeticoes):
    """Tempo médio e máximo (ms) de uma consulta, em `repeticoes` execuções."""
    tempos = []
    for _ in range(repeticoes):
        inicio = time.perf_counter()
        busca.buscar(pergunta, base, metodo)
        tempos.append((time.perf_counter() - inicio) * 1000)
    return sum(tempos) / len(tempos), max(tempos)


def base_sintetica(base, tamanho):
    """Copia os registros até `tamanho` (ids novos) para testar bases maiores."""
    registros = []
    original = base["registros"]
    for i in range(tamanho):
        reg = copy.deepcopy(original[i % len(original)])
        reg["id"] = "SIN-%05d" % i
        reg["relacionados"] = []
        registros.append(reg)
    grande = {"registros": registros, "sinonimos": base.get("sinonimos", {}),
              "registros_por_id": {r["id"]: r for r in registros}}
    return busca.preparar(grande)


def percentual(acertos, total):
    return 100.0 * acertos / total if total else 0.0


def avaliar_busca(base, perguntas):
    """Roda cada pergunta, mede o tempo e devolve as linhas do CSV."""
    linhas = []
    for q in perguntas:
        r_indice = busca.buscar(q["pergunta"], base, "indice")
        r_linear = busca.buscar(q["pergunta"], base, "linear")
        obtido = obtido_de(r_indice)
        t_indice, _ = medir_ms(q["pergunta"], base, "indice", REPETICOES)
        t_linear, _ = medir_ms(q["pergunta"], base, "linear", REPETICOES)
        linhas.append({
            "conjunto": q["conjunto"], "id": q["id"], "tipo": q["tipo"],
            "pergunta": q["pergunta"], "esperado": q["esperado"], "obtido": obtido,
            "resultado": "acerto" if obtido == q["esperado"] else "erro",
            "metodos_concordam": "sim" if r_indice == r_linear else "nao",
            "tempo_indice_ms": "%.4f" % t_indice, "tempo_linear_ms": "%.4f" % t_linear,
        })
    return linhas


def avaliar_modelos(base, perguntas):
    """Rubrica objetiva A x B nas perguntas que geram resposta (spec §8)."""
    linhas = []
    for q in perguntas:
        r = busca.buscar(q["pergunta"], base)
        if r["decisao"] != "RESPONDER":
            continue
        rid = r["candidatos"][0][0]
        reg = base["registros_por_id"][rid]
        ids = busca.relacionados_ordenados(base["grafo"], rid)
        rels = [base["registros_por_id"][i] for i in ids]
        for modelo in ("A", "B"):
            texto = respostas.formatar(reg, modelo, rels)
            tem_aviso = "Atenção:" in texto
            precisa = bool(reg.get("confirmar_antes")) or reg.get("abrangencia") == "estadual"
            linhas.append({
                "pergunta_id": q["id"], "modelo": modelo, "registro": rid,
                "tem_fonte_url_e_data": "sim" if (reg["referencia"] in texto and "verificado em" in texto) else "nao",
                "aviso_quando_aplicavel": ("sim" if tem_aviso else "nao") if precisa else "nao se aplica",
                "tem_relacionados": "sim" if ("Veja também" in texto or "Continue consultando" in texto) else "nao",
                "palavras": len(texto.split()),
                "passos": len(respostas.passos(reg)) if modelo == "B" else 0,
                "nota_clareza_1a5": "",  # preenchida à mão (rótulos X/Y), spec §8
            })
    return linhas


def gravar_csv(caminho, linhas):
    if not linhas:
        return
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        escritor.writeheader()
        escritor.writerows(linhas)


def resumo(linhas):
    """Imprime taxa de acerto geral, por tipo e por conjunto, e tempos."""
    total = len(linhas)
    acertos = sum(1 for l in linhas if l["resultado"] == "acerto")
    print("Taxa de acerto da busca: %d/%d = %.1f%%" % (acertos, total, percentual(acertos, total)))
    for campo, titulo in (("tipo", "Por tipo"), ("conjunto", "Por conjunto")):
        print(titulo + ":")
        grupos = {}
        for l in linhas:
            grupos.setdefault(l[campo], []).append(l)
        for nome, itens in grupos.items():
            ok = sum(1 for l in itens if l["resultado"] == "acerto")
            print("  %-12s %d/%d = %.1f%%" % (nome, ok, len(itens), percentual(ok, len(itens))))
    ti = [float(l["tempo_indice_ms"]) for l in linhas]
    tl = [float(l["tempo_linear_ms"]) for l in linhas]
    print("Tempo médio por consulta (%d repetições): índice %.4f ms | linear %.4f ms"
          % (REPETICOES, sum(ti) / len(ti), sum(tl) / len(tl)))
    print("Tempo máximo (média por pergunta): índice %.4f ms | linear %.4f ms" % (max(ti), max(tl)))
    discordam = [l["id"] for l in linhas if l["metodos_concordam"] != "sim"]
    print("Índice e busca linear concordam em todas: %s" % ("sim" if not discordam else "NAO " + str(discordam)))
    erros = [l for l in linhas if l["resultado"] == "erro"]
    if erros:
        print("Erros:")
        for l in erros:
            print("  %s esperado=%s obtido=%s  (%s)" % (l["id"], l["esperado"], l["obtido"], l["pergunta"]))


def escala(base):
    """Compara índice x linear em bases maiores (efeito do tamanho, Fase 6)."""
    print("Efeito do tamanho da base (consulta 'segunda via rg', ms por consulta):")
    for tamanho in (17, 1700, 17000):
        grande = base_sintetica(base, tamanho)
        reps = 200 if tamanho <= 1700 else 20
        ti, _ = medir_ms("segunda via rg", grande, "indice", reps)
        tl, _ = medir_ms("segunda via rg", grande, "linear", reps)
        print("  %6d registros: índice %.4f ms | linear %.4f ms" % (tamanho, ti, tl))


def executar(base):
    """Ponto de entrada de `--avaliar`. Devolve o código de saída."""
    busca.preparar(base)
    perguntas = json.loads(PERGUNTAS.read_text(encoding="utf-8"))
    linhas = avaliar_busca(base, perguntas)
    gravar_csv(SAIDA_RESULTADOS, linhas)
    gravar_csv(SAIDA_MODELOS, avaliar_modelos(base, perguntas))
    resumo(linhas)
    escala(base)
    print("Gravado: testes/resultados.csv e testes/comparacao_modelos.csv")
    return 0
