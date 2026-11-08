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
import shutil
import tempfile
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (BufferedInputFile, CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, LinkPreviewOptions, Message, WebAppInfo)

import agendador
import armazenamento
import briefing
import classificador
import cofre as modulo_cofre
import documentos
import painel
import ponte
import roteador
import tarefas
import transcricao

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
# Pergunta ambígua: os candidatos vão só nos botões (a lista numerada do terminal é inútil aqui).
MSG_ESCOLHA = "Encontrei mais de um assunto parecido. Toque no que você procura:"
BOTAO_VOLTAR = "Voltar aos temas"
# Comandos que aparecem no menu do Telegram (bot.set_my_commands, chamado ao iniciar).
COMANDOS = (("menu", "Ver os assuntos por tema"),
            ("localizacao", "Informar o seu estado"),
            ("painel", "Abrir o painel"),
            ("apagar_meus_dados", "Apagar os seus dados"))
# Quem escreve só uma destas palavras quer o menu, não uma busca.
PALAVRAS_DE_MENU = {"menu", "temas", "assuntos", "ajuda", "inicio", "início", "começar", "comecar"}


def contexto_do_botao(c):
    """(mensagem, dados, user_id) de um toque em botão, ou None se não der para responder.

    O Telegram pode mandar um botão de mensagem antiga ("inacessível") ou sem dados;
    nesses casos só confirmamos o toque."""
    if not isinstance(c.message, Message) or c.data is None:
        return None
    return c.message, c.data, c.from_user.id


async def _trocar_aviso(aviso, m, texto):
    """Troca o texto do aviso "Recebi seu áudio" pelo resultado; se não der, manda mensagem nova."""
    try:
        if aviso is not None:
            await aviso.edit_text(texto)
            return
    except Exception:
        pass
    await m.answer(texto)


def eh_palavra_de_menu(texto):
    """True se a mensagem é só uma palavra de menu. Mensagem sem texto (voz, foto) é False."""
    return bool(texto) and texto.strip().lower() in PALAVRAS_DE_MENU


MSG_ERRO = "Tive um problema para responder agora. Tente de novo em instantes."
MSG_VOZ_LONGA = "Esse áudio é longo demais. Mande um de até 2 minutos ou escreva sua dúvida."
MSG_VOZ_INDISPONIVEL = ("Ainda não consigo ouvir áudios neste servidor. "
                        "Escreva sua dúvida com palavras.")
MSG_VOZ_FALHOU = ("Não consegui entender esse áudio. Tente de novo, falando mais perto, "
                  "ou escreva sua dúvida.")
MSG_VOZ_RECEBIDA = "Recebi seu áudio. Estou transcrevendo, só um instante..."
MSG_ENVIO_EXPIROU = "Esse envio expirou. Mande o arquivo de novo."
TEMPO_LIMITE_VOZ_S = 90   # o Whisper em CPU pode demorar; passou disso, avisa e segue


def teclado(linhas):
    """Monta um teclado inline a partir de [[(texto, callback)]]."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t, callback_data=c) for t, c in linha] for linha in linhas])


def botoes_assuntos(base, ids, voltar=False):
    """Um botão por assunto (callback 'ab:<id>'); o id nunca aparece para o usuário.

    Com voltar=True, a última linha leva de volta à lista de temas."""
    # Título curto do assunto: a pergunta inteira fica cortada no botão.
    linhas = [[(ponte.titulo_do(base["registros_por_id"][i]), "ab:" + i)] for i in ids]
    if voltar:
        linhas.append([(BOTAO_VOLTAR, "menu:")])
    return teclado(linhas)


def criar_bot(config, base, armazem, links, cofre=None):
    """Cria Bot e Dispatcher com todos os handlers. `config` traz as variáveis do .env."""
    bot = Bot(token=config["TELEGRAM_BOT_TOKEN"],
              default=DefaultBotProperties(parse_mode=ParseMode.HTML,
                                        link_preview=LinkPreviewOptions(is_disabled=True)))
    dp = Dispatcher()
    rota = Router()
    dp.include_router(rota)
    chave_gemini = config.get("GEMINI_API_KEY")
    # GEMINI_MODELO (opcional) vai para o início da fila; os demais vêm da lista da chave.
    modelo_env = config.get("GEMINI_MODELO") or None
    modelo_whisper = transcricao.nome_do_modelo(config)
    feeds = briefing.carregar_feeds()  # data/feeds.json (feeds por tema de interesse)
    travas = {}  # uma fila por usuário, para responder na ordem em que as mensagens chegaram

    def trava_do_usuario(user_id):
        return travas.setdefault(user_id, asyncio.Lock())

    pendentes = documentos.Pendentes()  # documento esperando confirmação (só na memória)

    async def responder(mensagem, resultado, user_id):
        # O bot usa parse_mode HTML. A resposta de um assunto já vem em HTML escapado
        # (ponte.formatar_telegram); os demais textos passam por html.escape.
        texto = resultado.get("html") or html.escape(resultado["texto"])
        if resultado["decisao"] == "SEM_BASE":
            # Os temas vão nos botões; não repetir a lista numerada do terminal.
            texto = html.escape(MSG_SEM_BASE % ponte.GOV_BR)
        if resultado["decisao"] == "PEDIR_ESCOLHA":
            texto = html.escape(MSG_ESCOLHA)
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
        ctx = contexto_do_botao(c)
        if ctx:
            mensagem, dados, user_id = ctx
            try:
                armazem.definir_uf(user_id, dados[3:])
                texto = "Estado salvo: %s. Você pode mudar quando quiser (/localizacao)." % dados[3:]
                try:  # troca o teclado de UFs pela confirmação, em vez de deixá-lo na tela
                    await mensagem.edit_text(texto)
                except Exception:
                    await mensagem.answer(texto)
            except ValueError:
                await mensagem.answer(MSG_ERRO)
        await c.answer()

    # ---- Cofre no chat (spec §10.3): a senha NUNCA passa por aqui ----
    def botao_painel(texto):
        """Botão que abre o painel como Mini App. O Telegram só aceita https."""
        url = config.get("PAINEL_URL", "").rstrip("/")
        if not url.startswith("https://"):
            return None
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=texto, web_app=WebAppInfo(url=url))]])

    async def avisar_cofre_fechado(mensagem, estado):
        if estado == "indisponivel":
            await mensagem.answer(html.escape("O cofre não está disponível agora."))
        elif estado == "sem_cofre":
            await mensagem.answer(html.escape(
                "Você ainda não criou o cofre. Crie no painel: a senha é digitada só lá, nunca aqui no chat."),
                reply_markup=botao_painel("Criar o cofre no painel"))
        else:
            await mensagem.answer(html.escape(
                "O cofre está bloqueado. Desbloqueie no painel (a senha é digitada só lá) e envie de novo."),
                reply_markup=botao_painel("Desbloquear no painel"))

    async def sugerir_nome(mensagem, user_id):
        item = pendentes.obter(user_id)
        if item is None:
            await mensagem.answer(html.escape(MSG_ENVIO_EXPIROU))
            return
        if chave_gemini and item.get("usar_gemini", True):
            try:  # o Gemini roda em outra thread; falha vira nome padrão (classificador nunca levanta)
                _, nome = await asyncio.to_thread(classificador.classificar, item["conteudo"], item["mime"])
            except Exception:
                nome = modulo_cofre.nome_padrao()
        else:
            nome = modulo_cofre.nome_padrao()
        item["nome"], item["etapa"] = nome, "confirmar"
        await mensagem.answer(html.escape("Sugestão de nome: %s. Guardar assim?" % nome), reply_markup=teclado(
            [[("Guardar com esse nome", "doc:salvar")], [("Escolher outro nome", "doc:nome")],
             [("Cancelar", "doc:cancelar")]]))

    async def salvar_pendente(mensagem, user_id):
        item = pendentes.obter(user_id)
        if item is None:
            await mensagem.answer(html.escape(MSG_ENVIO_EXPIROU))
            return
        try:
            cofre.guardar(user_id, item["nome"], item["conteudo"])
        except modulo_cofre.CofreBloqueado:  # o desbloqueio venceu no meio do caminho
            pendentes.descartar(user_id)
            await avisar_cofre_fechado(mensagem, "bloqueado")
            return
        pendentes.descartar(user_id)
        await mensagem.answer(html.escape("Guardei como \"%s\". Para ver depois, peça no chat "
                                          "(por exemplo: me envie meu RG) ou abra o painel." % item["nome"]))

    @rota.message(F.photo | F.document)
    async def documento(m: Message):
        if m.from_user is None or m.bot is None:
            return
        uid = m.from_user.id
        if m.photo:
            anexo, mime = m.photo[-1], "image/jpeg"
        else:
            anexo, mime = m.document, (m.document.mime_type or "")
        # A mensagem com o documento some do chat em 5 minutos (spec §4 item 5).
        agendador.agendar_exclusao(armazem, uid, m.chat.id, m.message_id)
        ok, motivo = documentos.arquivo_aceito(mime, anexo.file_size or 0)
        if not ok:
            await m.answer(html.escape(motivo))
            return
        estado = documentos.estado_do_cofre(cofre, uid)
        if estado != "aberto":  # cofre fechado: não guarda nada (spec §10.3)
            await avisar_cofre_fechado(m, estado)
            return
        try:
            conteudo = (await m.bot.download(anexo)).getvalue()
        except Exception as erro:
            log.warning("Falha ao baixar o arquivo (%s)", type(erro).__name__)  # sem nome nem conteúdo
            await m.answer(MSG_ERRO)
            return
        pendentes.guardar(uid, conteudo, mime)
        if chave_gemini and not armazem.tem_consentimento(uid):
            await m.answer(html.escape(documentos.AVISO_CONSENTIMENTO), reply_markup=teclado(
                [[("Concordo, sugerir um nome", "doc:ok")], [("Prefiro escolher o nome", "doc:nome")],
                 [("Cancelar", "doc:cancelar")]]))
        else:
            await sugerir_nome(m, uid)

    @rota.callback_query(F.data.startswith("doc:"))
    async def decidiu_documento(c: CallbackQuery):
        ctx = contexto_do_botao(c)
        if ctx:
            mensagem, dados, uid = ctx
            acao = dados[4:]
            item = pendentes.obter(uid)
            if acao == "cancelar":
                pendentes.descartar(uid)
                await mensagem.answer("Tudo bem, não guardei nada.")
            elif item is None:
                await mensagem.answer(html.escape(MSG_ENVIO_EXPIROU))
            elif acao == "ok":
                armazem.registrar_consentimento(uid)
                await sugerir_nome(mensagem, uid)
            elif acao == "nome":
                # Sem sugestão do Gemini: o arquivo não sai do servidor.
                item["usar_gemini"], item["etapa"] = False, "nome"
                await mensagem.answer(html.escape("Digite o nome que você quer usar (até %d caracteres)."
                                                  % documentos.NOME_MAX))
            elif acao == "salvar":
                await salvar_pendente(mensagem, uid)
        await c.answer()

    async def tratar_cofre(m, uid, args, texto):
        """Ferramenta cofre_documento: listar, abrir (enviar no chat) e orientar o envio."""
        estado = documentos.estado_do_cofre(cofre, uid)
        if estado != "aberto":
            await avisar_cofre_fechado(m, estado)
            return
        acao = args.get("acao")
        if acao == "enviar":
            await m.answer(html.escape("Para guardar, envie aqui a foto ou o PDF do documento."))
            return
        docs = cofre.listar(uid)
        lista = "\n".join("- " + nome for _, nome in docs) or "(nenhum ainda)"
        if acao == "abrir":
            achado = documentos.localizar(cofre, uid, args.get("nome") or "")
            if achado is None:
                await m.answer(html.escape("Não achei esse documento. Seus documentos:\n" + lista))
                return
            nome, conteudo = cofre.abrir(uid, achado[0])
            ext = {"application/pdf": ".pdf", "image/png": ".png", "image/jpeg": ".jpg"}.get(
                painel.tipo_mime(conteudo), "")
            enviada = await m.answer_document(BufferedInputFile(conteudo, filename=nome + ext),
                                              caption=html.escape(documentos.AVISO_ENVIO))
            agendador.agendar_exclusao(armazem, uid, enviada.chat.id, enviada.message_id)
            return
        await m.answer(html.escape("Seus documentos:\n%s\n\nPara receber um, escreva: me envie meu RG."
                                   % lista))

    @rota.message(Command("painel"))
    async def comando_painel(m: Message):
        url = config.get("PAINEL_URL", "").rstrip("/")
        if not url:
            await m.answer("O painel ainda não está configurado.")
            return
        if m.from_user is None:  # mensagem sem remetente (ex.: canal): não há para quem gerar o link
            return
        token = links.gerar(m.from_user.id)
        await m.answer(html.escape("Seu link de acesso (vale 5 minutos e só funciona uma vez):\n%s/entrar?t=%s"
                                   % (url, token)))

    @rota.message(Command("apagar_meus_dados"))
    async def comando_apagar(m: Message):
        await m.answer("Isso apaga tudo o que guardei sobre você (estado, preferências, tarefas, "
                       "documentos do cofre e o cofre em si). Confirma?", reply_markup=teclado([[("Sim, apagar tudo", "apagar:sim"),
                                                           ("Cancelar", "apagar:nao")]]))

    @rota.callback_query(F.data.startswith("apagar:"))
    async def confirmou_apagar(c: CallbackQuery):
        ctx = contexto_do_botao(c)
        if ctx:
            mensagem, dados, user_id = ctx
            if dados == "apagar:sim":
                armazem.apagar_usuario(user_id)  # inclui cofre, tarefas e exclusões agendadas
                if cofre is not None:
                    cofre.bloquear(user_id)  # esquece também a chave que estava na memória
                pendentes.descartar(user_id)
                await mensagem.answer("Pronto. Seus dados foram apagados.")
            else:
                await mensagem.answer("Tudo certo, nada foi apagado.")
        await c.answer()

    @rota.callback_query(F.data.startswith("ab:"))
    async def abrir_assunto(c: CallbackQuery):
        ctx = contexto_do_botao(c)
        if ctx:
            mensagem, dados, user_id = ctx
            rid = dados[3:]
            if rid in base["registros_por_id"]:
                resultado = roteador.resposta_do_assunto(base, rid, armazem.obter_uf(user_id))
                await responder(mensagem, resultado, user_id)
        await c.answer()

    @rota.callback_query(F.data.startswith("tema:"))
    async def abrir_tema(c: CallbackQuery):
        ctx = contexto_do_botao(c)
        if ctx:
            mensagem, dados, _ = ctx
            tema = dados[5:]
            if tema in base["ids_por_tema"]:
                await mensagem.answer("<b>%s</b>\nToque num assunto ou escreva sua dúvida."
                                      % html.escape(base["temas"][tema]),
                                      reply_markup=botoes_assuntos(base, base["ids_por_tema"][tema],
                                                                   voltar=True))
        await c.answer()

    @rota.callback_query(F.data == "menu:")
    async def voltar_aos_temas(c: CallbackQuery):
        ctx = contexto_do_botao(c)
        if ctx:
            await ctx[0].answer(html.escape(MSG_MENU), reply_markup=teclado_de_temas())
        await c.answer()

    @rota.message(F.text)
    async def texto_livre(m: Message):
        if m.from_user is None or not m.text:  # sem remetente ou sem texto: nada a responder
            return
        await processar_texto(m, m.from_user.id, m.text)

    async def processar_texto(m: Message, user_id: int, texto: str):
        """Caminho único para texto digitado e para voz já transcrita.

        Uma mensagem por vez por usuário: sem isso, uma pergunta lenta (Gemini) era
        ultrapassada pela seguinte e as respostas chegavam fora de ordem."""
        async with trava_do_usuario(user_id):
            await _processar_texto(m, user_id, texto)

    async def _processar_texto(m: Message, user_id: int, texto: str):
        try:
            if pendentes.esta_pedindo_nome(user_id):  # o texto é o nome do documento, não uma pergunta
                nome = documentos.limpar_nome(texto)
                if not nome:
                    await m.answer(html.escape("Não entendi o nome. Digite de novo."))
                    return
                pendentes.obter(user_id)["nome"] = nome
                await salvar_pendente(m, user_id)
                return
            chamada = None
            # Botões nunca chamam IA. No texto livre, a IA só entra se a base não resolveu sozinha.
            if chave_gemini and roteador.resposta_direta_basta(texto, base):
                log.info("Resposta direta da base (sem Gemini)")
            elif chave_gemini:
                try:  # "digitando..." enquanto a IA pensa; se falhar, não faz diferença
                    if m.bot:
                        await m.bot.send_chat_action(m.chat.id, "typing")
                except Exception:
                    pass
                # O Gemini roda em outra thread, com tempo limite; se falhar, usa regras.
                try:
                    nome, args = await asyncio.wait_for(
                        asyncio.to_thread(roteador.chamar_gemini, texto, chave_gemini, modelo_env),
                        timeout=roteador.TEMPO_LIMITE_LLM)
                    chamada = roteador.validar_chamada(nome, args)
                except Exception as erro:
                    # Sem o texto da mensagem (spec §13): só o tipo do erro.
                    log.warning("Gemini sem resposta útil (%s); usando regras", type(erro).__name__)
                    chamada = None
            chamada = roteador.reconciliar(chamada, texto)
            if chamada["ferramenta"] == "cofre_documento":
                await tratar_cofre(m, user_id, chamada["args"], texto)
                return
            if chamada["ferramenta"] == "gerenciar_tarefas":
                # Tarefas e lembretes: o texto de "quando" é lido por regras, sem IA (src/tarefas.py).
                resultado = tarefas.executar(chamada["args"], armazem, user_id)
            elif chamada["ferramenta"] == "briefing_matinal":
                # Busca os feeds na rede: em outra thread, para não travar o bot.
                resultado = await asyncio.to_thread(
                    briefing.executar, chamada["args"], armazem, user_id, feeds, briefing.TEMAS_BRIEFING)
            else:
                resultado = roteador.executar(chamada, base, armazem.obter_uf(user_id))
            await responder(m, resultado, user_id)
        except Exception:
            log.exception("falha ao responder")  # sem o texto da mensagem
            await m.answer(MSG_ERRO)

    @rota.message(F.voice | F.audio)
    async def voz(m: Message):
        if m.from_user is None or m.bot is None:
            return
        anexo = m.voice or m.audio
        if anexo is None:
            return
        if (anexo.duration or 0) > transcricao.DURACAO_MAXIMA_S or \
                (anexo.file_size or 0) > transcricao.TAMANHO_MAXIMO_B:
            await m.answer(MSG_VOZ_LONGA)
            return
        ok, motivo = transcricao.disponivel()
        if not ok:
            log.warning("Voz indisponível: %s", motivo)  # motivo técnico só no log
            await m.answer(MSG_VOZ_INDISPONIVEL)
            return
        # Aviso imediato: o usuário sabe que o áudio chegou enquanto transcrevemos.
        aviso = None
        try:
            await m.bot.send_chat_action(m.chat.id, "typing")
            aviso = await m.answer(MSG_VOZ_RECEBIDA)
        except Exception:
            pass
        pasta = tempfile.mkdtemp(prefix="citizen-voz-")
        try:
            destino = Path(pasta) / "audio.ogg"
            await m.bot.download(anexo, destination=destino)
            texto = await asyncio.wait_for(
                asyncio.to_thread(transcricao.transcrever, destino, modelo_whisper),
                timeout=TEMPO_LIMITE_VOZ_S)
        except Exception as erro:
            log.warning("Falha na transcrição (%s)", type(erro).__name__)  # sem o conteúdo
            await _trocar_aviso(aviso, m, MSG_VOZ_FALHOU)
            return
        finally:
            shutil.rmtree(pasta, ignore_errors=True)  # o áudio não fica no disco
        # Mostra o que foi entendido antes de responder (spec §19.6).
        await _trocar_aviso(aviso, m, "Entendi: <i>%s</i>" % html.escape(texto))
        await processar_texto(m, m.from_user.id, texto)

    @rota.message()
    async def outros(m: Message):
        await m.answer("Por enquanto só entendo texto, áudio, foto e PDF. " + ponte.NAO_OFICIAL)

    return bot, dp
