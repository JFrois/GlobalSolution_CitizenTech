"""Testes de src/respostas.py: modelos A e B, avisos e mensagens."""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import base  # noqa: E402
import respostas  # noqa: E402


def reg(rid="DOC-001", **extra):
    r = {"id": rid, "tema": "documentacao", "titulo": "Assunto " + rid,
         "palavras_chave": ["x"], "pergunta": "Pergunta " + rid + "?",
         "orientacao": "Abra o app. Escolha a opção. Confirme os dados.",
         "referencia": "https://www.gov.br/exemplo", "data_verificacao": "2026-11-10",
         "relacionados": []}
    r.update(extra)
    return r


POR_ID = {r["id"]: r for r in (reg("DOC-001"), reg("DOC-002"), reg("SRV-001"), reg("DIR-001"))}
SUGESTOES = ["DOC-002", "SRV-001", "DIR-001"]


class TestPecas(unittest.TestCase):
    def test_data_formatada(self):
        self.assertEqual(respostas.formatar_data("2026-11-10"), "10/11/2026")

    def test_data_vazia_fica_pendente(self):
        self.assertIn("pendente", respostas.formatar_data(""))

    def test_titulo_usa_pergunta_se_faltar(self):
        r = reg()
        del r["titulo"]
        self.assertEqual(respostas.titulo_do(r), r["pergunta"])

    def test_passos_por_frase(self):
        self.assertEqual(respostas.dividir_passos("Um. Dois! Três?"), ["Um.", "Dois!", "Três?"])

    def test_passos_por_linha_descartam_numeracao(self):
        self.assertEqual(respostas.dividir_passos("1. Abra o app.\n2) Entre.\n\nSaia."),
                         ["Abra o app.", "Entre.", "Saia."])


class TestModelos(unittest.TestCase):
    def gerar(self, modelo, r=None):
        return respostas.montar_resposta(modelo, r or reg(), SUGESTOES, POR_ID)

    def test_ambos_tem_fonte_data_relacionados_e_frase(self):
        for modelo in "AB":
            texto = self.gerar(modelo)
            self.assertIn("Fonte: https://www.gov.br/exemplo", texto, modelo)
            self.assertIn("10/11/2026", texto, modelo)
            self.assertIn(respostas.FRASE_NAO_OFICIAL, texto, modelo)
            for sug in SUGESTOES:
                self.assertIn(POR_ID[sug]["titulo"], texto, modelo)

    def test_ordem_fixa_do_modelo_b(self):
        texto = self.gerar("B", reg(confirmar_antes=True))
        marcas = ["Assunto DOC-001", "1. Abra", "Atenção:", "Fonte:",
                  "Continue consultando:", respostas.FRASE_NAO_OFICIAL]
        posicoes = [texto.index(m) for m in marcas]
        self.assertEqual(posicoes, sorted(posicoes))

    def test_ordem_fixa_do_modelo_a(self):
        texto = self.gerar("A", reg(confirmar_antes=True))
        marcas = ["Assunto DOC-001: Abra", "Atenção:", "Fonte:", "Veja também:",
                  respostas.FRASE_NAO_OFICIAL]
        posicoes = [texto.index(m) for m in marcas]
        self.assertEqual(posicoes, sorted(posicoes))

    def test_aviso_so_quando_confirmar_antes(self):
        for modelo in "AB":
            self.assertNotIn("Atenção:", self.gerar(modelo))
            self.assertIn("Atenção:", self.gerar(modelo, reg(confirmar_antes=True)))

    def test_aviso_de_estado(self):
        texto = self.gerar("B", reg(abrangencia="estadual"))
        self.assertIn("mudam de estado para estado", texto)

    def test_modelo_b_nao_inventa_passos(self):
        r = reg()
        for passo in respostas.dividir_passos(r["orientacao"]):
            self.assertIn(passo, r["orientacao"])
        self.assertEqual(self.gerar("B").count("\n1. "), 1)

    def test_linhas_de_ate_80_colunas(self):
        longo = reg(orientacao="palavra " * 60)
        for modelo in "AB":
            for linha in self.gerar(modelo, longo).splitlines():
                self.assertLessEqual(len(linha), respostas.LARGURA, linha)

    def test_registro_sem_data_nao_parece_verificado(self):
        texto = self.gerar("A", reg(data_verificacao=""))
        self.assertIn("pendente", texto)
        self.assertNotIn("verificado em", texto)

    def test_sem_sugestoes_nao_quebra(self):
        for modelo in "AB":
            texto = respostas.montar_resposta(modelo, reg(), [], POR_ID)
            self.assertNotIn("Continue consultando", texto)
            self.assertNotIn("Veja também", texto)

    def test_sem_emoji_nem_nao_ascii_fora_do_texto_da_base(self):
        # Moldura e marcadores usam só ASCII (console do Windows).
        texto = self.gerar("B")
        for linha in texto.splitlines():
            if linha.startswith(("-", "Continue", "Fonte")):
                linha.encode("ascii")


class TestAvisos(unittest.TestCase):
    def test_pedir_escolha(self):
        texto = respostas.pedir_escolha(["DOC-001", "DOC-002"], POR_ID)
        self.assertIn("mais de um assunto parecido", texto)
        self.assertIn("  1  Assunto DOC-001", texto)
        self.assertIn("  2  Assunto DOC-002", texto)

    def test_aviso_sem_base(self):
        temas = {"a": "Tema A", "b": "Tema B"}
        texto = respostas.aviso_sem_base(temas)
        self.assertIn("Não encontrei orientação verificada", texto)
        self.assertIn("não vou inventar instruções", texto)
        self.assertIn("https://www.gov.br", texto)
        self.assertIn("  2  Tema B", texto)

    def test_mensagens_de_entrada(self):
        self.assertEqual(respostas.msg_entrada_invalida("  "), respostas.MSG_VAZIA)
        self.assertEqual(respostas.msg_entrada_invalida("???"), respostas.MSG_SEM_PALAVRAS)
        self.assertIn("A opção 7 não existe", respostas.msg_opcao_inexistente("7"))


class TestComBaseReal(unittest.TestCase):
    def test_todo_registro_gera_os_dois_modelos(self):
        dados = base.carregar_base()
        por_id = dados["por_id"]
        for rid, r in por_id.items():
            sug = [x for x in r["relacionados"]][:3]
            for modelo in "AB":
                texto = respostas.montar_resposta(modelo, r, sug, por_id)
                self.assertIn(r["referencia"], texto)


if __name__ == "__main__":
    unittest.main()
