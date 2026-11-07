"""Modelos de resposta A (resumido) e B (passo a passo) e avisos de limitação.

Núcleo da Onda 1: só biblioteca padrão. Textos conforme docs/ux.md §3.
Este módulo só FORMATA; quem decide qual registro responder é busca.py.
A e B recebem o mesmo resultado da busca, então a comparação A x B mede apenas
o formato (spec §8).

Convenção da orientação: cada passo fica numa linha do campo `orientacao`
(separados por "\\n"). Se houver uma linha só, os passos são as frases.
Saída em texto puro (a cor é aplicada por sistema.py).
"""
from __future__ import annotations

import re
import textwrap

LARGURA = 78
LINHA = "-" * 64
GOV_BR = "https://www.gov.br"
NAO_OFICIAL = "Este assistente não é um canal oficial."
SEM_REDACAO = "[orientação ainda não redigida pela equipe]"

# Mensagens de entrada inválida e erros de menu (docs/ux.md §3.7).
MSG_VAZIA = "Você não digitou nada. Escreva sua dúvida com palavras ou escolha um número."
MSG_SEM_PALAVRA = ("Não entendi. Tente com palavras, por exemplo: "
                   "como consultar minha situação eleitoral.")
MSG_LONGA = "Sua pergunta ficou longa. Tente resumir em uma frase curta."
LIMITE_PERGUNTA = 300


def msg_opcao_inexistente(opcao):
    return "A opção %s não existe aqui. Escolha um dos números da lista." % opcao


def _quebrar(texto, prefixo="", recuo=""):
    """Quebra o texto em linhas de até LARGURA colunas."""
    return textwrap.fill(texto, width=LARGURA, initial_indent=prefixo,
                         subsequent_indent=recuo or " " * len(prefixo))


def formatar_data(iso):
    """'2026-11-10' -> '10/11/2026'. Texto fora do padrão volta como está."""
    partes = str(iso).split("-")
    if len(partes) == 3 and all(p.isdigit() for p in partes):
        return "%s/%s/%s" % (partes[2], partes[1], partes[0])
    return str(iso)


def passos(registro):
    """Lista de passos da orientação (linhas ou, se for uma só, frases)."""
    texto = registro["orientacao"].strip()
    if texto == "PREENCHER":
        return [SEM_REDACAO]
    linhas = [l.strip() for l in texto.splitlines() if l.strip()]
    if len(linhas) > 1:
        return linhas
    frases = [f.strip() for f in re.split(r"(?<=[.!?])\s+", texto) if f.strip()]
    return frases or linhas


def fonte_e_aviso(registro, uf=None):
    """Escolhe o link (por UF, se houver) e monta o aviso de confirmação."""
    link = registro["referencia"]
    aviso = ""
    if registro.get("abrangencia") == "estadual":
        por_uf = registro.get("referencias_estaduais") or {}
        if uf and uf in por_uf:
            link = por_uf[uf]
        else:
            aviso = "O procedimento e a taxa mudam de estado para estado. "
    if registro.get("confirmar_antes") or aviso:
        aviso += "Confirme no site oficial antes de ir."
    return link, aviso


def _linha_fonte(registro, link):
    data = registro.get("data_verificacao")
    quando = formatar_data(data) if data else "data não informada"
    return "Fonte: %s (verificado em %s)" % (link, quando)


def _ou_vazio(relacionados):
    return relacionados or []


def formatar(registro, modelo, relacionados, uf=None):
    """Monta a resposta no modelo "A" (resumido) ou "B" (passo a passo)."""
    relacionados = _ou_vazio(relacionados)
    link, aviso = fonte_e_aviso(registro, uf)
    titulo = registro["pergunta"]
    linhas = []

    if modelo == "A":
        corpo = " ".join(passos(registro))
        linhas.append(_quebrar("%s: %s" % (titulo.rstrip("?. "), corpo)))
        if aviso:
            linhas.append(_quebrar("Atenção: " + aviso))
        linhas.append(_quebrar(_linha_fonte(registro, link)))
        if relacionados:
            itens = "  ".join("%d) %s" % (i, r["pergunta"])
                              for i, r in enumerate(relacionados, 1))
            linhas.append(_quebrar("Veja também: " + itens))
    else:  # modelo B
        linhas += [LINHA, titulo, LINHA]
        for i, p in enumerate(passos(registro), 1):
            linhas.append(_quebrar(p, "%d. " % i))
        linhas.append("")
        if aviso:
            linhas.append(_quebrar("Atenção: " + aviso))
        linhas.append(_quebrar(_linha_fonte(registro, link)))
        if relacionados:
            linhas += ["", "Continue consultando:"]
            for i, r in enumerate(relacionados, 1):
                linhas.append(_quebrar(r["pergunta"], "  %d  " % i))
    linhas += ["", NAO_OFICIAL]
    return "\n".join(linhas)


def pedir_escolha(candidatos):
    """Pergunta ambígua: lista numerada dos assuntos parecidos."""
    linhas = ["Encontrei mais de um assunto parecido. Qual deles você procura?", ""]
    for i, r in enumerate(candidatos, 1):
        linhas.append(_quebrar(r["pergunta"], "  %d  " % i))
    return "\n".join(linhas)


def aviso_sem_base(temas):
    """Aviso de limitação (sem base): nunca inventa instruções."""
    linhas = [
        "Não encontrei orientação verificada sobre isso na minha base.",
        "Não sou um canal oficial e não vou inventar instruções.",
        "",
        "Você pode consultar o portal oficial: " + GOV_BR,
        "ou escolher um destes temas:",
        "",
    ]
    for i, nome in enumerate(temas.values(), 1):
        linhas.append("  %d  %s" % (i, nome))
    return "\n".join(linhas)
