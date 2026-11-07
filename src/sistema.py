"""Citizen Assist AI - orientação cidadã NÃO OFICIAL (terminal).

Uso:
    python src/sistema.py                    consulta no terminal (offline, sem chaves)
    python src/sistema.py --simples          texto puro, sem cores nem molduras
    python src/sistema.py --validar-entrega  confere se a base está pronta para entregar
    python src/sistema.py --avaliar          taxa de acerto, tempos e comparação A x B (grava testes/*.csv)
    python src/sistema.py --servidor         bot e painel (precisa de .env e das bibliotecas do servidor)

Roda só com Python 3.9+, sem .env, sem internet e sem pip install (spec 5.3).
Telas e textos seguem docs/ux.md, seção 3.
"""
from __future__ import annotations

import sys

# Antes de qualquer outro import do projeto: versão mínima (spec 5.4).
if sys.version_info < (3, 9):
    print("Este programa precisa do Python 3.9 ou mais novo. "
          "Versão encontrada: %d.%d." % sys.version_info[:2])
    sys.exit(1)

import argparse
import os
import re
from collections import namedtuple
from pathlib import Path

# Os módulos do núcleo ficam ao lado deste arquivo, não importa de onde o
# programa foi chamado.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import base as modulo_base  # noqa: E402
import busca  # noqa: E402
import respostas  # noqa: E402

MAX_PERGUNTA = 300  # acima disso pedimos uma versão curta (ux 3.1)

# TODO(EM ABERTO, spec 8): o formato padrão (resumido = A, passo a passo = B)
# só será decidido depois da comparação A x B. "B" é provisório.
MODELO_PADRAO = "B"

DESPEDIDA = "Até logo. Lembre-se de confirmar as informações no site oficial."


# --------------------------------------------------------------------------
# Estilo: cores ANSI com texto puro como reserva (spec 5.4)
# --------------------------------------------------------------------------

class Estilo:
    """Aplica cores da identidade 'Estreia clara' (docs/ux.md, seção 9).

    Com ativo=False devolve o texto sem nenhum enfeite. A cor nunca é a única
    pista: 'Atenção:' e 'Fonte:' continuam escritos.
    """

    def __init__(self, ativo: bool = False, truecolor: bool = False):
        self.ativo = ativo
        self.truecolor = truecolor
        self.traco = "─" if ativo else "-"
        self.dupla = "═" if ativo else "="

    def _pintar(self, texto: str, rgb: tuple, basico: str, extra: str = "") -> str:
        if not self.ativo or texto == "":
            return texto
        codigo = "38;2;%d;%d;%d" % rgb if self.truecolor else basico
        return "\x1b[%s%sm%s\x1b[0m" % (extra, codigo, texto)

    def ambar(self, texto: str, negrito: bool = False) -> str:
        return self._pintar(texto, (245, 181, 68), "33", "1;" if negrito else "")

    def ciano(self, texto: str) -> str:
        return self._pintar(texto, (111, 211, 224), "36")

    def coral(self, texto: str) -> str:
        return self._pintar(texto, (255, 138, 107), "91")


def _ativar_cores_no_windows() -> bool:
    """Liga o modo de cores do console do Windows 10+. False se não der."""
    if os.name != "nt":
        return True
    try:
        import ctypes
        kernel = ctypes.windll.kernel32
        saida = kernel.GetStdHandle(-11)
        modo = ctypes.c_uint32()
        if not kernel.GetConsoleMode(saida, ctypes.byref(modo)):
            return False
        return bool(kernel.SetConsoleMode(saida, modo.value | 0x0004))
    except Exception:  # qualquer falha aqui só significa "sem cores"
        return False


def estilo_automatico(simples: bool) -> Estilo:
    """Escolhe o modo: texto puro se --simples, NO_COLOR, saída que não é
    terminal (arquivo, pipe, testes) ou terminal 'dumb'."""
    if (simples or os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb"
            or not sys.stdout.isatty() or not _ativar_cores_no_windows()):
        return Estilo(ativo=False)
    truecolor = os.environ.get("COLORTERM", "").lower() in ("truecolor", "24bit")
    return Estilo(ativo=True, truecolor=truecolor)


# --------------------------------------------------------------------------
# Sessão de terminal
# --------------------------------------------------------------------------

# tipo: menu, temas, tema, sugestoes, escolha, origem, destino, caminho, formato
# ids:  números da tela apontam para estes assuntos/temas (quando houver)
Tela = namedtuple("Tela", "tipo ids rodape extra")


class Sair(Exception):
    """Pedido de saída (opção 0, Ctrl+C ou fim da entrada)."""


def _faixa(n: int) -> str:
    return "[1]" if n == 1 else "[1-%d]" % n


class Sessao:
    """Uma conversa no terminal. Entrada e saída são injetadas para permitir testes."""

    def __init__(self, dados: dict, estilo: Estilo, entrada=input, saida=print):
        self.dados = dados
        self.estilo = estilo
        self.entrada = entrada
        self.saida = saida
        self.buscador = busca.Buscador(dados)
        self.por_id = dados["por_id"]
        self.temas = dados["temas"]
        self.ids_dos_temas = list(self.temas)
        self.modelo = MODELO_PADRAO
        # Assuntos numerados de 1 a N, agrupados por tema (menu 2).
        self.ordem = [r["id"] for t in self.ids_dos_temas
                      for r in sorted(dados["registros"], key=lambda x: x["id"])
                      if r["tema"] == t]
        self.tela = Tela("menu", [], "", None)  # tela inicial; tela_menu() a redesenha

    # ---- saída -----------------------------------------------------------

    def escrever(self, texto: str = "") -> None:
        self.saida(texto)

    def _rodape(self, texto: str) -> str:
        """Teclas válidas: o que está entre colchetes ganha destaque."""
        return re.sub(r"\[[^\]]+\]", lambda m: self.estilo.ambar(m.group(0)), texto)

    def _estilizar_resposta(self, texto: str) -> str:
        """Pinta a resposta já montada por respostas.py (só quando há cor)."""
        if not self.estilo.ativo:
            return texto
        e = self.estilo
        saida, bloco, barras = [], None, 0
        for linha in texto.split("\n"):
            if linha == "-" * respostas.LARGURA:
                barras += 1
                saida.append(e.ambar(e.traco * respostas.LARGURA))
                continue
            if barras == 1:  # linha entre as duas barras: título do assunto
                saida.append(e.ambar(linha, negrito=True))
                continue
            if linha.startswith("Atenção:"):
                bloco = "atencao"
            elif linha.startswith("Fonte:"):
                bloco = "fonte"
            elif linha.strip() == "":
                bloco = None
            if bloco == "atencao":
                linha = e.coral(linha)
            elif bloco == "fonte":
                linha = e.ciano(linha)
            else:
                linha = re.sub(r"^(\s*)(\d+)(\.|\s)", lambda m: m.group(1) + e.ambar(m.group(2)) + m.group(3), linha)
            saida.append(linha)
        return "\n".join(saida)

    def cabecalho(self) -> None:
        e = self.estilo
        barra = e.dupla * 64
        self.escrever(e.ambar(barra))
        self.escrever("  " + e.ambar("CITIZEN ASSIST AI", negrito=True)
                      + "  -  orientação cidadã NÃO OFICIAL")
        self.escrever(e.ambar(barra))

    # ---- telas -----------------------------------------------------------

    def tela_menu(self) -> None:
        self.cabecalho()
        self.escrever("Respondo só com informações verificadas em fontes oficiais.")
        self.escrever("Não sou um canal oficial do governo.")
        self.escrever("")
        self.escrever("Digite sua pergunta (ex.: como tirar a segunda via do RG)")
        self.escrever("ou escolha uma opção:")
        self.escrever("")
        e = self.estilo
        self.escrever("  %s  Ver assuntos por tema" % e.ambar("1"))
        self.escrever("  %s  Ver o caminho entre dois assuntos" % e.ambar("2"))
        self.escrever("  %s  Formato da resposta (agora: %s)"
                      % (e.ambar("3"), respostas.NOMES_DE_FORMATO[self.modelo]))
        self.escrever("  %s  Ajuda" % e.ambar("?"))
        self.escrever("  %s  Sair" % e.ambar("0"))
        self.tela = Tela("menu", [], "", None)

    def tela_ajuda(self) -> None:
        self.escrever("Exemplos de pergunta:")
        self.escrever("  como tirar a segunda via do RG")
        self.escrever("  como consultar minha situação eleitoral")
        self.escrever("  quero marcar perícia do INSS")
        self.escrever("")
        self.escrever("Teclas: " + self._rodape("[m]") + " menu   "
                      + self._rodape("[?]") + " ajuda   " + self._rodape("[0]")
                      + " sair (no menu)")
        self.escrever(respostas.FRASE_NAO_OFICIAL)

    def tela_temas(self, rodape: str = "[1-%d] escolher tema  [m] menu") -> None:
        self.escrever("Temas disponíveis:")
        for i, tid in enumerate(self.ids_dos_temas, start=1):
            qtd = sum(1 for r in self.dados["registros"] if r["tema"] == tid)
            self.escrever("  %s  %s (%d assuntos)" % (self.estilo.ambar(str(i)), self.temas[tid], qtd))
        self.tela = Tela("temas", list(self.ids_dos_temas),
                         rodape % len(self.ids_dos_temas) if "%d" in rodape else rodape, None)

    def tela_assuntos_do_tema(self, tema: str) -> None:
        ids = sorted(r["id"] for r in self.dados["registros"] if r["tema"] == tema)
        self.escrever(self.estilo.ambar(self.temas[tema], negrito=True))
        for i, rid in enumerate(ids, start=1):
            self.escrever("  %s  %s" % (self.estilo.ambar(str(i)), respostas.titulo_do(self.por_id[rid])))
        self.tela = Tela("tema", ids, "[número] abrir assunto  [m] menu  "
                         "ou digite uma pergunta sobre este tema", tema)

    def tela_escolher_assunto(self, tipo: str, titulo: str, origem=None) -> None:
        self.escrever(titulo)
        tema_atual = None
        for i, rid in enumerate(self.ordem, start=1):
            reg = self.por_id[rid]
            if reg["tema"] != tema_atual:
                tema_atual = reg["tema"]
                self.escrever(self.estilo.ambar(self.temas[tema_atual]))
            self.escrever("  %s  %s" % (self.estilo.ambar("%2d" % i), respostas.titulo_do(reg)))
        self.tela = Tela(tipo, list(self.ordem), "%s escolher  [m] menu" % _faixa(len(self.ordem)), origem)

    def tela_formato(self) -> None:
        self.escrever("Como você prefere ler as respostas?")
        self.escrever("  %s  Resumido: um parágrafo curto e a fonte" % self.estilo.ambar("1"))
        self.escrever("  %s  Passo a passo: lista de passos, avisos e assuntos relacionados"
                      % self.estilo.ambar("2"))
        self.escrever("Agora: %s." % respostas.NOMES_DE_FORMATO[self.modelo])
        self.tela = Tela("formato", [], "[1-2] escolher  [m] menu", None)

    def mostrar_resposta(self, rid: str) -> None:
        reg = self.por_id[rid]
        # Continue consultando: os 3 mais próximos pelo Dijkstra, sem o assunto exibido.
        sugestoes = self.buscador.sugestoes(rid, 3, excluir=(rid,))
        texto = respostas.montar_resposta(self.modelo, reg, sugestoes, self.por_id)
        self.escrever(self._estilizar_resposta(texto))
        self.tela = Tela("sugestoes", sugestoes, "%s abrir assunto  [m] menu  ou digite outra pergunta"
                         % _faixa(len(sugestoes)), None)

    def mostrar_caminho(self, origem: str, destino: str) -> None:
        if origem == destino:
            self.escrever("Escolha dois assuntos diferentes.")
            return self.tela_escolher_assunto("destino", "Para qual assunto?", origem)
        achado = self.buscador.caminho(origem, destino)
        if achado is None:
            self.escrever("Esses dois assuntos não estão ligados na base. Escolha outro par.")
            return self.tela_escolher_assunto("origem", "De qual assunto você parte?")
        _, caminho = achado
        titulos = [respostas.titulo_do(self.por_id[c]) for c in caminho]
        self.escrever(respostas.quebrar('Caminho de "%s" até "%s":' % (titulos[0], titulos[-1])))
        self.escrever("")
        self.escrever("  " + titulos[0])
        for t in titulos[1:]:
            self.escrever("   -> " + t)
        self.escrever("")
        passos = len(caminho) - 1
        self.escrever("%d %s. Assuntos de temas diferentes contam como passos mais longos."
                      % (passos, "passo" if passos == 1 else "passos"))
        self.tela = Tela("caminho", caminho, "%s abrir um assunto do caminho  [m] menu"
                         % _faixa(len(caminho)), None)

    def reexibir(self) -> None:
        """Depois de uma mensagem de erro, mostra a tela atual de novo. Nas
        telas de resposta só a linha de teclas volta (ler() a imprime)."""
        t = self.tela
        if t.tipo == "menu":
            self.tela_menu()
        elif t.tipo == "temas":
            self.tela_temas()
        elif t.tipo == "tema":
            self.tela_assuntos_do_tema(t.extra)
        elif t.tipo in ("origem", "destino"):
            self.tela_escolher_assunto(t.tipo, "De qual assunto você parte?" if t.tipo == "origem"
                                       else "Para qual assunto?", t.extra)
        elif t.tipo == "formato":
            self.tela_formato()

    # ---- pergunta --------------------------------------------------------

    def perguntar(self, texto: str, tema=None) -> None:
        r = self.buscador.buscar(texto, tema=tema)
        if r.decisao == busca.INVALIDA:
            self.escrever(respostas.msg_entrada_invalida(texto))
            return self.reexibir()
        if r.decisao == busca.SEM_BASE:
            self.escrever(respostas.aviso_sem_base(self.temas))
            self.tela = Tela("temas", list(self.ids_dos_temas),
                             "[1-%d] ver tema  [m] menu  ou tente outra pergunta"
                             % len(self.ids_dos_temas), None)
            return
        if r.decisao == busca.PEDIR_ESCOLHA:
            self.escrever(respostas.pedir_escolha(r.candidatos, self.por_id))
            self.tela = Tela("escolha", r.candidatos, "%s escolher  [m] menu  ou reescreva a pergunta"
                             % _faixa(len(r.candidatos)), None)
            return
        self.mostrar_resposta(r.candidatos[0])

    # ---- entrada ---------------------------------------------------------

    def ler(self) -> str:
        if self.tela.rodape:
            self.escrever("")
            self.escrever(self._rodape(self.tela.rodape))
        try:
            return self.entrada(self.estilo.ambar(">") + " ")
        except (EOFError, KeyboardInterrupt):
            raise Sair()

    def tratar_numero(self, n: int) -> None:
        t = self.tela
        if t.tipo == "menu":
            if n == 0:
                raise Sair()
            if n == 1:
                return self.tela_temas()
            if n == 2:
                return self.tela_escolher_assunto("origem", "De qual assunto você parte?")
            if n == 3:
                return self.tela_formato()
        elif t.tipo == "formato":
            if n in (1, 2):
                self.modelo = "A" if n == 1 else "B"
                self.escrever("Formato: %s." % respostas.NOMES_DE_FORMATO[self.modelo])
                return self.tela_menu()
        elif 1 <= n <= len(t.ids):
            alvo = t.ids[n - 1]
            if t.tipo == "temas":
                return self.tela_assuntos_do_tema(alvo)
            if t.tipo == "origem":
                return self.tela_escolher_assunto("destino", "Para qual assunto?", alvo)
            if t.tipo == "destino":
                return self.mostrar_caminho(t.extra, alvo)
            return self.mostrar_resposta(alvo)  # tema, sugestoes, escolha, caminho
        self.escrever(respostas.msg_opcao_inexistente(str(n)))
        self.reexibir()

    def tratar(self, bruto: str) -> None:
        texto = bruto.strip()
        baixo = texto.lower()
        if texto == "":
            self.escrever(respostas.MSG_VAZIA)
            return self.reexibir()
        if len(texto) > MAX_PERGUNTA:
            self.escrever(respostas.MSG_LONGA)
            return self.reexibir()
        if baixo in ("m", "menu"):
            return self.tela_menu()
        if baixo in ("?", "ajuda"):
            self.tela_ajuda()
            return self.reexibir()
        if re.fullmatch(r"[0-9]+", texto):
            return self.tratar_numero(int(texto))
        if self.tela.tipo in ("origem", "destino", "formato"):
            self.escrever("Escolha um dos números da lista, ou digite m para voltar ao menu.")
            return self.reexibir()
        tema = self.tela.extra if self.tela.tipo == "tema" else None
        self.perguntar(texto, tema=tema)

    def executar(self) -> None:
        """Laço principal. Nunca encerra por erro de entrada."""
        self.tela_menu()
        try:
            while True:
                self.tratar(self.ler())
        except Sair:
            self.escrever("")
            self.escrever(DESPEDIDA)


# --------------------------------------------------------------------------
# Linha de comando
# --------------------------------------------------------------------------

def _argumentos(argv):
    p = argparse.ArgumentParser(prog="sistema.py", description="Citizen Assist AI (terminal)")
    p.add_argument("--simples", action="store_true", help="texto puro, sem cores nem molduras")
    p.add_argument("--validar-entrega", action="store_true",
                   help="recusa registros ainda não preenchidos ou sem data de verificação")
    p.add_argument("--avaliar", action="store_true", help="taxa de acerto, tempos e comparação A x B; grava CSVs em testes/")
    p.add_argument("--servidor", action="store_true", help="bot e painel (precisa de .env; ver .env.example)")
    p.add_argument("--base", default=None, help="caminho de outro base.json (testes)")
    return p.parse_args(argv)


def principal(argv=None, entrada=input, saida=print) -> int:
    args = _argumentos(argv)
    try:
        getattr(sys.stdout, "reconfigure")(encoding="utf-8")  # acentos no console do Windows
    except (AttributeError, ValueError):
        pass

    if args.servidor:
        # Import tardio: só aqui as bibliotecas da Onda 2 são necessárias (spec 5.3).
        import servidor
        return servidor.iniciar(args.base)

    try:
        dados = modulo_base.carregar_base(args.base)
    except modulo_base.ErroBase as erro:
        saida("Não consegui abrir a base de orientações: %s. Avise a equipe." % erro)
        return 1

    if args.validar_entrega:
        pendencias = modulo_base.pendencias_de_entrega(dados)
        for linha in pendencias:
            saida(linha)
        saida("Base pronta para entrega." if not pendencias
              else "%d pendência(s). Base ainda não está pronta para entrega." % len(pendencias))
        return 1 if pendencias else 0

    if args.avaliar:
        import avaliacao
        saida(avaliacao.avaliar(dados))
        saida("")
        saida("Arquivos gravados em testes/: resultados.csv e comparacao_modelos.csv")
        return 0

    Sessao(dados, estilo_automatico(args.simples), entrada, saida).executar()
    return 0


if __name__ == "__main__":
    sys.exit(principal())
