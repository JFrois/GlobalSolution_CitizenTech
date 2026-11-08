"""Modo --servidor: sobe o bot do Telegram e o painel (Onda 2).

Tudo da Onda 2 é importado AQUI DENTRO (import tardio, spec §5.3), então o modo
terminal continua rodando só com Python. Segredos vêm do .env (nunca do Git).
"""
from __future__ import annotations

import os
import socket
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
OBRIGATORIAS = ("TELEGRAM_BOT_TOKEN", "SESSAO_SEGREDO")


def ler_env(caminho=None):
    """Lê o .env (formato CHAVE=valor) sem bibliotecas. Variáveis do ambiente vencem."""
    config = {}
    caminho = Path(caminho) if caminho else RAIZ / ".env"
    if caminho.is_file():
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if linha and not linha.startswith("#") and "=" in linha:
                chave, _, valor = linha.partition("=")
                config[chave.strip()] = valor.strip().strip('"').strip("'")
    for chave in list(config) + list(OBRIGATORIAS) + ["GEMINI_API_KEY", "GEMINI_MODELO", "WHISPER_MODELO", "PAINEL_URL", "PAINEL_PORTA"]:
        if chave in os.environ:
            config[chave] = os.environ[chave]
    return config


PORTA_PADRAO = 8000


def porta_livre(porta, host="127.0.0.1"):
    """True se dá para abrir um servidor nessa porta (ninguém está usando)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # mesmo modo do uvicorn
        try:
            s.bind((host, porta))
        except OSError:
            return False
    return True


def faltando(config):
    """Nomes das variáveis obrigatórias ausentes ou vazias."""
    return [n for n in OBRIGATORIAS if not config.get(n)]


def iniciar(caminho_base=None):
    """Ponto de entrada de `python src/sistema.py --servidor`."""
    config = ler_env()
    ausentes = faltando(config)
    if ausentes:
        print("Não consegui iniciar o servidor: faltam no .env: %s." % ", ".join(ausentes))
        print("Copie .env.example para .env e preencha (o .env nunca vai para o Git).")
        return 1
    try:
        import asyncio
        import html
        import logging
        import aiogram  # noqa: F401
        import fastapi  # noqa: F401
        import uvicorn
    except ImportError as erro:
        print("Faltam bibliotecas do modo servidor (%s)." % erro.name)
        print("Instale com: pip install -r requirements.txt")
        return 1

    try:
        porta = int(config.get("PAINEL_PORTA") or PORTA_PADRAO)
    except ValueError:
        print("PAINEL_PORTA no .env precisa ser um número (ex.: 8000).")
        return 1
    if not porta_livre(porta):
        print("A porta %d já está em uso: provavelmente há outro servidor deste projeto rodando." % porta)
        print("Feche o outro (Ctrl+C na aba dele) ou veja quem usa a porta: lsof -i :%d" % porta)
        print("Dois servidores com o mesmo token do bot brigam pelas mensagens.")
        print("Para usar outra porta, coloque PAINEL_PORTA=8001 no .env.")
        return 1

    import armazenamento
    import base as modulo_base
    import ponte
    import agendador
    import cofre
    import painel
    import telegram_bot

    try:
        dados = ponte.preparar(modulo_base.carregar_base(caminho_base))
    except modulo_base.ErroBase as erro:
        print("Não consegui abrir a base de orientações: " + str(erro))
        return 1

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    armazem = armazenamento.ArmazenamentoSQLite()
    links = painel.LinksUnicos()
    bot, dp = telegram_bot.criar_bot(config, dados, armazem, links)
    cofre_usuarios = cofre.Cofre(armazem)  # chaves só em memória, TTL de 10 min
    app = painel.criar_app(dados, config["TELEGRAM_BOT_TOKEN"], config["SESSAO_SEGREDO"],
                           links, config.get("PAINEL_URL", ""), cofre_usuarios, armazem)

    async def rodar():
        # Registra os comandos no menu do Telegram. Se falhar (rede), o bot segue sem eles.
        try:
            from aiogram.types import BotCommand
            await bot.set_my_commands([BotCommand(command=c, description=d)
                                       for c, d in telegram_bot.COMANDOS])
        except Exception as erro:
            logging.getLogger("citizen.bot").warning("set_my_commands falhou (%s)", type(erro).__name__)
        # Lembretes e autodestruição (src/agendador.py): o primeiro tick já cumpre o que venceu.
        agendador.iniciar(armazem, lambda uid, texto: bot.send_message(uid, html.escape(texto)),
                          lambda chat, msg: bot.delete_message(chat, msg))
        # Painel só em localhost: o Caddy faz o HTTPS na frente (spec §12).
        servidor_web = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=porta,
                                                     log_level="warning"))
        await asyncio.gather(servidor_web.serve(), dp.start_polling(bot))

    try:
        asyncio.run(rodar())
    except KeyboardInterrupt:
        pass
    return 0
