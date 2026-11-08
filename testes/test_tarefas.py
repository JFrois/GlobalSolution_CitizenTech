"""Testes de tarefas, lembretes e agendador (sem rede, sem APScheduler)."""
import asyncio
import datetime
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import agendador  # noqa: E402
import armazenamento  # noqa: E402
import tarefas  # noqa: E402

BRT = datetime.timezone(datetime.timedelta(hours=-3))
AGORA = datetime.datetime(2026, 11, 8, 14, 0, tzinfo=BRT)  # domingo


def q(texto):
    return tarefas.interpretar_quando(texto, AGORA)[0]


def dt(d, h, m=0, mes=11):
    return datetime.datetime(2026, mes, d, h, m, tzinfo=BRT)


class TestInterpretarQuando(unittest.TestCase):
    def test_formas_comuns(self):
        self.assertEqual(q("amanhã às 9h"), dt(9, 9))
        self.assertEqual(q("amanha 9h30"), dt(9, 9, 30))
        self.assertEqual(q("hoje 18:30"), dt(8, 18, 30))
        self.assertEqual(q("depois de amanhã"), dt(10, 9))
        self.assertEqual(q("dia 15 às 10h"), dt(15, 10))
        self.assertEqual(q("15/12 às 8h"), dt(15, 8, mes=12))
        self.assertEqual(q("2026-11-20 7:00"), dt(20, 7))
        self.assertEqual(q("daqui a 2 horas"), AGORA + datetime.timedelta(hours=2))
        self.assertEqual(q("daqui a 30 minutos"), AGORA + datetime.timedelta(minutes=30))

    def test_so_hora_passada_vai_para_amanha(self):
        self.assertEqual(q("às 8h"), dt(9, 8))
        self.assertEqual(q("às 20h"), dt(8, 20))

    def test_dia_ja_passado_vai_para_o_mes_seguinte(self):
        self.assertEqual(q("dia 3"), dt(3, 9, mes=12))

    def test_sem_tempo(self):
        self.assertIsNone(q("pagar a conta"))

    def test_data_impossivel_levanta_erro(self):
        with self.assertRaises(tarefas.DataImpossivel):
            q("dia 31/02")

    def test_titulo_sem_a_expressao_de_tempo(self):
        _, titulo = tarefas.interpretar_quando("pagar a conta amanhã às 9h", AGORA)
        self.assertEqual(titulo, "pagar a conta")


class TestExecutar(unittest.TestCase):
    def setUp(self):
        self.arm = armazenamento.ArmazenamentoSQLite(":memory:")

    def run_(self, uid, **args):
        return tarefas.executar(args, self.arm, uid, AGORA)["texto"]

    def test_criar_listar_concluir(self):
        self.assertIn("Anotado", self.run_(1, acao="criar", titulo="me lembre de pagar a conta amanhã às 9h"))
        self.assertIn("1. pagar a conta (09/11 às 09:00)", self.run_(1, acao="listar"))
        self.assertIn("concluí", self.run_(1, acao="concluir", titulo="1"))
        self.assertIn("não tem tarefas", self.run_(1, acao="listar"))

    def test_quando_separado_e_sem_data(self):
        self.assertIn("20/11 às 07:00", self.run_(1, acao="criar", titulo="consulta", quando="2026-11-20 7:00"))
        self.assertIn("Sem data", self.run_(1, acao="criar", titulo="comprar pão"))

    def test_quando_ilegivel_nao_cria(self):
        self.assertIn("Não entendi quando", self.run_(1, acao="criar", titulo="x", quando="um dia desses"))
        self.assertEqual(self.arm.listar_tarefas(1), [])

    def test_data_impossivel_nao_cria_tarefa(self):
        for args in ({"acao": "criar", "titulo": "pagar a luz dia 31/02"},
                     {"acao": "criar", "titulo": "pagar a luz", "quando": "31/02"}):
            self.assertIn("não existe no calendário", self.run_(1, **args))
        self.assertEqual(self.arm.listar_tarefas(1), [])

    def test_passado_e_sem_titulo(self):
        self.assertIn("já passou", self.run_(1, acao="criar", titulo="x", quando="2026-11-01 9h"))
        self.assertIn("Qual é a tarefa", self.run_(1, acao="criar", titulo="", quando="amanhã"))

    def test_isolamento_por_usuario(self):
        self.run_(1, acao="criar", titulo="segredo do 1", quando="amanhã")
        self.assertIn("não tem tarefas", self.run_(2, acao="listar"))
        tid = self.arm.listar_tarefas(1)[0][0]
        self.assertFalse(self.arm.concluir_tarefa(2, tid))
        self.assertIn("Não achei", self.run_(2, acao="concluir", titulo="segredo"))

    def test_concluir_por_trecho_do_titulo(self):
        self.run_(1, acao="criar", titulo="Pagar IPTU", quando="amanhã")
        self.assertIn("concluí", self.run_(1, acao="concluir", titulo="iptu"))

    def test_apagar_usuario_remove_tarefas_e_exclusoes(self):
        self.run_(1, acao="criar", titulo="x", quando="amanhã")
        agendador.agendar_exclusao(self.arm, 1, 10, 20, agora=0)
        self.arm.apagar_usuario(1)
        self.assertEqual(self.arm.listar_tarefas(1), [])
        self.assertEqual(self.arm.exclusoes_vencidas(10**12), [])


class TestAgendador(unittest.TestCase):
    def setUp(self):
        self.arm = armazenamento.ArmazenamentoSQLite(":memory:")
        self.enviados, self.apagados = [], []

    async def enviar(self, uid, texto):
        self.enviados.append((uid, texto))

    async def apagar(self, chat, msg):
        self.apagados.append((chat, msg))

    def processar(self, agora):
        return asyncio.run(agendador.processar(self.arm, self.enviar, self.apagar, agora))

    def test_lembrete_vence_e_so_avisa_uma_vez(self):
        self.arm.criar_tarefa(1, "pagar conta", 1000)
        self.assertEqual(self.processar(999), (0, 0))
        self.assertEqual(self.processar(1001), (1, 0))
        self.assertEqual(self.enviados, [(1, "Lembrete: pagar conta")])
        self.assertEqual(self.processar(2000), (0, 0))

    def test_tarefa_concluida_nao_avisa(self):
        tid = self.arm.criar_tarefa(1, "x", 1000)
        self.arm.concluir_tarefa(1, tid)
        self.assertEqual(self.processar(2000), (0, 0))

    def test_falha_no_envio_tenta_no_proximo_tick(self):
        self.arm.criar_tarefa(1, "x", 1000)
        async def quebra(uid, texto):
            raise RuntimeError("rede")
        self.assertEqual(asyncio.run(agendador.processar(self.arm, quebra, self.apagar, 2000)), (0, 0))
        self.assertEqual(self.processar(2001), (1, 0))

    def test_exclusao_em_5_minutos_e_vencidas_na_subida(self):
        agendador.agendar_exclusao(self.arm, 1, 10, 20, agora=1000)
        self.assertEqual(self.processar(1000 + 299), (0, 0))
        self.assertEqual(self.processar(1000 + 3600), (0, 1))  # servidor voltou tarde: cumpre assim mesmo
        self.assertEqual(self.apagados, [(10, 20)])
        self.assertEqual(self.processar(10**6), (0, 0))

    def test_falha_ao_apagar_nao_repete(self):
        agendador.agendar_exclusao(self.arm, 1, 10, 20, agora=0)
        async def quebra(chat, msg):
            raise RuntimeError("mensagem velha")
        asyncio.run(agendador.processar(self.arm, self.enviar, quebra, 10**6))
        self.assertEqual(self.arm.exclusoes_vencidas(10**7), [])


class TestTarefasParaPainel(unittest.TestCase):
    """tentar_criar e lista_para_painel: o painel precisa saber se criou e receber dados."""

    def setUp(self):
        self.arm = armazenamento.ArmazenamentoSQLite(":memory:")

    def test_cria_com_data_e_lista_em_dados(self):
        criou, msg = tarefas.tentar_criar("pagar a conta", "amanhã às 9h", self.arm, 1, AGORA)
        self.assertTrue(criou)
        self.assertIn("Anotado", msg)
        [item] = tarefas.lista_para_painel(self.arm, 1)
        self.assertEqual(item["titulo"], "pagar a conta")
        self.assertEqual(item["quando"], int(dt(9, 9).timestamp()))
        self.assertTrue(item["quando_texto"])

    def test_sem_data_fica_sem_aviso(self):
        self.assertTrue(tarefas.tentar_criar("ligar para o INSS", "", self.arm, 1, AGORA)[0])
        [item] = tarefas.lista_para_painel(self.arm, 1)
        self.assertEqual((item["quando"], item["quando_texto"]), (None, None))

    def test_recusas_nao_criam_nada(self):
        casos = (("x", "quando der", tarefas.MSG_NAO_ENTENDI_QUANDO),
                 ("x", "2026-11-01 7:00", tarefas.MSG_PASSADO),
                 ("x", "31/02 às 9h", tarefas.MSG_DATA_IMPOSSIVEL),
                 ("", "", None))
        for titulo, quando, esperado in casos:
            criou, msg = tarefas.tentar_criar(titulo, quando, self.arm, 1, AGORA)
            self.assertFalse(criou, (titulo, quando))
            if esperado:
                self.assertEqual(msg, esperado)
        self.assertEqual(tarefas.lista_para_painel(self.arm, 1), [])

    def test_lista_so_do_proprio_usuario(self):
        tarefas.tentar_criar("tarefa de A", "", self.arm, 1, AGORA)
        self.assertEqual(tarefas.lista_para_painel(self.arm, 2), [])


if __name__ == "__main__":
    unittest.main()


class TestRoteamentoDeTarefas(unittest.TestCase):
    def test_regras_escolhem_a_acao(self):
        import roteador
        f = roteador.fallback_por_regras
        self.assertEqual(f("me lembre de pagar a conta amanhã às 9h")["args"]["acao"], "criar")
        self.assertEqual(f("meus lembretes")["args"]["acao"], "listar")
        self.assertEqual(f("concluir tarefa 1")["args"]["acao"], "concluir")
        self.assertEqual(f("como pagar o IPVA")["ferramenta"], "buscar_orientacao")
