"""
Filtros. A ordem importa:
  1. título  -> a vaga é da minha área?
  2. geografia -> eu posso legalmente pegar essa vaga?
O filtro geográfico é o que salva seu tempo — é ele que remove as vagas
"remote" que na prática são US-only.
"""
import re
import config


def _norm(s):
    return re.sub(r"\s+", " ", (s or "").lower())


# --------------------------------------------------------------------------
# Deduplicação
# --------------------------------------------------------------------------
def deduplicate(jobs):
    seen, out = set(), []
    for j in jobs:
        key = (_norm(j["title"])[:70], _norm(j["company"])[:40])
        if key in seen:
            continue
        seen.add(key)
        out.append(j)
    return out


# --------------------------------------------------------------------------
# Filtro 1 — título
# --------------------------------------------------------------------------
def match_title(job):
    t = _norm(job["title"])
    if not t:
        return False
    for bad in config.TITLE_EXCLUDE:
        if bad in t:
            return False
    return any(k in t for k in config.TITLE_KEYWORDS)


# --------------------------------------------------------------------------
# Filtro 2 — elegibilidade geográfica
# --------------------------------------------------------------------------
def geo_verdict(job):
    """
    Retorna (status, motivo).
      status: "open"    -> aceita Brasil / global
              "maybe"   -> nada conclusivo, vale ler
              "blocked" -> exclusão explícita

    Ordem de precedência (do mais forte para o mais fraco):
      1. Brasil citado explicitamente          -> open
      2. Restrição explícita na descrição      -> blocked
      3. País único travado na localização     -> blocked
         (exceto se houver menção a Brasil)
      4. Lista LATAM que NÃO inclui Brasil     -> blocked
      5. Sinal global/aberto                   -> open
      6. Nada conclusivo                       -> maybe
    """
    loc = _norm(job["location"])
    desc = _norm(job["description"])
    blob = f"{loc} {desc}"

    # ---- 1. Brasil explícito vence tudo -----------------------------------
    if "brazil" in blob or "brasil" in blob:
        return "open", "menciona Brasil"

    # ---- 2. Restrição explícita na descrição ------------------------------
    for term in config.GEO_NEGATIVE:
        if term in blob:
            return "blocked", f"restrição: '{term}'"

    # ---- 3. Localização travada num país específico -----------------------
    # Isso vem ANTES dos sinais positivos: "independent contractor" numa
    # vaga de Costa Rica não te torna elegível.
    for country in config.GEO_COUNTRY_LOCK:
        if country in loc:
            return "blocked", f"localização restrita: {job['location']}"

    # ---- 4. Lista de países LATAM sem o Brasil ----------------------------
    # Ex.: "anywhere in Mexico, Guatemala, Colombia or Ecuador"
    latam_named = [c for c in config.LATAM_COUNTRIES if c in blob]
    if len(latam_named) >= 2:
        return "blocked", (f"lista LATAM sem Brasil "
                           f"({', '.join(latam_named[:3])})")

    # ---- 5. Sinais de abertura --------------------------------------------
    for term in config.GEO_POSITIVE:
        if term in blob:
            return "open", f"sinal aberto: '{term}'"

    return "maybe", "sem sinal claro — verificar manualmente"


# --------------------------------------------------------------------------
# Pontuação heurística (sem IA — a Fase 2 substitui por Claude)
# --------------------------------------------------------------------------
PROFILE_SIGNALS = {
    # sinal: peso
    "articulate": 10, "rise": 6, "storyline": 8, "scorm": 6,
    "instructional design": 10, "learning design": 10,
    "curriculum": 5, "elearning": 6, "e-learning": 6,
    "adult learning": 5, "learning experience": 6,
    "enablement": 8, "customer education": 8, "onboarding": 5,
    "change management": 7, "adoption": 4,
    "ai": 6, "artificial intelligence": 6, "generative": 6,
    "chatgpt": 5, "claude": 5, "synthesia": 6,
    "lms": 6, "successfactors": 7, "cornerstone": 7, "degreed": 7,
    "power bi": 6, "analytics": 4, "dashboard": 3,
    "spanish": 8, "portuguese": 9, "multilingual": 7,
    "bilingual": 6, "localization": 7, "latam": 9,
    "camtasia": 5, "contractor": 5, "b2b": 3,
}


def score(job):
    blob = _norm(job["title"] + " " + job["description"])
    hits, total = [], 0
    for sig, weight in PROFILE_SIGNALS.items():
        if sig in blob:
            total += weight
            hits.append(sig)
    # bônus quando o sinal está no próprio título
    t = _norm(job["title"])
    for sig in ("instructional design", "learning design", "enablement",
                "customer education"):
        if sig in t:
            total += 12
    return min(total, 100), hits


# --------------------------------------------------------------------------
# Pipeline
# --------------------------------------------------------------------------
def run(jobs):
    stats = {"bruto": len(jobs)}

    jobs = deduplicate(jobs)
    stats["apos_dedup"] = len(jobs)

    jobs = [j for j in jobs if match_title(j)]
    stats["match_titulo"] = len(jobs)

    open_jobs, maybe_jobs, blocked = [], [], 0
    for j in jobs:
        status, reason = geo_verdict(j)
        j["geo_status"] = status
        j["geo_reason"] = reason
        j["score"], j["signals"] = score(j)
        if status == "open":
            open_jobs.append(j)
        elif status == "maybe":
            maybe_jobs.append(j)
        else:
            blocked += 1

    stats["elegiveis"] = len(open_jobs)
    stats["talvez"] = len(maybe_jobs)
    stats["bloqueadas"] = blocked

    open_jobs.sort(key=lambda x: x["score"], reverse=True)
    maybe_jobs.sort(key=lambda x: x["score"], reverse=True)

    return open_jobs, maybe_jobs, stats
