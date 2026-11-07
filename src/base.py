"""Carga e validação da base de conhecimento (data/base.json).

Só usa a biblioteca padrão e roda em Python 3.9 ou superior (spec 5.2 e 5.4).
Qualquer problema na base vira um ErroBase com mensagem clara; o chamador
(sistema.py) mostra a mensagem e sai, sem traceback.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

# Caminho padrão resolvido a partir deste arquivo, nunca da pasta atual (spec 5.4).
CAMINHO_PADRAO = Path(__file__).resolve().parent.parent / "data" / "base.json"

# Campos que todo registro precisa ter (spec 7.1).
CAMPOS_OBRIGATORIOS = (
    "id", "tema", "palavras_chave", "pergunta", "orientacao",
    "referencia", "data_verificacao", "relacionados",
)

# Valores aceitos em "abrangencia" (campo opcional).
ABRANGENCIAS = ("nacional", "estadual")

# Marcador dos registros ainda não redigidos pela equipe.
MARCA_PENDENTE = "PREENCHER"

_FORMATO_ID = re.compile(r"^[A-Z]{3}-\d{3}$")


class ErroBase(Exception):
    """Problema ao abrir ou validar a base. A mensagem já é para o usuário."""


def _texto_ok(valor) -> bool:
    """True se o valor é um texto com pelo menos um caractere visível."""
    return isinstance(valor, str) and valor.strip() != ""


def _data_valida(valor: str) -> bool:
    """True se o texto é uma data real no formato AAAA-MM-DD."""
    try:
        date.fromisoformat(valor)
    except ValueError:
        return False
    return True


def _validar_registro(reg, posicao: int, temas: dict) -> list:
    """Valida um registro isolado e devolve a lista de problemas achados."""
    if not isinstance(reg, dict):
        return ["registro #%d: deveria ser um objeto JSON" % posicao]

    nome = reg.get("id") if _texto_ok(reg.get("id")) else "#%d" % posicao
    erros = []

    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in reg:
            erros.append("registro %s: falta o campo '%s'" % (nome, campo))
    if erros:
        # Sem os campos básicos não adianta checar os tipos.
        return erros

    if not _texto_ok(reg["id"]) or not _FORMATO_ID.match(reg["id"]):
        erros.append("registro %s: 'id' deve ter o formato AAA-000" % nome)
    if reg["tema"] not in temas:
        erros.append("registro %s: tema '%s' não existe em 'temas'" % (nome, reg["tema"]))
    if not _texto_ok(reg["pergunta"]):
        erros.append("registro %s: 'pergunta' está vazia" % nome)
    if not _texto_ok(reg["orientacao"]):
        erros.append("registro %s: 'orientacao' está vazia" % nome)
    if not _texto_ok(reg["referencia"]) or not reg["referencia"].startswith("http"):
        erros.append("registro %s: 'referencia' deve ser um link (http...)" % nome)

    palavras = reg["palavras_chave"]
    if (not isinstance(palavras, list) or not palavras
            or not all(_texto_ok(p) for p in palavras)):
        erros.append("registro %s: 'palavras_chave' deve ser uma lista de textos, "
                     "com pelo menos uma" % nome)

    if not isinstance(reg["relacionados"], list) or not all(
            isinstance(r, str) for r in reg["relacionados"]):
        erros.append("registro %s: 'relacionados' deve ser uma lista de ids" % nome)

    data = reg["data_verificacao"]
    # Vazia é aceita no esqueleto; no modo de entrega é recusada (ver pendencias_de_entrega).
    if not isinstance(data, str) or (data != "" and not _data_valida(data)):
        erros.append("registro %s: 'data_verificacao' deve estar vazia ou ser AAAA-MM-DD" % nome)

    # Campos opcionais.
    if "titulo" in reg and not _texto_ok(reg["titulo"]):
        erros.append("registro %s: 'titulo' está vazio" % nome)
    if "confirmar_antes" in reg and not isinstance(reg["confirmar_antes"], bool):
        erros.append("registro %s: 'confirmar_antes' deve ser true ou false" % nome)
    if "abrangencia" in reg and reg["abrangencia"] not in ABRANGENCIAS:
        erros.append("registro %s: 'abrangencia' deve ser 'nacional' ou 'estadual'" % nome)
    if "referencias_estaduais" in reg:
        est = reg["referencias_estaduais"]
        if not isinstance(est, dict) or not all(
                _texto_ok(uf) and _texto_ok(url) for uf, url in est.items()):
            erros.append("registro %s: 'referencias_estaduais' deve mapear UF para link" % nome)

    return erros


def validar_base(dados) -> list:
    """Valida a estrutura inteira e devolve a lista de problemas (vazia = ok)."""
    if not isinstance(dados, dict):
        return ["o arquivo deve conter um objeto JSON na raiz"]

    erros = []
    temas = dados.get("temas")
    if not isinstance(temas, dict) or not temas:
        erros.append("falta 'temas' (dicionário id -> nome do tema)")
        temas = {}
    sinonimos = dados.get("sinonimos", {})
    if not isinstance(sinonimos, dict) or not all(
            isinstance(v, list) and all(isinstance(x, str) for x in v)
            for v in sinonimos.values()):
        erros.append("'sinonimos' deve mapear um termo para uma lista de textos")

    registros = dados.get("registros")
    if not isinstance(registros, list) or not registros:
        erros.append("falta 'registros' ou a lista está vazia")
        return erros

    ids_vistos = set()
    for posicao, reg in enumerate(registros, start=1):
        erros.extend(_validar_registro(reg, posicao, temas))
        if isinstance(reg, dict) and isinstance(reg.get("id"), str):
            if reg["id"] in ids_vistos:
                erros.append("id duplicado: %s" % reg["id"])
            ids_vistos.add(reg["id"])

    # Relacionados precisam apontar para ids que existem (e não para si mesmo).
    for reg in registros:
        if not isinstance(reg, dict) or not isinstance(reg.get("relacionados"), list):
            continue
        for alvo in reg["relacionados"]:
            if alvo not in ids_vistos:
                erros.append("registro %s: relacionado '%s' não existe" % (reg.get("id"), alvo))
            elif alvo == reg.get("id"):
                erros.append("registro %s: relaciona-se consigo mesmo" % reg.get("id"))
    return erros


def pendencias_de_entrega(base: dict) -> list:
    """Lista o que ainda impede a entrega: orientação não redigida ou sem data.

    Usado por 'sistema.py --validar-entrega' (spec 7.2).
    """
    pendencias = []
    for reg in base["registros"]:
        if reg["orientacao"].strip() == MARCA_PENDENTE:
            pendencias.append("%s: orientação ainda marcada como %s" % (reg["id"], MARCA_PENDENTE))
        if reg["data_verificacao"] == "":
            pendencias.append("%s: sem data de verificação" % reg["id"])
    return pendencias


def carregar_base(caminho=None) -> dict:
    """Lê e valida o JSON. Devolve a base com o atalho 'por_id'.

    Levanta ErroBase se o arquivo faltar, estiver vazio, for JSON inválido
    ou tiver inconsistências.
    """
    caminho = Path(caminho) if caminho is not None else CAMINHO_PADRAO

    if not caminho.is_file():
        raise ErroBase("arquivo não encontrado: %s" % caminho)
    try:
        texto = caminho.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ErroBase("não foi possível ler %s (%s)" % (caminho.name, exc.__class__.__name__))
    if texto.strip() == "":
        raise ErroBase("o arquivo %s está vazio" % caminho.name)
    try:
        dados = json.loads(texto)
    except ValueError as exc:
        raise ErroBase("JSON inválido em %s (%s)" % (caminho.name, exc))

    erros = validar_base(dados)
    if erros:
        raise ErroBase("; ".join(erros))

    dados.setdefault("sinonimos", {})
    # Dicionário para recuperar registro por id (spec 2.2).
    dados["por_id"] = {reg["id"]: reg for reg in dados["registros"]}
    return dados
