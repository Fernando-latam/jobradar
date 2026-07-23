#!/usr/bin/env python3
"""
JobRadar — ponto de entrada.
Uso:  python run.py
"""
import sys
import traceback

import config
import filters
import report
from collectors import sources


def main():
    print("=" * 60)
    print("JobRadar")
    print("=" * 60)

    jobs = sources.collect_all()

    if not jobs:
        print("\nNenhuma vaga coletada. Veja o diagnóstico acima:")
        print("as fontes podem estar temporariamente indisponíveis,")
        print("ou o ambiente pode estar bloqueando o acesso à internet.")
        report.build([], [], [], {"bruto": 0, "apos_dedup": 0,
                                  "match_titulo": 0, "prioridade": 0,
                                  "local": 0, "talvez": 0, "bloqueadas": 0},
                     sources.DIAGNOSTICS)
        return 1

    priority, local, maybe, stats = filters.run(jobs)

    print("\n" + "-" * 60)
    print(f"  Coletadas .......... {stats['bruto']}")
    print(f"  Após deduplicar .... {stats['apos_dedup']}")
    print(f"  Da sua área ........ {stats['match_titulo']}")
    print(f"  PRIORIDADE ......... {stats['prioridade']}")
    print(f"  Local BR ........... {stats['local']}")
    print(f"  Talvez ............. {stats['talvez']}")
    print(f"  Bloqueadas ......... {stats['bloqueadas']}")
    print("-" * 60)

    path = report.build(priority, local, maybe, stats, sources.DIAGNOSTICS)
    print(f"\nRelatório gerado: {path}\n")

    for j in priority[:5]:
        print(f"  [{j['score']:>3}] {j['title'][:55]:<55} {j['company'][:20]}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
