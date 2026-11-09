"""Supabase: o adaptador contra um servidor PostgREST FALSO em memória, e a volta para o SQLite.

O servidor falso entende só o que o adaptador usa (eq, lt, lte, gte, neq, not.is.null,
is.null, or, order, select, limit, upsert, return=representation). Os mesmos testes de
comportamento rodam no SQLite e no Supabase falso, para garantir que os dois se comportam igual.
"""
import json
import logging
import threading
import unittest
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import armazenamento  # noqa: E402
import armazenamento_supabase as sb  # noqa: E402

CHAVE = "sb_secret_teste"
COM_ID = ("cofre_docs", "tarefas", "exclusoes")


def _cmp(valor, op):
    ops = {"eq": lambda a, b: a == b, "neq": lambda a, b: a != b, "lt": lambda a, b: a < b,
           "lte": lambda a, b: a <= b, "gte": lambda a, b: a >= b}
    nome, _, resto = op.partition(".")
    if nome == "is":
        return (valor is None) if resto == "null" else (valor is not None)
    if nome == "not":
        return not _cmp(valor, resto)
    if valor is None:
        return False
    try:
        alvo = type(valor)(resto)
    except (TypeError, ValueError):
        alvo = resto
    return ops[nome](valor, alvo)


def _casa(linha, filtros):
    for chave, op in filtros:
        if chave == "or":
            partes = op.strip("()").split(",")
            if not any(_cmp(linha.get(p.split(".", 1)[0]), p.split(".", 1)[1]) for p in partes):
                return False
        elif not _cmp(linha.get(chave), op):
            return False
    return True


class PostgRESTFalso(BaseHTTPRequestHandler):
    tabelas = {}
    proximo_id = {}
    chave_valida = CHAVE

    def log_message(self, *a):
        pass

    def _tratar(self, metodo):
        if self.headers.get("apikey") != self.chave_valida:
            return self._resp(401, {"message": "chave"})
        u = urllib.parse.urlparse(self.path)
        tabela = u.path.rsplit("/", 1)[-1]
        q = urllib.parse.parse_qsl(u.query)
        especiais = ("select", "order", "limit", "on_conflict")
        filtros = [(k, v) for k, v in q if k not in especiais]
        dados = self.tabelas.setdefault(tabela, [])
        prefer = self.headers.get("Prefer", "")
        corpo = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)) or 0) or "null")
        if metodo == "GET":
            linhas = [l for l in dados if _casa(l, filtros)]
            for k, v in q:
                if k == "order":
                    for campo in reversed([c for c in v.split(",")]):
                        nome, _, ordem = campo.partition(".")
                        nulos_fim = "nullslast" in ordem
                        linhas.sort(key=lambda l: ((l.get(nome) is None) == nulos_fim and 0 or 1,
                                                   l.get(nome) if l.get(nome) is not None else 0))
                        if nulos_fim:
                            linhas.sort(key=lambda l: l.get(nome) is None)
                if k == "limit":
                    linhas = linhas[:int(v)]
            return self._resp(200, [self._proj(l, q) for l in linhas])
        if metodo == "POST":
            conflito = dict(q).get("on_conflict")
            if conflito and "merge-duplicates" in prefer:
                for l in dados:
                    if l.get(conflito) == corpo[conflito]:
                        l.update(corpo)
                        return self._resp(201, None)
            novo = dict(corpo)
            if tabela == "tarefas":  # valores padrão que o Postgres aplica (ver deploy/supabase_schema.sql)
                novo.setdefault("concluida", 0)
                novo.setdefault("avisada", 0)
            if tabela in COM_ID:
                self.proximo_id[tabela] = self.proximo_id.get(tabela, 0) + 1
                novo["id"] = self.proximo_id[tabela]
            dados.append(novo)
            return self._resp(201, [self._proj(novo, q)] if "representation" in prefer else None)
        alvos = [l for l in dados if _casa(l, filtros)]
        if metodo == "PATCH":
            for l in alvos:
                l.update(corpo)
        if metodo == "DELETE":
            for l in alvos:
                dados.remove(l)
        return self._resp(200, [self._proj(l, q) for l in alvos] if "representation" in prefer else None)

    @staticmethod
    def _proj(linha, q):
        sel = dict(q).get("select")
        return {c: linha.get(c) for c in sel.split(",")} if sel else dict(linha)

    def _resp(self, codigo, corpo):
        dados = b"" if corpo is None else json.dumps(corpo).encode()
        self.send_response(codigo)
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self): self._tratar("GET")
    def do_POST(self): self._tratar("POST")
    def do_PATCH(self): self._tratar("PATCH")
    def do_DELETE(self): self._tratar("DELETE")


class ComServidorFalso(unittest.TestCase):
    def setUp(self):
        PostgRESTFalso.tabelas, PostgRESTFalso.proximo_id = {}, {}
        self.srv = HTTPServer(("127.0.0.1", 0), PostgRESTFalso)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = "http://127.0.0.1:%d" % self.srv.server_port
        self.addCleanup(self.srv.server_close)
        self.addCleanup(self.srv.shutdown)


class TestContrato(ComServidorFalso):
    """Mesmo comportamento no SQLite e no Supabase falso."""

    def armazens(self):
        return [("sqlite", armazenamento.ArmazenamentoSQLite(":memory:")),
                ("supabase", sb.ArmazenamentoSupabase(self.url, CHAVE))]

    def para_cada(self, funcao):
        for nome, a in self.armazens():
            with self.subTest(nome):
                funcao(a)

    def test_uf_e_temas_isolados_por_usuario(self):
        def f(a):
            a.definir_uf(1, "sp")
            a.definir_uf(2, "RJ")
            a.definir_temas_briefing(1, ["musica", "filmes"])
            self.assertEqual((a.obter_uf(1), a.obter_uf(2), a.obter_uf(3)), ("SP", "RJ", None))
            self.assertEqual(a.obter_temas_briefing(1), ["musica", "filmes"])
            self.assertEqual(a.obter_temas_briefing(2), [])
            self.assertEqual(a.obter_uf(1), "SP")  # tema não apagou a UF
            with self.assertRaises(ValueError):
                a.definir_uf(1, "XX")
        self.para_cada(f)

    def test_cofre_binario_e_isolamento(self):
        def f(a):
            a.salvar_config_cofre(1, b"\x00salt\xff", b"verif", 600000)
            self.assertEqual(a.obter_config_cofre(1), {"salt": b"\x00salt\xff", "verificador": b"verif",
                                                       "iteracoes": 600000})
            self.assertIsNone(a.obter_config_cofre(2))
            i = a.salvar_doc(1, b"nome\x01", b"conteudo\x02")
            self.assertEqual(a.listar_docs(1), [(i, b"nome\x01")])
            self.assertEqual(a.listar_docs(2), [])
            self.assertEqual(tuple(a.obter_doc(1, i)), (b"nome\x01", b"conteudo\x02"))
            self.assertIsNone(a.obter_doc(2, i))
            self.assertFalse(a.apagar_doc(2, i))
            self.assertTrue(a.apagar_doc(1, i))
            self.assertEqual(a.listar_docs(1), [])
        self.para_cada(f)

    def test_tarefas(self):
        def f(a):
            sem_data = a.criar_tarefa(1, "sem data")
            b = a.criar_tarefa(1, "b", 200)
            c = a.criar_tarefa(1, "c", 100)
            a.criar_tarefa(2, "do outro", 50)
            self.assertEqual([t[1] for t in a.listar_tarefas(1)], ["c", "b", "sem data"])
            self.assertEqual(sorted(t[2] for t in a.tarefas_a_avisar(150)), ["c", "do outro"])
            a.marcar_avisada(c)
            self.assertEqual(a.listar_tarefas_avisadas(1), {c})
            self.assertEqual(sorted(t[2] for t in a.tarefas_a_avisar(150)), ["do outro"])
            self.assertEqual([t[1] for t in a.tarefas_do_dia(1, 100, 201)], ["c", "b"])
            self.assertFalse(a.concluir_tarefa(2, b))  # outro usuário
            self.assertTrue(a.concluir_tarefa(1, b))
            self.assertEqual([t[0] for t in a.listar_tarefas(1)], [c, sem_data])
        self.para_cada(f)

    def test_briefing_consentimento_exclusoes_e_apagar_usuario(self):
        def f(a):
            a.definir_hora_briefing(1, "07:30")
            self.assertEqual(a.obter_hora_briefing(1), "07:30")
            self.assertEqual(a.briefings_a_enviar("2026-11-09", "07:29"), [])
            self.assertEqual(a.briefings_a_enviar("2026-11-09", "08:00"), [(1, "07:30")])
            a.marcar_briefing_enviado(1, "2026-11-09")
            self.assertEqual(a.briefings_a_enviar("2026-11-09", "08:00"), [])
            self.assertEqual(a.briefings_a_enviar("2026-11-10", "08:00"), [(1, "07:30")])
            a.definir_hora_briefing(1, "07:45")  # trocar a hora não perde o último envio
            self.assertEqual(a.briefings_a_enviar("2026-11-09", "08:00"), [])
            self.assertFalse(a.tem_consentimento(1))
            a.registrar_consentimento(1)
            a.registrar_consentimento(1)
            self.assertTrue(a.tem_consentimento(1))
            self.assertFalse(a.tem_consentimento(2))
            a.agendar_exclusao(1, 10, 20, 100)
            [(eid, chat, msg)] = a.exclusoes_vencidas(100)
            self.assertEqual((chat, msg), (10, 20))
            self.assertEqual(a.exclusoes_vencidas(99), [])
            a.remover_exclusao(eid)
            self.assertEqual(a.exclusoes_vencidas(100), [])
            a.definir_uf(1, "SP")
            a.criar_tarefa(1, "x")
            a.salvar_doc(1, b"n", b"c")
            a.apagar_usuario(1)
            self.assertEqual((a.obter_uf(1), a.listar_tarefas(1), a.listar_docs(1), a.tem_consentimento(1),
                              a.obter_hora_briefing(1)), (None, [], [], False, None))
        self.para_cada(f)


class TestEscolhaDoArmazenamento(ComServidorFalso):
    def criar(self, **config):
        return armazenamento.criar(config, logging.getLogger("teste"))

    def test_sem_chave_usa_sqlite(self):
        self.assertIsInstance(self.criar(SUPABASE_URL=self.url), armazenamento.ArmazenamentoSQLite)

    def test_chave_publica_cai_para_sqlite(self):
        with self.assertLogs("teste", "WARNING"):
            a = self.criar(SUPABASE_URL="https://abc.supabase.co", SUPABASE_KEY="sb_publishable_xyz")
        self.assertIsInstance(a, armazenamento.ArmazenamentoSQLite)

    def test_url_invalida_cai_para_sqlite(self):
        with self.assertLogs("teste", "WARNING"):
            a = self.criar(SUPABASE_URL="https://exemplo.com", SUPABASE_KEY="sb_secret_x")
        self.assertIsInstance(a, armazenamento.ArmazenamentoSQLite)

    def test_url_do_dashboard_vira_url_da_api(self):
        self.assertEqual(sb.normalizar_url("https://supabase.com/dashboard/project/wdbigrykcsoadfunsutf"),
                         "https://wdbigrykcsoadfunsutf.supabase.co")
        self.assertEqual(sb.normalizar_url("https://abc.supabase.co/"), "https://abc.supabase.co")
        self.assertEqual(sb.normalizar_url("http://abc.supabase.co"), "")

    def test_tipos_de_chave(self):
        self.assertTrue(sb.chave_e_secreta("sb_secret_abc"))
        self.assertFalse(sb.chave_e_secreta("sb_publishable_abc"))
        self.assertFalse(sb.chave_e_secreta("qualquer"))
        import base64
        def jwt(papel):
            corpo = base64.urlsafe_b64encode(json.dumps({"role": papel}).encode()).decode().rstrip("=")
            return "h.%s.s" % corpo
        self.assertTrue(sb.chave_e_secreta(jwt("service_role")))
        self.assertFalse(sb.chave_e_secreta(jwt("anon")))

    def test_servidor_fora_do_ar_levanta_erro_sem_dados(self):
        morto = sb.ArmazenamentoSupabase("http://127.0.0.1:1", CHAVE, tempo_limite=1)
        with self.assertRaises(sb.ErroSupabase):
            morto.verificar()

    def test_chave_errada_e_erro(self):
        with self.assertRaises(sb.ErroSupabase) as e:
            sb.ArmazenamentoSupabase(self.url, "outra").verificar()
        self.assertNotIn("outra", str(e.exception))


if __name__ == "__main__":
    unittest.main()
