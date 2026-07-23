"""
Avaliação de vagas com a API da Anthropic.

O Claude lê a descrição completa de cada vaga e a compara com o perfil,
devolvendo uma nota, um veredicto de elegibilidade e a razão em português.
Substitui a heurística de palavras-chave por leitura real do texto.

Se a chave de API não estiver configurada, o módulo se desativa sozinho e
o pipeline segue com o score heurístico.
"""
import json
import os
import re
import time
import urllib.error
import urllib.request

from profile import PROFILE

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5-20251001"
MAX_JOBS = 40          # teto de vagas avaliadas por execução
BATCH_SIZE = 5         # vagas por chamada
TIMEOUT = 90

SYSTEM = f"""Você avalia vagas de emprego para um profissional específico.

{PROFILE}

Para cada vaga, responda com objetividade e ceticismo. O candidato já perdeu
meses se candidatando a vagas que nunca poderiam contratá-lo — seu trabalho é
evitar que isso continue.

Critérios, em ordem de importância:

1. ELEGIBILIDADE. Ele pode ser contratado? Vaga que exige residência ou
   autorização de trabalho em país específico é inviável, mesmo com fit
   técnico perfeito. Na dúvida, classifique como "incerto" — não invente
   otimismo. Quando o texto não diz nada sobre localização, isso é "incerto",
   não "elegível".

2. IDIOMA. Exige idioma além de PT/EN/ES? Se sim, inviável.

3. FIT REAL. O trabalho descrito é o que ele faz? Preste atenção à diferença
   entre enablement de cliente/parceiro (fit) e enablement de vendas (não é
   o perfil dele). Cargo de gestão de vendas, engenharia ou clínico não serve.

4. LACUNAS. O que a vaga pede que ele não tem? Seja específico.

Responda APENAS com um array JSON válido, sem texto antes ou depois, sem
blocos de código markdown. Um objeto por vaga, na mesma ordem recebida:

[{{"id": 0,
   "nota": 0-100,
   "elegibilidade": "elegivel" | "incerto" | "inviavel",
   "motivo_elegibilidade": "uma frase curta em português",
   "fit": "uma ou duas frases em português sobre por que serve ou não",
   "lacunas": ["item", "item"],
   "acao": "uma frase: o que fazer com essa vaga"}}]

Notas: 80+ só para fit excelente E elegibilidade plausível. 60-79 bom fit com
alguma incerteza. 40-59 fit parcial. Abaixo de 40, não vale o tempo dele."""


def enabled():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _call(payload):
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "content-type": "application/json",
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read())


def _parse(text):
    """Extrai o array JSON da resposta, tolerando cercas de markdown."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("sem array JSON na resposta")
    return json.loads(text[start:end + 1])


def _batch(jobs, offset):
    linhas = []
    for i, j in enumerate(jobs):
        desc = j["description"][:2200]
        linhas.append(
            f"### VAGA {i}\n"
            f"Título: {j['title']}\n"
            f"Empresa: {j['company']}\n"
            f"Localização: {j['location'] or 'não informada'}\n"
            f"Descrição: {desc}\n")

    payload = {
        "model": MODEL,
        "max_tokens": 2000,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": "\n".join(linhas)}],
    }

    data = _call(payload)
    texto = "".join(b.get("text", "") for b in data.get("content", [])
                    if b.get("type") == "text")
    return _parse(texto)


def evaluate(jobs):
    """
    Avalia as vagas e devolve a mesma lista com os campos de análise
    preenchidos. Falhas parciais não interrompem: a vaga fica sem análise
    e mantém o score heurístico.
    """
    if not enabled():
        print("  ANTHROPIC_API_KEY não configurada — usando score heurístico")
        return jobs, False

    alvo = jobs[:MAX_JOBS]
    print(f"\nAvaliando {len(alvo)} vagas com Claude...")

    ok, erros = 0, 0
    for inicio in range(0, len(alvo), BATCH_SIZE):
        lote = alvo[inicio:inicio + BATCH_SIZE]
        try:
            resultados = _batch(lote, inicio)
            for r in resultados:
                idx = r.get("id")
                if idx is None or idx >= len(lote):
                    continue
                j = lote[idx]
                j["ai_nota"] = int(r.get("nota", 0))
                j["ai_elegibilidade"] = r.get("elegibilidade", "incerto")
                j["ai_motivo_eleg"] = r.get("motivo_elegibilidade", "")
                j["ai_fit"] = r.get("fit", "")
                j["ai_lacunas"] = r.get("lacunas", []) or []
                j["ai_acao"] = r.get("acao", "")
                ok += 1
            print(f"  lote {inicio // BATCH_SIZE + 1}: {len(resultados)} avaliadas")
        except urllib.error.HTTPError as e:
            corpo = e.read().decode()[:180]
            print(f"  lote {inicio // BATCH_SIZE + 1} FALHOU: HTTP {e.code} {corpo}")
            erros += 1
        except Exception as e:
            print(f"  lote {inicio // BATCH_SIZE + 1} FALHOU: {repr(e)[:120]}")
            erros += 1
        time.sleep(1.2)

    print(f"  total avaliado: {ok} vagas ({erros} lotes com erro)")
    return jobs, ok > 0


def rank(jobs):
    """Ordena pela nota do Claude quando existir, senão pelo score heurístico."""
    return sorted(jobs,
                  key=lambda j: (j.get("ai_nota", -1), j.get("score", 0)),
                  reverse=True)
