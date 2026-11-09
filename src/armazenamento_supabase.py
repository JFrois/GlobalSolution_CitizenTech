"""Armazenamento no Supabase (Postgres via API REST). Só no modo --servidor.

Mesmos métodos de `ArmazenamentoSQLite`, para o resto do código não notar a troca.
Usa só a biblioteca padrão (urllib), sem instalar nada. Os dados binários (salt,
verificador, nome e conteúdo cifrados do cofre) vão em colunas de texto em base64.

Só liga quando SUPABASE_URL e uma chave SECRETA estão no .env; se algo falhar na
subida, `armazenamento.criar` volta sozinho para o SQLite. O schema fica em
deploy/supabase_schema.sql (rode uma vez no SQL Editor do Supabase).

Privacidade (spec §13): toda consulta é filtrada por user_id e o schema liga RLS sem
políticas, então a chave pública (publishable/anon) não lê nada.
"""
from __future__ import annotations

import base64
import json
import re
import urllib.error
import urllib.parse
import urllib.request

from armazenamento import UFS

TEMPO_LIMITE_S = 10
_DASHBOARD = re.compile(r"https://supabase\.com/dashboard/project/([a-z0-9]+)")
_PROJETO = re.compile(r"https://[a-z0-9]+\.supabase\.co")


class ErroSupabase(Exception):
    """Falha ao falar com o Supabase. A mensagem não leva dados do usuário."""


def normalizar_url(url):
    """Aceita a URL da API ou a do dashboard (que tem o id do projeto) e devolve a da API."""
    url = (url or "").strip().rstrip("/")
    m = _DASHBOARD.match(url)
    if m:
        return "https://%s.supabase.co" % m.group(1)
    return url if _PROJETO.fullmatch(url) else ""


def chave_e_secreta(chave):
    """True só para chave que contorna o RLS (secret ou service_role). Publishable/anon, não."""
    if chave.startswith("sb_secret_"):
        return True
    if chave.startswith("sb_publishable_"):
        return False
    partes = chave.split(".")
    if len(partes) == 3:  # chave antiga em JWT: o papel vem no meio
        try:
            meio = partes[1] + "=" * (-len(partes[1]) % 4)
            return json.loads(base64.urlsafe_b64decode(meio)).get("role") == "service_role"
        except (ValueError, UnicodeDecodeError):
            return False
    return False


def _b64(dado):
    return base64.b64encode(bytes(dado)).decode("ascii")


def _bin(texto):
    return base64.b64decode(texto) if texto is not None else None


class ArmazenamentoSupabase:
    def __init__(self, url, chave, tempo_limite=TEMPO_LIMITE_S):
        self._base = url.rstrip("/") + "/rest/v1/"
        self._chave = chave
        self._tempo = tempo_limite

    # --- HTTP ---

    def _req(self, metodo, tabela, filtros=(), corpo=None, prefer=None):
        url = self._base + tabela
        if filtros:
            url += "?" + urllib.parse.urlencode(list(filtros))
        cab = {"apikey": self._chave, "Authorization": "Bearer " + self._chave,
               "Content-Type": "application/json"}
        if prefer:
            cab["Prefer"] = prefer
        dados = None if corpo is None else json.dumps(corpo).encode("utf-8")
        pedido = urllib.request.Request(url, data=dados, headers=cab, method=metodo)
        try:
            with urllib.request.urlopen(pedido, timeout=self._tempo) as r:
                texto = r.read().decode("utf-8")
        except urllib.error.HTTPError as erro:
            raise ErroSupabase("Supabase respondeu %d em %s" % (erro.code, tabela)) from None
        except (urllib.error.URLError, OSError, ValueError) as erro:
            raise ErroSupabase("Supabase inacessível (%s)" % type(erro).__name__) from None
        return json.loads(texto) if texto.strip() else []

    def _ler(self, tabela, filtros):
        return self._req("GET", tabela, filtros)

    def _upsert(self, tabela, linha, chave):
        self._req("POST", tabela, [("on_conflict", chave)], linha,
                  "resolution=merge-duplicates,return=minimal")

    def verificar(self):
        """Confere se o schema existe e a chave serve. Levanta ErroSupabase se não."""
        if not isinstance(self._ler("usuarios", [("select", "user_id"), ("limit", "1")]), list):
            raise ErroSupabase("resposta inesperada do Supabase")

    # --- usuários ---

    def definir_uf(self, user_id, uf):
        uf = str(uf).upper()
        if uf not in UFS:
            raise ValueError("UF inválida")
        self._upsert("usuarios", {"user_id": int(user_id), "uf": uf}, "user_id")

    def obter_uf(self, user_id):
        l = self._ler("usuarios", [("user_id", "eq.%d" % int(user_id)), ("select", "uf")])
        return l[0]["uf"] if l else None

    def definir_temas_briefing(self, user_id, temas):
        self._upsert("usuarios", {"user_id": int(user_id), "temas_briefing": json.dumps(list(temas))}, "user_id")

    def obter_temas_briefing(self, user_id):
        l = self._ler("usuarios", [("user_id", "eq.%d" % int(user_id)), ("select", "temas_briefing")])
        return json.loads(l[0]["temas_briefing"]) if l and l[0]["temas_briefing"] else []

    # --- cofre (tudo já cifrado; filtrado por user_id) ---

    def salvar_config_cofre(self, user_id, salt, verificador, iteracoes):
        self._upsert("cofre_config", {"user_id": int(user_id), "salt": _b64(salt),
                                      "verificador": _b64(verificador), "iteracoes": int(iteracoes)}, "user_id")

    def obter_config_cofre(self, user_id):
        l = self._ler("cofre_config", [("user_id", "eq.%d" % int(user_id))])
        if not l:
            return None
        return {"salt": _bin(l[0]["salt"]), "verificador": _bin(l[0]["verificador"]),
                "iteracoes": int(l[0]["iteracoes"])}

    def salvar_doc(self, user_id, nome_cifrado, conteudo_cifrado):
        l = self._req("POST", "cofre_docs", [("select", "id")],
                      {"user_id": int(user_id), "nome": _b64(nome_cifrado), "conteudo": _b64(conteudo_cifrado)},
                      "return=representation")
        return int(l[0]["id"])

    def listar_docs(self, user_id):
        l = self._ler("cofre_docs", [("user_id", "eq.%d" % int(user_id)), ("select", "id,nome"), ("order", "id.asc")])
        return [(int(x["id"]), _bin(x["nome"])) for x in l]

    def obter_doc(self, user_id, doc_id):
        l = self._ler("cofre_docs", [("id", "eq.%d" % int(doc_id)), ("user_id", "eq.%d" % int(user_id)),
                                     ("select", "nome,conteudo")])
        return (_bin(l[0]["nome"]), _bin(l[0]["conteudo"])) if l else None

    def apagar_doc(self, user_id, doc_id):
        l = self._req("DELETE", "cofre_docs", [("id", "eq.%d" % int(doc_id)), ("user_id", "eq.%d" % int(user_id)),
                                               ("select", "id")], prefer="return=representation")
        return len(l) > 0

    # --- tarefas e lembretes ---

    def criar_tarefa(self, user_id, titulo, quando=None):
        l = self._req("POST", "tarefas", [("select", "id")],
                      {"user_id": int(user_id), "titulo": titulo,
                       "quando": None if quando is None else int(quando)}, "return=representation")
        return int(l[0]["id"])

    def listar_tarefas(self, user_id):
        l = self._ler("tarefas", [("user_id", "eq.%d" % int(user_id)), ("concluida", "eq.0"),
                                  ("select", "id,titulo,quando"), ("order", "quando.asc.nullslast,id.asc")])
        return [(int(x["id"]), x["titulo"], x["quando"]) for x in l]

    def listar_tarefas_avisadas(self, user_id):
        l = self._ler("tarefas", [("user_id", "eq.%d" % int(user_id)), ("concluida", "eq.0"),
                                  ("avisada", "eq.1"), ("select", "id")])
        return {int(x["id"]) for x in l}

    def concluir_tarefa(self, user_id, tarefa_id):
        l = self._req("PATCH", "tarefas", [("id", "eq.%d" % int(tarefa_id)), ("user_id", "eq.%d" % int(user_id)),
                                           ("select", "id")], {"concluida": 1}, "return=representation")
        return len(l) > 0

    def tarefas_a_avisar(self, agora):
        l = self._ler("tarefas", [("concluida", "eq.0"), ("avisada", "eq.0"), ("quando", "not.is.null"),
                                  ("quando", "lte.%d" % int(agora)), ("select", "id,user_id,titulo,quando")])
        return [(int(x["id"]), int(x["user_id"]), x["titulo"], int(x["quando"])) for x in l]

    def marcar_avisada(self, tarefa_id):
        self._req("PATCH", "tarefas", [("id", "eq.%d" % int(tarefa_id))], {"avisada": 1}, "return=minimal")

    def tarefas_do_dia(self, user_id, inicio, fim):
        l = self._ler("tarefas", [("user_id", "eq.%d" % int(user_id)), ("concluida", "eq.0"),
                                  ("quando", "gte.%d" % int(inicio)), ("quando", "lt.%d" % int(fim)),
                                  ("select", "id,titulo,quando"), ("order", "quando.asc")])
        return [(int(x["id"]), x["titulo"], int(x["quando"])) for x in l]

    # --- resumo da manhã ---

    def definir_hora_briefing(self, user_id, hora):
        self._upsert("briefing_config", {"user_id": int(user_id), "hora": hora}, "user_id")

    def obter_hora_briefing(self, user_id):
        l = self._ler("briefing_config", [("user_id", "eq.%d" % int(user_id)), ("select", "hora")])
        return l[0]["hora"] if l else None

    def briefings_a_enviar(self, hoje, hora_atual):
        l = self._ler("briefing_config", [("hora", "lte." + hora_atual),
                                          ("or", "(ultimo_envio.is.null,ultimo_envio.neq.%s)" % hoje),
                                          ("select", "user_id,hora")])
        return [(int(x["user_id"]), x["hora"]) for x in l]

    def marcar_briefing_enviado(self, user_id, hoje):
        self._req("PATCH", "briefing_config", [("user_id", "eq.%d" % int(user_id))],
                  {"ultimo_envio": hoje}, "return=minimal")

    # --- consentimento do envio ao Gemini ---

    def registrar_consentimento(self, user_id):
        self._upsert("consentimento_gemini", {"user_id": int(user_id)}, "user_id")

    def tem_consentimento(self, user_id):
        return bool(self._ler("consentimento_gemini", [("user_id", "eq.%d" % int(user_id)), ("select", "user_id")]))

    # --- autodestruição de mensagens ---

    def agendar_exclusao(self, user_id, chat_id, message_id, apagar_em):
        self._req("POST", "exclusoes", corpo={"user_id": int(user_id), "chat_id": int(chat_id),
                                              "message_id": int(message_id), "apagar_em": int(apagar_em)},
                  prefer="return=minimal")

    def exclusoes_vencidas(self, agora):
        l = self._ler("exclusoes", [("apagar_em", "lte.%d" % int(agora)), ("select", "id,chat_id,message_id")])
        return [(int(x["id"]), int(x["chat_id"]), int(x["message_id"])) for x in l]

    def remover_exclusao(self, exclusao_id):
        self._req("DELETE", "exclusoes", [("id", "eq.%d" % int(exclusao_id))], prefer="return=minimal")

    def apagar_usuario(self, user_id):
        """Remove tudo do usuário (/apagar_meus_dados), inclusive o cofre."""
        for tabela in ("cofre_docs", "cofre_config", "tarefas", "exclusoes", "briefing_config",
                       "consentimento_gemini", "usuarios"):
            self._req("DELETE", tabela, [("user_id", "eq.%d" % int(user_id))], prefer="return=minimal")
