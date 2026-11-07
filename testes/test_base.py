"""Testes de src/base.py: carga, validação e pendências de entrega."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

# O núcleo roda como script (sem pacote), então src entra no caminho de import.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import base  # noqa: E402


def registro(**extra):
    """Registro válido mínimo; 'extra' sobrescreve campos."""
    reg = {
        "id": "DOC-001", "tema": "documentacao", "palavras_chave": ["rg"],
        "pergunta": "Pergunta?", "orientacao": "Texto.",
        "referencia": "https://www.gov.br", "data_verificacao": "2026-11-10",
        "relacionados": [],
    }
    reg.update(extra)
    return reg


def base_minima(*registros):
    return {"versao": 1, "temas": {"documentacao": "Documentação"},
            "registros": list(registros) or [registro()]}


class TestArquivo(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.pasta = Path(self._dir.name)

    def escrever(self, conteudo):
        caminho = self.pasta / "base.json"
        caminho.write_text(conteudo, encoding="utf-8")
        return caminho

    def test_arquivo_ausente(self):
        with self.assertRaisesRegex(base.ErroBase, "não encontrado"):
            base.carregar_base(self.pasta / "nao_existe.json")

    def test_arquivo_vazio(self):
        with self.assertRaisesRegex(base.ErroBase, "vazio"):
            base.carregar_base(self.escrever("  \n"))

    def test_json_invalido(self):
        with self.assertRaisesRegex(base.ErroBase, "JSON inválido"):
            base.carregar_base(self.escrever("{ quebrado"))

    def test_raiz_nao_objeto(self):
        with self.assertRaisesRegex(base.ErroBase, "objeto JSON"):
            base.carregar_base(self.escrever("[]"))

    def test_base_valida_cria_por_id(self):
        dados = base.carregar_base(self.escrever(json.dumps(base_minima())))
        self.assertIn("DOC-001", dados["por_id"])
        self.assertEqual(dados["sinonimos"], {})


class TestValidacao(unittest.TestCase):
    def erros(self, dados):
        return " | ".join(base.validar_base(dados))

    def test_base_minima_ok(self):
        self.assertEqual(base.validar_base(base_minima()), [])

    def test_campo_faltando(self):
        reg = registro()
        del reg["referencia"]
        self.assertIn("falta o campo 'referencia'", self.erros(base_minima(reg)))

    def test_id_duplicado(self):
        self.assertIn("id duplicado", self.erros(base_minima(registro(), registro())))

    def test_relacionado_inexistente(self):
        dados = base_minima(registro(relacionados=["DOC-999"]))
        self.assertIn("'DOC-999' não existe", self.erros(dados))

    def test_relacionado_consigo_mesmo(self):
        dados = base_minima(registro(relacionados=["DOC-001"]))
        self.assertIn("consigo mesmo", self.erros(dados))

    def test_tema_inexistente(self):
        self.assertIn("tema 'x'", self.erros(base_minima(registro(tema="x"))))

    def test_palavras_chave_vazias(self):
        self.assertIn("palavras_chave", self.erros(base_minima(registro(palavras_chave=[]))))

    def test_data_invalida(self):
        self.assertIn("data_verificacao", self.erros(base_minima(registro(data_verificacao="10/11/2026"))))

    def test_data_vazia_aceita_no_esqueleto(self):
        self.assertEqual(base.validar_base(base_minima(registro(data_verificacao=""))), [])

    def test_opcionais_invalidos(self):
        self.assertIn("confirmar_antes", self.erros(base_minima(registro(confirmar_antes="sim"))))
        self.assertIn("abrangencia", self.erros(base_minima(registro(abrangencia="x"))))
        self.assertIn("referencias_estaduais",
                      self.erros(base_minima(registro(referencias_estaduais=["SP"]))))

    def test_registros_vazio(self):
        dados = base_minima()
        dados["registros"] = []
        self.assertIn("registros", self.erros(dados))

    def test_registro_nao_objeto(self):
        self.assertIn("deveria ser um objeto", self.erros(base_minima("texto")))


class TestPendenciasDeEntrega(unittest.TestCase):
    def test_registro_completo_sem_pendencia(self):
        self.assertEqual(base.pendencias_de_entrega(base_minima()), [])

    def test_registro_incompleto_gera_pendencias(self):
        dados = base_minima(registro(orientacao="PREENCHER", data_verificacao=""))
        pendencias = base.pendencias_de_entrega(dados)
        self.assertEqual(len(pendencias), 2)


class TestBaseReal(unittest.TestCase):
    """Garante o esqueleto do projeto: 17 registros, 3 temas, grafo conexo."""

    @classmethod
    def setUpClass(cls):
        cls.dados = base.carregar_base()

    def test_quantidades(self):
        self.assertEqual(len(self.dados["registros"]), 17)
        self.assertEqual(len(self.dados["temas"]), 3)

    def test_grafo_conexo(self):
        vizinhos = {rid: set() for rid in self.dados["por_id"]}
        for reg in self.dados["registros"]:
            for alvo in reg["relacionados"]:
                vizinhos[reg["id"]].add(alvo)
                vizinhos[alvo].add(reg["id"])  # não direcionado (spec 7.3)
        inicio = next(iter(vizinhos))
        visitados, pilha = {inicio}, [inicio]
        while pilha:
            for v in vizinhos[pilha.pop()]:
                if v not in visitados:
                    visitados.add(v)
                    pilha.append(v)
        self.assertEqual(visitados, set(vizinhos))

    def test_nao_alterada_por_copia(self):
        # Sanidade: validar não deve mexer nos dados.
        antes = copy.deepcopy(self.dados["registros"])
        base.validar_base(self.dados)
        self.assertEqual(antes, self.dados["registros"])


if __name__ == "__main__":
    unittest.main()
