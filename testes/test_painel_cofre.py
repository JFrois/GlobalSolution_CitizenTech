"""Testes das rotas de cofre e configuração do painel (precisa de fastapi, httpx e cryptography)."""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import painel  # noqa: E402


def _dependencias():
    try:
        import cryptography, fastapi, httpx  # noqa: F401,E401
    except ImportError:
        return False
    return True


class TestFuncoesPuras(unittest.TestCase):
    def test_tipo_mime_pelos_bytes(self):
        self.assertEqual(painel.tipo_mime(b"%PDF-1.4"), "application/pdf")
        self.assertEqual(painel.tipo_mime(b"\x89PNG\r\n\x1a\nxx"), "image/png")
        self.assertEqual(painel.tipo_mime(b"\xff\xd8\xffxx"), "image/jpeg")
        self.assertEqual(painel.tipo_mime(b"texto"), "application/octet-stream")

    def test_validar_config(self):
        temas = {"documentacao": "Doc"}
        self.assertEqual(painel.validar_config({"uf": "sp", "temas": ["documentacao"]}, temas),
                         ("SP", ["documentacao"]))
        for ruim in ({"uf": "XX"}, {"temas": ["inexistente"]}, {"temas": "doc"}, [1], {"uf": 3}):
            with self.assertRaises(ValueError):
                painel.validar_config(ruim, temas)


@unittest.skipUnless(_dependencias(), "precisa de fastapi, httpx e cryptography")
class TestRotasCofre(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        import armazenamento
        import base
        import cofre
        import criptografia
        import ponte
        self.arm = armazenamento.ArmazenamentoSQLite(":memory:")
        self.cofre = cofre.Cofre(self.arm, criptografia.ChavesEmMemoria(), iteracoes=1000)
        self.links = painel.LinksUnicos()
        self.app = painel.criar_app(ponte.preparar(base.carregar_base()), "1:T", "segredo",
                                    self.links, "https://painel.exemplo", self.cofre, self.arm)
        self.TestClient = TestClient

    def cliente(self, uid):
        c = self.TestClient(self.app, base_url="https://testserver")
        c.get("/entrar", params={"t": self.links.gerar(uid)})
        return c

    def test_sem_login_tudo_recusado(self):
        c = self.TestClient(self.app, base_url="https://testserver")
        for m, u in (("get", "/api/estado"), ("get", "/api/cofre/docs"), ("post", "/api/cofre/criar"),
                     ("put", "/api/config"), ("delete", "/api/cofre/docs/1")):
            self.assertEqual(getattr(c, m)(u).status_code, 401, u)

    def test_fluxo_completo(self):
        c = self.cliente(42)
        self.assertFalse(c.get("/api/estado").json()["cofre_existe"])
        self.assertEqual(c.post("/api/cofre/criar", json={"senha": "curta"}).status_code, 400)
        self.assertEqual(c.post("/api/cofre/criar", json={"senha": "senha-bem-longa"}).status_code, 200)
        self.assertEqual(c.post("/api/cofre/criar", json={"senha": "senha-bem-longa"}).status_code, 409)
        i = self.cofre.guardar(42, "rg-ficticio", b"%PDF-1.4 fake")
        self.assertEqual(c.get("/api/cofre/docs").json()["docs"], [{"id": i, "nome": "rg-ficticio"}])
        r = c.get("/api/cofre/docs/%d" % i)
        self.assertEqual((r.status_code, r.headers["content-type"], r.content),
                         (200, "application/pdf", b"%PDF-1.4 fake"))
        self.assertEqual(c.delete("/api/cofre/docs/%d" % i).status_code, 200)
        self.assertEqual(c.delete("/api/cofre/docs/%d" % i).status_code, 404)

    def test_bloqueado_423_e_senha_errada_403(self):
        c = self.cliente(42)
        c.post("/api/cofre/criar", json={"senha": "senha-bem-longa"})
        c.post("/api/cofre/bloquear")
        self.assertEqual(c.get("/api/cofre/docs").status_code, 423)
        self.assertEqual(c.post("/api/cofre/desbloquear", json={"senha": "outra-senha-longa"}).status_code, 403)
        self.assertEqual(c.post("/api/cofre/desbloquear", json={"senha": "senha-bem-longa"}).status_code, 200)
        self.assertEqual(c.get("/api/cofre/docs").status_code, 200)

    def test_tentativas_de_senha_limitadas(self):
        c = self.cliente(42)
        c.post("/api/cofre/criar", json={"senha": "senha-bem-longa"})
        codigos = [c.post("/api/cofre/desbloquear", json={"senha": "errada-errada"}).status_code
                   for _ in range(7)]
        self.assertEqual(codigos, [403] * 5 + [429] * 2)

    def test_usuario_a_nao_acessa_documento_de_b(self):
        a, b = self.cliente(1), self.cliente(2)
        a.post("/api/cofre/criar", json={"senha": "senha-bem-longa"})
        b.post("/api/cofre/criar", json={"senha": "senha-bem-longa"})
        i = self.cofre.guardar(1, "doc-de-a", b"x")
        self.assertEqual(b.get("/api/cofre/docs/%d" % i).status_code, 404)
        self.assertEqual(b.delete("/api/cofre/docs/%d" % i).status_code, 404)
        self.assertEqual(b.get("/api/cofre/docs").json()["docs"], [])

    def test_config_e_estado(self):
        c = self.cliente(42)
        self.assertEqual(c.put("/api/config", json={"uf": "RJ", "temas": ["servicos"]}).status_code, 200)
        e = c.get("/api/estado").json()
        self.assertEqual((e["uf"], e["temas_briefing"]), ("RJ", ["servicos"]))
        self.assertEqual(c.put("/api/config", json={"uf": "ZZ"}).status_code, 400)

    def test_front_servido_com_csp(self):
        c = self.TestClient(self.app, base_url="https://testserver")
        r = c.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Citizen Assist AI", r.text)
        self.assertEqual(c.get("/static/painel.js").status_code, 200)
        self.assertIn("frame-ancestors", r.headers["content-security-policy"])
        self.assertNotIn("unsafe-inline", r.headers["content-security-policy"])


if __name__ == "__main__":
    unittest.main()
