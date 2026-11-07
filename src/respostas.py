"""Modelos de resposta A e B, avisos de limitação e mensagens de entrada inválida.

Só biblioteca padrão, Python 3.9+. Texto puro com linhas de até 80 colunas;
cores e molduras ficam por conta de sistema.py (spec 5.4).

Os dois modelos recebem o MESMO resultado da busca e a MESMA lista de
relacionados (quem ordena é busca.py). Por isso a comparação A x B mede só o
formato da resposta (spec 8). Textos e ordem seguem docs/ux.md 3.3 a 3.7 e a
ordem fixa da spec 19.5: conteúdo, Atenção, Fonte, assuntos para continuar,
frase de não-oficialidade.
"""
from __future__ import annotations

import re
import textwrap

LARGURA = 80

FRASE_NAO_OFICIAL = "Este assistente não é um canal oficial."
PORTAL_GOV = "https://www.gov.br"

AVISO_CONFIRMAR = "Atenção: confirme no site oficial antes de ir."
AVISO_ESTADUAL = ("Atenção: o procedimento e a taxa mudam de estado para estado. "
                  "Confirme no site oficial antes de ir.")

# Mensagens de entrada inválida (docs/ux.md 3.7).
MSG_VAZIA = "Você não digitou nada. Escreva sua dúvida com palavras ou escolha um número."
MSG_SEM_PALAVRAS = ("Não entendi. Tente com palavras, por exemplo: "
                    "como consultar minha situação eleitoral.")
MSG_LONGA = "Sua pergunta ficou longa. Tente resumir em uma frase curta."


def msg_opcao_inexistente(opcao: str) -> str:
    return "A opção %s não existe aqui. Escolha um dos números da lista." % opcao


def msg_entrada_invalida(texto: str) -> str:
    """Mensagem para a decisão ¬C: vazia ou sem nenhuma palavra útil."""
    return MSG_VAZIA if texto.strip() == "" else MSG_SEM_PALAVRAS


# --------------------------------------------------------------------------
# Peças de texto
# --------------------------------------------------------------------------

def _quebrar(texto: str, prefixo: str = "", recuo: str = "") -> str:
    """Quebra o texto em linhas de até LARGURA colunas, sem cortar links."""
    return textwrap.fill(texto, width=LARGURA, initial_indent=prefixo,
                         subsequent_indent=recuo, break_long_words=False,
                         break_on_hyphens=False)


# Nome público para outros módulos (sistema.py).
quebrar = _quebrar


def titulo_do(reg: dict) -> str:
    """Nome curto do assunto; se o registro não tiver 'titulo', usa a pergunta."""
    return reg.get("titulo") or reg["pergunta"]


def formatar_data(iso: str) -> str:
    """AAAA-MM-DD -> DD/MM/AAAA. Data vazia (registro ainda não verificado)
    aparece como pendente, para ninguém achar que a orientação foi conferida."""
    if not iso:
        return "data de verificação pendente"
    ano, mes, dia = iso.split("-")
    return "%s/%s/%s" % (dia, mes, ano)


def linha_fonte(reg: dict) -> str:
    """'Fonte: <url> (verificado em dd/mm/aaaa)'; sem data, diz que está pendente."""
    if reg["data_verificacao"]:
        verificado = "(verificado em %s)" % formatar_data(reg["data_verificacao"])
    else:
        verificado = "(%s)" % formatar_data("")
    return _quebrar("Fonte: %s %s" % (reg["referencia"], verificado), recuo="  ")


def texto_do_aviso(reg: dict) -> str:
    """Texto do aviso de 'confirmar antes', sem quebra de linha; vazio se não se aplica."""
    if reg.get("abrangencia") == "estadual":
        return AVISO_ESTADUAL
    if reg.get("confirmar_antes"):
        return AVISO_CONFIRMAR
    return ""


def aviso_do(reg: dict) -> str:
    """Aviso de 'confirmar antes' já quebrado em linhas de até 80 colunas."""
    texto = texto_do_aviso(reg)
    return _quebrar(texto) if texto else ""


def dividir_passos(orientacao: str) -> list:
    """Passos da orientação para o Modelo B (spec 7.1). Várias linhas: cada
    linha é um passo. Uma linha só: cada frase é um passo. Numeração do
    próprio texto ("1.", "2)") é descartada. Nunca inventa passo."""
    linhas = [l.strip() for l in orientacao.splitlines() if l.strip()]
    if len(linhas) == 1:
        linhas = [f.strip() for f in re.split(r"(?<=[.!?])\s+", linhas[0]) if f.strip()]
    return [re.sub(r"^\d+[.)]\s*", "", l) for l in linhas]


def _paragrafo(orientacao: str) -> str:
    """A orientação inteira como um parágrafo corrido (Modelo A)."""
    return " ".join(l.strip() for l in orientacao.splitlines() if l.strip())


def _numerados(titulos: list, formato: str = "  %d  %s") -> list:
    return [formato % (i, t) for i, t in enumerate(titulos, start=1)]


# --------------------------------------------------------------------------
# Modelos A e B
# --------------------------------------------------------------------------

def modelo_a(reg: dict, sugestoes: list, por_id: dict) -> str:
    """Modelo A, resumido: um parágrafo + Atenção + Fonte + 'Veja também'."""
    partes = [_quebrar("%s: %s" % (titulo_do(reg), _paragrafo(reg["orientacao"])))]
    aviso = aviso_do(reg)
    if aviso:
        partes.append(aviso)
    partes.append(linha_fonte(reg))
    if sugestoes:
        veja = "  ".join("%d) %s" % (i, titulo_do(por_id[s]))
                         for i, s in enumerate(sugestoes, start=1))
        partes.append(_quebrar("Veja também: " + veja, recuo="  "))
    partes.append("")
    partes.append(FRASE_NAO_OFICIAL)
    return "\n".join(partes)


def modelo_b(reg: dict, sugestoes: list, por_id: dict) -> str:
    """Modelo B, passo a passo: título, passos numerados, Atenção, Fonte,
    'Continue consultando' e a frase de não-oficialidade."""
    barra = "-" * LARGURA
    linhas = [barra, titulo_do(reg), barra]
    for i, passo in enumerate(dividir_passos(reg["orientacao"]), start=1):
        linhas.append(_quebrar(passo, prefixo="%d. " % i, recuo="   "))
    linhas.append("")
    aviso = aviso_do(reg)
    if aviso:
        linhas.append(aviso)
    linhas.append(linha_fonte(reg))
    if sugestoes:
        linhas.append("")
        linhas.append("Continue consultando:")
        linhas.extend(_numerados([titulo_do(por_id[s]) for s in sugestoes]))
    linhas.append("")
    linhas.append(FRASE_NAO_OFICIAL)
    return "\n".join(linhas)


# Nomes técnicos A/B só existem no código, README e relatório; o cidadão vê
# "resumido" e "passo a passo" (spec 19.3).
MODELOS = {"A": modelo_a, "B": modelo_b}
NOMES_DE_FORMATO = {"A": "resumido", "B": "passo a passo"}


def montar_resposta(modelo: str, reg: dict, sugestoes: list, por_id: dict) -> str:
    return MODELOS[modelo](reg, sugestoes, por_id)


# --------------------------------------------------------------------------
# Pedido de escolha e aviso de limitação
# --------------------------------------------------------------------------

def pedir_escolha(candidatos: list, por_id: dict) -> str:
    """Pergunta ambígua (C·A·¬B): lista os candidatos para o usuário escolher."""
    linhas = ["Encontrei mais de um assunto parecido. Qual deles você procura?", ""]
    linhas.extend(_numerados([titulo_do(por_id[c]) for c in candidatos]))
    return "\n".join(linhas)


def aviso_sem_base(temas: dict) -> str:
    """Aviso de limitação (C·¬A): não inventa nada, aponta o portal oficial e
    os temas disponíveis. 'temas' é o dicionário id -> nome do tema."""
    linhas = [
        "Não encontrei orientação verificada sobre isso na minha base.",
        "Não sou um canal oficial e não vou inventar instruções.",
        "",
        "Você pode consultar o portal oficial: %s" % PORTAL_GOV,
        "ou escolher um destes temas:",
        "",
    ]
    linhas.extend(_numerados(list(temas.values())))
    return "\n".join(linhas)
