"""Transcrição de voz com Whisper local (modo --servidor).

O áudio é transcrito na própria máquina: nada é enviado a serviço externo.
A biblioteca `whisper` e o `ffmpeg` só são usados aqui, por import tardio
(spec §5.3): o modo terminal não depende de nenhum dos dois.

Privacidade (spec §13): este módulo nunca registra o texto transcrito nem o
conteúdo do áudio; só o tipo do erro e a duração.
"""
from __future__ import annotations

import logging
import shutil
import threading

log = logging.getLogger("citizen.voz")

MODELO_PADRAO = "base"
MODELOS_VALIDOS = ("tiny", "base", "small", "medium")
IDIOMA = "pt"
# Dica de vocabulário: o Whisper `base` ouviu "segundo aviado" no lugar de "segunda via".
# Com esta frase de contexto ele acerta os termos do projeto (medido em 07/11, ver uso_ia.md).
VOCABULARIO = ("Perguntas sobre documentos e serviços públicos: segunda via do RG, CIN, "
               "título de eleitor, CadÚnico, Meu INSS, CNIS, Consumidor.gov.br, "
               "Defensoria Pública, Disque 100, Ligue 180.")
DURACAO_MAXIMA_S = 120      # áudio mais longo que isso é recusado antes de transcrever
TAMANHO_MAXIMO_B = 10 * 1024 * 1024

_modelo = None
_nome_carregado = None
_trava = threading.Lock()   # o Whisper não é seguro para duas transcrições ao mesmo tempo


class ErroTranscricao(Exception):
    """Falha que o bot explica ao usuário (sem stack trace)."""


def nome_do_modelo(config):
    """Modelo do .env (WHISPER_MODELO); valor desconhecido volta ao padrão."""
    nome = (config.get("WHISPER_MODELO") or MODELO_PADRAO).strip().lower()
    return nome if nome in MODELOS_VALIDOS else MODELO_PADRAO


def disponivel():
    """(ok, motivo): se dá para transcrever nesta máquina."""
    if shutil.which("ffmpeg") is None:
        return False, "ffmpeg não instalado"
    try:
        import whisper  # noqa: F401
    except ImportError:
        return False, "biblioteca whisper não instalada"
    return True, ""


def _carregar(nome):
    """Carrega o modelo uma vez e reaproveita nas chamadas seguintes."""
    global _modelo, _nome_carregado
    if _modelo is None or _nome_carregado != nome:
        import whisper  # import tardio: só o servidor precisa
        log.info("Carregando modelo Whisper '%s'", nome)
        _modelo = whisper.load_model(nome)
        _nome_carregado = nome
    return _modelo


def transcrever(caminho, nome_modelo=MODELO_PADRAO):
    """Transcreve o arquivo de áudio e devolve o texto. Bloqueante: chame em thread."""
    ok, motivo = disponivel()
    if not ok:
        raise ErroTranscricao(motivo)
    try:
        with _trava:
            modelo = _carregar(nome_modelo)
            # fp16=False: em CPU o Whisper avisa e cai para fp32 de qualquer jeito.
            saida = modelo.transcribe(str(caminho), language=IDIOMA, fp16=False,
                                     initial_prompt=VOCABULARIO)
    except ErroTranscricao:
        raise
    except Exception as erro:
        log.warning("Whisper falhou (%s)", type(erro).__name__)
        raise ErroTranscricao("falha ao transcrever") from erro
    texto = str(saida.get("text") or "").strip()
    if not texto:
        raise ErroTranscricao("áudio sem fala reconhecida")
    return texto
