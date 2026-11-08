"""Testes de src/sistema.py: sessões roteirizadas, entradas inválidas e modos de exibição."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import base  # noqa: E402
import sistema  # noqa: E402


def rodar(*entradas, estilo=None, argv=("--simples",)):
    """Roda uma sessão com entradas roteirizadas; devolve (código, texto da saída)."""
    fila = list(entradas)
    saida = []

    def entrada(_prompt):
        if not fila:
            raise EOFError
        return fila.pop(0)

    if estilo is None:
        codigo = sistema.principal(list(argv), entrada=entrada, saida=saida.append)
    else:
        dados = base.carregar_base()
        sistema.Sessao(dados, estilo, entrada, saida.append).executar()
        codigo = 0
    return codigo, "\n".join(saida)


class TestFluxo(unittest.TestCase):
    def test_pergunta_direta_mostra_fonte_e_relacionados(self):
        _, texto = rodar("Como tirar a segunda via do RG?", "0")
        self.assertIn("2ª via da identidade", texto)
        self.assertIn("Fonte:", texto)
        self.assertIn("Continue consultando:", texto)
        self.assertIn(sistema.DESPEDIDA, texto)

    def test_numero_abre_relacionado(self):
        _, texto = rodar("Como tirar a segunda via do RG?", "1", "0")
        self.assertEqual(texto.count("Continue consultando:"), 2)

    def test_entradas_invalidas_nao_encerram(self):
        _, texto = rodar("", "???", "7", "0")
        self.assertIn("Você não digitou nada", texto)
        self.assertIn("Não entendi", texto)
        self.assertIn("A opção 7 não existe", texto)
        self.assertIn(sistema.DESPEDIDA, texto)

    def test_pergunta_ambigua_pede_escolha(self):
        _, texto = rodar("documento", "1", "0")
        self.assertIn("mais de um assunto parecido", texto)
        self.assertIn("Fonte:", texto)  # a escolha 1 abriu uma resposta

    def test_sem_base_avisa_e_nao_inventa(self):
        _, texto = rodar("como tirar passaporte?", "0")
        self.assertIn("Não encontrei orientação verificada", texto)
        self.assertIn("https://www.gov.br", texto)
        self.assertNotIn("Fonte:", texto)

    def test_texto_longo(self):
        _, texto = rodar("a" * 301, "0")
        self.assertIn("Sua pergunta ficou longa", texto)

    def test_zero_fora_do_menu_nao_sai(self):
        _, texto = rodar("Como tirar a segunda via do RG?", "0", "m", "0")
        self.assertIn("A opção 0 não existe", texto)
        self.assertIn(sistema.DESPEDIDA, texto)

    def test_fim_da_entrada_sai_com_despedida(self):
        codigo, texto = rodar()
        self.assertEqual(codigo, 0)
        self.assertIn(sistema.DESPEDIDA, texto)

    def test_ctrl_c_sai_sem_traceback(self):
        def entrada(_):
            raise KeyboardInterrupt
        saida = []
        sistema.Sessao(base.carregar_base(), sistema.Estilo(), entrada, saida.append).executar()
        self.assertIn(sistema.DESPEDIDA, "\n".join(saida))

    def test_menu_temas_e_pergunta_dentro_do_tema(self):
        _, texto = rodar("1", "2", "inss", "0")
        self.assertIn("Serviços públicos", texto)
        self.assertIn("Meu INSS", texto)

    def test_pergunta_filtrada_pelo_tema_ignora_outros_temas(self):
        # Tema 1 (documentação) não tem nada sobre INSS: cai em "sem base".
        _, texto = rodar("1", "1", "meu inss", "0")
        self.assertIn("Não encontrei orientação verificada", texto)

    def test_caminho_entre_assuntos(self):
        # Origem: 2º da lista (DOC-002, CIN digital); destino: último (DIR-006).
        _, texto = rodar("2", "2", "17", "0")
        self.assertIn('Caminho de "CIN digital no app gov.br"', texto)
        self.assertIn("-> Tarifa Social de Energia Elétrica", texto)
        self.assertIn("passos", texto)

    def test_caminho_mesmo_assunto(self):
        _, texto = rodar("2", "1", "1", "0")
        self.assertIn("Escolha dois assuntos diferentes", texto)

    def test_formato_resumido(self):
        _, texto = rodar("3", "1", "Como tirar a segunda via do RG?", "0")
        self.assertIn("Formato: resumido.", texto)
        self.assertIn("Veja também:", texto)
        self.assertNotIn("Continue consultando:", texto)

    def test_ajuda(self):
        _, texto = rodar("?", "0")
        self.assertIn("Exemplos de pergunta:", texto)

    def test_saida_simples_cabe_em_80_colunas(self):
        _, texto = rodar("Como tirar a segunda via do RG?", "documento", "1", "1", "3", "1",
                         "m", "2", "1", "17", "?", "0")
        for linha in texto.splitlines():
            # Um link não pode ser quebrado; linha que é só link fica de fora.
            if len(linha.split()) == 1 and linha.strip().startswith("http"):
                continue
            self.assertLessEqual(len(linha), 80, linha)


class TestEstilo(unittest.TestCase):
    def test_texto_puro_nao_tem_codigo_ansi(self):
        _, texto = rodar("Como tirar a segunda via do RG?", "0")
        self.assertNotIn("\x1b[", texto)

    def test_identidade_tem_cor_e_continua_com_rotulos(self):
        _, texto = rodar("Como tirar a segunda via do RG?", "0",
                         estilo=sistema.Estilo(ativo=True, truecolor=True))
        self.assertIn("\x1b[", texto)
        self.assertIn("Fonte:", texto)       # a cor nunca é a única pista
        self.assertIn("Atenção:", texto)

    def test_16_cores_quando_nao_ha_truecolor(self):
        _, texto = rodar("Como tirar a segunda via do RG?", "0",
                         estilo=sistema.Estilo(ativo=True, truecolor=False))
        self.assertIn("\x1b[94m", texto)
        self.assertNotIn("38;2;", texto)


class TestLinhaDeComando(unittest.TestCase):
    def test_base_com_problema_sai_com_codigo_1_sem_traceback(self):
        with tempfile.TemporaryDirectory() as pasta:
            ruim = Path(pasta) / "base.json"
            ruim.write_text("{ quebrado", encoding="utf-8")
            saida = []
            codigo = sistema.principal(["--base", str(ruim)], saida=saida.append)
        self.assertEqual(codigo, 1)
        self.assertIn("Não consegui abrir a base de orientações", saida[0])
        self.assertIn("Avise a equipe", saida[0])

    def test_validar_entrega_recusa_base_com_preencher(self):
        # Copia a base real e volta um registro ao estado de esqueleto.
        dados = json.loads((RAIZ / "data" / "base.json").read_text(encoding="utf-8"))
        dados["registros"][0]["orientacao"] = "PREENCHER"
        dados["registros"][0]["data_verificacao"] = ""
        with tempfile.TemporaryDirectory() as pasta:
            incompleta = Path(pasta) / "base.json"
            incompleta.write_text(json.dumps(dados), encoding="utf-8")
            saida = []
            codigo = sistema.principal(["--validar-entrega", "--base", str(incompleta)],
                                       saida=saida.append)
        self.assertEqual(codigo, 1)
        self.assertIn("ainda marcada como PREENCHER", "\n".join(saida))

    def test_validar_entrega_aceita_base_completa(self):
        saida = []
        codigo = sistema.principal(["--validar-entrega"], saida=saida.append)
        self.assertEqual(codigo, 0, saida)

    def test_executa_como_script_e_sai_limpo(self):
        proc = subprocess.run([sys.executable, str(RAIZ / "src" / "sistema.py"), "--simples"],
                              input="como tirar a segunda via do RG\n0\n", capture_output=True,
                              text=True, encoding="utf-8", cwd="/")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertIn(sistema.DESPEDIDA, proc.stdout)


if __name__ == "__main__":
    unittest.main()
