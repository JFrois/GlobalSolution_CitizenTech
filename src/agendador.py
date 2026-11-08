"""Agendador (spec §11): lembretes e autodestruição de mensagens. Só no modo --servidor.

Decisão de projeto: a "persistência" vem do banco, não de um jobstore do APScheduler.
Lembretes e exclusões ficam nas tabelas `tarefas` e `exclusoes`; a cada tick o
`processar` executa tudo o que venceu. Assim, ao subir o servidor, o primeiro tick já
cumpre o que venceu enquanto ele estava fora (exigência da spec), sem depender de
SQLAlchemy. O APScheduler só dispara o tick (import tardio).

Privacidade (spec §13): o log não traz título de tarefa nem conteúdo de mensagem.
"""
from __future__ import annotations

import datetime
import logging
import time

import tarefas

log = logging.getLogger("citizen.agendador")

INTERVALO_S = 30
ATRASO_EXCLUSAO_S = 5 * 60      # documento some do chat em 5 minutos (spec §4 item 5)
IDADE_MAX_EXCLUSAO_S = 48 * 3600  # o Telegram só deixa apagar mensagens com menos de 48 h


def agendar_exclusao(armazem, user_id, chat_id, message_id, agora=None):
    """Marca uma mensagem com documento para ser apagada em 5 minutos."""
    agora = time.time() if agora is None else agora
    armazem.agendar_exclusao(user_id, chat_id, message_id, agora + ATRASO_EXCLUSAO_S)


# Atraso a partir do qual o lembrete avisa o horário original (servidor fora do ar, máquina dormindo).
ATRASO_AVISADO_SEG = 5 * 60


def texto_do_lembrete(titulo, quando, agora):
    """"Lembrete: X"; se chegar com mais de 5 min de atraso, diz o horário que estava marcado."""
    if quando is not None and agora - quando > ATRASO_AVISADO_SEG:
        return "Lembrete (marcado para %s, enviado com atraso): %s" % (tarefas.formatar_quando(quando), titulo)
    return "Lembrete: %s" % titulo


# Resumo da manhã com mais atraso que isto (servidor parado) é pulado: não faz sentido às 22h.
ATRASO_MAX_BRIEFING_MIN = 3 * 60


def erro_definitivo(erro):
    """True quando tentar de novo não adianta: o usuário bloqueou o bot ou a conversa não existe.

    Compara pelo nome da classe para não importar o aiogram aqui (o agendador é testado sem ele)."""
    nome = type(erro).__name__
    if nome == "TelegramForbiddenError":
        return True
    return nome == "TelegramBadRequest" and "chat not found" in str(erro).lower()


def _minutos(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


async def processar(armazem, enviar, apagar, agora=None, briefing=None):
    """Cumpre o que venceu. Devolve (lembretes enviados, mensagens apagadas).

    `enviar(user_id, texto)` e `apagar(chat_id, message_id)` são corrotinas do bot.
    `briefing(user_id)` (opcional, corrotina) devolve o texto do resumo da manhã.
    Falha de um item não derruba os outros: o lembrete fica pendente e tenta no próximo tick."""
    agora = time.time() if agora is None else agora
    avisos = apagadas = 0
    for tarefa_id, user_id, titulo, quando in armazem.tarefas_a_avisar(agora):
        try:
            await enviar(user_id, texto_do_lembrete(titulo, quando, agora))
            armazem.marcar_avisada(tarefa_id)
            avisos += 1
        except Exception as erro:
            if erro_definitivo(erro):
                # Bot bloqueado ou conversa apagada: marca para não tentar a cada 30 s para sempre.
                armazem.marcar_avisada(tarefa_id)
                log.info("lembrete descartado (%s): usuário inacessível", type(erro).__name__)
            else:
                log.warning("lembrete não enviado (%s); tenta de novo", type(erro).__name__)
    if briefing is not None:
        local = datetime.datetime.fromtimestamp(agora, tarefas.FUSO_PADRAO)
        hoje, agora_hhmm = local.strftime("%Y-%m-%d"), local.strftime("%H:%M")
        for user_id, hora in armazem.briefings_a_enviar(hoje, agora_hhmm):
            if _minutos(agora_hhmm) - _minutos(hora) > ATRASO_MAX_BRIEFING_MIN:
                armazem.marcar_briefing_enviado(user_id, hoje)  # atrasado demais: volta amanhã
                log.info("resumo da manhã pulado: mais de 3 h de atraso")
                continue
            try:
                texto = await briefing(user_id)
                if texto:
                    await enviar(user_id, texto)
                armazem.marcar_briefing_enviado(user_id, hoje)
            except Exception as erro:
                if erro_definitivo(erro):
                    armazem.marcar_briefing_enviado(user_id, hoje)
                    log.info("resumo descartado (%s): usuário inacessível", type(erro).__name__)
                else:
                    log.warning("briefing não enviado (%s); tenta de novo", type(erro).__name__)
    for excl_id, chat_id, message_id in armazem.exclusoes_vencidas(agora):
        try:
            await apagar(chat_id, message_id)
            apagadas += 1
        except Exception as erro:
            # Mensagem já apagada ou velha demais: não adianta tentar de novo.
            log.info("mensagem não apagada (%s)", type(erro).__name__)
        armazem.remover_exclusao(excl_id)
    return avisos, apagadas


def iniciar(armazem, enviar, apagar, intervalo=INTERVALO_S, briefing=None):
    """Liga o APScheduler (dentro do loop do asyncio já em execução). Devolve o agendador."""
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    agendador = AsyncIOScheduler()
    agendador.add_job(processar, "interval", seconds=intervalo, args=[armazem, enviar, apagar, None, briefing],
                      # Primeiro tick já na subida: cumpre o que venceu com o servidor fora do ar.
                      next_run_time=datetime.datetime.now(), max_instances=1, coalesce=True, id="tick")
    agendador.start()
    return agendador
