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
    """
    Detecta localização travada nos EUA.
    Estados de 2 letras só contam no fim da string ("Austin, TX"), senão
    ", co" bloquearia Colombia e ", ma" bloquearia Malaysia.
    """
    for marker in config.US_LOCATION_MARKERS:
        if marker in loc:
            return True
    # "cidade, XX" ou "cidade, XX (remote)"
    m = re.search(r",\s*([a-z]{2})\b\s*(\(.*\))?\s*$", loc)
    if m and m.group(1) in config.US_STATE_SUFFIXES:
        return True
    return False


def language_blocked(job):
    """
    Retorna (True, motivo) se a vaga exige idioma que você não domina.
    Você fala Português, Inglês e Espanhol — o resto bloqueia.
    """
    if not getattr(config, "BLOCK_BY_LANGUAGE", True):
        return False, ""

    blob = _norm(job["title"] + " " + job["description"])
    for term in config.LANGUAGE_BLOCK:
        if term in blob:
            idioma = term.split()[-1] if " " in term else term
            return True, f"exige idioma: {term}"

    # Título escrito em idioma estrangeiro = vaga local não-anglófona
    t = _norm(job["title"])
    for marker in config.FOREIGN_TITLE_MARKERS:
        if marker in t:
            return True, f"vaga em idioma estrangeiro ('{marker.strip()}')"

    return False, ""


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

    # ---- 0. Idioma --------------------------------------------------------
    lang_bad, lang_reason = language_blocked(job)
    if lang_bad:
        return "blocked", lang_reason

    # ---- 0b. Localização declaradamente aberta -----------------------------
    # "Anywhere in the World", "Remote - Worldwide": a empresa declarou no
    # campo de localização que a vaga não tem restrição. Evidência forte,
    # avaliada antes de qualquer outra coisa.
    for term in getattr(config, "GEO_POSITIVE_LOCATION_ONLY", []):
        if term in loc:
            return "open", f"localização aberta: {job['location']}"

    # ---- 1. Localização travada -------------------------------------------
    country_review = None
    if not brazil_in_loc:
        for country in config.GEO_COUNTRY_LOCK:
            if country in loc:
                return "blocked", f"localização restrita: {job['location']}"
        for country in config.GEO_COUNTRY_REVIEW:
            if country in loc:
                country_review = country
                break
        if not country_review and _location_is_us(loc):
            country_review = "estados unidos"

    # ---- 2. Restrição explícita na descrição ------------------------------
    for term in config.GEO_NEGATIVE:
        if term in blob:
            return "blocked", f"restrição: '{term}'"

    # ---- 3. Lista LATAM fechada sem o Brasil -------------------------------
    # 3+ países nomeados sem o Brasil = lista de elegibilidade que exclui você
    latam_named = [c for c in config.LATAM_COUNTRIES if c in blob]
    if len(latam_named) >= 3 and not brazil_in_blob:
        return "blocked", f"lista LATAM sem Brasil ({', '.join(latam_named[:3])})"

    # ---- 4. Brasil citado --------------------------------------------------
    if brazil_in_blob:
        return "open", "menciona Brasil"

    # ---- 5. LATAM aberto ---------------------------------------------------
    for term in config.GEO_LATAM_OPEN:
        if term in loc:
            return "open", f"localização LATAM: {job['location']}"

    # ---- 6. Sinal de contratação global no texto ---------------------------
    # Só frases que falam sobre CONTRATAÇÃO. Frases sobre cultura da empresa
    # ("globally distributed team") ficam de fora de propósito: aparecem em
    # vagas US-only e geravam falso positivo.
    for term in config.GEO_POSITIVE:
        if term in blob:
            return "open", f"contratação global: '{term}'"

    # ---- 7. País que pede verificação --------------------------------------
    if country_review:
        return "maybe", f"sediada em {job['location']} — verificar se aceita contractor"

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
    # Ferramentas de autoria
    "articulate": 10, "storyline": 8, "articulate rise": 8, "scorm": 6,
    "camtasia": 5, "captivate": 4, "easygenerator": 7,
    # Design instrucional
    "instructional design": 10, "learning design": 10,
    "curriculum": 5, "elearning": 6, "e-learning": 6,
    "adult learning": 5, "learning experience": 6,
    # Enablement / educação de cliente
    "enablement": 8, "customer education": 9, "onboarding": 5,
    "partner enablement": 8, "product training": 6,
    # Change management
    "change management": 8, "adoption": 4, "stakeholder": 3,
    # IA aplicada
    "generative ai": 7, "artificial intelligence": 5,
    "chatgpt": 5, "synthesia": 6, "ai-assisted": 7, "ai-powered": 6,
    # Plataformas
    "lms": 6, "successfactors": 7, "cornerstone": 7, "degreed": 7,
    "docebo": 5, "moodle": 4,
    # Dados
    "power bi": 6, "learning analytics": 6, "dashboard": 3,
    "power automate": 6,
    # Idiomas — seu maior diferencial
    "spanish": 8, "portuguese": 9, "multilingual": 8,
    "bilingual": 6, "trilingual": 9, "localization": 8,
    "latam": 7, "latin america": 7, "translation": 5,
}

# "rise" sozinho dá falso positivo ("rise to the challenge"), então
# só conta quando acompanhado de contexto.
CONTEXT_SIGNALS = {
    "rise": ("articulate", "storyline", "elearning", "authoring"),
    "ai": ("tool", "assisted", "content", "generative", "leverage"),
}


def gaps(job):
    """
    Identifica requisitos que o perfil não cobre.
    Não bloqueia nada — só sinaliza no relatório, para você saber antes
    de abrir a vaga.
    """
    blob = _norm(job["title"] + " " + job["description"])
    found = []
    for termo, rotulo in GAP_SIGNALS.items():
        if termo in blob:
            found.append(rotulo)
    return sorted(set(found))


GAP_SIGNALS = {
    "xapi": "xAPI",
    "x-api": "xAPI",
    "tin can": "xAPI",
    "adobe captivate": "Captivate",
    "lectora": "Lectora",
    "vyond": "Vyond",
    "after effects": "After Effects",
    "wcag": "WCAG/acessibilidade",
    "section 508": "WCAG/acessibilidade",
    "javascript": "JavaScript",
    "html/css": "HTML/CSS",
    "workday learning": "Workday Learning",
    "docebo": "Docebo",
    "security clearance": "clearance",
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

    # Bônus: trabalho por projeto / part-time / contractor.
    # Você aceita esses formatos, e eles são o caminho mais provável
    # para contratação internacional.
    for sig in getattr(config, "PROJECT_WORK_SIGNALS", []):
        if sig in blob:
            total += 6
            hits.append(sig)
            break

    t = _norm(job["title"])
    for sig in ("instructional design", "learning design", "enablement",
                "customer education", "learning experience", "localization"):
        if sig in t:
            total += 12

    # Penalidade: vaga com forte orientação comercial.
    # Enablement de vendas exige background de quota, pipeline e ciclo de
    # venda — fora do perfil. Não bloqueia, mas desce no ranking.
    sales_hits = sum(1 for s in SALES_CONTEXT if s in blob)
    if sales_hits >= 3:
        total -= 25
    elif sales_hits == 2:
        total -= 12

    return max(min(total, 100), 0), hits


# Termos que indicam vaga de enablement comercial em vez de aprendizagem
SALES_CONTEXT = [
    "quota", "pipeline", "sales cycle", "sales methodology",
    "meddic", "meddpicc", "challenger sale", "spin selling",
    "sales playbook", "win rate", "deal desk", "sales kickoff",
    "arr", "bookings", "sales quota", "closing deals",
    "prospecting", "cold calling", "sales performance",
    "account executives", "sales reps", "sdr", "bdr",
]


# --------------------------------------------------------------------------
# Pipeline
# --------------------------------------------------------------------------
def run(jobs):
    stats = {"bruto": len(jobs)}

    jobs = deduplicate(jobs)
    stats["apos_dedup"] = len(jobs)

    jobs = [j for j in jobs if match_title(j)]
    stats["match_titulo"] = len(jobs)

    priority, local, maybe, blocked_jobs = [], [], [], []

    for j in jobs:
        geo, geo_reason = geo_verdict(j)
        j["geo_status"], j["geo_reason"] = geo, geo_reason
        pay, pay_reason = pay_verdict(j)
        j["pay_status"], j["pay_reason"] = pay, pay_reason
        j["score"], j["signals"] = score(j)
        j["gaps"] = gaps(j)

        if geo == "blocked":
            blocked_jobs.append(j)
        elif geo == "open" and pay == "local":
            # Elegível, mas provável folha em reais
            local.append(j)
        elif geo == "open":
            # "foreign" ou "unknown": vaga internacional elegível.
            # "unknown" é o caso mais comum — a maioria das vagas não
            # declara moeda. Entra na prioridade mesmo assim.
            priority.append(j)
        else:
            maybe.append(j)

    stats["prioridade"] = len(priority)
    stats["local"] = len(local)
    stats["talvez"] = len(maybe)
    stats["bloqueadas"] = len(blocked_jobs)

    # Contagem de motivos de bloqueio — mostra se o filtro está exagerando
    motivos = {}
    for j in blocked_jobs:
        chave = j["geo_reason"].split(":")[0].strip()
        motivos[chave] = motivos.get(chave, 0) + 1
    stats["motivos_bloqueio"] = sorted(
        motivos.items(), key=lambda x: x[1], reverse=True)

    # Bloqueadas com score alto: candidatas a falso positivo
    blocked_jobs.sort(key=lambda x: x["score"], reverse=True)
    stats["bloqueadas_relevantes"] = blocked_jobs[:8]

    for bucket in (priority, local, maybe):
        bucket.sort(key=lambda x: x["score"], reverse=True)

    return priority, local, maybe, stats
