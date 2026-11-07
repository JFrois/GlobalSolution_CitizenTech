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

    def apagar_usuario(self, user_id):
        """Remove tudo do usuário (/apagar_meus_dados)."""
        with self._lock:
            self._con.execute("DELETE FROM usuarios WHERE user_id = ?", (int(user_id),))
            self._con.commit()
