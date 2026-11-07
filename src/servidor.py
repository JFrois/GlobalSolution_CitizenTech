"""Modo --servidor: sobe o bot do Telegram e o painel (Onda 2).

Tudo da Onda 2 é importado AQUI DENTRO (import tardio, spec §5.3), então o modo
terminal continua rodando só com Python. Segredos vêm do .env (nunca do Git).
"""
from __future__ import annotations

import os
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
    for chave in list(config) + list(OBRIGATORIAS) + ["GEMINI_API_KEY", "GEMINI_MODELO", "PAINEL_URL"]:
        if chave in os.environ:
            config[chave] = os.environ[chave]
    return config


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
        import logging
        import aiogram  # noqa: F401
        import fastapi  # noqa: F401
        import uvicorn
    except ImportError as erro:
        print("Faltam bibliotecas do modo servidor (%s)." % erro.name)
        print("Instale com: pip install -r requirements.txt")
        return 1

    import armazenamento
    import base as modulo_base
    import ponte
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
    app = painel.criar_app(dados, config["TELEGRAM_BOT_TOKEN"], config["SESSAO_SEGREDO"],
                           links, config.get("PAINEL_URL", ""))

    async def rodar():
        # Registra os comandos no menu do Telegram. Se falhar (rede), o bot segue sem eles.
        try:
            from aiogram.types import BotCommand
            await bot.set_my_commands([BotCommand(command=c, description=d)
                                       for c, d in telegram_bot.COMANDOS])
        except Exception as erro:
            logging.getLogger("citizen.bot").warning("set_my_commands falhou (%s)", type(erro).__name__)
        # Painel só em localhost: o Caddy faz o HTTPS na frente (spec §12).
        servidor_web = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000,
                                                     log_level="warning"))
        await asyncio.gather(servidor_web.serve(), dp.start_polling(bot))

    try:
        asyncio.run(rodar())
    except KeyboardInterrupt:
        pass
    return 0
