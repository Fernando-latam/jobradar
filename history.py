"""
Histórico de vagas já enviadas.

Evita que a mesma vaga apareça no email todo dia. Guardado em JSON no
próprio repositório, então persiste entre execuções do GitHub Actions.
"""
import hashlib
import json
import os
from datetime import datetime, timedelta

ARQUIVO = "seen_jobs.json"
VALIDADE_DIAS = 45


def _chave(job):
    base = f"{job['title']}|{job['company']}".lower()
    return hashlib.md5(base.encode()).hexdigest()[:16]


def carregar():
    if not os.path.exists(ARQUIVO):
        return {}
    try:
        with open(ARQUIVO, encoding="utf-8") as f:
            dados = json.load(f)
    except Exception:
        return {}

    # descarta entradas antigas
    limite = (datetime.now() - timedelta(days=VALIDADE_DIAS)).isoformat()
    return {k: v for k, v in dados.items() if v >= limite}


def salvar(historico):
    try:
        with open(ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(historico, f, indent=1)
    except Exception as e:
        print(f"  aviso: não foi possível salvar o histórico ({e})")


def separar_novas(jobs, historico):
    """Devolve (novas, ja_vistas)."""
    novas, vistas = [], []
    for j in jobs:
        if _chave(j) in historico:
            vistas.append(j)
        else:
            novas.append(j)
    return novas, vistas


def registrar(jobs, historico):
    agora = datetime.now().isoformat()
    for j in jobs:
        historico[_chave(j)] = agora
    return historico
