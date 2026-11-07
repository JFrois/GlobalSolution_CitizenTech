"""Testes da busca, da regra de decisão, do grafo e do Dijkstra."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import base  # noqa: E402
import busca  # noqa: E402

FIXTURE = RAIZ / "testes" / "fixtures" / "base_exemplo.json"


def carregar():
    return base.carregar_base(FIXTURE)


class TestNormalizacao(unittest.TestCase):
    def test_minusculas_acentos_pontuacao_stopwords(self):
        self.assertEqual(busca.normalizar("Como TIRAR a 2ª via, do título?"),
                         ["2a", "via", "titulo"])

    def test_so_simbolos_nao_tem_palavra(self):
        self.assertEqual(busca.normalizar("???"), [])

    def test_expansao_de_sinonimos_nos_dois_sentidos(self):
        exp = busca.montar_expansao({"identidade": ["rg", "cin"]})
        self.assertIn("rg", busca.expandir("identidade", exp))
        self.assertIn("identidade", busca.expandir("rg", exp))


class TestDecisao(unittest.TestCase):
    def setUp(self):
        self.base = carregar()

    def test_quatro_saidas(self):
        casos = {
            "": "INVALIDA",
            "???": "INVALIDA",
            "como pagar o IPVA?": "SEM_BASE",
            "como tirar a segunda via do RG?": "RESPONDER",
            "documento": "PEDIR_ESCOLHA",
        }
        for pergunta, esperado in casos.items():
            self.assertEqual(busca.buscar(pergunta, self.base)["decisao"], esperado, pergunta)

    def test_entrada_que_nao_e_texto_e_invalida(self):
        self.assertEqual(busca.buscar(None, self.base)["decisao"], "INVALIDA")

    def test_responde_o_registro_certo(self):
        r = busca.buscar("Como pedir segunda via do título de eleitor?", self.base)
        self.assertEqual(r["candidatos"][0][0], "DOC-003")

    def test_linear_igual_ao_indice(self):
        for pergunta in ["segunda via rg", "meu inss", "defensoria", "documento",
                         "tarifa social de energia", "xyz"]:
            self.assertEqual(busca.buscar(pergunta, self.base, "indice"),
                             busca.buscar(pergunta, self.base, "linear"), pergunta)

    def test_filtro_por_tema_e_registro_ja_exibido(self):
        r = busca.buscar("documento", self.base, apenas_tema="direitos")
        self.assertTrue(all(c[0].startswith("DIR") for c in r["candidatos"]))
        r = busca.buscar("segunda via rg", self.base, ids_excluidos={"DOC-001"})
        self.assertNotIn("DOC-001", [c[0] for c in r["candidatos"]])

    def test_empate_vai_para_o_menor_id(self):
        r = busca.buscar("documento", self.base)
        ids = [c[0] for c in r["candidatos"]]
        self.assertEqual(ids, sorted(ids))

    def test_maximo_de_tres_candidatos(self):
        self.assertLessEqual(len(busca.buscar("documento", self.base)["candidatos"]), 3)


class TestGrafo(unittest.TestCase):
    def setUp(self):
        self.base = carregar()
        self.grafo = busca.montar_grafo(self.base)

    def test_grafo_nao_direcionado(self):
        for rid, vizinhos in self.grafo.items():
            for outro, custo in vizinhos:
                self.assertIn((rid, custo), self.grafo[outro])

    def test_custo_depende_do_tema(self):
        custos = dict(self.grafo["DOC-001"])
        self.assertEqual(custos["DOC-002"], 1)   # mesmo tema
        self.assertEqual(custos["SRV-004"], 2)   # temas diferentes

    def test_dijkstra_caminho_conhecido(self):
        custo, caminho = busca.dijkstra(self.grafo, "DOC-002", "DIR-006")
        self.assertEqual(caminho, ["DOC-002", "DOC-001", "SRV-004", "DIR-006"])
        self.assertEqual(custo, 1 + 2 + 2)

    def test_dijkstra_mesmo_no(self):
        self.assertEqual(busca.dijkstra(self.grafo, "DOC-001", "DOC-001"), (0, ["DOC-001"]))

    def test_dijkstra_sem_caminho(self):
        grafo = {"A": [], "B": []}
        self.assertIsNone(busca.dijkstra(grafo, "A", "B"))
        self.assertIsNone(busca.dijkstra(self.grafo, "DOC-001", "NAO-EXISTE"))

    def test_todo_registro_tem_tres_relacionados(self):
        for rid in self.base["registros_por_id"]:
            rel = busca.relacionados_ordenados(self.grafo, rid)
            self.assertEqual(len(rel), 3, rid)
            self.assertNotIn(rid, rel)

    def test_vizinhos_diretos_vem_primeiro(self):
        rel = busca.relacionados_ordenados(self.grafo, "DOC-002")
        self.assertEqual(rel[0], "DOC-001")


if __name__ == "__main__":
    unittest.main()
