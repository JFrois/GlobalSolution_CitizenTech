"""Resumo da manhã (spec §11). Só no modo --servidor.

Duas partes SEPARADAS: (1) tarefas e lembretes do dia, do próprio usuário; (2) até 3
manchetes por tema, de feeds RSS, sempre rotuladas "Notícias — fonte não oficial".
As manchetes nunca se misturam com a base verificada nem viram orientação.
Falha de um feed (rede, XML ruim) não derruba o briefing: aquele feed é ignorado.

Os feeds ficam em `data/feeds.json` (dados, não código).
TODO (EM ABERTO, spec §11 e §17): a equipe escolhe os feeds de cada tema.
"""
from __future__ import annotations

import datetime
import json
import logging
import re
import urllib.request
from pathlib import Path

import tarefas

log = logging.getLogger("citizen.briefing")

CAMINHO_FEEDS = Path(__file__).resolve().parent.parent / "data" / "feeds.json"
MAX_POR_TEMA = 3
TEMPO_LIMITE_FEED_S = 8
TAM_MAX_FEED = 2 * 1024 * 1024
ROTULO_NOTICIAS = "Notícias — fonte não oficial"
FORMATO_HORA = re.compile(r"([01]\d|2[0-3]):[0-5]\d")


def carregar_feeds(caminho=CAMINHO_FEEDS):
    """{tema: [urls http(s)]}. Arquivo ausente ou inválido → {} (só as tarefas aparecem)."""
    try:
        dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(dados, dict):
        return {}
    return {tema: [u for u in urls if isinstance(u, str) and u.startswith(("http://", "https://"))]
            for tema, urls in dados.items() if isinstance(urls, list) and not tema.startswith("_")}


def coletar_rss(url):
    """Baixa um feed e devolve [(título, link)]. Import tardio do feedparser."""
    import feedparser
    pedido = urllib.request.Request(url, headers={"User-Agent": "CitizenAssistAI/1.0"})
    with urllib.request.urlopen(pedido, timeout=TEMPO_LIMITE_FEED_S) as r:
        conteudo = r.read(TAM_MAX_FEED)
    saida = []
    for e in feedparser.parse(conteudo).entries:
        titulo = re.sub(r"\s+", " ", str(e.get("title", ""))).strip()[:140]
        link = str(e.get("link", ""))
        if titulo:
            saida.append((titulo, link if link.startswith(("http://", "https://")) else ""))
    return saida


def manchetes_do_tema(urls, coletor=coletar_rss, maximo=MAX_POR_TEMA):
    """Até `maximo` manchetes, juntando os feeds do tema na ordem. Feed com erro é pulado."""
    achadas = []
    for url in urls:
        try:
            achadas.extend(coletor(url))
        except Exception as erro:
            log.warning("feed ignorado (%s)", type(erro).__name__)  # sem a URL nem o conteúdo
        if len(achadas) >= maximo:
            break
    return achadas[:maximo]


def montar(user_id, armazem, feeds, nomes_dos_temas, agora=None, coletor=coletar_rss):
    """Texto do resumo do dia (sem HTML; quem envia escapa)."""
    agora = agora or tarefas.agora_local()
    inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    fim = inicio + datetime.timedelta(days=1)
    linhas = ["Bom dia! Seu resumo de %s." % agora.strftime("%d/%m"), ""]
    do_dia = armazem.tarefas_do_dia(user_id, inicio.timestamp(), fim.timestamp())
    if do_dia:
        linhas.append("Tarefas e lembretes de hoje:")
        linhas += ["- %s (%s)" % (t, tarefas.formatar_quando(q)[-5:]) for _, t, q in do_dia]
    else:
        linhas.append("Você não tem tarefas com data para hoje.")
    temas = armazem.obter_temas_briefing(user_id)
    blocos = []
    for tema in temas:
        itens = manchetes_do_tema(feeds.get(tema, []), coletor)
        if itens:
            blocos.append((nomes_dos_temas.get(tema, tema), itens))
    if blocos:
        linhas += ["", ROTULO_NOTICIAS + " (não são orientações verificadas)"]
        for nome, itens in blocos:
            linhas.append(nome + ":")
            for titulo, link in itens:
                linhas.append("- " + titulo + ("\n  " + link if link else ""))
    elif temas:
        linhas += ["", "Sem manchetes disponíveis agora para os seus temas."]
    return "\n".join(linhas)


def definir_hora(armazem, user_id, hora, agora=None):
    """Grava o horário do resumo. Se o horário de hoje já passou, o primeiro resumo é o de
    amanhã: sem isso, quem configura 07:30 às 14:00 receberia o resumo na hora (o agendador
    também cobre o dia de um servidor que subiu atrasado)."""
    agora = agora or tarefas.agora_local()
    armazem.definir_hora_briefing(user_id, hora)
    if hora <= agora.strftime("%H:%M"):
        armazem.marcar_briefing_enviado(user_id, agora.strftime("%Y-%m-%d"))


def executar(args, armazem, user_id, feeds, nomes_dos_temas, agora=None, coletor=coletar_rss):
    """Ferramenta briefing_matinal. Devolve {"texto", "opcoes", "decisao"}. Pode demorar (rede)."""
    def resp(texto):
        return {"texto": texto, "opcoes": [], "decisao": "BRIEFING"}
    if args.get("acao") != "configurar":
        return resp(montar(user_id, armazem, feeds, nomes_dos_temas, agora, coletor))
    temas, hora = args.get("temas"), args.get("hora")
    if not temas and not hora:
        return resp("Para configurar, diga o horário e os temas. Por exemplo: "
                    "resumo da manhã às 07:30. Você também pode ajustar no /painel.")
    partes = []
    if temas is not None:
        validos = [t for t in temas if t in nomes_dos_temas]
        if not validos:
            return resp("Não reconheci esses temas. Os disponíveis são: %s." % ", ".join(nomes_dos_temas.values()))
        armazem.definir_temas_briefing(user_id, validos)
        partes.append("temas: " + ", ".join(nomes_dos_temas[t] for t in validos))
    if hora:
        if not FORMATO_HORA.fullmatch(hora):
            return resp("Não entendi o horário. Use o formato 07:30.")
        definir_hora(armazem, user_id, hora, agora)
        partes.append("horário: " + hora)
    return resp("Resumo da manhã configurado (%s)." % "; ".join(partes))
