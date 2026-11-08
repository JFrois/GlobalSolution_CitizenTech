"""Testes das rotas de tarefas do painel (precisa de fastapi e httpx)."""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import painel  # noqa: E402


def _dependencias():
    try:
        import fastapi, httpx  # noqa: F401,E401
    except ImportError:
        return False
    return True


@unittest.skipUnless(_dependencias(), "precisa de fastapi e httpx")
class TestRotasTarefas(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        import armazenamento
        import base
        import ponte
        self.arm = armazenamento.ArmazenamentoSQLite(":memory:")
        self.links = painel.LinksUnicos()
        self.base = ponte.preparar(base.carregar_base())
        self.app = painel.criar_app(self.base, "1:T", "segredo", self.links,
                                    "https://painel.exemplo", None, self.arm)
        self.TestClient = TestClient

    def cliente(self, uid, app=None):
        c = self.TestClient(app or self.app, base_url="https://testserver")
        c.get("/entrar", params={"t": self.links.gerar(uid)})
        return c

    def test_sem_login_recusado(self):
        c = self.TestClient(self.app, base_url="https://testserver")
        for m, u in (("get", "/api/tarefas"), ("post", "/api/tarefas"), ("post", "/api/tarefas/1/concluir")):
            self.assertEqual(getattr(c, m)(u).status_code, 401, u)

    def test_criar_listar_e_concluir(self):
        c = self.cliente(42)
        self.assertEqual(c.get("/api/tarefas").json(), {"tarefas": []})
        r = c.post("/api/tarefas", json={"titulo": "pagar a conta de luz", "quando": ""})
        self.assertEqual(r.status_code, 200)
        dados = r.json()
        self.assertIn("Anotado", dados["mensagem"])
        [t] = dados["tarefas"]
        self.assertEqual((t["titulo"], t["quando"], t["quando_texto"]), ("pagar a conta de luz", None, None))
        self.assertEqual(c.post("/api/tarefas/%d/concluir" % t["id"]).json()["tarefas"], [])
        # Concluir de novo não dá erro (clique duplo) e a lista continua vazia.
        self.assertEqual(c.post("/api/tarefas/%d/concluir" % t["id"]).json()["tarefas"], [])
        self.assertEqual(c.post("/api/tarefas/9999/concluir").status_code, 404)

    def test_com_data_traz_texto_do_aviso(self):
        c = self.cliente(42)
        [t] = c.post("/api/tarefas", json={"titulo": "consulta", "quando": "daqui a 2 horas"}).json()["tarefas"]
        self.assertIsInstance(t["quando"], int)
        self.assertTrue(t["quando_texto"])

    def test_entradas_ruins_dao_400_com_mensagem(self):
        c = self.cliente(42)
        for corpo in ({"titulo": "x", "quando": "quando der"}, {"titulo": "", "quando": ""},
                      {"titulo": "x" * 201, "quando": ""}, {"titulo": "x", "quando": "y" * 81}):
            r = c.post("/api/tarefas", json=corpo)
            self.assertEqual(r.status_code, 400, corpo)
            self.assertTrue(r.json()["detail"])
        self.assertEqual(c.post("/api/tarefas", content=b"nao e json",
                                headers={"content-type": "application/json"}).status_code, 400)
        self.assertEqual(self.arm.listar_tarefas(42), [])

    def test_usuario_b_nao_ve_nem_conclui_tarefa_de_a(self):
        a, b = self.cliente(1), self.cliente(2)
        [t] = a.post("/api/tarefas", json={"titulo": "tarefa de A", "quando": ""}).json()["tarefas"]
        self.assertEqual(b.get("/api/tarefas").json(), {"tarefas": []})
        self.assertEqual(b.post("/api/tarefas/%d/concluir" % t["id"]).status_code, 404)
        self.assertEqual(len(a.get("/api/tarefas").json()["tarefas"]), 1)

    def test_sem_armazenamento_responde_503(self):
        app = painel.criar_app(self.base, "1:T", "segredo", self.links, "https://painel.exemplo", None, None)
        c = self.cliente(42, app)
        self.assertEqual(c.get("/api/tarefas").status_code, 503)

    def test_front_tem_a_aba_tarefas(self):
        c = self.TestClient(self.app, base_url="https://testserver")
        html = c.get("/").text
        self.assertIn('id="aba-tarefas"', html)
        self.assertIn('id="form-tarefa"', html)


if __name__ == "__main__":
    unittest.main()
