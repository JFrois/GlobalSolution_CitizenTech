"""Testes do cofre: isolamento por user_id, senha errada, expiração, apagar."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

try:
    import cryptography  # noqa: F401
    import criptografia as c
    import cofre as cf
    from armazenamento import ArmazenamentoSQLite
    TEM = True
except ImportError:
    TEM = False

IT = 1000
SENHA = "senha-bem-longa"


@unittest.skipUnless(TEM, "cryptography não instalada")
class TestCofre(unittest.TestCase):
    def setUp(self):
        self.relogio = [0.0]
        self.arm = ArmazenamentoSQLite(":memory:")
        chaves = c.ChavesEmMemoria(ttl=60, relogio=lambda: self.relogio[0])
        self.cofre = cf.Cofre(self.arm, chaves, IT)

    def test_guardar_listar_abrir(self):
        self.cofre.criar(1, SENHA)
        i = self.cofre.guardar(1, "rg-ficticio", b"conteudo")
        self.assertEqual(self.cofre.listar(1), [(i, "rg-ficticio")])
        self.assertEqual(self.cofre.abrir(1, i), ("rg-ficticio", b"conteudo"))

    def test_nada_em_claro_no_armazenamento(self):
        self.cofre.criar(1, SENHA)
        self.cofre.guardar(1, "rg-ficticio", b"conteudo-secreto")
        nome, conteudo = self.arm.obter_doc(1, 1)
        self.assertNotIn(b"rg-ficticio", nome)
        self.assertNotIn(b"conteudo-secreto", conteudo)

    def test_usuario_a_nao_le_b(self):
        self.cofre.criar(1, SENHA)
        self.cofre.criar(2, SENHA)
        i = self.cofre.guardar(1, "doc", b"x")
        self.assertIsNone(self.cofre.abrir(2, i))
        self.assertEqual(self.cofre.listar(2), [])
        self.assertFalse(self.cofre.apagar(2, i))
        self.assertEqual(len(self.cofre.listar(1)), 1)

    def test_senha_errada(self):
        self.cofre.criar(1, SENHA)
        self.cofre.bloquear(1)
        with self.assertRaises(c.SenhaIncorreta):
            self.cofre.desbloquear(1, "outra-senha-longa")
        self.assertFalse(self.cofre.esta_desbloqueado(1))

    def test_bloqueado_nao_guarda_nem_abre(self):
        self.cofre.criar(1, SENHA)
        self.cofre.bloquear(1)
        with self.assertRaises(cf.CofreBloqueado):
            self.cofre.guardar(1, "doc", b"x")
        with self.assertRaises(cf.CofreBloqueado):
            self.cofre.listar(1)

    def test_expira(self):
        self.cofre.criar(1, SENHA)
        self.relogio[0] = 61
        self.assertFalse(self.cofre.esta_desbloqueado(1))
        self.cofre.desbloquear(1, SENHA)
        self.assertTrue(self.cofre.esta_desbloqueado(1))

    def test_desbloquear_sem_cofre(self):
        with self.assertRaises(cf.CofreInexistente):
            self.cofre.desbloquear(9, SENHA)

    def test_apagar_doc_e_apagar_usuario(self):
        self.cofre.criar(1, SENHA)
        i = self.cofre.guardar(1, "doc", b"x")
        self.assertTrue(self.cofre.apagar(1, i))
        self.assertEqual(self.cofre.listar(1), [])
        self.cofre.guardar(1, "doc2", b"y")
        self.arm.apagar_usuario(1)
        self.assertFalse(self.cofre.existe(1))
        self.assertEqual(self.arm.listar_docs(1), [])

    def test_buscar_por_nome(self):
        self.cofre.criar(1, SENHA)
        i = self.cofre.guardar(1, "RG-ficticio", b"x")
        self.assertEqual(self.cofre.buscar_por_nome(1, "rg"), (i, "RG-ficticio"))
        self.assertIsNone(self.cofre.buscar_por_nome(1, "cnh"))


if __name__ == "__main__":
    unittest.main()
