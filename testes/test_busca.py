"""Testes de src/busca.py: normalização, busca, decisão, De Morgan, grafo e Dijkstra."""
import itertools
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import base  # noqa: E402
import busca  # noqa: E402


def reg(rid, tema, palavras, pergunta="", orientacao="texto", relacionados=()):
    return {"id": rid, "tema": tema, "palavras_chave": palavras,
            "pergunta": pergunta or "assunto " + rid, "orientacao": orientacao,
            "referencia": "https://www.gov.br", "data_verificacao": "2026-11-10",
            "relacionados": list(relacionados)}


def mini_base(registros, sinonimos=None):
    return {"temas": {"a": "A", "b": "B"}, "sinonimos": sinonimos or {},
            "registros": registros}


class TestNormalizar(unittest.TestCase):
    def test_acento_pontuacao_e_stopwords(self):
        self.assertEqual(busca.normalizar("Como tirar a 2ª via do RG?"), ["2a", "via", "rg"])

    def test_so_simbolos_e_vazio(self):
        self.assertEqual(busca.normalizar("???"), [])
        self.assertEqual(busca.normalizar(""), [])

    def test_ponto_separa_palavras(self):
        self.assertEqual(busca.normalizar("Consumidor.gov.br"), ["consumidor"])


class TestDeMorgan(unittest.TestCase):
    def test_formas_equivalentes_em_todas_as_combinacoes(self):
        for a, b in itertools.product([False, True], repeat=2):
            self.assertEqual(busca.incluir_registro(a, b),
                             busca.incluir_registro_equivalente(a, b))


class TestDecisao(unittest.TestCase):
    def test_tabela_da_regra(self):
        casos = {
            (False, False, False): busca.INVALIDA,
            (False, True, True): busca.INVALIDA,
            (True, True, True): busca.RESPONDER,
            (True, True, False): busca.PEDIR_ESCOLHA,
            (True, False, True): busca.SEM_BASE,
            (True, False, False): busca.SEM_BASE,
        }
        for (c, a, b), esperado in casos.items():
            self.assertEqual(busca.decidir(c, a, b), esperado)

    def test_quatro_saidas_na_busca(self):
        s = busca.Buscador(mini_base([
            reg("DOC-001", "a", ["alfa"]),
            reg("DOC-002", "a", ["beta"]),
            reg("DOC-003", "a", ["beta"]),
        ]))
        self.assertEqual(s.buscar("").decisao, busca.INVALIDA)
        self.assertEqual(s.buscar("???").decisao, busca.INVALIDA)
        self.assertEqual(s.buscar("zzz").decisao, busca.SEM_BASE)
        self.assertEqual(s.buscar("alfa").decisao, busca.RESPONDER)
        r = s.buscar("beta")
        self.assertEqual(r.decisao, busca.PEDIR_ESCOLHA)
        self.assertEqual(r.candidatos, ["DOC-002", "DOC-003"])  # empate: menor id primeiro

    def test_abaixo_do_limiar_e_sem_base(self):
        # Palavra só na orientação vale 1 ponto, menos que LIMIAR_MINIMO.
        s = busca.Buscador(mini_base([reg("DOC-001", "a", ["alfa"], orientacao="gama")]))
        self.assertEqual(s.buscar("gama").decisao, busca.SEM_BASE)


class TestPontuacao(unittest.TestCase):
    def test_pesos_por_campo(self):
        s = busca.Buscador(mini_base([
            reg("DOC-001", "a", ["rg"], pergunta="rg", orientacao="rg")]))
        self.assertEqual(s.buscar("rg").ranking, [("DOC-001", 3 + 2 + 1)])

    def test_bonus_de_expressao(self):
        s = busca.Buscador(mini_base([
            reg("DOC-001", "a", ["segunda via"]),
            reg("DOC-002", "a", ["segunda", "via"])]))
        pontos = dict(s.buscar("segunda via").ranking)
        self.assertEqual(pontos["DOC-001"], pontos["DOC-002"] + busca.BONUS_EXPRESSAO)

    def test_sinonimo_conta_uma_vez_por_campo(self):
        s = busca.Buscador(mini_base(
            [reg("DOC-001", "a", ["identidade", "rg"])],
            sinonimos={"identidade": ["rg", "cin"]}))
        # "rg" e "identidade" estão no mesmo campo: pontua 3, não 6.
        self.assertEqual(s.buscar("rg").ranking, [("DOC-001", 3)])
        self.assertEqual(s.buscar("cin").decisao, busca.RESPONDER)  # via sinônimo

    def test_filtro_de_tema_e_excluir(self):
        s = busca.Buscador(mini_base([
            reg("DOC-001", "a", ["alfa"]),
            reg("SRV-001", "b", ["alfa"])]))
        self.assertEqual([r for r, _ in s.buscar("alfa", tema="b").ranking], ["SRV-001"])
        self.assertEqual([r for r, _ in s.buscar("alfa", excluir=("DOC-001",)).ranking],
                         ["SRV-001"])


class TestBaseReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = base.carregar_base()
        cls.s = busca.Buscador(cls.base)
        caminho = RAIZ / "testes" / "perguntas.json"
        cls.perguntas = json.loads(caminho.read_text(encoding="utf-8"))["perguntas"]

    def test_indice_e_linear_dao_o_mesmo_resultado(self):
        for p in self.perguntas:
            self.assertEqual(self.s.buscar(p["pergunta"], metodo="indice"),
                             self.s.buscar(p["pergunta"], metodo="linear"), p["id"])

    def test_limites_da_spec(self):
        self.assertEqual(self.s.buscar("").decisao, busca.INVALIDA)
        r = self.s.buscar("documento")
        self.assertEqual(r.decisao, busca.PEDIR_ESCOLHA)
        self.assertGreaterEqual(len(r.candidatos), 2)
        self.assertEqual(self.s.buscar("como tirar passaporte?").decisao, busca.SEM_BASE)

    def test_pedaco_de_palavra_chave_com_assunto_desconhecido(self):
        # "tarifa" sozinha é pedaço de "tarifa social"; "onibus" não existe na base.
        for pergunta in ("tarifa de ônibus", "quanto custa a tarifa de onibus"):
            self.assertEqual(self.s.buscar(pergunta).decisao, busca.SEM_BASE, pergunta)
            self.assertEqual(self.s.buscar(pergunta, metodo="linear").decisao, busca.SEM_BASE, pergunta)
        # Palavra-chave inteira continua respondendo, mesmo com palavra desconhecida.
        for pergunta, rid in (("tarifa social", "DIR-006"), ("tarifa de luz", "DIR-006"),
                              ("segunda via rg urgente", "DOC-001")):
            r = self.s.buscar(pergunta)
            self.assertEqual((r.decisao, r.candidatos), (busca.RESPONDER, [rid]), pergunta)

    def test_pergunta_direta(self):
        r = self.s.buscar("Como tirar a segunda via do RG?")
        self.assertEqual((r.decisao, r.candidatos), (busca.RESPONDER, ["DOC-001"]))


class TestCorrecaoDeDigitacao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = busca.Buscador(base.carregar_base())

    def test_erro_de_digitacao_e_corrigido(self):
        r = self.s.buscar("docuumento")
        self.assertEqual(r.decisao, busca.PEDIR_ESCOLHA)
        self.assertEqual(r.corrigidos, {"docuumento": "documento"})

    def test_indice_e_linear_dao_o_mesmo_resultado(self):
        a = self.s.buscar("docuumento", metodo="indice")
        b = self.s.buscar("docuumento", metodo="linear")
        self.assertEqual((a.decisao, a.candidatos), (b.decisao, b.candidatos))

    def test_fora_da_base_continua_sem_base(self):
        for pergunta in ("como pagar o IPVA", "como abrir um MEI", "como tirar passaporte?",
                         "qwertyuiop asdfghjkl"):
            r = self.s.buscar(pergunta)
            self.assertEqual(r.decisao, busca.SEM_BASE, pergunta)
            self.assertEqual(r.corrigidos, {})

    def test_quem_ja_responde_nao_e_alterado(self):
        r = self.s.buscar("como tirar a segunda via do RG?")
        self.assertEqual(r.decisao, busca.RESPONDER)
        self.assertEqual(r.corrigidos, {})

    def test_palavra_curta_nao_e_corrigida(self):
        self.assertEqual(self.s._corrigir(["ipva", "mei"]), {})


class TestGrafo(unittest.TestCase):
    def setUp(self):
        self.regs = [
            reg("DOC-001", "a", ["x"], relacionados=["DOC-002"]),
            reg("DOC-002", "a", ["y"]),
            reg("SRV-001", "b", ["z"], relacionados=["DOC-002"]),
            reg("SRV-002", "b", ["w"]),  # isolado
        ]
        self.s = busca.Buscador(mini_base(self.regs))

    def test_grafo_nao_direcionado(self):
        self.assertIn("DOC-001", self.s.grafo["DOC-002"])
        self.assertIn("SRV-001", self.s.grafo["DOC-002"])

    def test_custos_e_caminho(self):
        # DOC-001 -> DOC-002 (mesmo tema, 1) -> SRV-001 (temas diferentes, 2)
        self.assertEqual(self.s.caminho("DOC-001", "SRV-001"),
                         (3, ["DOC-001", "DOC-002", "SRV-001"]))
        self.assertEqual(self.s.caminho("DOC-001", "DOC-001"), (0, ["DOC-001"]))

    def test_sem_caminho(self):
        self.assertIsNone(self.s.caminho("DOC-001", "SRV-002"))

    def test_assunto_desconhecido(self):
        with self.assertRaises(ValueError):
            self.s.caminho("DOC-001", "XXX-999")

    def test_dijkstra_escolhe_o_mais_barato(self):
        # Atalho caro (temas diferentes, 2) contra rota de duas arestas baratas (1 + 1).
        regs = [
            reg("DOC-001", "a", ["x"], relacionados=["DOC-002", "SRV-001"]),
            reg("DOC-002", "a", ["y"], relacionados=["DOC-003"]),
            reg("DOC-003", "a", ["z"]),
            reg("SRV-001", "b", ["w"], relacionados=["DOC-003"]),
        ]
        s = busca.Buscador(mini_base(regs))
        self.assertEqual(s.caminho("DOC-001", "DOC-003"),
                         (2, ["DOC-001", "DOC-002", "DOC-003"]))

    def test_sugestoes_completam_ate_tres(self):
        # DOC-001 tem 1 vizinho direto; as outras completam pelos mais próximos.
        s = busca.Buscador(base.carregar_base())
        for rid in s.por_id:
            sug = s.sugestoes(rid)
            self.assertEqual(len(sug), 3, rid)
            self.assertNotIn(rid, sug)
            diretos = s.grafo[rid]
            self.assertTrue(set(list(diretos)[:1]) <= set(sug) or len(diretos) > 3)

    def test_sugestoes_respeitam_excluir(self):
        s = busca.Buscador(base.carregar_base())
        sug = s.sugestoes("DOC-002", excluir=("DOC-001",))
        self.assertNotIn("DOC-001", sug)


if __name__ == "__main__":
    unittest.main()
