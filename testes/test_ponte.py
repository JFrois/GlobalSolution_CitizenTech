"""Testes de src/ponte.py: ligação do servidor com o núcleo."""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import base  # noqa: E402
import ponte  # noqa: E402


class TestPonte(unittest.TestCase):
    def setUp(self):
        self.base = ponte.preparar(base.carregar_base())

    def test_preparar_e_idempotente(self):
        buscador = self.base["_buscador"]
        self.assertIs(ponte.preparar(self.base)["_buscador"], buscador)
        self.assertEqual(sum(len(v) for v in self.base["ids_por_tema"].values()), 17)

    def test_buscar_devolve_decisao_e_candidatos(self):
        r = ponte.buscar("Como tirar a segunda via do RG?", self.base)
        self.assertEqual(r["decisao"], "RESPONDER")
        self.assertEqual(r["candidatos"][0][0], "DOC-001")
        self.assertEqual(ponte.buscar("como pagar o IPVA", self.base)["candidatos"], [])
        self.assertEqual(len(ponte.buscar("documento", self.base)["candidatos"]), 3)

    def test_relacionados_sao_tres_e_sem_o_proprio(self):
        for rid in self.base["registros_por_id"]:
            rel = ponte.relacionados(self.base, rid)
            self.assertEqual(len(rel), 3)
            self.assertNotIn(rid, rel)

    def test_uf_com_link_estadual_e_sem(self):
        reg = dict(self.base["registros_por_id"]["DOC-001"],
                   referencias_estaduais={"SP": "https://sp.exemplo.gov.br"})
        self.assertEqual(ponte.fonte_e_aviso(reg, "SP")[0], "https://sp.exemplo.gov.br")
        self.assertEqual(ponte.fonte_e_aviso(reg, "RJ")[0], reg["referencia"])
        self.assertIn("mudam de estado", ponte.fonte_e_aviso(reg, "RJ")[1])

    def test_formatar_usa_link_da_uf_e_os_relacionados(self):
        reg = dict(self.base["registros_por_id"]["DOC-001"],
                   referencias_estaduais={"SP": "https://sp.exemplo.gov.br"})
        regs = [self.base["registros_por_id"][i] for i in ponte.relacionados(self.base, "DOC-001")]
        texto = ponte.formatar(reg, "B", regs, uf="SP")
        self.assertIn("https://sp.exemplo.gov.br", texto)
        self.assertIn("Continue consultando:", texto)
        self.assertIn(ponte.NAO_OFICIAL, texto)

    def test_formatar_telegram_em_html_seguro(self):
        reg = dict(self.base["registros_por_id"]["DOC-001"],
                   titulo='Título <b>"x"</b> & cia',
                   orientacao='Passo com <script>alert(1)</script> e "aspas".\nSegundo & passo.',
                   referencia='https://www.exemplo.gov.br/a?x=1&y="2"')
        html_ = ponte.formatar_telegram(reg)
        self.assertNotIn("<script>", html_)
        self.assertIn("&lt;script&gt;", html_)
        self.assertTrue(html_.startswith("<b>Título &lt;b&gt;"))
        self.assertIn("1. Passo com", html_)
        self.assertIn("2. Segundo &amp; passo.", html_)
        self.assertIn('<a href="https://www.exemplo.gov.br/a?x=1&amp;y=&quot;2&quot;">exemplo.gov.br</a>', html_)
        self.assertNotIn("----", html_)

    def test_formatar_telegram_tem_aviso_fonte_e_frase_oficial(self):
        reg = self.base["registros_por_id"]["DOC-001"]  # estadual, confirmar antes
        html_ = ponte.formatar_telegram(reg)
        self.assertIn("<b>Atenção:</b> o procedimento", html_)
        self.assertIn("<b>Fonte:</b>", html_)
        self.assertIn("verificado em 07/11/2026", html_)
        self.assertTrue(html_.rstrip().endswith("</i>"))
        self.assertIn(ponte.NAO_OFICIAL, html_)

    def test_formatar_telegram_usa_link_da_uf(self):
        reg = dict(self.base["registros_por_id"]["DOC-001"],
                   referencias_estaduais={"SP": "https://sp.exemplo.gov.br"})
        self.assertIn('href="https://sp.exemplo.gov.br"', ponte.formatar_telegram(reg, uf="SP"))

    def test_titulos_cabem_no_botao_do_telegram(self):
        # Botão não quebra linha: título longo fica cortado na tela do celular.
        for rid, reg in self.base["registros_por_id"].items():
            self.assertLessEqual(len(ponte.titulo_do(reg)), 36, rid)


if __name__ == "__main__":
    unittest.main()
