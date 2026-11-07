"""Citizen Assist AI - orientação cidadã NÃO OFICIAL (terminal).

Uso:
    python src/sistema.py                    consulta no terminal (offline)
    python src/sistema.py --simples          texto puro, sem cor nem molduras
    python src/sistema.py --avaliar          taxa de acerto e tempo (testes/)
    python src/sistema.py --validar-entrega  confere se a base está completa
    python src/sistema.py --servidor         bot, painel e agendador (Onda 2)

O modo terminal usa SOMENTE a biblioteca padrão do Python: sem pip, sem .env,
sem internet (spec §5.3). Bibliotecas da Onda 2 só são importadas dentro de
--servidor. Telas e textos seguem docs/ux.md §3.
"""
from __future__ import annotations

import sys

# Versão mínima do núcleo (spec §5.4). Checada antes de qualquer outro import.
if sys.version_info < (3, 9):
    print("O Citizen Assist AI precisa do Python 3.9 ou superior.")
    print("Sua versão: %d.%d. Instale uma versão mais nova e tente de novo."
          % sys.version_info[:2])
    sys.exit(1)

import argparse
import os
from pathlib import Path

# Garante que os módulos vizinhos (base, busca, respostas) sejam encontrados,
# não importa de que pasta o programa foi chamado (spec §5.4).
sys.path.insert(0, str(Path(__file__).resolve().parent))

import base as modulo_base  # noqa: E402
import busca  # noqa: E402
import respostas  # noqa: E402

NOME_FORMATO = {"A": "resumido", "B": "passo a passo"}
# TODO (EM ABERTO, spec §8): o formato padrão será o vencedor da comparação A x B.
FORMATO_PADRAO = "A"


# ---------------------------------------------------------------------------
# Estilo: cores ANSI e molduras (modo identidade) ou texto puro (modo simples)
# ---------------------------------------------------------------------------
class Estilo:
    """Aplica a identidade visual só quando é seguro; senão devolve texto puro."""

    # Cores do terminal (docs/design/tokens.json): 24 bits e aproximação de 16 cores.
    CORES = {
        "ambar": ((245, 181, 68), "33"),
        "ciano": ((111, 211, 224), "36"),
        "atencao": ((255, 138, 107), "91"),
        "apoio": ((139, 147, 161), "90"),
    }

    def __init__(self, forcar_simples=False):
        # Texto puro: pedido do usuário, NO_COLOR ou saída que não é terminal.
        eh_terminal = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
        self.ativo = eh_terminal and not forcar_simples and "NO_COLOR" not in os.environ
        self.truecolor = os.environ.get("COLORTERM", "").lower() in ("truecolor", "24bit")
        if self.ativo:
            self.ativo = _habilitar_cores_windows()

    def cor(self, nome, texto, negrito=False):
        if not self.ativo:
            return texto
        rgb, basico = self.CORES[nome]
        codigo = "38;2;%d;%d;%d" % rgb if self.truecolor else basico
        if negrito:
            codigo = "1;" + codigo
        return "\033[%sm%s\033[0m" % (codigo, texto)

    def linha_dupla(self):
        return ("═" if self.ativo else "=") * 64

    def decorar(self, texto):
        """Colore uma resposta pronta, linha a linha. A cor nunca é a única pista."""
        if not self.ativo:
            return texto
        saida = []
        for linha in texto.splitlines():
            if linha.startswith("Atenção:"):
                linha = self.cor("atencao", "Atenção:", True) + linha[len("Atenção:"):]
            elif linha.startswith("Fonte:"):
                linha = self.cor("ciano", linha)
            elif linha.startswith(respostas.LINHA[:10]):
                linha = self.cor("apoio", linha)
            elif linha == respostas.NAO_OFICIAL:
                linha = self.cor("apoio", linha)
            else:
                linha = _colorir_numero(self, linha)
            saida.append(linha)
        return "\n".join(saida)


def _colorir_numero(estilo, linha):
    """Números das opções (ex.: '  1  Assunto') em âmbar."""
    espacos = len(linha) - len(linha.lstrip())
    resto = linha.lstrip()
    inicio = resto.split(" ", 1)
    if espacos and len(inicio) == 2 and inicio[0].isdigit():
        return linha[:espacos] + estilo.cor("ambar", inicio[0], True) + " " + inicio[1]
    return linha


def _habilitar_cores_windows():
    """No Windows 10+, liga o modo de cores ANSI do console (só biblioteca padrão)."""
    if os.name != "nt":
        return True
    try:
        import ctypes
        kernel = ctypes.windll.kernel32
        manipulador = kernel.GetStdHandle(-11)
        modo = ctypes.c_uint32()
        if not kernel.GetConsoleMode(manipulador, ctypes.byref(modo)):
            return False
        return bool(kernel.SetConsoleMode(manipulador, modo.value | 0x0004))
    except Exception:  # console antigo: cai para texto puro
        return False


# ---------------------------------------------------------------------------
# Terminal interativo
# ---------------------------------------------------------------------------
class Terminal:
    """Máquina de estados do menu. `contexto` diz o que os números significam."""

    def __init__(self, base, estilo, formato=FORMATO_PADRAO, entrada=input):
        self.base = busca.preparar(base)
        self.estilo = estilo
        self.formato = formato
        self.entrada = entrada
        self.contexto = {"tipo": "menu"}

    # ---- entrada e saída -------------------------------------------------
    def dizer(self, texto=""):
        # Mensagens soltas longas são quebradas para caber em 80 colunas.
        if len(texto) > 80 and "\n" not in texto and not texto.startswith(" "):
            texto = respostas._quebrar(texto)
        print(self.estilo.decorar(texto))

    def ler(self):
        """Lê uma linha. Devolve None no fim da entrada ou em Ctrl+C."""
        try:
            return self.entrada("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return None

    def titulo_do(self, rid):
        return self.base["registros_por_id"][rid]["pergunta"]

    def lista(self, ids):
        for i, rid in enumerate(ids, 1):
            self.dizer(respostas._quebrar(self.titulo_do(rid), "  %d  " % i))

    # ---- telas -------------------------------------------------------------
    def tela_menu(self):
        e = self.estilo
        moldura = e.linha_dupla()
        self.dizer(e.cor("ambar", moldura))
        self.dizer("  " + e.cor("ambar", "CITIZEN ASSIST AI", True)
                   + "  -  orientação cidadã NÃO OFICIAL")
        self.dizer(e.cor("ambar", moldura))
        self.dizer("Respondo só com informações verificadas em fontes oficiais.")
        self.dizer("Não sou um canal oficial do governo.")
        self.dizer()
        self.dizer("Digite sua pergunta (ex.: como tirar a segunda via do RG)")
        self.dizer("ou escolha uma opção:")
        self.dizer()
        self.dizer("  1  Ver assuntos por tema")
        self.dizer("  2  Ver o caminho entre dois assuntos")
        self.dizer("  3  Formato da resposta (agora: %s)" % NOME_FORMATO[self.formato])
        self.dizer("  ?  Ajuda")
        self.dizer("  0  Sair")
        self.dizer()
        self.contexto = {"tipo": "menu"}

    def tela_ajuda(self):
        self.dizer("Exemplos de pergunta:")
        self.dizer("  - como consultar minha situação eleitoral")
        self.dizer("  - quero marcar perícia do INSS")
        self.dizer("  - como me inscrever no CadÚnico")
        self.dizer()
        self.dizer("Teclas: [m] menu  [?] ajuda  [0] sair (no menu)  "
                   "ou digite sua dúvida.")
        self.dizer(respostas.NAO_OFICIAL)

    def tela_temas(self):
        self.dizer("Temas disponíveis:")
        for i, (tid, nome) in enumerate(self.base["temas"].items(), 1):
            n = len(self.base["ids_por_tema"][tid])
            self.dizer("  %d  %s (%d assuntos)" % (i, nome, n))
        self.dizer("[1-%d] escolher tema  [m] menu" % len(self.base["temas"]))
        self.contexto = {"tipo": "temas", "ids": list(self.base["temas"])}

    def tela_assuntos_do_tema(self, tema):
        ids = self.base["ids_por_tema"][tema]
        self.dizer(self.estilo.cor("ambar", self.base["temas"][tema], True))
        self.lista(ids)
        self.dizer("[número] abrir assunto  [m] menu  "
                   "ou digite uma pergunta sobre este tema")
        self.contexto = {"tipo": "tema", "tema": tema, "ids": ids}

    def tela_formato(self):
        self.dizer("Como você prefere ler as respostas?")
        self.dizer("  1  Resumido: um parágrafo curto e a fonte")
        self.dizer("  2  Passo a passo: lista de passos, avisos e assuntos relacionados")
        self.dizer("Agora: %s." % NOME_FORMATO[self.formato])
        self.dizer("[1-2] escolher  [m] menu")
        self.contexto = {"tipo": "formato"}

    def mostrar_assunto(self, rid):
        """Mostra um assunto no formato escolhido, com relacionados numerados."""
        grafo = self.base["grafo"]
        ids = busca.relacionados_ordenados(grafo, rid)
        regs = [self.base["registros_por_id"][i] for i in ids]
        self.dizer(respostas.formatar(self.base["registros_por_id"][rid], self.formato, regs))
        if ids:
            self.dizer("[1-%d] abrir assunto  [m] menu  ou digite outra pergunta" % len(ids))
        else:
            self.dizer("[m] menu  ou digite outra pergunta")
        self.contexto = {"tipo": "resposta", "ids": ids}

    # ---- ações -------------------------------------------------------------
    def perguntar(self, texto, apenas_tema=None):
        if len(texto) > respostas.LIMITE_PERGUNTA:
            self.dizer(respostas.MSG_LONGA)
            return
        r = busca.buscar(texto, self.base, apenas_tema=apenas_tema)
        decisao = r["decisao"]
        if decisao == "INVALIDA":
            self.dizer(respostas.MSG_SEM_PALAVRA)
        elif decisao == "RESPONDER":
            self.mostrar_assunto(r["candidatos"][0][0])
        elif decisao == "PEDIR_ESCOLHA":
            ids = [c[0] for c in r["candidatos"]]
            self.dizer(respostas.pedir_escolha([self.base["registros_por_id"][i] for i in ids]))
            self.dizer()
            self.dizer("[1-%d] escolher  [m] menu  ou reescreva a pergunta" % len(ids))
            self.contexto = {"tipo": "escolha", "ids": ids}
        else:  # SEM_BASE
            self.dizer(respostas.aviso_sem_base(self.base["temas"]))
            self.dizer()
            self.dizer("[1-%d] ver tema  [m] menu  ou tente outra pergunta"
                       % len(self.base["temas"]))
            self.contexto = {"tipo": "temas", "ids": list(self.base["temas"])}

    def caminho(self):
        """Menu 2: o usuário escolhe origem e destino pela lista numerada."""
        ordem = [rid for tema in self.base["temas"] for rid in self.base["ids_por_tema"][tema]]
        self.dizer("Escolha o assunto de ORIGEM e depois o de DESTINO:")
        n = 0
        for tema, nome in self.base["temas"].items():
            self.dizer(self.estilo.cor("ambar", nome, True))
            for rid in self.base["ids_por_tema"][tema]:
                n += 1
                self.dizer(respostas._quebrar(self.titulo_do(rid), "  %2d  " % n))
        origem = self._escolher_numero("origem", ordem)
        if origem is None:
            return
        destino = self._escolher_numero("destino", ordem)
        if destino is None:
            return
        achado = busca.dijkstra(self.base["grafo"], origem, destino)
        if achado is None:
            self.dizer("Esses dois assuntos não estão ligados na base. Escolha outro par.")
            return
        custo, ids = achado
        self.dizer("Caminho de \"%s\" até \"%s\":" % (self.titulo_do(origem), self.titulo_do(destino)))
        self.dizer()
        for i, rid in enumerate(ids):
            prefixo = "  " if i == 0 else "   -> "
            self.dizer(respostas._quebrar(self.titulo_do(rid), prefixo))
        self.dizer()
        self.dizer("%d passos (custo %d). Assuntos de temas diferentes contam como passos "
                   "mais longos." % (len(ids) - 1, custo))
        self.dizer("[1-%d] abrir um assunto do caminho  [m] menu" % len(ids))
        self.contexto = {"tipo": "caminho", "ids": ids}

    def _escolher_numero(self, rotulo, ordem):
        """Pede um número da lista; repete até valer. None se o usuário sair."""
        while True:
            self.dizer("Número do assunto de %s [1-%d]  ([m] volta ao menu):" % (rotulo, len(ordem)))
            entrada = self.ler()
            if entrada is None:
                self.despedida_pendente = True
                return None
            texto = entrada.strip().lower()
            if texto == "m":
                return None
            if texto.isdigit() and 1 <= int(texto) <= len(ordem):
                return ordem[int(texto) - 1]
            if texto == "":
                self.dizer(respostas.MSG_VAZIA)
            elif texto.isdigit():
                self.dizer(respostas.msg_opcao_inexistente(texto))
            else:
                self.dizer("Digite o número do assunto da lista.")

    def tratar_numero(self, numero):
        """Interpreta um número conforme a tela atual. Devolve False para sair."""
        tipo = self.contexto["tipo"]
        ids = self.contexto.get("ids", [])
        if tipo == "menu":
            if numero == 0:
                return False
            if numero == 1:
                self.tela_temas()
            elif numero == 2:
                self.caminho()
            elif numero == 3:
                self.tela_formato()
            else:
                self.dizer(respostas.msg_opcao_inexistente(numero))
                self.tela_menu()
            return True
        if tipo == "formato":
            if numero in (1, 2):
                self.formato = "A" if numero == 1 else "B"
                self.dizer("Formato alterado: %s." % NOME_FORMATO[self.formato])
                self.tela_menu()
            else:
                self.dizer(respostas.msg_opcao_inexistente(numero))
                self.tela_formato()
            return True
        if 1 <= numero <= len(ids):
            escolhido = ids[numero - 1]
            if tipo == "temas":
                self.tela_assuntos_do_tema(escolhido)
            else:  # tema, resposta, escolha, caminho: abrem um assunto
                self.mostrar_assunto(escolhido)
            return True
        self.dizer(respostas.msg_opcao_inexistente(numero))
        return True

    # ---- laço principal ----------------------------------------------------
    def executar(self):
        self.despedida_pendente = False
        self.tela_menu()
        while True:
            entrada = self.ler()
            if entrada is None or self.despedida_pendente:
                break
            texto = entrada.strip()
            baixo = texto.lower()
            if texto == "":
                self.dizer(respostas.MSG_VAZIA)
            elif baixo == "m":
                self.tela_menu()
            elif baixo in ("?", "ajuda"):
                self.tela_ajuda()
            elif texto.isdigit():
                if not self.tratar_numero(int(texto)):
                    break
            else:
                tema = self.contexto.get("tema") if self.contexto["tipo"] == "tema" else None
                self.perguntar(texto, apenas_tema=tema)
            if self.despedida_pendente:
                break
        self.dizer("Até logo. Lembre-se de confirmar as informações no site oficial.")


# ---------------------------------------------------------------------------
# Modos de execução
# ---------------------------------------------------------------------------
def abrir_base(caminho, modo_entrega=False):
    """Carrega a base ou encerra com mensagem clara (sem traceback)."""
    try:
        return modulo_base.carregar_base(caminho, modo_entrega=modo_entrega)
    except modulo_base.ErroBase as erro:
        if len(erro.problemas) == 1:
            print("Não consegui abrir a base de orientações: %s." % erro.problemas[0])
        else:
            print("Não consegui abrir a base de orientações:")
            for problema in erro.problemas:
                print("  - " + problema)
        print("Avise a equipe.")
        sys.exit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Citizen Assist AI - orientação cidadã NÃO OFICIAL.")
    parser.add_argument("--simples", action="store_true",
                        help="texto puro, sem cor nem molduras (leitores de tela)")
    parser.add_argument("--avaliar", action="store_true",
                        help="roda as perguntas de testes/ e mostra taxa de acerto e tempo")
    parser.add_argument("--validar-entrega", action="store_true",
                        help="confere se a base está completa para a entrega")
    parser.add_argument("--servidor", action="store_true",
                        help="sobe bot, painel e agendador (precisa de .env)")
    parser.add_argument("--base", default=None, help="caminho de outra base JSON")
    args = parser.parse_args(argv)

    # Garante UTF-8 no console (Windows) sem quebrar se não for possível.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    if args.servidor:
        # Import tardio: só aqui as bibliotecas da Onda 2 são necessárias.
        import servidor
        return servidor.iniciar(args.base)

    dados = abrir_base(args.base, modo_entrega=args.validar_entrega)
    if args.validar_entrega:
        print("Base pronta para entrega: %d assuntos completos." % len(dados["registros"]))
        return 0
    if args.avaliar:
        import avaliacao
        return avaliacao.executar(dados)

    estilo = Estilo(forcar_simples=args.simples)
    pendentes = sum(1 for r in dados["registros"] if r["orientacao"].strip() == "PREENCHER")
    if pendentes:
        print(estilo.cor("apoio", "Aviso: %d assuntos ainda sem orientação redigida pela "
                         "equipe." % pendentes))
    Terminal(dados, estilo).executar()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nAté logo. Lembre-se de confirmar as informações no site oficial.")
        sys.exit(0)
