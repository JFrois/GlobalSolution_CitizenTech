"""Folha cega de clareza (scripts/folha_clareza.py): sorteio estável e cálculo das médias."""
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("folha_clareza", RAIZ / "scripts" / "folha_clareza.py")
folha = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(folha)


class TestFolhaClareza(unittest.TestCase):
    def test_sorteio_estavel_e_cada_par_tem_a_e_b(self):
        p1, p2 = folha.montar_pares(), folha.montar_pares()
        self.assertEqual([(i, {r: m for r, (m, _) in rot.items()}) for i, _, rot in p1],
                         [(i, {r: m for r, (m, _) in rot.items()}) for i, _, rot in p2])
        self.assertTrue(p1)
        for _, _, rot in p1:
            self.assertEqual(sorted(m for m, _ in rot.values()), ["A", "B"])

    def test_folha_nao_revela_o_modelo(self):
        pares = folha.montar_pares()
        with tempfile.TemporaryDirectory() as d:
            folha.SAIDA = Path(d) / "f.md"
            folha.gravar_folha(pares)
            texto = folha.SAIDA.read_text(encoding="utf-8")
        self.assertNotIn("Modelo A", texto)
        self.assertNotIn("Modelo B", texto)

    def test_calcular_media_por_modelo(self):
        pares = folha.montar_pares()
        pid, _, rot = pares[0]
        rotulo_a = next(r for r, (m, _) in rot.items() if m == "A")
        rotulo_b = "Y" if rotulo_a == "X" else "X"
        with tempfile.TemporaryDirectory() as d:
            arq = Path(d) / "n.csv"
            with open(arq, "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["avaliador", "id", "rotulo", "nota"])
                w.writerow(["P1", pid, rotulo_a, 5])
                w.writerow(["P1", pid, rotulo_b, 3])
            import io
            from contextlib import redirect_stdout
            saida = io.StringIO()
            with redirect_stdout(saida):
                folha.calcular(arq, pares)
        self.assertIn("Modelo A: média 5.00", saida.getvalue())
        self.assertIn("Modelo B: média 3.00", saida.getvalue())


if __name__ == "__main__":
    unittest.main()
