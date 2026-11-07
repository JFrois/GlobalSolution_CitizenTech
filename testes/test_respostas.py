"""Testes dos modelos de resposta A e B."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import base  # noqa: E402
import busca  # noqa: E402
import respostas  # noqa: E402

FIXTURE = RAIZ / "testes" / "fixtures" / "base_exemplo.json"


class TestRespostas(unittest.TestCase):
    def setUp(self):
        self.base = base.carregar_base(FIXTURE)
        busca.preparar(self.base)

    def _rel(self, rid):
        ids = busca.relacionados_ordenados(self.base["grafo"], rid)
        return [self.base["registros_por_id"][i] for i in ids]

    def test_toda_resposta_tem_fonte_data_e_relacionados(self):
        for modelo in ("A", "B"):
            for rid, reg in self.base["registros_por_id"].items():
                texto = respostas.formatar(reg, modelo, self._rel(rid))
                self.assertIn("Fonte: " + reg["referencia"], texto)
                self.assertIn("10/11/2026", texto)
                self.assertIn("não é um canal oficial", texto)
                for r in self._rel(rid):
                    self.assertIn(" ".join(r["pergunta"].split()[:3]), " ".join(texto.split()))

    def test_aviso_quando_confirmar_antes(self):
        reg = self.base["registros_por_id"]["DOC-003"]  # confirmar_antes
        self.assertIn("Atenção:", respostas.formatar(reg, "B", []))
        reg = self.base["registros_por_id"]["DOC-002"]  # sem confirmar_antes
        self.assertNotIn("Atenção:", respostas.formatar(reg, "B", []))

    def test_estadual_usa_link_da_uf_ou_avisa(self):
        reg = dict(self.base["registros_por_id"]["DOC-001"])
        reg["referencias_estaduais"] = {"SP": "https://exemplo.sp.gov.br"}
        self.assertIn("https://exemplo.sp.gov.br", respostas.formatar(reg, "A", [], uf="SP"))
        texto = respostas.formatar(reg, "A", [], uf="AC")
        self.assertIn(reg["referencia"], texto)
        self.assertIn("mudam de estado para estado", texto)

    def test_modelo_b_numera_passos_e_modelo_a_e_compacto(self):
        reg = self.base["registros_por_id"]["DOC-002"]
        b = respostas.formatar(reg, "B", [])
        self.assertIn("1. ", b)
        self.assertIn("3. ", b)
        a = respostas.formatar(reg, "A", [])
        self.assertLess(len(a.splitlines()), len(b.splitlines()))

    def test_linhas_com_ate_80_colunas(self):
        for rid, reg in self.base["registros_por_id"].items():
            for modelo in ("A", "B"):
                for linha in respostas.formatar(reg, modelo, self._rel(rid)).splitlines():
                    self.assertLessEqual(len(linha), 80)

    def test_orientacao_nao_redigida_nao_quebra(self):
        reg = dict(self.base["registros_por_id"]["DOC-002"])
        reg["orientacao"] = "PREENCHER"
        reg["data_verificacao"] = ""
        texto = respostas.formatar(reg, "B", [])
        self.assertIn("ainda não redigida", texto)
        self.assertIn("data não informada", texto)

    def test_sem_base_e_pedir_escolha(self):
        aviso = respostas.aviso_sem_base(self.base["temas"])
        self.assertIn("não vou inventar instruções", aviso)
        self.assertIn("https://www.gov.br", aviso)
        self.assertIn("1  Documentação pessoal", aviso)
        regs = [self.base["registros_por_id"][i] for i in ("DOC-001", "DOC-002")]
        self.assertIn("2  ", respostas.pedir_escolha(regs))


if __name__ == "__main__":
    unittest.main()
