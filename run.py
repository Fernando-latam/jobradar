#!/usr/bin/env python3
"""
JobRadar — ponto de entrada.

Fluxo:
  coletar -> filtrar -> remover já vistas -> avaliar com Claude
          -> relatório HTML -> email
"""
import os
import sys
import traceback

import ai_scoring
import config
import filters
import history
import mailer
import report
from collectors import sources

PAGES_URL = os.environ.get("PAGES_URL", "")


def main():
    print("=" * 62)
    print("JobRadar")
    print("=" * 62)

    jobs = sources.collect_all()

    if not jobs:
        print("\nNenhuma vaga coletada. Veja o diagnóstico acima.")
        report.build([], [], [], {"bruto": 0, "apos_dedup": 0,
                                  "match_titulo": 0, "prioridade": 0,
                                  "local": 0, "talvez": 0, "bloqueadas": 0},
                     sources.DIAGNOSTICS)
        return 1

    priority, local, maybe, stats = filters.run(jobs)

    print("\n" + "-" * 62)
    print(f"  Coletadas .......... {stats['bruto']}")
    print(f"  Após deduplicar .... {stats['apos_dedup']}")
    print(f"  Da sua área ........ {stats['match_titulo']}")
    print(f"  Prioridade ......... {stats['prioridade']}")
    print(f"  Local BR ........... {stats['local']}")
    print(f"  Talvez ............. {stats['talvez']}")
    print(f"  Bloqueadas ......... {stats['bloqueadas']}")
    print("-" * 62)

    # ---- histórico: só o que é novo vai para a avaliação e o email --------
    historico = history.carregar()
    candidatas = priority + maybe
    novas, ja_vistas = history.separar_novas(candidatas, historico)
    print(f"\n  Novas desde a última execução: {len(novas)} "
          f"({len(ja_vistas)} já enviadas antes)")

    # ---- avaliação com Claude ---------------------------------------------
    ordenadas = sorted(novas, key=lambda j: j.get("score", 0), reverse=True)
    ordenadas, usou_ia = ai_scoring.evaluate(ordenadas)

    if usou_ia:
        ordenadas = ai_scoring.rank(ordenadas)
        # descarta o que o Claude classificou como inviável
        viaveis = [j for j in ordenadas
                   if j.get("ai_elegibilidade") != "inviavel"]
        descartadas = len(ordenadas) - len(viaveis)
        if descartadas:
            print(f"  Claude descartou {descartadas} como inviáveis")
        destaques = [j for j in viaveis if j.get("ai_nota", 0) >= 55][:8]
        outras = [j for j in viaveis if j not in destaques]
    else:
        destaques = ordenadas[:8]
        outras = ordenadas[8:]

    # ---- relatório HTML ----------------------------------------------------
    path = report.build(priority, local, maybe, stats, sources.DIAGNOSTICS)
    print(f"\n  Relatório: {path}")

    # ---- email -------------------------------------------------------------
    print("\nEnviando email...")
    mailer.enviar(destaques, outras, stats, PAGES_URL)

    # ---- registrar o que foi enviado ---------------------------------------
    historico = history.registrar(destaques + outras, historico)
    history.salvar(historico)

    print("\nTop do dia:")
    for j in destaques[:5]:
        nota = j.get("ai_nota", j.get("score", 0))
        print(f"  [{nota:>3}] {j['title'][:52]:<52} {j['company'][:18]}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
