"""Tarefas e lembretes (spec §11). Só no modo --servidor, mas sem dependências externas.

O LLM (ou as regras) só escolhem a ação; aqui o texto de "quando" é interpretado
por regras fixas (sem IA) e tudo é filtrado por user_id.

TODO (EM ABERTO, spec §11): fuso do usuário. Por ora vale America/Sao_Paulo para todos.
"""
from __future__ import annotations

import datetime
import re
import unicodedata

try:
    from zoneinfo import ZoneInfo
    FUSO_PADRAO = ZoneInfo("America/Sao_Paulo")
except Exception:  # sem tzdata (ex.: Windows): Brasília sem horário de verão desde 2019
    FUSO_PADRAO = datetime.timezone(datetime.timedelta(hours=-3))

HORA_PADRAO = 9  # data sem hora: lembrar às 9h
MSG_NAO_ENTENDI_QUANDO = ("Não entendi quando devo te avisar. Escreva, por exemplo: "
                          "amanhã às 9h, hoje 18:30, dia 15 às 10h ou daqui a 2 horas.")
MSG_PASSADO = "Essa data e hora já passou. Diga um momento no futuro."
MSG_DATA_IMPOSSIVEL = "Essa data não existe no calendário. Confira o dia e o mês e tente de novo."


class DataImpossivel(ValueError):
    """O texto tem uma data no formato certo, mas que não existe (ex.: 31/02)."""


def agora_local(fuso=FUSO_PADRAO):
    return datetime.datetime.now(fuso)


def _sem_acento(texto):
    # Remove só as marcas combinadas: o tamanho fica igual e os índices valem no original.
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower())
                   if not unicodedata.combining(c))


def interpretar_quando(texto, agora):
    """Lê data/hora em português. Devolve (datetime ou None, texto sem a expressão de tempo).

    `agora` tem fuso. Levanta DataImpossivel se a data escrita não existe. Aceita: hoje, amanhã, depois de amanhã, dia 15, 15/11, 15/11/2026,
    2026-11-15, 9h, 9h30, 09:30, "às 9", "daqui a 2 horas/30 minutos". Só data → 9h;
    só hora → hoje (ou amanhã se já passou)."""
    t = _sem_acento(texto)
    usados = []  # trechos (início, fim) reconhecidos, para tirar do título

    def achar(padrao):
        m = re.search(padrao, t)
        if m:
            usados.append(m.span())
        return m

    def limpo():
        partes, fim = [], 0
        for a, b in sorted(usados):
            partes.append(texto[fim:a]); fim = max(fim, b)
        partes.append(texto[fim:])
        return re.sub(r"\s+", " ", " ".join(partes)).strip(" ,.-:")

    m = achar(r"daqui a (\d{1,3}) ?(minutos?|min|horas?|h)\b")
    if m:
        n = int(m.group(1))
        delta = datetime.timedelta(minutes=n) if m.group(2).startswith("m") else datetime.timedelta(hours=n)
        return agora + delta, limpo()

    dia = None
    if achar(r"\bdepois de amanha\b"):
        dia = agora.date() + datetime.timedelta(days=2)
    elif achar(r"\bamanha\b"):
        dia = agora.date() + datetime.timedelta(days=1)
    elif achar(r"\bhoje\b"):
        dia = agora.date()
    else:
        try:
            m = achar(r"\b(\d{4})-(\d{2})-(\d{2})\b")
            if m:
                dia = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            else:
                m = achar(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\b")
                if m:
                    ano = int(m.group(3)) if m.group(3) else agora.year
                    dia = datetime.date(ano, int(m.group(2)), int(m.group(1)))
                    if not m.group(3) and dia < agora.date():
                        dia = dia.replace(year=ano + 1)
                else:
                    m = achar(r"\bdia (\d{1,2})\b")
                    if m:
                        d = int(m.group(1))
                        ano, mes = agora.year, agora.month
                        if d < agora.day:
                            mes += 1
                            if mes > 12:
                                mes, ano = 1, ano + 1
                        dia = datetime.date(ano, mes, d)
        except ValueError:
            raise DataImpossivel(texto)  # ex.: dia 31 de fevereiro

    hora = None
    m = achar(r"\b(?:as )?([01]?\d|2[0-3]) ?(?:h|:) ?([0-5]\d)?\b") or achar(r"\bas ([01]?\d|2[0-3])\b")
    if m:
        hora = (int(m.group(1)), int(m.group(2)) if m.lastindex and m.lastindex >= 2 and m.group(2) else 0)
    if dia is None and hora is None:
        return None, texto.strip()
    if dia is None:
        dia = agora.date()
    h, mi = hora if hora else (HORA_PADRAO, 0)
    quando = datetime.datetime(dia.year, dia.month, dia.day, h, mi, tzinfo=agora.tzinfo)
    if quando <= agora and hora is not None and dia == agora.date() and not re.search(r"\bhoje\b", t):
        quando += datetime.timedelta(days=1)  # "às 8h" já passou hoje: amanhã
    return quando, limpo()


def _limpar_titulo(titulo):
    titulo = re.sub(r"^(me lembre?( de)?|lembrete( de)?|criar tarefa|nova tarefa|tarefa)\b[: ]*", "",
                    titulo.strip(), flags=re.I)
    return titulo.strip(" ,.-:")[:200]


def formatar_quando(quando, fuso=FUSO_PADRAO):
    dt = datetime.datetime.fromtimestamp(quando, fuso)
    return dt.strftime("%d/%m às %H:%M")


def executar(args, armazem, user_id, agora=None):
    """Ação de tarefas/lembretes. Devolve {"texto", "opcoes", "decisao"} como o roteador."""
    agora = agora or agora_local()
    acao = args.get("acao")
    if acao == "criar":
        return _criar(args, armazem, user_id, agora)
    if acao == "concluir":
        return _concluir(args, armazem, user_id)
    return _listar(armazem, user_id)


def _resp(texto):
    return {"texto": texto, "opcoes": [], "decisao": "TAREFA"}


def _criar(args, armazem, user_id, agora):
    _, texto = tentar_criar(args.get("titulo"), args.get("quando"), armazem, user_id, agora)
    return _resp(texto)


def tentar_criar(titulo, pedido_quando, armazem, user_id, agora=None):
    """Cria a tarefa se o texto for válido. Devolve (criou, mensagem para o usuário).

    Usada pelo chat (via _criar) e pelo painel, que precisa saber se deu certo."""
    agora = agora or agora_local()
    titulo = (titulo or "").strip()
    pedido_quando = (pedido_quando or "").strip()
    try:
        quando, resto = interpretar_quando(pedido_quando, agora) if pedido_quando else (None, "")
        if pedido_quando and quando is None:
            return False, MSG_NAO_ENTENDI_QUANDO
        if quando is None and titulo:  # a data pode estar dentro do próprio título
            quando, resto_titulo = interpretar_quando(titulo, agora)
            if quando is not None:
                titulo = resto_titulo
    except DataImpossivel:
        return False, MSG_DATA_IMPOSSIVEL
    titulo = _limpar_titulo(titulo)
    if not titulo:
        return False, "Qual é a tarefa? Escreva, por exemplo: me lembre de pagar a conta amanhã às 9h."
    if quando is not None and quando <= agora:
        return False, MSG_PASSADO
    armazem.criar_tarefa(user_id, titulo, quando.timestamp() if quando else None)
    if quando:
        return True, "Anotado: %s, %s. Aviso você nessa hora." % (titulo, formatar_quando(quando.timestamp()))
    return True, "Anotado: %s. (Sem data, então não vou avisar.)" % titulo


def lista_para_painel(armazem, user_id):
    """Pendentes do usuário em formato de dados: [{id, titulo, quando, quando_texto}]."""
    return [{"id": i, "titulo": t, "quando": q,
             "quando_texto": formatar_quando(q) if q else None}
            for i, t, q in armazem.listar_tarefas(user_id)]


def _listar(armazem, user_id):
    itens = armazem.listar_tarefas(user_id)
    if not itens:
        return _resp("Você não tem tarefas pendentes.")
    linhas = ["%d. %s%s" % (n, t, " (%s)" % formatar_quando(q) if q else "")
              for n, (_, t, q) in enumerate(itens, 1)]
    return _resp("Suas tarefas:\n" + "\n".join(linhas) + "\n\nPara concluir, escreva: concluir tarefa 1.")


def _concluir(args, armazem, user_id):
    itens = armazem.listar_tarefas(user_id)
    alvo = (args.get("titulo") or "").strip()
    achada = None
    m = re.search(r"\d+", alvo)
    if m and 1 <= int(m.group()) <= len(itens):
        achada = itens[int(m.group()) - 1]
    elif alvo:
        achada = next((i for i in itens if _sem_acento(alvo) in _sem_acento(i[1])), None)
    if achada is None:
        return _resp("Não achei essa tarefa. Escreva \"minhas tarefas\" para ver a lista.")
    armazem.concluir_tarefa(user_id, achada[0])
    return _resp("Pronto, concluí: %s." % achada[1])
