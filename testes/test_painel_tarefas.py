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
        self.app = painel.criar_app(ponte.preparar(base.carregar_base()), "1:T", "segredo",
                                    self.links, "https://painel.exemplo", None, self.arm)
        self.TestClient = TestClient

    def cliente(self, uid):
        c = self.TestClient(self.app, base_url="https://testserver")
        c.get("/entrar", params={"t": self.links.gerar(uid)})
        return c

    def test_sem_login_recusa(self):
        c = self.TestClient(self.app, base_url="https://testserver")
        self.assertEqual(c.get("/api/tarefas").status_code, 401)
        self.assertEqual(c.post("/api/tarefas", json={"titulo": "x"}).status_code, 401)
        self.assertEqual(c.post("/api/tarefas/1/concluir").status_code, 401)

    def test_criar_listar_e_concluir(self):
        c = self.cliente(42)
        self.assertEqual(c.get("/api/tarefas").json(), {"tarefas": []})
        r = c.post("/api/tarefas", json={"titulo": "pagar a conta", "quando": "amanhã às 9h"})
        self.assertEqual(r.status_code, 200)
        itens = r.json()["tarefas"]
        self.assertEqual([i["titulo"] for i in itens], ["pagar a conta"])
        self.assertIsNotNone(itens[0]["quando"])
        self.assertIn("09:00", itens[0]["quando_texto"])
        c.post("/api/tarefas", json={"titulo": "ligar para o INSS"})  # sem data
        self.assertEqual(len(c.get("/api/tarefas").json()["tarefas"]), 2)
        r = c.post("/api/tarefas/%d/concluir" % itens[0]["id"])
        self.assertEqual(r.status_code, 200)
        self.assertEqual([i["titulo"] for i in r.json()["tarefas"]], ["ligar para o INSS"])

    def test_entradas_invalidas_dao_400_com_mensagem(self):
        c = self.cliente(42)
        for corpo in ({"titulo": ""}, {"titulo": "x", "quando": "quando der"}, {"titulo": "x", "quando": "31/02"},
                      {"titulo": "x", "quando": "01/01/2020 às 9h"}, [1], {"titulo": "a" * 201}, {"titulo": 5}):
            r = c.post("/api/tarefas", json=corpo)
            self.assertEqual(r.status_code, 400, corpo)
            self.assertIsInstance(r.json()["detail"], str)
        self.assertEqual(c.get("/api/tarefas").json(), {"tarefas": []})

    def test_usuario_a_nao_ve_nem_conclui_tarefa_de_b(self):
        a, b = self.cliente(1), self.cliente(2)
        a.post("/api/tarefas", json={"titulo": "segredo de A"})
        self.assertEqual(b.get("/api/tarefas").json(), {"tarefas": []})
        id_a = a.get("/api/tarefas").json()["tarefas"][0]["id"]
        self.assertEqual(b.post("/api/tarefas/%d/concluir" % id_a).status_code, 404)
        self.assertEqual(len(a.get("/api/tarefas").json()["tarefas"]), 1)

    def test_concluir_inexistente_404(self):
        self.assertEqual(self.cliente(1).post("/api/tarefas/999/concluir").status_code, 404)

    def test_pedidos_de_criar_sao_limitados(self):
        c = self.cliente(7)
        codigos = [c.post("/api/tarefas", json={"titulo": "t%d" % i}).status_code for i in range(40)]
        self.assertIn(429, codigos)

    def test_static_revalida_sempre(self):
        r = self.TestClient(self.app, base_url="https://testserver").get("/static/painel.css")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers["cache-control"], "no-cache")

    def test_sem_armazem_da_503(self):
        import base, ponte
        app = painel.criar_app(ponte.preparar(base.carregar_base()), "1:T", "segredo", self.links, "", None, None)
        c = self.TestClient(app, base_url="https://testserver")
        c.get("/entrar", params={"t": self.links.gerar(1)})
        self.assertEqual(c.get("/api/tarefas").status_code, 503)


if __name__ == "__main__":
    unittest.main()
