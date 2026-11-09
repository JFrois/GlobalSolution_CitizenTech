"""Folha cega para a nota de clareza dos modelos A e B (spec 8, item B3).

Quem dá a nota vê só os rótulos X e Y (sorteados por pergunta), sem saber qual é o
modelo A e qual é o B. Três passos:

    python scripts/folha_clareza.py folha               # grava testes/clareza_folha.md (distribua esta)
    python scripts/folha_clareza.py calcular notas.csv  # lê as notas e mostra a média por modelo
    python scripts/folha_clareza.py gabarito            # mostra qual rótulo é A ou B (só depois das notas)

O arquivo de notas é um CSV com o cabeçalho `avaliador,id,rotulo,nota` (nota de 1 a 5).
Use apelidos como P1 e P2 em `avaliador`, nunca nomes. O sorteio usa semente fixa, então
o gabarito é sempre o mesmo para a mesma base e as mesmas perguntas.
"""
from __future__ import annotations

import csv
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import avaliacao  # noqa: E402
import base  # noqa: E402
import busca  # noqa: E402
import respostas  # noqa: E402

SEMENTE = 20261109
SAIDA = RAIZ / "testes" / "clareza_folha.md"


def montar_pares():
    """[(id, pergunta, {'X': (modelo, texto), 'Y': (modelo, texto)})] com sorteio estável."""
    dados = base.carregar_base(RAIZ / "data" / "base.json")
    buscador = busca.Buscador(dados)
    sorteio = random.Random(SEMENTE)
    pares = []
    for p in avaliacao.carregar_perguntas():
        r = buscador.buscar(p["pergunta"])
        if r.decisao != busca.RESPONDER:
            continue
        rid = r.candidatos[0]
        reg = buscador.por_id[rid]
        sugestoes = buscador.sugestoes(rid, 3, excluir=(rid,))
        textos = {m: respostas.montar_resposta(m, reg, sugestoes, buscador.por_id) for m in ("A", "B")}
        ordem = ["A", "B"]
        sorteio.shuffle(ordem)
        pares.append((p["id"], p["pergunta"], {"X": (ordem[0], textos[ordem[0]]),
                                               "Y": (ordem[1], textos[ordem[1]])}))
    return pares


def gravar_folha(pares):
    linhas = ["# Folha de clareza (cega)", "",
              "Leia as duas respostas de cada pergunta (X e Y) e dê uma nota de **1 (confusa) a 5 (muito clara)** "
              "para cada uma. Não procure saber qual é qual. Identifique-se só por apelido (P1, P2...).", ""]
    for pid, pergunta, rotulos in pares:
        linhas += ["---", "", "## %s: %s" % (pid, pergunta), ""]
        for rotulo in ("X", "Y"):
            linhas += ["### Resposta %s" % rotulo, "", "```text", rotulos[rotulo][1].rstrip(), "```",
                       "", "Nota %s (1 a 5): ____" % rotulo, ""]
    SAIDA.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("Folha gravada em %s (%d perguntas)." % (SAIDA, len(pares)))


def calcular(caminho, pares):
    gabarito = {(pid, r): m for pid, _, rot in pares for r, (m, _) in rot.items()}
    notas = {"A": [], "B": []}
    with open(caminho, encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            chave = (linha["id"].strip(), linha["rotulo"].strip().upper())
            if chave not in gabarito:
                print("Ignorado (id ou rótulo desconhecido): %s" % (chave,))
                continue
            nota = int(linha["nota"])
            if not 1 <= nota <= 5:
                print("Ignorado (nota fora de 1 a 5): %s" % (chave,))
                continue
            notas[gabarito[chave]].append(nota)
    for modelo, lista in notas.items():
        media = sum(lista) / len(lista) if lista else float("nan")
        print("Modelo %s: média %.2f (%d notas)" % (modelo, media, len(lista)))


def main(argv):
    if not argv or argv[0] not in ("folha", "calcular", "gabarito"):
        print(__doc__)
        return 2
    pares = montar_pares()
    if argv[0] == "folha":
        gravar_folha(pares)
    elif argv[0] == "gabarito":
        for pid, _, rot in pares:
            print("%s: X = modelo %s, Y = modelo %s" % (pid, rot["X"][0], rot["Y"][0]))
    else:
        if len(argv) < 2:
            print("Informe o CSV de notas.")
            return 2
        calcular(argv[1], pares)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
