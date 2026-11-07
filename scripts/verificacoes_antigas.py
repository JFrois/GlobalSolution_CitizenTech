"""Lista os registros cuja data de verificação passou de 90 dias (spec 7.1, A11).

Uso:
    python scripts/verificacoes_antigas.py [--dias 90] [--hoje AAAA-MM-DD] [--base caminho]

Registros sem data também aparecem, porque ainda não foram verificados.
Sai com código 1 se houver algum registro na lista (útil para automação).
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import base  # noqa: E402

LIMITE_PADRAO = 90


def registros_antigos(dados: dict, hoje: date, dias: int = LIMITE_PADRAO) -> list:
    """[(id, motivo)] dos registros sem data ou verificados há mais de 'dias' dias."""
    lista = []
    for reg in dados["registros"]:
        texto = reg["data_verificacao"]
        if not texto:
            lista.append((reg["id"], "sem data de verificação"))
            continue
        verificado = date.fromisoformat(texto)
        if hoje - verificado > timedelta(days=dias):
            lista.append((reg["id"], "verificado em %s (%d dias atrás)"
                          % (texto, (hoje - verificado).days)))
    return lista


def principal(argv=None) -> int:
    p = argparse.ArgumentParser(description="Lista registros com verificação antiga")
    p.add_argument("--dias", type=int, default=LIMITE_PADRAO)
    p.add_argument("--hoje", default=None, help="data de referência AAAA-MM-DD (testes)")
    p.add_argument("--base", default=None)
    args = p.parse_args(argv)
    try:
        dados = base.carregar_base(args.base)
        hoje = date.fromisoformat(args.hoje) if args.hoje else date.today()
    except (base.ErroBase, ValueError) as erro:
        print("Não consegui abrir a base de orientações: %s. Avise a equipe." % erro)
        return 1
    lista = registros_antigos(dados, hoje, args.dias)
    for rid, motivo in lista:
        print("%s: %s" % (rid, motivo))
    print("%d registro(s) para reverificar." % len(lista))
    return 1 if lista else 0


if __name__ == "__main__":
    sys.exit(principal())
