"""Painel web (esqueleto da Onda 2): login e rota /api/perguntar.

Nesta rodada: validação do `initData` do Telegram, link de uso único, sessão
assinada, limite de taxa e a rota que devolve a resposta em JSON estruturado
(spec §10.4 e §10.5). Cofre, telas e criptografia ficam para a próxima rodada.

As funções puras (sem FastAPI) usam só a biblioteca padrão e são testadas sem
rede. O FastAPI é importado dentro de `criar_app` (import tardio, spec §5.3).
A pergunta enviada em /api/perguntar NÃO é gravada nem logada (spec §13).
"""

# Atenção: este módulo NÃO usa "from __future__ import annotations". O FastAPI lê as
# anotações das rotas (Request, Response...) em tempo de execução; como esses tipos são
# importados dentro de criar_app, anotações em texto não seriam resolvidas.
import hashlib
import hmac
import json
import secrets
import time
from urllib.parse import parse_qsl

import ponte

IDADE_MAX_INITDATA = 3600      # segundos: initData mais velho que isso é recusado
VALIDADE_LINK = 300            # link de uso único vale 5 minutos
VALIDADE_SESSAO = 3600


# ---- Login pelo Mini App ---------------------------------------------------
def validar_init_data(init_data, token_bot, agora=None, idade_max=IDADE_MAX_INITDATA):
    """Valida o `initData` assinado pelo Telegram. Devolve o user_id ou None.

    Algoritmo oficial: chave = HMAC-SHA256("WebAppData", token); a assinatura é
    o HMAC dos pares ordenados "chave=valor" separados por quebra de linha.
    """
    try:
        pares = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
    except ValueError:
        return None
    recebido = pares.pop("hash", None)
    if not recebido or not token_bot:
        return None
    texto = "\n".join("%s=%s" % (k, pares[k]) for k in sorted(pares))
    chave = hmac.new(b"WebAppData", token_bot.encode(), hashlib.sha256).digest()
    esperado = hmac.new(chave, texto.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(esperado, recebido):
        return None
    agora = time.time() if agora is None else agora
    try:
        if agora - int(pares.get("auth_date", "0")) > idade_max:
            return None  # assinatura válida, mas antiga demais
        return int(json.loads(pares["user"])["id"])
    except (KeyError, ValueError, TypeError):
        return None


# ---- Login pelo navegador (link de uso único) ------------------------------
class LinksUnicos:
    """Tokens de uso único e curta duração, gerados por /painel no bot."""

    def __init__(self, validade=VALIDADE_LINK):
        self._tokens = {}
        self._validade = validade

    def gerar(self, user_id, agora=None):
        agora = time.time() if agora is None else agora
        # Descarta links vencidos que ninguém usou, para o dicionário não crescer sem limite.
        self._tokens = {t: d for t, d in self._tokens.items() if d[1] >= agora}
        token = secrets.token_urlsafe(32)
        self._tokens[token] = (int(user_id), agora + self._validade)
        return token

    def consumir(self, token, agora=None):
        """Devolve o user_id e invalida o token; None se inválido ou vencido."""
        dados = self._tokens.pop(token, None)  # pop: só funciona uma vez
        if not dados:
            return None
        agora = time.time() if agora is None else agora
        return dados[0] if agora <= dados[1] else None


def assinar_sessao(user_id, segredo, agora=None, validade=VALIDADE_SESSAO):
    """Cookie de sessão assinado: 'user_id.expira.assinatura'."""
    expira = int((time.time() if agora is None else agora) + validade)
    corpo = "%d.%d" % (user_id, expira)
    assinatura = hmac.new(segredo.encode(), corpo.encode(), hashlib.sha256).hexdigest()
    return corpo + "." + assinatura


def verificar_sessao(cookie, segredo, agora=None):
    """Devolve o user_id da sessão ou None se adulterada ou vencida."""
    try:
        user_id, expira, assinatura = cookie.split(".")
        corpo = "%s.%s" % (user_id, expira)
        esperado = hmac.new(segredo.encode(), corpo.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(esperado, assinatura):
            return None
        if (time.time() if agora is None else agora) > int(expira):
            return None
        return int(user_id)
    except (ValueError, AttributeError):
        return None


class LimitadorTaxa:
    """Limite simples de requisições por chave numa janela de tempo."""

    def __init__(self, maximo=20, janela=60):
        self.maximo, self.janela, self._hits = maximo, janela, {}

    def permitir(self, chave, agora=None):
        agora = time.time() if agora is None else agora
        if len(self._hits) > 1000:  # limpeza de chaves antigas, para não crescer sem limite
            self._hits = {c: h for c, h in self._hits.items()
                          if any(agora - t < self.janela for t in h)}
        recentes = [t for t in self._hits.get(chave, []) if agora - t < self.janela]
        if len(recentes) >= self.maximo:
            self._hits[chave] = recentes
            return False
        recentes.append(agora)
        self._hits[chave] = recentes
        return True


def pergunta_do_corpo(corpo):
    """Extrai a pergunta do JSON recebido; qualquer formato inesperado vira texto vazio."""
    if isinstance(corpo, dict) and isinstance(corpo.get("pergunta"), str):
        return corpo["pergunta"]
    return ""


# ---- Resposta estruturada (sem LLM) ----------------------------------------
def resposta_estruturada(pergunta, base, uf=None):
    """JSON da aba "Perguntar": só dados da base, o front apenas desenha."""
    ponte.preparar(base)
    if not isinstance(pergunta, str) or len(pergunta) > ponte.LIMITE_PERGUNTA:
        return {"decisao": "INVALIDA", "mensagem": ponte.MSG_LONGA}
    r = ponte.buscar(pergunta, base)
    por_id = base["registros_por_id"]
    saida = {"decisao": r["decisao"]}
    if r["decisao"] == "INVALIDA":
        saida["mensagem"] = ponte.MSG_SEM_PALAVRA if pergunta.strip() else ponte.MSG_VAZIA
    elif r["decisao"] == "SEM_BASE":
        saida["mensagem"] = ponte.aviso_sem_base(base["temas"])
        saida["portal"] = ponte.GOV_BR
        saida["temas"] = list(base["temas"].values())
    elif r["decisao"] == "PEDIR_ESCOLHA":
        saida["candidatos"] = [{"id": c[0], "titulo": por_id[c[0]]["pergunta"]}
                               for c in r["candidatos"]]
    else:
        rid = r["candidatos"][0][0]
        reg = por_id[rid]
        link, aviso = ponte.fonte_e_aviso(reg, uf)
        saida.update({
            "id": rid, "titulo": reg["pergunta"], "passos": ponte.passos(reg),
            "atencao": aviso or None, "fonte": link,
            "verificado_em": ponte.formatar_data(reg["data_verificacao"]),
            "relacionados": [{"id": i, "titulo": por_id[i]["pergunta"]}
                             for i in ponte.relacionados(base, rid)],
            "total_orientacoes": len(base["registros"]),
            "aviso": ponte.NAO_OFICIAL,
        })
    return saida


# ---- Aplicativo web --------------------------------------------------------
def criar_app(base, token_bot, segredo_sessao, links, painel_url=""):
    """Monta o app FastAPI. Import tardio: só o modo --servidor precisa dele."""
    from fastapi import Cookie, FastAPI, Header, HTTPException, Request, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    # CORS restrito ao domínio do painel (spec §10.4).
    app.add_middleware(CORSMiddleware, allow_origins=[painel_url] if painel_url else [],
                       allow_methods=["POST", "GET"], allow_headers=["content-type"],
                       allow_credentials=True)
    limitador = LimitadorTaxa()

    @app.middleware("http")
    async def cabecalhos(request: Request, call_next):
        resp = await call_next(request)
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "SAMEORIGIN"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'self' https://web.telegram.org"
        return resp

    def usuario(initdata, cookie):
        """Autentica por initData (Mini App) ou cookie de sessão (navegador)."""
        uid = validar_init_data(initdata, token_bot) if initdata else None
        if uid is None and cookie:
            uid = verificar_sessao(cookie, segredo_sessao)
        if uid is None:
            raise HTTPException(status_code=401, detail="Faça login pelo bot.")
        return uid

    @app.get("/entrar")
    def entrar(t: str, response: Response):
        uid = links.consumir(t)
        if uid is None:
            raise HTTPException(status_code=401, detail="Link inválido ou vencido.")
        response.set_cookie("sessao", assinar_sessao(uid, segredo_sessao), httponly=True,
                            secure=True, samesite="strict", max_age=VALIDADE_SESSAO)
        return {"ok": True}

    @app.post("/api/perguntar")
    async def perguntar(request: Request, x_telegram_init_data: str = Header(default=""),
                        sessao: str = Cookie(default="")):
        uid = usuario(x_telegram_init_data, sessao)
        if not limitador.permitir(uid):
            raise HTTPException(status_code=429, detail="Muitas perguntas seguidas. Aguarde um instante.")
        try:
            corpo = await request.json()
        except ValueError:
            raise HTTPException(status_code=400, detail="Pedido inválido.")
        # A pergunta não é gravada nem logada (spec §10.5 e §13).
        return JSONResponse(resposta_estruturada(pergunta_do_corpo(corpo), base))

    return app
