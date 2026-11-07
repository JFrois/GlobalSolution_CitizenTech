"""Testa a chave do Gemini do .env e mostra quais modelos ela enxerga (não imprime a chave).

Uso (com o ambiente do servidor ativo, onde google-genai está instalado):
    python scripts/testar_gemini.py

Faz duas coisas:
  1. lista os modelos que aceitam generateContent para essa chave;
  2. chama cada modelo da cascata do bot (src/roteador.py) com uma pergunta trivial e
     mostra o tempo e o resultado (ok, 404 = nome não existe, 429 = cota, timeout...).
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import roteador  # noqa: E402
import servidor  # noqa: E402


def main() -> int:
    config = servidor.ler_env()
    chave = config.get("GEMINI_API_KEY")
    if not chave:
        print("Falta GEMINI_API_KEY no .env.")
        return 1
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Falta o google-genai. Ative o ambiente (.venv) e rode: pip install -r requirements.txt")
        return 1

    cliente = genai.Client(api_key=chave, http_options=types.HttpOptions(timeout=15000))
    print("Modelos que a chave enxerga (generateContent):")
    try:
        nomes = []
        for m in cliente.models.list():
            acoes = getattr(m, "supported_actions", None) or []
            if "generateContent" in acoes and "gemini" in (m.name or ""):
                nomes.append((m.name or "").replace("models/", ""))
        for nome in sorted(nomes):
            print("  " + nome)
        if not nomes:
            print("  (nenhum; confira a chave e o faturamento do projeto)")
    except Exception as erro:
        print("  não consegui listar (%s %s)" % (type(erro).__name__, getattr(erro, "code", "")))

    modelo_env = config.get("GEMINI_MODELO")
    cascata = ([modelo_env] if modelo_env else []) + [m for m in roteador.MODELOS_GEMINI if m != modelo_env]
    print("\nTeste de cada modelo da cascata do bot:")
    for modelo in cascata:
        inicio = time.time()
        try:
            r = cliente.models.generate_content(model=modelo, contents="Responda só com a palavra: ok")
            print("  %-28s OK em %.1fs (%s)" % (modelo, time.time() - inicio, (r.text or "").strip()[:20]))
        except Exception as erro:
            print("  %-28s FALHOU em %.1fs: %s %s" % (modelo, time.time() - inicio,
                                                      type(erro).__name__, getattr(erro, "code", "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
