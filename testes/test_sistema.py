"""Testes de fumaça do terminal e proteção do núcleo (spec §5.3 e §13)."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SISTEMA = str(RAIZ / "src" / "sistema.py")
FIXTURE = str(RAIZ / "testes" / "fixtures" / "base_exemplo.json")


def rodar(entrada, *args):
    """Roda o terminal com a entrada simulada; devolve (código, saída)."""
    r = subprocess.run([sys.executable, SISTEMA, "--base", FIXTURE, *args],
                       input=entrada, capture_output=True, text=True,
                       encoding="utf-8", timeout=60)
    return r.returncode, r.stdout + r.stderr


class TestTerminal(unittest.TestCase):
    def test_pergunta_resposta_com_fonte(self):
        codigo, saida = rodar("como tirar a segunda via do RG\n0\n")
        self.assertEqual(codigo, 0)
        self.assertIn("Fonte:", saida)
        self.assertNotIn("Traceback", saida)

    def test_entradas_invalidas_nao_encerram_nem_quebram(self):
        entrada = "\n???\n7\n999\nxyz\n" + ("a" * 400) + "\nm\n0\n"
        codigo, saida = rodar(entrada)
        self.assertEqual(codigo, 0)
        self.assertNotIn("Traceback", saida)
        self.assertIn("Você não digitou nada", saida)
        self.assertIn("Não entendi", saida)
        self.assertIn("não existe aqui", saida)
        self.assertIn("Sua pergunta ficou longa", saida)
        self.assertIn("Até logo", saida)

    def test_fim_da_entrada_sai_sem_traceback(self):
        codigo, saida = rodar("")
        self.assertEqual(codigo, 0)
        self.assertNotIn("Traceback", saida)

    def test_sem_base_nao_inventa(self):
        _, saida = rodar("como pagar o IPVA?\n0\n")
        self.assertIn("não vou inventar instruções", saida)

    def test_saida_sem_terminal_e_texto_puro(self):
        _, saida = rodar("segunda via rg\n0\n")
        self.assertNotIn("\033[", saida)

    def test_linhas_ate_80_colunas(self):
        _, saida = rodar("segunda via rg\n1\n2\n0\n", "--simples")
        for linha in saida.splitlines():
            self.assertLessEqual(len(linha), 80, linha)

    def test_base_inexistente_sai_com_codigo_1(self):
        r = subprocess.run([sys.executable, SISTEMA, "--base", "nao_existe.json"],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 1)
        self.assertIn("Não consegui abrir a base", r.stdout)
        self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_validar_entrega_falha_com_esqueleto(self):
        r = subprocess.run([sys.executable, SISTEMA, "--validar-entrega"],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 1)

    def test_validar_entrega_passa_com_base_completa(self):
        r = subprocess.run([sys.executable, SISTEMA, "--validar-entrega", "--base", FIXTURE],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0)


class TestNucleoSemDependencias(unittest.TestCase):
    def test_nucleo_importa_sem_pacotes_instalados(self):
        """`python -S` ignora site-packages: o núcleo só pode usar a biblioteca padrão."""
        r = subprocess.run(
            [sys.executable, "-S", "-c",
             "import sys; sys.path.insert(0, %r); import base, busca, respostas" % str(RAIZ / "src")],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
