"""Fluxo de documentos do bot (spec §10.3): lógica sem aiogram, para poder testar.

Regras que valem aqui:
- Se o cofre está bloqueado, o bot NÃO guarda: pede o desbloqueio no painel e que o
  usuário reenvie (a senha nunca passa pelo chat).
- O arquivo só fica na memória do servidor enquanto o usuário confirma (TTL curto).
- O nome pode ser sugerido pelo Gemini, mas o usuário confirma ou edita.
- Conteúdo de arquivo é dado, nunca instrução (spec §13 item 6).
Nenhum nome ou conteúdo de documento vai para o log (spec §13).
"""
from __future__ import annotations

import re
import time
import unicodedata

import classificador

TAMANHO_MAX = classificador.TAMANHO_MAX
MIMES_ACEITOS = classificador.MIMES_ACEITOS
VALIDADE_PENDENTE_S = 5 * 60
NOME_MAX = 60

AVISO_CONSENTIMENTO = (
    "Para reconhecer o tipo do documento e sugerir um nome, vou enviar este arquivo ao Gemini "
    "(Google, plano gratuito). Nesse plano o Google pode usar o arquivo para melhorar seus "
    "produtos, pode permitir que pessoas o revisem e pode processá-lo em outros países. "
    "Não envie documentos reais se isso for um problema para você. "
    "Se preferir, não precisa usar a sugestão: escolha um nome seu e o arquivo não é enviado.")
AVISO_ENVIO = ("Vou apagar esta mensagem do chat em 5 minutos. Isso apaga do chat, não do seu "
               "aparelho. Conversas com bots do Telegram não são protegidas de ponta a ponta.")


def estado_do_cofre(cofre, user_id):
    """'indisponivel' | 'sem_cofre' | 'bloqueado' | 'aberto'."""
    if cofre is None:
        return "indisponivel"
    if not cofre.existe(user_id):
        return "sem_cofre"
    return "aberto" if cofre.esta_desbloqueado(user_id) else "bloqueado"


def arquivo_aceito(mime, tamanho):
    """(ok, motivo para o usuário)."""
    if mime not in MIMES_ACEITOS:
        return False, "Só consigo guardar foto (JPG ou PNG) e PDF."
    if tamanho and tamanho > TAMANHO_MAX:
        return False, "Esse arquivo é grande demais. O limite é 10 MB."
    return True, ""


def _sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if not unicodedata.combining(c))


def limpar_nome(texto):
    """Nome digitado pelo usuário: sem quebras de linha, tamanho limitado. '' se vazio."""
    return re.sub(r"\s+", " ", texto or "").strip()[:NOME_MAX]


def localizar(cofre, user_id, pedido):
    """Acha um documento pelo que o usuário escreveu (sem acento e sem caixa).

    Tenta a frase inteira e depois cada palavra de 2+ letras. Devolve (id, nome) ou None."""
    pedido = _sem_acento(pedido or "").strip()
    if not pedido:
        return None
    docs = [(i, n, _sem_acento(n)) for i, n in cofre.listar(user_id)]
    for termo in [pedido] + [p for p in re.findall(r"\w+", pedido) if len(p) >= 2]:
        for i, nome, norm in docs:
            if termo in norm:
                return i, nome
    return None


class Pendentes:
    """Documento recebido que ainda espera confirmação. Só na memória, com validade."""

    def __init__(self, validade=VALIDADE_PENDENTE_S, relogio=time.monotonic):
        self._validade, self._relogio, self._itens = validade, relogio, {}

    def guardar(self, user_id, conteudo, mime, **extra):
        self._itens[int(user_id)] = dict(conteudo=conteudo, mime=mime, etapa="consentimento",
                                         expira=self._relogio() + self._validade, **extra)

    def obter(self, user_id):
        item = self._itens.get(int(user_id))
        if item is None:
            return None
        if self._relogio() >= item["expira"]:
            del self._itens[int(user_id)]
            return None
        return item

    def descartar(self, user_id):
        self._itens.pop(int(user_id), None)

    def esta_pedindo_nome(self, user_id):
        item = self.obter(user_id)
        return item is not None and item["etapa"] == "nome"
