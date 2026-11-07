"""Testes de src/transcricao.py com o Whisper falso: sem baixar modelo nem precisar de ffmpeg."""
from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import transcricao  # noqa: E402


def whisper_falso(texto="como tirar a segunda via do RG", erro=None):
    """Módulo `whisper` de mentira que devolve 'texto' (ou levanta 'erro')."""
    modelo = mock.Mock()
    if erro:
        modelo.transcribe.side_effect = erro
    else:
        modelo.transcribe.return_value = {"text": "  %s " % texto}
    modulo = types.ModuleType("whisper")
    modulo.load_model = mock.Mock(return_value=modelo)  # type: ignore[attr-defined]
    return modulo, modelo


class TestTranscricao(unittest.TestCase):
    def setUp(self):
        transcricao._modelo = None
        transcricao._nome_carregado = None

    def test_nome_do_modelo(self):
        self.assertEqual(transcricao.nome_do_modelo({}), "base")
        self.assertEqual(transcricao.nome_do_modelo({"WHISPER_MODELO": " Small "}), "small")
        self.assertEqual(transcricao.nome_do_modelo({"WHISPER_MODELO": "gigante"}), "base")

    def test_sem_ffmpeg_ou_whisper_nao_esta_disponivel(self):
        with mock.patch("shutil.which", return_value=None):
            ok, motivo = transcricao.disponivel()
        self.assertFalse(ok)
        self.assertIn("ffmpeg", motivo)
        with mock.patch("shutil.which", return_value="/usr/bin/ffmpeg"), \
                mock.patch.dict(sys.modules, {"whisper": None}):  # None = ImportError
            ok, motivo = transcricao.disponivel()
        self.assertFalse(ok)
        self.assertIn("whisper", motivo)

    def test_transcreve_e_limpa_o_texto(self):
        modulo, modelo = whisper_falso()
        with mock.patch("shutil.which", return_value="/usr/bin/ffmpeg"), \
                mock.patch.dict(sys.modules, {"whisper": modulo}):
            texto = transcricao.transcrever("a.ogg", "base")
        self.assertEqual(texto, "como tirar a segunda via do RG")
        _, kwargs = modelo.transcribe.call_args
        self.assertEqual(kwargs["language"], "pt")

    def test_modelo_e_carregado_uma_vez(self):
        modulo, _ = whisper_falso()
        with mock.patch("shutil.which", return_value="/usr/bin/ffmpeg"), \
                mock.patch.dict(sys.modules, {"whisper": modulo}):
            transcricao.transcrever("a.ogg", "base")
            transcricao.transcrever("b.ogg", "base")
        modulo.load_model.assert_called_once_with("base")  # type: ignore[attr-defined]

    def test_audio_sem_fala_vira_erro_claro(self):
        modulo, _ = whisper_falso(texto="   ")
        with mock.patch("shutil.which", return_value="/usr/bin/ffmpeg"), \
                mock.patch.dict(sys.modules, {"whisper": modulo}):
            with self.assertRaises(transcricao.ErroTranscricao):
                transcricao.transcrever("a.ogg")

    def test_falha_do_whisper_nao_vaza_o_erro_original_ao_usuario(self):
        modulo, _ = whisper_falso(erro=RuntimeError("detalhe interno"))
        with mock.patch("shutil.which", return_value="/usr/bin/ffmpeg"), \
                mock.patch.dict(sys.modules, {"whisper": modulo}):
            with self.assertRaises(transcricao.ErroTranscricao) as ctx:
                transcricao.transcrever("a.ogg")
        self.assertNotIn("detalhe interno", str(ctx.exception))

    def test_log_nao_traz_o_texto_transcrito(self):
        modulo, _ = whisper_falso(texto="meu cpf e um numero secreto")
        with mock.patch("shutil.which", return_value="/usr/bin/ffmpeg"), \
                mock.patch.dict(sys.modules, {"whisper": modulo}), \
                self.assertLogs("citizen.voz", level="DEBUG") as logs:
            transcricao.transcrever("a.ogg")
            transcricao.log.info("fim")  # garante ao menos um registro no assertLogs
        self.assertNotIn("secreto", "\n".join(logs.output))


if __name__ == "__main__":
    unittest.main()
