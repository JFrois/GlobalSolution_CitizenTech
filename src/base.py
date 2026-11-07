"""Carga e validação da base de conhecimento (data/base.json).

Núcleo da Onda 1: usa SOMENTE a biblioteca padrão (spec §5.2 e §5.3).
A validação acumula todos os problemas e os mostra juntos (ErroBase), para a
equipe corrigir tudo de uma vez. O programa que chama captura ErroBase e mostra
uma mensagem clara, sem traceback.
"""
from __future__ import annotations

import json
from pathlib import Path

# Caminho padrão resolvido a partir deste arquivo, nunca da pasta atual (spec §5.4).
CAMINHO_PADRAO = Path(__file__).resolve().parent.parent / "data" / "base.json"

# Campos obrigatórios de cada registro (spec §7.1).
CAMPOS_OBRIGATORIOS = (
    "id", "tema", "palavras_chave", "pergunta", "orientacao",
    "referencia", "data_verificacao", "relacionados",
)

# Marca de orientação ainda não redigida pela equipe.
MARCA_PREENCHER = "PREENCHER"


class ErroBase(Exception):
    """Problema ao abrir ou validar a base. Guarda a lista de motivos."""

    def __init__(self, problemas):
        if isinstance(problemas, str):
            problemas = [problemas]
        self.problemas = list(problemas)
        super().__init__("; ".join(self.problemas))


def _validar_registro(reg, indice, temas, modo_entrega):
    """Valida um registro e devolve a lista de problemas encontrados."""
    problemas = []
    if not isinstance(reg, dict):
        return ["registro #%d não é um objeto JSON" % (indice + 1)]
    rid = reg.get("id") or "registro #%d" % (indice + 1)

    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in reg:
            problemas.append("%s sem o campo '%s'" % (rid, campo))
    if problemas:
        return problemas

    if not isinstance(reg["id"], str) or not reg["id"].strip():
        problemas.append("%s: 'id' deve ser texto não vazio" % rid)
    if reg["tema"] not in temas:
        problemas.append("%s: tema desconhecido '%s'" % (rid, reg["tema"]))
    if not isinstance(reg["palavras_chave"], list):
        problemas.append("%s: 'palavras_chave' deve ser uma lista" % rid)
    if not isinstance(reg["relacionados"], list):
        problemas.append("%s: 'relacionados' deve ser uma lista" % rid)
    for campo in ("pergunta", "orientacao", "referencia"):
        if not isinstance(reg[campo], str) or not reg[campo].strip():
            problemas.append("%s: '%s' deve ser texto não vazio" % (rid, campo))
    if not str(reg["referencia"]).startswith(("http://", "https://")):
        problemas.append("%s: 'referencia' deve ser uma URL" % rid)
    if "abrangencia" in reg and reg["abrangencia"] not in ("nacional", "estadual"):
        problemas.append("%s: 'abrangencia' deve ser nacional ou estadual" % rid)

    # Modo de entrega (--validar-entrega): recusa registros ainda incompletos.
    if modo_entrega:
        if str(reg["orientacao"]).strip() == MARCA_PREENCHER:
            problemas.append("%s: orientação ainda marcada como PREENCHER" % rid)
        if not str(reg["data_verificacao"]).strip():
            problemas.append("%s: sem data de verificação" % rid)
        if isinstance(reg["palavras_chave"], list) and not reg["palavras_chave"]:
            problemas.append("%s: sem palavras-chave" % rid)
    return problemas


def validar_dados(dados, modo_entrega=False):
    """Valida o conteúdo já carregado do JSON; devolve a lista de problemas."""
    if not isinstance(dados, dict):
        return ["a base deve ser um objeto JSON"]
    problemas = []
    for chave in ("versao", "temas", "registros"):
        if chave not in dados:
            problemas.append("estrutura inválida: falta '%s'" % chave)
    if problemas:
        return problemas
    temas = dados["temas"]
    registros = dados["registros"]
    if not isinstance(temas, dict) or not temas:
        return ["'temas' deve ser um dicionário não vazio"]
    if not isinstance(registros, list) or not registros:
        return ["'registros' deve ser uma lista não vazia"]
    if "sinonimos" in dados and not isinstance(dados["sinonimos"], dict):
        problemas.append("'sinonimos' deve ser um dicionário")

    ids_vistos = set()
    for i, reg in enumerate(registros):
        problemas.extend(_validar_registro(reg, i, temas, modo_entrega))
        if isinstance(reg, dict) and isinstance(reg.get("id"), str):
            if reg["id"] in ids_vistos:
                problemas.append("id duplicado: %s" % reg["id"])
            ids_vistos.add(reg["id"])

    # Relacionados precisam apontar para ids que existem.
    for reg in registros:
        if isinstance(reg, dict) and isinstance(reg.get("relacionados"), list):
            for outro in reg["relacionados"]:
                if outro not in ids_vistos:
                    problemas.append(
                        "%s: relacionado inexistente '%s'" % (reg.get("id"), outro))
                elif outro == reg.get("id"):
                    problemas.append("%s: relacionado aponta para si mesmo" % outro)
    return problemas


def carregar_base(caminho=None, modo_entrega=False):
    """Lê e valida a base. Devolve um dicionário pronto para a busca.

    Retorno: {"versao", "temas", "sinonimos", "registros", "registros_por_id",
    "ids_por_tema"}. Lança ErroBase com todos os problemas encontrados.
    """
    caminho = Path(caminho) if caminho else CAMINHO_PADRAO
    if not caminho.is_file():
        raise ErroBase("arquivo não encontrado: %s" % caminho.name)
    try:
        texto = caminho.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ErroBase("não foi possível ler %s (%s)" % (caminho.name, exc))
    if not texto.strip():
        raise ErroBase("arquivo vazio: %s" % caminho.name)
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as exc:
        raise ErroBase("JSON inválido na linha %d" % exc.lineno)

    problemas = validar_dados(dados, modo_entrega)
    if problemas:
        raise ErroBase(problemas)

    registros = dados["registros"]
    ids_por_tema = {tema: [] for tema in dados["temas"]}
    for reg in registros:
        ids_por_tema[reg["tema"]].append(reg["id"])
    return {
        "versao": dados["versao"],
        "temas": dados["temas"],
        "sinonimos": dados.get("sinonimos", {}),
        "registros": registros,
        "registros_por_id": {r["id"]: r for r in registros},
        "ids_por_tema": ids_por_tema,
    }
