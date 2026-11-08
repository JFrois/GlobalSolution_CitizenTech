"""Testes do resumo da manhã: tarefas do dia, manchetes rotuladas, falha de feed e agendamento."""
import asyncio
import datetime
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import agendador  # noqa: E402
import armazenamento  # noqa: E402
import briefing  # noqa: E402

BRT = datetime.timezone(datetime.timedelta(hours=-3))
AGORA = datetime.datetime(2026, 11, 9, 7, 30, tzinfo=BRT)
TEMAS = {"documentacao": "Documentação pessoal", "servicos": "Serviços públicos"}


def coletor_falso(url):
    if "ruim" in url:
        raise RuntimeError("feed fora do ar")
    return [("Manchete %d de %s" % (i, url[-1]), "https://exemplo.org/%d" % i) for i in range(1, 6)]


class TestFeeds(unittest.TestCase):
    def test_carregar_feeds_tolerante(self):
        with tempfile.TemporaryDirectory() as d:
            ok = Path(d) / "f.json"
            ok.write_text(json.dumps({"_aviso": "x", "servicos": ["https://a.org/rss", "javascript:x", 3],
                                      "documentacao": "nao-lista"}), encoding="utf-8")
            self.assertEqual(briefing.carregar_feeds(ok), {"servicos": ["https://a.org/rss"]})
            ruim = Path(d) / "r.json"
            ruim.write_text("{ruim", encoding="utf-8")
            self.assertEqual(briefing.carregar_feeds(ruim), {})
            self.assertEqual(briefing.carregar_feeds(Path(d) / "nao-existe.json"), {})

    def test_feeds_do_projeto_comecam_vazios(self):
        feeds = briefing.carregar_feeds()
        self.assertTrue(all(v == [] for v in feeds.values()))

    def test_maximo_de_3_e_feed_com_erro_e_pulado(self):
        itens = briefing.manchetes_do_tema(["https://ruim.org/a", "https://x.org/b"], coletor_falso)
        self.assertEqual(len(itens), 3)
        self.assertEqual(briefing.manchetes_do_tema(["https://ruim.org/a"], coletor_falso), [])


class TestMontar(unittest.TestCase):
    def setUp(self):
        self.arm = armazenamento.ArmazenamentoSQLite(":memory:")

    def montar(self, uid=1, feeds=None):
        return briefing.montar(uid, self.arm, feeds or {}, TEMAS, AGORA, coletor_falso)

    def test_tarefas_do_dia_so_do_proprio_usuario(self):
        hoje = AGORA.replace(hour=15, minute=0).timestamp()
        amanha = (AGORA + datetime.timedelta(days=1)).timestamp()
        self.arm.criar_tarefa(1, "pagar conta", hoje)
        self.arm.criar_tarefa(1, "tarefa de amanhã", amanha)
        self.arm.criar_tarefa(2, "tarefa do outro", hoje)
        t = self.montar(1)
        self.assertIn("pagar conta (15:00)", t)
        self.assertNotIn("amanhã", t)
        self.assertNotIn("outro", t)
        self.assertIn("não tem tarefas", self.montar(3))

    def test_manchetes_rotuladas_e_limitadas(self):
        self.arm.definir_temas_briefing(1, ["servicos"])
        t = self.montar(1, {"servicos": ["https://x.org/a"]})
        self.assertIn("Notícias — fonte não oficial", t)
        self.assertEqual(t.count("- Manchete"), 3)
        self.assertIn("https://exemplo.org/1", t)

    def test_sem_feeds_so_tarefas(self):
        self.arm.definir_temas_briefing(1, ["servicos"])
        t = self.montar(1, {})
        self.assertNotIn("Notícias — fonte não oficial", t)
        self.assertIn("Sem manchetes disponíveis", t)

    def test_configurar(self):
        r = briefing.executar({"acao": "configurar", "temas": ["servicos"], "hora": "07:30"},
                              self.arm, 1, {}, TEMAS, AGORA)["texto"]
        self.assertIn("configurado", r)
        self.assertEqual(self.arm.obter_hora_briefing(1), "07:30")
        self.assertEqual(self.arm.obter_temas_briefing(1), ["servicos"])
        self.assertIn("Não reconheci", briefing.executar(
            {"acao": "configurar", "temas": ["esportes"]}, self.arm, 1, {}, TEMAS)["texto"])
        self.assertIn("Não entendi o horário", briefing.executar(
            {"acao": "configurar", "hora": "7h"}, self.arm, 1, {}, TEMAS)["texto"])
        self.assertEqual(self.arm.obter_hora_briefing(2), None)


class TestAgendamento(unittest.TestCase):
    def setUp(self):
        self.arm = armazenamento.ArmazenamentoSQLite(":memory:")
        self.enviados = []

    def rodar(self, agora):
        async def enviar(uid, texto):
            self.enviados.append((uid, texto))

        async def apagar(c, m):
            pass

        async def resumo(uid):
            return "resumo de %d" % uid
        return asyncio.run(agendador.processar(self.arm, enviar, apagar, agora, resumo))

    def test_envia_uma_vez_por_dia_na_hora(self):
        self.arm.definir_hora_briefing(1, "07:30")
        antes = AGORA.replace(hour=7, minute=29).timestamp()
        self.rodar(antes)
        self.assertEqual(self.enviados, [])
        self.rodar(AGORA.timestamp())
        self.rodar(AGORA.timestamp() + 600)  # outro tick no mesmo dia: não repete
        self.assertEqual(self.enviados, [(1, "resumo de 1")])
        self.rodar(AGORA.timestamp() + 86400)  # dia seguinte: envia de novo
        self.assertEqual(len(self.enviados), 2)

    def test_servidor_que_subiu_atrasado_ainda_envia_no_dia(self):
        self.arm.definir_hora_briefing(1, "07:30")
        self.rodar(AGORA.replace(hour=10).timestamp())
        self.assertEqual(len(self.enviados), 1)

    def test_apagar_usuario_remove_config(self):
        self.arm.definir_hora_briefing(1, "07:30")
        self.arm.apagar_usuario(1)
        self.assertIsNone(self.arm.obter_hora_briefing(1))


if __name__ == "__main__":
    unittest.main()
