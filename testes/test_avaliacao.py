"""Testes do --avaliar e do script de datas antigas."""
from __future__ import annotations

import csv
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "scripts"))

import avaliacao  # noqa: E402
import base  # noqa: E402
import datas_antigas  # noqa: E402

FIXTURE = RAIZ / "testes" / "fixtures" / "base_exemplo.json"


class TestAvaliacao(unittest.TestCase):
    def test_gera_csvs_e_resumo(self):
        pasta = Path(tempfile.mkdtemp())
        avaliacao.SAIDA_RESULTADOS = pasta / "resultados.csv"
        avaliacao.SAIDA_MODELOS = pasta / "comparacao.csv"
        avaliacao.REPETICOES = 2
        avaliacao.escala = lambda b: None  # evita a medição pesada no teste
        saida = io.StringIO()
        with redirect_stdout(saida):
            codigo = avaliacao.executar(base.carregar_base(FIXTURE))
        self.assertEqual(codigo, 0)
        self.assertIn("Taxa de acerto da busca", saida.getvalue())
        with open(pasta / "resultados.csv", encoding="utf-8") as f:
            linhas = list(csv.DictReader(f))
        self.assertGreaterEqual(len(linhas), 15)
        self.assertTrue(all(l["metodos_concordam"] == "sim" for l in linhas))
        with open(pasta / "comparacao.csv", encoding="utf-8") as f:
            modelos = list(csv.DictReader(f))
        self.assertEqual({m["modelo"] for m in modelos}, {"A", "B"})
        self.assertTrue(all(m["tem_fonte_url_e_data"] == "sim" for m in modelos))


class TestDatasAntigas(unittest.TestCase):
    def test_lista_registro_com_data_antiga(self):
        dados = base.carregar_base(FIXTURE)
        reg = dados["registros"][0]
        reg["data_verificacao"] = "2020-01-01"
        antigos = datas_antigas.registros_antigos(dados["registros"], hoje="2026-11-10")
        self.assertEqual([a[0] for a in antigos][0], reg["id"])
        self.assertNotIn(dados["registros"][1]["id"], [a[0] for a in antigos])


if __name__ == "__main__":
    unittest.main()
