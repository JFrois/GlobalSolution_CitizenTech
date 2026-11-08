"""Testes do fluxo de documentos do bot (lógica sem aiogram) e do roteamento do cofre."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import documentos as d  # noqa: E402
import roteador  # noqa: E402

try:
    import cryptography  # noqa: F401
    import armazenamento
    import cofre as cf
    import criptografia
    TEM_CRIPTO = True
except ImportError:
    TEM_CRIPTO = False


class TestPuras(unittest.TestCase):
    def test_arquivo_aceito(self):
        self.assertTrue(d.arquivo_aceito("application/pdf", 1000)[0])
        self.assertTrue(d.arquivo_aceito("image/jpeg", 0)[0])
        self.assertFalse(d.arquivo_aceito("application/zip", 10)[0])
        self.assertIn("10 MB", d.arquivo_aceito("image/png", d.TAMANHO_MAX + 1)[1])

    def test_limpar_nome(self):
        self.assertEqual(d.limpar_nome("  meu \n RG   novo "), "meu RG novo")
        self.assertEqual(len(d.limpar_nome("x" * 500)), d.NOME_MAX)
        self.assertEqual(d.limpar_nome(None), "")

    def test_pendentes_expiram_e_pedem_nome(self):
        agora = [0.0]
        p = d.Pendentes(validade=60, relogio=lambda: agora[0])
        p.guardar(1, b"x", "image/png")
        self.assertFalse(p.esta_pedindo_nome(1))
        p.obter(1)["etapa"] = "nome"
        self.assertTrue(p.esta_pedindo_nome(1))
        self.assertIsNone(p.obter(2))  # isolado por usuário
        agora[0] = 61
        self.assertIsNone(p.obter(1))
        self.assertFalse(p.esta_pedindo_nome(1))

    def test_aviso_de_consentimento_diz_a_verdade(self):
        for trecho in ("Gemini", "treinar", "abuso", "outros países"):
            self.assertIn(trecho, d.AVISO_CONSENTIMENTO)
        self.assertIn("não é de ponta a ponta" if False else "ponta a ponta", d.AVISO_ENVIO)


@unittest.skipUnless(TEM_CRIPTO, "cryptography não instalada")
class TestCofreNoChat(unittest.TestCase):
    def setUp(self):
        self.arm = armazenamento.ArmazenamentoSQLite(":memory:")
        self.cofre = cf.Cofre(self.arm, criptografia.ChavesEmMemoria(), iteracoes=1000)

    def test_estados(self):
        self.assertEqual(d.estado_do_cofre(None, 1), "indisponivel")
        self.assertEqual(d.estado_do_cofre(self.cofre, 1), "sem_cofre")
        self.cofre.criar(1, "senha-bem-longa")
        self.assertEqual(d.estado_do_cofre(self.cofre, 1), "aberto")
        self.cofre.bloquear(1)
        self.assertEqual(d.estado_do_cofre(self.cofre, 1), "bloqueado")

    def test_consentimento_por_usuario(self):
        self.assertFalse(self.arm.tem_consentimento(1))
        self.arm.registrar_consentimento(1)
        self.assertTrue(self.arm.tem_consentimento(1))
        self.assertFalse(self.arm.tem_consentimento(2))
        self.arm.apagar_usuario(1)
        self.assertFalse(self.arm.tem_consentimento(1))

    def test_localizar_sem_acento_e_por_palavra(self):
        self.cofre.criar(1, "senha-bem-longa")
        i = self.cofre.guardar(1, "certidao-de-nascimento", b"x")
        j = self.cofre.guardar(1, "RG", b"y")
        self.assertEqual(d.localizar(self.cofre, 1, "certidão de nascimento"), (i, "certidao-de-nascimento"))
        self.assertEqual(d.localizar(self.cofre, 1, "meu rg"), (j, "RG"))
        self.assertIsNone(d.localizar(self.cofre, 1, "cnh"))
        self.assertIsNone(d.localizar(self.cofre, 1, ""))

    def test_localizar_nao_ve_documento_de_outro(self):
        self.cofre.criar(1, "senha-bem-longa")
        self.cofre.criar(2, "senha-bem-longa")
        self.cofre.guardar(1, "RG", b"y")
        self.assertIsNone(d.localizar(self.cofre, 2, "rg"))


class TestRoteamentoDoCofre(unittest.TestCase):
    def test_regras(self):
        f = roteador.fallback_por_regras
        self.assertEqual(f("me envie meu RG")["args"], {"acao": "abrir", "nome": "rg"})
        self.assertEqual(f("guarde este documento")["args"]["acao"], "enviar")
        self.assertEqual(f("meus documentos")["args"]["acao"], "listar")
        self.assertEqual(f("abrir o cofre")["args"]["acao"], "listar")

    def test_buscas_normais_nao_viram_cofre(self):
        f = roteador.fallback_por_regras
        for pergunta in ("documento", "como abrir um MEI", "Como tirar a segunda via do RG?",
                         "como tirar passaporte?"):
            self.assertEqual(f(pergunta)["ferramenta"], "buscar_orientacao", pergunta)


def _tem_aiogram():
    try:
        import aiogram  # noqa: F401
        import cryptography  # noqa: F401
    except ImportError:
        return False
    return True


@unittest.skipUnless(_tem_aiogram(), "precisa de aiogram e cryptography")
class TestBotComCofre(unittest.TestCase):
    def test_bot_monta_com_cofre_e_handlers_de_documento(self):
        import base
        import painel
        import ponte
        import telegram_bot
        arm = armazenamento.ArmazenamentoSQLite(":memory:")
        cofre = cf.Cofre(arm, criptografia.ChavesEmMemoria(), iteracoes=1000)
        bot, dp = telegram_bot.criar_bot({"TELEGRAM_BOT_TOKEN": "1:ABC", "PAINEL_URL": "https://p.exemplo"},
                                         ponte.preparar(base.carregar_base()), arm, painel.LinksUnicos(), cofre)
        self.assertEqual(str(bot.default.parse_mode), "ParseMode.HTML")
        self.assertGreaterEqual(len(dp.sub_routers[0].message.handlers), 8)


if __name__ == "__main__":
    unittest.main()
