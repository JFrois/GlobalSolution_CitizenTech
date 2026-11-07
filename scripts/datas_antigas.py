"""Lista os registros da base com data de verificação antiga (> 90 dias).

Uso: python scripts/datas_antigas.py [--dias 90] [--base caminho.json]
Só biblioteca padrão. Ajuda a equipe a reverificar as fontes (spec §7.1).
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import base  # noqa: E402


def registros_antigos(registros, dias=90, hoje=None):
    """Devolve [(id, data, idade_em_dias)] dos registros vencidos ou sem data."""
    hoje = date.fromisoformat(hoje) if hoje else date.today()
    achados = []
    for reg in registros:
        texto = str(reg.get("data_verificacao", "")).strip()
        try:
            idade = (hoje - date.fromisoformat(texto)).days
        except ValueError:
            achados.append((reg["id"], texto or "sem data", None))
            continue
        if idade > dias:
            achados.append((reg["id"], texto, idade))
    return achados


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dias", type=int, default=90)
    parser.add_argument("--base", default=None)
    args = parser.parse_args()
    try:
        dados = base.carregar_base(args.base)
    except base.ErroBase as erro:
        print("Não consegui abrir a base: " + "; ".join(erro.problemas))
        return 1
    achados = registros_antigos(dados["registros"], args.dias)
    if not achados:
        print("Todos os registros foram verificados nos últimos %d dias." % args.dias)
    for rid, data, idade in achados:
        extra = "" if idade is None else " (%d dias)" % idade
        print("%s  verificado em: %s%s" % (rid, data, extra))
    return 0


if __name__ == "__main__":
    sys.exit(main())
