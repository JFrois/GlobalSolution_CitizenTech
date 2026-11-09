"""Armazenamento mínimo da Onda 2 (UF e temas do briefing), por user_id.

Interface que o resto do código usa. Há duas implementações com os mesmos métodos:
SQLite local (padrão, biblioteca padrão) e Supabase (`armazenamento_supabase.py`, só liga
com SUPABASE_URL e chave secreta no .env; se falhar, volta para o SQLite). Ver `criar`.

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
        # Tarefas e lembretes (spec §11). `quando` e `apagar_em` são segundos desde 1970 (UTC).
        self._con.execute(
            "CREATE TABLE IF NOT EXISTS tarefas ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, titulo TEXT NOT NULL, "
            "quando INTEGER, concluida INTEGER NOT NULL DEFAULT 0, avisada INTEGER NOT NULL DEFAULT 0)")
        # Horário do resumo da manhã (HH:MM, fuso de Brasília) e o último dia enviado.
        self._con.execute(
            "CREATE TABLE IF NOT EXISTS briefing_config ("
            "user_id INTEGER PRIMARY KEY, hora TEXT NOT NULL, ultimo_envio TEXT)")
        # Consentimento para enviar documentos ao Gemini (spec §10.3): pedido uma vez por usuário.
        self._con.execute("CREATE TABLE IF NOT EXISTS consentimento_gemini (user_id INTEGER PRIMARY KEY)")
        # Mensagens com documento a apagar do chat (autodestruição, spec §11).
        self._con.execute(
            "CREATE TABLE IF NOT EXISTS exclusoes ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, chat_id INTEGER NOT NULL, "
            "message_id INTEGER NOT NULL, apagar_em INTEGER NOT NULL)")
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

    # --- tarefas e lembretes ---

    def criar_tarefa(self, user_id, titulo, quando=None):
        with self._lock:
            cur = self._con.execute("INSERT INTO tarefas (user_id, titulo, quando) VALUES (?, ?, ?)",
                                    (int(user_id), titulo, None if quando is None else int(quando)))
            self._con.commit()
            return cur.lastrowid

    def listar_tarefas(self, user_id):
        """Pendentes do usuário: [(id, titulo, quando)], as com data primeiro."""
        with self._lock:
            return self._con.execute(
                "SELECT id, titulo, quando FROM tarefas WHERE user_id = ? AND concluida = 0 "
                "ORDER BY quando IS NULL, quando, id", (int(user_id),)).fetchall()

    def listar_tarefas_avisadas(self, user_id):
        """Ids das pendentes cujo lembrete já foi enviado (o painel as separa das ainda por vir)."""
        with self._lock:
            return {r[0] for r in self._con.execute(
                "SELECT id FROM tarefas WHERE user_id = ? AND concluida = 0 AND avisada = 1",
                (int(user_id),)).fetchall()}

    def concluir_tarefa(self, user_id, tarefa_id):
        with self._lock:
            cur = self._con.execute(
                "UPDATE tarefas SET concluida = 1 WHERE id = ? AND user_id = ?",
                (int(tarefa_id), int(user_id)))
            self._con.commit()
            return cur.rowcount > 0

    def tarefas_a_avisar(self, agora):
        """Lembretes vencidos ainda não avisados: [(id, user_id, titulo, quando)]."""
        with self._lock:
            return self._con.execute(
                "SELECT id, user_id, titulo, quando FROM tarefas WHERE concluida = 0 AND avisada = 0 "
                "AND quando IS NOT NULL AND quando <= ?", (int(agora),)).fetchall()

    def marcar_avisada(self, tarefa_id):
        with self._lock:
            self._con.execute("UPDATE tarefas SET avisada = 1 WHERE id = ?", (int(tarefa_id),))
            self._con.commit()

    def tarefas_do_dia(self, user_id, inicio, fim):
        """Pendentes com data entre `inicio` e `fim` (para o briefing)."""
        with self._lock:
            return self._con.execute(
                "SELECT id, titulo, quando FROM tarefas WHERE user_id = ? AND concluida = 0 "
                "AND quando >= ? AND quando < ? ORDER BY quando", (int(user_id), int(inicio), int(fim))
            ).fetchall()

    # --- resumo da manhã ---

    def definir_hora_briefing(self, user_id, hora):
        with self._lock:
            self._con.execute(
                "INSERT INTO briefing_config (user_id, hora) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET hora = excluded.hora",
                (int(user_id), hora))
            self._con.commit()

    def obter_hora_briefing(self, user_id):
        with self._lock:
            l = self._con.execute("SELECT hora FROM briefing_config WHERE user_id = ?",
                                  (int(user_id),)).fetchone()
        return l[0] if l else None

    def briefings_a_enviar(self, hoje, hora_atual):
        """[(user_id, hora)] cujo horário já chegou hoje e que ainda não receberam hoje (strings ISO / HH:MM)."""
        with self._lock:
            return [(l[0], l[1]) for l in self._con.execute(
                "SELECT user_id, hora FROM briefing_config WHERE hora <= ? "
                "AND (ultimo_envio IS NULL OR ultimo_envio <> ?)", (hora_atual, hoje)).fetchall()]

    def marcar_briefing_enviado(self, user_id, hoje):
        with self._lock:
            self._con.execute("UPDATE briefing_config SET ultimo_envio = ? WHERE user_id = ?",
                              (hoje, int(user_id)))
            self._con.commit()

    # --- consentimento do envio ao Gemini ---

    def registrar_consentimento(self, user_id):
        with self._lock:
            self._con.execute("INSERT OR IGNORE INTO consentimento_gemini VALUES (?)", (int(user_id),))
            self._con.commit()

    def tem_consentimento(self, user_id):
        with self._lock:
            return self._con.execute("SELECT 1 FROM consentimento_gemini WHERE user_id = ?",
                                     (int(user_id),)).fetchone() is not None

    # --- autodestruição de mensagens ---

    def agendar_exclusao(self, user_id, chat_id, message_id, apagar_em):
        with self._lock:
            self._con.execute(
                "INSERT INTO exclusoes (user_id, chat_id, message_id, apagar_em) VALUES (?, ?, ?, ?)",
                (int(user_id), int(chat_id), int(message_id), int(apagar_em)))
            self._con.commit()

    def exclusoes_vencidas(self, agora):
        """[(id, chat_id, message_id)] que já passaram da hora."""
        with self._lock:
            return self._con.execute(
                "SELECT id, chat_id, message_id FROM exclusoes WHERE apagar_em <= ?",
                (int(agora),)).fetchall()

    def remover_exclusao(self, exclusao_id):
        with self._lock:
            self._con.execute("DELETE FROM exclusoes WHERE id = ?", (int(exclusao_id),))
            self._con.commit()

    def apagar_usuario(self, user_id):
        """Remove tudo do usuário (/apagar_meus_dados), inclusive o cofre."""
        with self._lock:
            for tabela in ("cofre_docs", "cofre_config", "tarefas", "exclusoes", "briefing_config", "consentimento_gemini", "usuarios"):
                self._con.execute("DELETE FROM %s WHERE user_id = ?" % tabela, (int(user_id),))
            self._con.commit()


def criar(config, log=None):
    """Escolhe o armazenamento: Supabase se o .env tiver SUPABASE_URL e uma chave secreta
    que funcione; em qualquer outro caso (ou se a verificação falhar), SQLite local.
    Nunca levanta por causa do Supabase: o sistema volta sozinho para o SQLite."""
    import logging
    log = log or logging.getLogger("citizen.armazenamento")
    chave = (config.get("SUPABASE_KEY") or "").strip()
    if not chave:
        return ArmazenamentoSQLite()
    try:
        import armazenamento_supabase as sb
        url = sb.normalizar_url(config.get("SUPABASE_URL"))
        if not url:
            raise sb.ErroSupabase("SUPABASE_URL inválida (use https://<projeto>.supabase.co)")
        if not sb.chave_e_secreta(chave):
            raise sb.ErroSupabase("SUPABASE_KEY não é uma chave secreta (sb_secret_...)")
        armazem = sb.ArmazenamentoSupabase(url, chave)
        armazem.verificar()
    except Exception as erro:  # qualquer falha: SQLite, sem derrubar o servidor
        log.warning("Supabase desligado, usando SQLite local: %s", erro)
        return ArmazenamentoSQLite()
    log.info("Armazenamento: Supabase")
    return armazem
