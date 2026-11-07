"""Bot do Telegram (aiogram 3.x): interface, user_id, comandos e botões.

Só é importado pelo modo --servidor (import tardio). Textos conforme
docs/ux.md §4. Regras de privacidade (spec §13): não registra o texto das
mensagens nem tokens nos logs, e toda leitura/escrita usa o user_id.
O bot nunca fica mudo: qualquer erro vira uma mensagem amigável.
"""
from __future__ import annotations

import asyncio
import html
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,
                           LinkPreviewOptions, Message)

import armazenamento
import ponte
import roteador

log = logging.getLogger("citizen.bot")

MSG_BOAS_VINDAS = (
    "Olá! Sou o Citizen Assist AI, um assistente de orientação cidadã NÃO OFICIAL.\n"
    "Respondo só com informações verificadas em fontes oficiais e sempre mostro a fonte.\n\n"
    "Escreva sua dúvida, por exemplo: como consultar minha situação eleitoral.\n"
    "Ou toque em /menu para ver os assuntos por tema.\n"
    "Comandos: /menu  /localizacao  /painel  /apagar_meus_dados")
MSG_MENU = "Escolha um tema para ver os assuntos, ou escreva sua dúvida com suas palavras."
MSG_SEM_BASE = ("Não encontrei orientação verificada sobre isso na minha base. "
                "Não sou um canal oficial e não vou inventar instruções.\n\n"
                "Você pode consultar o portal oficial: %s\nou escolher um tema abaixo:")
# Comandos que aparecem no menu do Telegram (bot.set_my_commands, chamado ao iniciar).
COMANDOS = (("menu", "Ver os assuntos por tema"),
            ("localizacao", "Informar o seu estado"),
            ("painel", "Abrir o painel"),
            ("apagar_meus_dados", "Apagar os seus dados"))
# Quem escreve só uma destas palavras quer o menu, não uma busca.
PALAVRAS_DE_MENU = {"menu", "temas", "assuntos", "ajuda", "inicio", "início", "começar", "comecar"}


def eh_palavra_de_menu(texto):
    """True se a mensagem é só uma palavra de menu. Mensagem sem texto (voz, foto) é False."""
    return bool(texto) and texto.strip().lower() in PALAVRAS_DE_MENU


MSG_ERRO = "Tive um problema para responder agora. Tente de novo em instantes."


def teclado(linhas):
    """Monta um teclado inline a partir de [[(texto, callback)]]."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t, callback_data=c) for t, c in linha] for linha in linhas])


def botoes_assuntos(base, ids):
    """Um botão por assunto (callback 'ab:<id>'); o id nunca aparece para o usuário."""
    # Título curto do assunto: a pergunta inteira fica cortada no botão.
    return teclado([[(ponte.titulo_do(base["registros_por_id"][i]), "ab:" + i)] for i in ids])


def criar_bot(config, base, armazem, links):
    """Cria Bot e Dispatcher com todos os handlers. `config` traz as variáveis do .env."""
    bot = Bot(token=config["TELEGRAM_BOT_TOKEN"],
              default=DefaultBotProperties(parse_mode=ParseMode.HTML,
                                        link_preview=LinkPreviewOptions(is_disabled=True)))
    dp = Dispatcher()
    rota = Router()
    dp.include_router(rota)
    chave_gemini = config.get("GEMINI_API_KEY")
    # GEMINI_MODELO (opcional) vira o primeiro da cascata; os demais ficam de reserva.
    modelo_env = config.get("GEMINI_MODELO")
    modelos = ((modelo_env,) + tuple(m for m in roteador.MODELOS_GEMINI if m != modelo_env)
               if modelo_env else roteador.MODELOS_GEMINI)

    async def responder(mensagem, resultado, user_id):
        # O bot usa parse_mode HTML. A resposta de um assunto já vem em HTML escapado
        # (ponte.formatar_telegram); os demais textos passam por html.escape.
        texto = resultado.get("html") or html.escape(resultado["texto"])
        if resultado["decisao"] == "SEM_BASE":
            # Os temas vão nos botões; não repetir a lista numerada do terminal.
            texto = html.escape(MSG_SEM_BASE % ponte.GOV_BR)
        markup = botoes_assuntos(base, resultado["opcoes"]) if resultado["opcoes"] else None
        if resultado["decisao"] == "SEM_BASE":
            markup = teclado([[(nome, "tema:" + tid)] for tid, nome in base["temas"].items()])
        await mensagem.answer(texto, reply_markup=markup)
        registro = base["registros_por_id"].get(resultado.get("registro", ""), {})
        if registro.get("abrangencia") == "estadual" and not armazem.obter_uf(user_id):
            await mensagem.answer("Para ver o link do seu estado, use /localizacao.")

    def teclado_de_temas():
        return teclado([[(nome, "tema:" + tid)] for tid, nome in base["temas"].items()])

    @rota.message(Command("menu", "ajuda"))
    async def comando_menu(m: Message):
        await m.answer(html.escape(MSG_MENU), reply_markup=teclado_de_temas())

    @rota.message(F.text.func(eh_palavra_de_menu))
    async def palavra_de_menu(m: Message):
        await m.answer(html.escape(MSG_MENU), reply_markup=teclado_de_temas())

    @rota.message(Command("start"))
    async def comando_start(m: Message):
        await m.answer(html.escape(MSG_BOAS_VINDAS))

    @rota.message(Command("localizacao"))
    async def comando_localizacao(m: Message):
        ufs = armazenamento.UFS
        linhas = [[(uf, "uf:" + uf) for uf in ufs[i:i + 6]] for i in range(0, len(ufs), 6)]
        await m.answer("Qual é o seu estado (UF)? Uso só para mostrar o link certo.",
                       reply_markup=teclado(linhas))

    @rota.callback_query(F.data.startswith("uf:"))
    async def escolheu_uf(c: CallbackQuery):
        try:
            armazem.definir_uf(c.from_user.id, c.data[3:])
            await c.message.answer("Estado salvo: %s. Você pode mudar quando quiser." % c.data[3:])
        except ValueError:
            await c.message.answer(MSG_ERRO)
        await c.answer()

    @rota.message(Command("painel"))
    async def comando_painel(m: Message):
        url = config.get("PAINEL_URL", "").rstrip("/")
        if not url:
            await m.answer("O painel ainda não está configurado.")
            return
        token = links.gerar(m.from_user.id)
        await m.answer(html.escape("Seu link de acesso (vale 5 minutos e só funciona uma vez):\n%s/entrar?t=%s"
                                   % (url, token)))

    @rota.message(Command("apagar_meus_dados"))
    async def comando_apagar(m: Message):
        await m.answer("Isso apaga tudo o que guardei sobre você (estado, preferências). "
                       "Confirma?", reply_markup=teclado([[("Sim, apagar tudo", "apagar:sim"),
                                                           ("Cancelar", "apagar:nao")]]))

    @rota.callback_query(F.data.startswith("apagar:"))
    async def confirmou_apagar(c: CallbackQuery):
        if c.data == "apagar:sim":
            armazem.apagar_usuario(c.from_user.id)  # TODO: apagar também o cofre (Onda 2)
            await c.message.answer("Pronto. Seus dados foram apagados.")
        else:
            await c.message.answer("Tudo certo, nada foi apagado.")
        await c.answer()

    @rota.callback_query(F.data.startswith("ab:"))
    async def abrir_assunto(c: CallbackQuery):
        rid = c.data[3:]
        if rid in base["registros_por_id"]:
            resultado = roteador.resposta_do_assunto(base, rid, armazem.obter_uf(c.from_user.id))
            await responder(c.message, resultado, c.from_user.id)
        await c.answer()

    @rota.callback_query(F.data.startswith("tema:"))
    async def abrir_tema(c: CallbackQuery):
        tema = c.data[5:]
        if tema in base["ids_por_tema"]:
            await c.message.answer(html.escape(base["temas"][tema]),
                                   reply_markup=botoes_assuntos(base, base["ids_por_tema"][tema]))
        await c.answer()

    @rota.message(F.text)
    async def texto_livre(m: Message):
        try:
            chamada = None
            if chave_gemini:
                # O Gemini roda em outra thread, com tempo limite; se falhar, usa regras.
                try:
                    nome, args = await asyncio.wait_for(
                        asyncio.to_thread(roteador.chamar_gemini, m.text, chave_gemini, modelos),
                        timeout=roteador.TEMPO_LIMITE_LLM)
                    chamada = roteador.validar_chamada(nome, args)
                except Exception as erro:
                    # Sem o texto da mensagem (spec §13): só o tipo do erro.
                    log.warning("Gemini sem resposta útil (%s); usando regras", type(erro).__name__)
                    chamada = None
            chamada = chamada or roteador.fallback_por_regras(m.text)
            resultado = roteador.executar(chamada, base, armazem.obter_uf(m.from_user.id))
            await responder(m, resultado, m.from_user.id)
        except Exception:
            log.exception("falha ao responder")  # sem o texto da mensagem
            await m.answer(MSG_ERRO)

    @rota.message()
    async def outros(m: Message):
        # Foto, PDF e voz entram na próxima rodada (cofre e transcrição).
        await m.answer("Por enquanto só entendo mensagens de texto. " + ponte.NAO_OFICIAL)

    return bot, dp
