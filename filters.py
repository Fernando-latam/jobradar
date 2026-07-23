"""
Filtros.

Três perguntas, nesta ordem:
  1. TÍTULO      — a vaga é da minha área?
  2. ELEGIBILIDADE — posso legalmente ser contratado?
  3. PAGAMENTO   — paga em moeda forte ou é folha local?

A ordem de precedência dentro do filtro geográfico importa muito.
Uma localização travada num país vence qualquer sinal positivo encontrado
no corpo do texto — porque "worldwide" aparece no texto institucional de
praticamente toda empresa e não significa nada sobre onde ela contrata.
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
def _location_is_us(loc):
    """Detecta localização travada nos EUA, inclusive abreviações."""
    for marker in config.US_LOCATION_MARKERS:
        if marker in loc:
            return True
    return False


def geo_verdict(job):
    """
    Retorna (status, motivo).
      "open"    -> posso ser contratado
      "maybe"   -> nada conclusivo, vale ler
      "blocked" -> exclusão explícita

    Precedência (do mais forte ao mais fraco):
      1. LOCALIZAÇÃO travada num país          -> blocked
         (a menos que o país seja o Brasil)
      2. Restrição explícita na descrição      -> blocked
      3. Lista LATAM sem o Brasil              -> blocked
      4. Brasil citado                         -> open
      5. LATAM aberto (sem lista de países)    -> open
      6. Frase inequívoca de contratação global-> open
      7. Nada conclusivo                       -> maybe
    """
    loc = _norm(job["location"])
    desc = _norm(job["description"])
    blob = f"{loc} {desc}"

    brazil_in_loc = any(t in loc for t in config.GEO_BRAZIL)
    brazil_in_blob = any(t in blob for t in config.GEO_BRAZIL)

    # ---- 1. Localização travada -------------------------------------------
    # Esta checagem vem PRIMEIRO. É a correção do bug em que uma vaga
    # "Remote - US" era liberada porque o texto continha "worldwide".
    if not brazil_in_loc:
        if _location_is_us(loc):
            return "blocked", f"localização US: {job['location']}"
        for country in config.GEO_COUNTRY_LOCK:
            if country in loc:
                return "blocked", f"localização restrita: {job['location']}"

    # ---- 2. Restrição explícita na descrição ------------------------------
    for term in config.GEO_NEGATIVE:
        if term in blob:
            return "blocked", f"restrição: '{term}'"

    # ---- 3. Lista LATAM sem o Brasil --------------------------------------
    latam_named = [c for c in config.LATAM_COUNTRIES if c in blob]
    if len(latam_named) >= 2 and not brazil_in_blob:
        return "blocked", f"lista LATAM sem Brasil ({', '.join(latam_named[:3])})"

    # ---- 4. Brasil citado --------------------------------------------------
    if brazil_in_blob:
        return "open", "menciona Brasil"

    # ---- 5. LATAM aberto ---------------------------------------------------
    for term in config.GEO_LATAM_OPEN:
        if term in loc:
            return "open", f"localização LATAM: {job['location']}"

    # ---- 6. Frase inequívoca de contratação global -------------------------
    for term in config.GEO_POSITIVE:
        if term in blob:
            return "open", f"contratação global: '{term}'"

    return "maybe", "sem sinal claro — verificar manualmente"


# --------------------------------------------------------------------------
# Filtro 3 — moeda / tipo de contratação
# --------------------------------------------------------------------------
def pay_verdict(job):
    """
    Retorna (status, motivo).
      "foreign" -> provável pagamento em moeda forte
      "local"   -> provável contratação local no Brasil (folha em reais)
      "unknown" -> não deu para determinar
    """
    loc = _norm(job["location"])
    desc = _norm(job["description"])
    blob = f"{loc} {desc}"

    # Sinais explícitos de contratação local
    for term in config.LOCAL_HIRE_SIGNALS:
        if term in blob:
            return "local", f"contratação local: '{term}'"

    # Cidade brasileira na localização, sem sinal de contrato internacional
    city_hit = next((c for c in config.BR_CITIES if c in loc), None)
    if city_hit:
        has_intl = any(s in blob for s in
                       ("employer of record", "independent contractor",
                        "usd", "b2b", "contractor agreement"))
        if not has_intl:
            return "local", f"vaga sediada em {job['location']}"

    # Sinais de moeda forte / contrato
    for term in config.STRONG_CURRENCY_SIGNALS:
        if term in blob:
            return "foreign", f"sinal de moeda/contrato: '{term}'"

    return "unknown", "moeda não identificada"


# --------------------------------------------------------------------------
# Pontuação heurística
# --------------------------------------------------------------------------
PROFILE_SIGNALS = {
    "articulate": 10, "storyline": 8, "articulate rise": 8, "scorm": 6,
    "instructional design": 10, "learning design": 10,
    "curriculum": 5, "elearning": 6, "e-learning": 6,
    "adult learning": 5, "learning experience": 6,
    "enablement": 8, "customer education": 9, "onboarding": 5,
    "change management": 7, "adoption": 4,
    "generative ai": 7, "artificial intelligence": 5,
    "chatgpt": 5, "synthesia": 6, "ai-assisted": 7,
    "lms": 6, "successfactors": 7, "cornerstone": 7, "degreed": 7,
    "power bi": 6, "learning analytics": 6, "dashboard": 3,
    "spanish": 8, "portuguese": 9, "multilingual": 7,
    "bilingual": 6, "localization": 7, "latam": 7,
    "camtasia": 5, "captivate": 4,
}

# "rise" sozinho dá falso positivo ("rise to the challenge"), então
# só conta quando acompanhado de contexto.
CONTEXT_SIGNALS = {
    "rise": ("articulate", "storyline", "elearning", "authoring"),
    "ai": ("tool", "assisted", "content", "generative", "leverage"),
}


def score(job):
    blob = _norm(job["title"] + " " + job["description"])
    hits, total = [], 0

    for sig, weight in PROFILE_SIGNALS.items():
        if sig in blob:
            total += weight
            hits.append(sig)

    for sig, needs in CONTEXT_SIGNALS.items():
        if re.search(rf"\b{re.escape(sig)}\b", blob):
            if any(n in blob for n in needs):
                total += 4
                hits.append(sig)

    t = _norm(job["title"])
    for sig in ("instructional design", "learning design", "enablement",
                "customer education", "learning experience"):
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

    priority, local, maybe, blocked = [], [], [], 0

    for j in jobs:
        geo, geo_reason = geo_verdict(j)
        j["geo_status"], j["geo_reason"] = geo, geo_reason
        pay, pay_reason = pay_verdict(j)
        j["pay_status"], j["pay_reason"] = pay, pay_reason
        j["score"], j["signals"] = score(j)

        if geo == "blocked":
            blocked += 1
        elif geo == "open" and pay == "local":
            local.append(j)
        elif geo == "open":
            priority.append(j)
        else:
            maybe.append(j)

    stats["prioridade"] = len(priority)
    stats["local"] = len(local)
    stats["talvez"] = len(maybe)
    stats["bloqueadas"] = blocked

    for bucket in (priority, local, maybe):
        bucket.sort(key=lambda x: x["score"], reverse=True)

    return priority, local, maybe, stats
