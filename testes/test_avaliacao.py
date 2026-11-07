"""Testes de src/avaliacao.py (A9) e scripts/verificacoes_antigas.py (A11)."""
import csv
import importlib.util
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import avaliacao  # noqa: E402
import base  # noqa: E402
import busca  # noqa: E402


def carregar_script():
    espec = importlib.util.spec_from_file_location(
        "verificacoes_antigas", RAIZ / "scripts" / "verificacoes_antigas.py")
    assert espec is not None and espec.loader is not None
    modulo = importlib.util.module_from_spec(espec)
    espec.loader.exec_module(modulo)
    return modulo


class TestAvaliacao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dados = base.carregar_base()
        cls.buscador = busca.Buscador(cls.dados)
        cls.perguntas = avaliacao.carregar_perguntas()

    def test_perguntas_no_formato_da_spec(self):
        self.assertGreaterEqual(len([p for p in self.perguntas if p["tipo"] != "limite"]), 12)
        self.assertGreaterEqual(len([p for p in self.perguntas if p["tipo"] == "limite"]), 3)
        for p in self.perguntas:
            self.assertEqual(set(p), {"id", "conjunto", "tipo", "pergunta", "esperado"})

    def test_taxa_de_acerto(self):
        linhas = avaliacao.avaliar_busca(self.buscador, self.perguntas, repeticoes=1)
        acertos, total, pct = avaliacao.taxa(linhas)
        self.assertEqual(total, len(self.perguntas))
        self.assertAlmostEqual(pct, 100.0 * acertos / total)

    def test_erro_e_contado(self):
        falsas = [{"id": "X", "conjunto": "equipe", "tipo": "direta",
                   "pergunta": "Como tirar a segunda via do RG?", "esperado": "SRV-001"}]
        linhas = avaliacao.avaliar_busca(self.buscador, falsas, repeticoes=1)
        self.assertEqual(linhas[0]["resultado"], "erro")
        self.assertEqual(avaliacao.taxa(linhas)[2], 0.0)

    def test_comparacao_ab_usa_o_mesmo_resultado(self):
        comp = avaliacao.comparar_modelos(self.buscador, self.perguntas)
        por_pergunta = {}
        for c in comp:
            por_pergunta.setdefault(c["id"], []).append(c)
        for pares in por_pergunta.values():
            self.assertEqual(sorted(c["modelo"] for c in pares), ["A", "B"])
            self.assertEqual(pares[0]["registro"], pares[1]["registro"])

    def test_criterios_do_formato(self):
        reg = {"confirmar_antes": True}
        ok = avaliacao.criterios_do_formato(
            "x\nAtenção: confirme\nFonte: https://a.b (verificado em 10/11/2026)\n"
            "Continue consultando:\n1. passo", reg)
        self.assertEqual((ok["tem_fonte_com_data"], ok["tem_aviso"], ok["tem_relacionados"]),
                         ("sim", "sim", "sim"))
        ruim = avaliacao.criterios_do_formato("Fonte: https://a.b (data de verificação pendente)", reg)
        self.assertEqual((ruim["tem_fonte_com_data"], ruim["tem_aviso"]), ("nao", "nao"))
        self.assertEqual(avaliacao.criterios_do_formato("x", {})["tem_aviso"], "n/a")

    def test_base_ampliada(self):
        grande = avaliacao.ampliar_base(self.dados, 100)
        self.assertEqual(len(grande["registros"]), 100)
        self.assertEqual(len({r["id"] for r in grande["registros"]}), 100)

    def test_avaliar_grava_os_dois_csv(self):
        with tempfile.TemporaryDirectory() as pasta:
            resumo = avaliacao.avaliar(self.dados, pasta=pasta, escala=False, repeticoes=1)
            with open(Path(pasta) / "resultados.csv", encoding="utf-8", newline="") as f:
                linhas = list(csv.DictReader(f))
            with open(Path(pasta) / "comparacao_modelos.csv", encoding="utf-8", newline="") as f:
                comparacao = list(csv.DictReader(f))
        self.assertEqual(len(linhas), len(self.perguntas))
        self.assertEqual(list(linhas[0]), avaliacao.CAB_RESULTADOS)
        self.assertEqual(list(comparacao[0]), avaliacao.CAB_COMPARACAO)
        self.assertIn("TAXA DE ACERTO DA BUSCA", resumo)
        self.assertIn("MODELOS A x B", resumo)


class TestVerificacoesAntigas(unittest.TestCase):
    def test_lista_antigos_e_sem_data(self):
        modulo = carregar_script()
        dados = {"registros": [
            {"id": "DOC-001", "data_verificacao": "2026-01-01"},   # antigo
            {"id": "DOC-002", "data_verificacao": "2026-11-01"},   # recente
            {"id": "DOC-003", "data_verificacao": ""},             # sem data
        ]}
        lista = modulo.registros_antigos(dados, date(2026, 11, 10))
        self.assertEqual([rid for rid, _ in lista], ["DOC-001", "DOC-003"])

    def test_limite_de_dias_e_exato(self):
        modulo = carregar_script()
        dados = {"registros": [{"id": "DOC-001", "data_verificacao": "2026-08-12"}]}
        self.assertEqual(modulo.registros_antigos(dados, date(2026, 11, 10)), [])  # 90 dias
        self.assertEqual(len(modulo.registros_antigos(dados, date(2026, 11, 11))), 1)  # 91 dias


if __name__ == "__main__":
    unittest.main()
