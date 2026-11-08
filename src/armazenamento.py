"""Armazenamento mínimo da Onda 2 (UF e temas do briefing), por user_id.

TODO (EM ABERTO, spec §5.2 e §17): o armazenamento definitivo (Supabase ou
equivalente) ainda não foi confirmado. Esta é a interface que o resto do código
usa; hoje há uma implementação em SQLite local (biblioteca padrão). Para trocar
de serviço, basta outra classe com os mesmos métodos.

Regra de privacidade (spec §13): TODA consulta é filtrada por user_id e só se
guarda o mínimo (UF e temas do briefing). Nenhum texto de mensagem é gravado.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

UFS = ("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO").split()


class ArmazenamentoSQLite:
    """Implementação local. `caminho=':memory:'` serve para os testes."""

    def __init__(self, caminho=None):
        if caminho is None:
            caminho = Path(__file__).resolve().parent.parent / "data" / "citizen.db"
        self._lock = threading.Lock()
        self._con = sqlite3.connect(str(caminho), check_same_thread=False)
        self._con.execute(
            "CREATE TABLE IF NOT EXISTS usuarios ("
            "user_id INTEGER PRIMARY KEY, uf TEXT, temas_briefing TEXT)")
        # Cofre (spec §10): só dados já cifrados; o servidor não guarda a senha.
        self._con.execute(
            "CREATE TABLE IF NOT EXISTS cofre_config ("
            "user_id INTEGER PRIMARY KEY, salt BLOB, verificador BLOB, iteracoes INTEGER)")
        self._con.execute(
            "CREATE TABLE IF NOT EXISTS cofre_docs ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, "
            "nome BLOB, conteudo BLOB)")
        self._con.commit()

    def _garantir(self, user_id):
        self._con.execute("INSERT OR IGNORE INTO usuarios (user_id) VALUES (?)", (int(user_id),))

    def definir_uf(self, user_id, uf):
        uf = str(uf).upper()
        if uf not in UFS:
            raise ValueError("UF inválida")
        with self._lock:
            self._garantir(user_id)
            self._con.execute("UPDATE usuarios SET uf = ? WHERE user_id = ?", (uf, int(user_id)))
            self._con.commit()

    def obter_uf(self, user_id):
        with self._lock:
            linha = self._con.execute(
                "SELECT uf FROM usuarios WHERE user_id = ?", (int(user_id),)).fetchone()
        return linha[0] if linha else None

    def definir_temas_briefing(self, user_id, temas):
        with self._lock:
            self._garantir(user_id)
            self._con.execute("UPDATE usuarios SET temas_briefing = ? WHERE user_id = ?",
                              (json.dumps(list(temas)), int(user_id)))
            self._con.commit()

    def obter_temas_briefing(self, user_id):
        with self._lock:
            linha = self._con.execute(
                "SELECT temas_briefing FROM usuarios WHERE user_id = ?", (int(user_id),)).fetchone()
        return json.loads(linha[0]) if linha and linha[0] else []

    # --- cofre: toda consulta filtrada por user_id (spec §13, item 3) ---

    def salvar_config_cofre(self, user_id, salt, verificador, iteracoes):
        with self._lock:
            self._con.execute(
                "INSERT OR REPLACE INTO cofre_config VALUES (?, ?, ?, ?)",
                (int(user_id), salt, verificador, int(iteracoes)))
            self._con.commit()

    def obter_config_cofre(self, user_id):
        with self._lock:
            l = self._con.execute(
                "SELECT salt, verificador, iteracoes FROM cofre_config WHERE user_id = ?",
                (int(user_id),)).fetchone()
        return {"salt": l[0], "verificador": l[1], "iteracoes": l[2]} if l else None

    def salvar_doc(self, user_id, nome_cifrado, conteudo_cifrado):
        with self._lock:
            cur = self._con.execute(
                "INSERT INTO cofre_docs (user_id, nome, conteudo) VALUES (?, ?, ?)",
                (int(user_id), nome_cifrado, conteudo_cifrado))
            self._con.commit()
            return cur.lastrowid

    def listar_docs(self, user_id):
        """[(id, nome_cifrado)] só do usuário."""
        with self._lock:
            return self._con.execute(
                "SELECT id, nome FROM cofre_docs WHERE user_id = ? ORDER BY id",
                (int(user_id),)).fetchall()

    def obter_doc(self, user_id, doc_id):
        with self._lock:
            return self._con.execute(
                "SELECT nome, conteudo FROM cofre_docs WHERE id = ? AND user_id = ?",
                (int(doc_id), int(user_id))).fetchone()

    def apagar_doc(self, user_id, doc_id):
        with self._lock:
            cur = self._con.execute(
                "DELETE FROM cofre_docs WHERE id = ? AND user_id = ?",
                (int(doc_id), int(user_id)))
            self._con.commit()
            return cur.rowcount > 0

    def apagar_usuario(self, user_id):
        """Remove tudo do usuário (/apagar_meus_dados), inclusive o cofre."""
        with self._lock:
            for tabela in ("cofre_docs", "cofre_config", "usuarios"):
                self._con.execute("DELETE FROM %s WHERE user_id = ?" % tabela, (int(user_id),))
            self._con.commit()
