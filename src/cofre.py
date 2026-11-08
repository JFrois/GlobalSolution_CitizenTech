"""Cofre de documentos (spec §10). Só no modo --servidor.

Fluxo: criar (senha só no painel) → desbloquear (chave na memória, TTL curto) →
guardar / listar / abrir / apagar. Nome e conteúdo são cifrados antes de ir ao
armazenamento. Toda operação é filtrada por user_id.
A senha NUNCA passa pelo chat do Telegram e não é gravada.
"""
from __future__ import annotations

import datetime

import criptografia as cripto


class CofreBloqueado(Exception):
    """Cofre sem chave em memória (nunca desbloqueado ou TTL vencido)."""


class CofreInexistente(Exception):
    """Usuário ainda não criou o cofre."""


def nome_padrao(hoje=None):
    """Nome usado quando o classificador falha (spec §10.3)."""
    hoje = hoje or datetime.date.today()
    return "documento-%s" % hoje.strftime("%Y%m%d")


class Cofre:
    def __init__(self, armazenamento, chaves=None, iteracoes=cripto.ITERACOES):
        self._arm = armazenamento
        self._chaves = chaves or cripto.ChavesEmMemoria()
        self._iteracoes = iteracoes

    def existe(self, user_id):
        return self._arm.obter_config_cofre(user_id) is not None

    def esta_desbloqueado(self, user_id):
        return self._chaves.obter(user_id) is not None

    def segundos_restantes(self, user_id):
        return self._chaves.segundos_restantes(user_id)

    def criar(self, user_id, senha):
        if self.existe(user_id):
            raise ValueError("O cofre já existe.")
        c = cripto.criar_cofre(senha, self._iteracoes)
        self._arm.salvar_config_cofre(user_id, c["salt"], c["verificador"], c["iteracoes"])
        self._chaves.guardar(user_id, cripto.abrir_cofre(
            senha, c["salt"], c["verificador"], c["iteracoes"]))

    def desbloquear(self, user_id, senha):
        """Senha errada → criptografia.SenhaIncorreta."""
        cfg = self._arm.obter_config_cofre(user_id)
        if cfg is None:
            raise CofreInexistente()
        self._chaves.guardar(user_id, cripto.abrir_cofre(
            senha, cfg["salt"], cfg["verificador"], cfg["iteracoes"]))

    def bloquear(self, user_id):
        self._chaves.bloquear(user_id)

    def _chave(self, user_id):
        chave = self._chaves.obter(user_id)
        if chave is None:
            raise CofreBloqueado()
        return chave

    def guardar(self, user_id, nome, conteudo):
        chave = self._chave(user_id)
        return self._arm.salvar_doc(
            user_id, cripto.cifrar(chave, nome.encode("utf-8")), cripto.cifrar(chave, conteudo))

    def listar(self, user_id):
        """[(id, nome)] decifrado; exige cofre desbloqueado."""
        chave = self._chave(user_id)
        return [(i, cripto.decifrar(chave, n).decode("utf-8"))
                for i, n in self._arm.listar_docs(user_id)]

    def abrir(self, user_id, doc_id):
        """(nome, conteudo) ou None se o documento não é deste usuário."""
        chave = self._chave(user_id)
        linha = self._arm.obter_doc(user_id, doc_id)
        if linha is None:
            return None
        return cripto.decifrar(chave, linha[0]).decode("utf-8"), cripto.decifrar(chave, linha[1])

    def apagar(self, user_id, doc_id):
        """Apaga de verdade (arquivo e metadados). Não exige senha desbloqueada."""
        return self._arm.apagar_doc(user_id, doc_id)
