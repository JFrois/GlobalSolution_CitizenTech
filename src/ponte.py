"""Ponte entre o servidor (bot, roteador, painel) e o núcleo (busca.py, respostas.py).

O servidor foi escrito pensando em um conjunto de funções simples (preparar,
buscar, formatar...). Este módulo oferece esses nomes em cima do núcleo
oficial, para que o servidor não duplique regra de busca nem de resposta.
Tudo aqui é só biblioteca padrão. O núcleo continua sendo a única fonte da
orientação (a resposta nunca vem do LLM).
"""
from __future__ import annotations

import html
from urllib.parse import urlparse

import busca
import respostas

# Textos e limites reaproveitados do núcleo, com os nomes que o servidor usa.
MSG_VAZIA = respostas.MSG_VAZIA
MSG_SEM_PALAVRA = respostas.MSG_SEM_PALAVRAS
MSG_LONGA = respostas.MSG_LONGA
NAO_OFICIAL = respostas.FRASE_NAO_OFICIAL
GOV_BR = respostas.PORTAL_GOV
LIMITE_PERGUNTA = 300  # mesmo limite do terminal (sistema.MAX_PERGUNTA)

aviso_sem_base = respostas.aviso_sem_base
formatar_data = respostas.formatar_data

tokenizar = busca.normalizar


def preparar(base: dict) -> dict:
    """Acrescenta à base os atalhos que o servidor usa (idempotente)."""
    if "_buscador" not in base:
        base["_buscador"] = busca.Buscador(base)
        base["registros_por_id"] = base["por_id"]
        base["grafo"] = base["_buscador"].grafo
        base["ids_por_tema"] = {}
        for reg in sorted(base["registros"], key=lambda r: r["id"]):
            base["ids_por_tema"].setdefault(reg["tema"], []).append(reg["id"])
    return base


def buscar(pergunta: str, base: dict) -> dict:
    """{'decisao': ..., 'candidatos': [(id, pontos), ...]} (1 candidato se responder)."""
    preparar(base)
    r = base["_buscador"].buscar(pergunta)
    pontos = dict(r.ranking)
    return {"decisao": r.decisao, "candidatos": [(i, pontos[i]) for i in r.candidatos]}


def relacionados(base: dict, rid: str) -> list:
    """Os 3 assuntos mais próximos (Dijkstra), sem o próprio assunto."""
    preparar(base)
    return base["_buscador"].sugestoes(rid, 3, excluir=(rid,))


def fonte_e_aviso(reg: dict, uf=None) -> tuple:
    """(link, aviso). Em registro estadual usa o link da UF, se existir;
    senão fica o link nacional e o aviso de que muda de estado para estado."""
    link = reg["referencia"]
    if reg.get("abrangencia") == "estadual" and uf:
        link = reg.get("referencias_estaduais", {}).get(uf, link)
    return link, respostas.aviso_do(reg)


def passos(reg: dict) -> list:
    return respostas.dividir_passos(reg["orientacao"])


def pedir_escolha(regs: list) -> str:
    por_id = {r["id"]: r for r in regs}
    return respostas.pedir_escolha(list(por_id), por_id)


def formatar_telegram(reg: dict, uf=None) -> str:
    """Resposta em HTML do Telegram: título em negrito, passos numerados, aviso, fonte
    com link e a frase de não-oficialidade. Sem molduras nem quebra em 80 colunas (a
    tela do celular é estreita). Os assuntos para continuar vão em botões, não no texto.
    Todo texto vindo da base passa por html.escape."""
    esc = html.escape
    link, _ = fonte_e_aviso(reg, uf)
    partes = ["<b>%s</b>" % esc(respostas.titulo_do(reg)), ""]
    partes += ["%d. %s" % (i, esc(p)) for i, p in enumerate(passos(reg), start=1)]
    aviso = respostas.texto_do_aviso(reg)
    if aviso:
        partes += ["", "<b>Atenção:</b> " + esc(aviso.replace("Atenção: ", "", 1))]
    dominio = urlparse(link).netloc.replace("www.", "") or link
    verificado = ("verificado em " + formatar_data(reg["data_verificacao"])
                  if reg["data_verificacao"] else formatar_data(""))
    partes += ["", '<b>Fonte:</b> <a href="%s">%s</a> (%s)' % (esc(link, quote=True), esc(dominio), verificado),
               "", "<i>%s</i>" % esc(NAO_OFICIAL)]
    return "\n".join(partes)


def formatar(reg: dict, modelo: str, regs: list, uf=None) -> str:
    """Resposta completa no modelo A ou B, com os assuntos de 'regs' para continuar."""
    link, _ = fonte_e_aviso(reg, uf)
    reg_uf = dict(reg, referencia=link)
    por_id = {r["id"]: r for r in regs}
    return respostas.montar_resposta(modelo, reg_uf, [r["id"] for r in regs], por_id)
