"""Testes da carga e validação da base (spec §14.2)."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import base  # noqa: E402


def _gravar(conteudo):
    """Grava um texto num arquivo temporário e devolve o caminho."""
    pasta = tempfile.mkdtemp()
    caminho = Path(pasta) / "base.json"
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho


def _dados():
    return json.loads(base.CAMINHO_PADRAO.read_text(encoding="utf-8"))


class TestBase(unittest.TestCase):
    def test_base_real_carrega(self):
        b = base.carregar_base()
        self.assertEqual(len(b["registros"]), 17)
        self.assertEqual(len(b["temas"]), 3)

    def test_grafo_conexo(self):
        b = base.carregar_base()
        viz = {i: set() for i in b["registros_por_id"]}
        for r in b["registros"]:
            for o in r["relacionados"]:
                viz[r["id"]].add(o)
                viz[o].add(r["id"])
        visto, fila = set(), ["DOC-001"]
        while fila:
            atual = fila.pop()
            if atual not in visto:
                visto.add(atual)
                fila.extend(viz[atual])
        self.assertEqual(len(visto), 17)

    def test_arquivo_ausente(self):
        with self.assertRaises(base.ErroBase):
            base.carregar_base(Path(tempfile.mkdtemp()) / "nao_existe.json")

    def test_arquivo_vazio(self):
        with self.assertRaises(base.ErroBase):
            base.carregar_base(_gravar("   \n"))

    def test_json_invalido(self):
        with self.assertRaises(base.ErroBase):
            base.carregar_base(_gravar("{ invalido"))

    def test_campo_faltando_id_duplicado_e_relacionado(self):
        d = _dados()
        del d["registros"][0]["referencia"]
        d["registros"][2]["id"] = "DOC-001"
        d["registros"][3]["relacionados"] = ["XXX-999"]
        with self.assertRaises(base.ErroBase) as ctx:
            base.carregar_base(_gravar(json.dumps(d)))
        texto = " | ".join(ctx.exception.problemas)
        self.assertIn("sem o campo 'referencia'", texto)
        self.assertIn("id duplicado", texto)
        self.assertIn("relacionado inexistente", texto)

    def test_tema_desconhecido(self):
        d = _dados()
        d["registros"][0]["tema"] = "outro"
        with self.assertRaises(base.ErroBase):
            base.carregar_base(_gravar(json.dumps(d)))

    def test_modo_entrega_recusa_esqueleto(self):
        with self.assertRaises(base.ErroBase) as ctx:
            base.carregar_base(modo_entrega=True)
        self.assertIn("PREENCHER", " ".join(ctx.exception.problemas))

    def test_modo_entrega_aceita_base_completa(self):
        d = copy.deepcopy(_dados())
        for r in d["registros"]:
            r["orientacao"] = "Texto de exemplo."
            r["data_verificacao"] = "2026-11-10"
            r["palavras_chave"] = ["exemplo"]
        b = base.carregar_base(_gravar(json.dumps(d)), modo_entrega=True)
        self.assertEqual(len(b["registros"]), 17)


if __name__ == "__main__":
    unittest.main()
