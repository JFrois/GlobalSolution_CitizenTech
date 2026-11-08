"""Testes da criptografia do cofre. Pulados se `cryptography` não estiver instalada."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

try:
    import cryptography  # noqa: F401
    import criptografia as c
    TEM = True
except ImportError:  # núcleo roda sem a biblioteca
    TEM = False

IT = 1000  # poucas iterações só para os testes ficarem rápidos


@unittest.skipUnless(TEM, "cryptography não instalada")
class TestCriptografia(unittest.TestCase):
    def test_ida_e_volta(self):
        cofre = c.criar_cofre("senha-bem-longa", IT)
        chave = c.abrir_cofre("senha-bem-longa", cofre["salt"], cofre["verificador"], IT)
        blob = c.cifrar(chave, b"documento ficticio")
        self.assertNotIn(b"documento", blob)
        self.assertEqual(c.decifrar(chave, blob), b"documento ficticio")

    def test_senha_errada_falha(self):
        cofre = c.criar_cofre("senha-bem-longa", IT)
        with self.assertRaises(c.SenhaIncorreta):
            c.abrir_cofre("outra-senha-longa", cofre["salt"], cofre["verificador"], IT)

    def test_dado_adulterado_falha(self):
        chave = c.derivar_chave("senha-bem-longa", b"s" * 16, IT)
        blob = bytearray(c.cifrar(chave, b"abc"))
        blob[-1] ^= 1
        with self.assertRaises(c.SenhaIncorreta):
            c.decifrar(chave, bytes(blob))

    def test_senha_curta_recusada(self):
        with self.assertRaises(ValueError):
            c.criar_cofre("curta", IT)

    def test_salt_diferente_por_cofre(self):
        a, b = c.criar_cofre("senha-bem-longa", IT), c.criar_cofre("senha-bem-longa", IT)
        self.assertNotEqual(a["salt"], b["salt"])

    def test_chave_expira(self):
        agora = [0.0]
        mem = c.ChavesEmMemoria(ttl=60, relogio=lambda: agora[0])
        mem.guardar(1, b"k")
        self.assertEqual(mem.obter(1), b"k")
        self.assertEqual(mem.segundos_restantes(1), 60)
        agora[0] = 61
        self.assertIsNone(mem.obter(1))
        self.assertEqual(mem.segundos_restantes(1), 0)

    def test_chaves_isoladas_por_usuario(self):
        mem = c.ChavesEmMemoria()
        mem.guardar(1, b"k1")
        self.assertIsNone(mem.obter(2))
        mem.bloquear(1)
        self.assertIsNone(mem.obter(1))


if __name__ == "__main__":
    unittest.main()
