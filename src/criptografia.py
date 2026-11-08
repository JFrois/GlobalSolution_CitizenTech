"""Criptografia do cofre (spec §10.2). Só roda no modo --servidor.

Parâmetros usados (documentados porque a spec pede):
- Derivação: PBKDF2-HMAC-SHA256, 600 000 iterações, salt aleatório de 16 bytes
  por usuário, chave de 256 bits. (Argon2id não é biblioteca padrão; PBKDF2 é o
  reserva previsto na spec.)
- Cifra: AES-256-GCM, nonce aleatório de 96 bits por arquivo.
- Verificador de senha: uma constante conhecida cifrada com a chave derivada.
  Validar a senha = tentar decifrar. Nenhum hash reutilizável é guardado.
- Chave do usuário: só na memória do servidor, com TTL curto após desbloquear.

A biblioteca `cryptography` é importada dentro das funções (import tardio,
spec §5.3), para o núcleo continuar rodando só com a biblioteca padrão.
"""
from __future__ import annotations

import hashlib
import os
import threading
import time

ITERACOES = 600_000
TAM_SALT = 16
TAM_NONCE = 12
SENHA_MIN = 10
TTL_PADRAO = 600  # segundos (10 min, spec §10.2)
_CONSTANTE = b"citizen-assist-cofre-v1"


class SenhaIncorreta(Exception):
    """Senha errada ou dado adulterado (o GCM falha na verificação)."""


def _aesgcm(chave):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    return AESGCM(chave)


def derivar_chave(senha, salt, iteracoes=ITERACOES):
    """Deriva a chave de 256 bits a partir da senha e do salt do usuário."""
    return hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, iteracoes, dklen=32)


def cifrar(chave, dados, associado=b""):
    """Devolve nonce + texto cifrado. `associado` amarra o dado a um contexto."""
    nonce = os.urandom(TAM_NONCE)
    return nonce + _aesgcm(chave).encrypt(nonce, dados, associado or None)


def decifrar(chave, blob, associado=b""):
    """Inverte `cifrar`. Chave errada ou dado alterado → SenhaIncorreta."""
    from cryptography.exceptions import InvalidTag
    if len(blob) <= TAM_NONCE:
        raise SenhaIncorreta("dado inválido")
    try:
        return _aesgcm(chave).decrypt(blob[:TAM_NONCE], blob[TAM_NONCE:], associado or None)
    except InvalidTag:
        raise SenhaIncorreta("senha incorreta ou dado alterado")


def criar_cofre(senha, iteracoes=ITERACOES):
    """Gera salt e verificador para um cofre novo. O que sai pode ser gravado;
    a senha e a chave não."""
    if len(senha) < SENHA_MIN:
        raise ValueError("A senha precisa ter pelo menos %d caracteres." % SENHA_MIN)
    salt = os.urandom(TAM_SALT)
    chave = derivar_chave(senha, salt, iteracoes)
    return {"salt": salt, "verificador": cifrar(chave, _CONSTANTE), "iteracoes": iteracoes}


def abrir_cofre(senha, salt, verificador, iteracoes=ITERACOES):
    """Valida a senha e devolve a chave. Senha errada → SenhaIncorreta."""
    chave = derivar_chave(senha, salt, iteracoes)
    if decifrar(chave, verificador) != _CONSTANTE:
        raise SenhaIncorreta("senha incorreta")
    return chave


class ChavesEmMemoria:
    """Guarda a chave de cada usuário só na memória, com validade curta."""

    def __init__(self, ttl=TTL_PADRAO, relogio=time.monotonic):
        self._ttl = ttl
        self._relogio = relogio
        self._chaves = {}  # user_id -> (chave, expira_em)
        self._lock = threading.Lock()

    def guardar(self, user_id, chave):
        with self._lock:
            self._chaves[int(user_id)] = (chave, self._relogio() + self._ttl)

    def obter(self, user_id):
        """Chave se ainda válida; senão None (e esquece a chave vencida)."""
        with self._lock:
            item = self._chaves.get(int(user_id))
            if item is None:
                return None
            if self._relogio() >= item[1]:
                del self._chaves[int(user_id)]
                return None
            return item[0]

    def segundos_restantes(self, user_id):
        with self._lock:
            item = self._chaves.get(int(user_id))
        if item is None:
            return 0
        return max(0, int(item[1] - self._relogio()))

    def bloquear(self, user_id):
        with self._lock:
            self._chaves.pop(int(user_id), None)
