"""
JobRadar - Configuração central
Edite ESTE arquivo para ajustar sua busca. Não precisa mexer no resto.
"""

# ---------------------------------------------------------------------------
# 1. TÍTULOS QUE INTERESSAM
# Basta uma dessas expressões aparecer no título da vaga.
# Tudo é comparado em minúsculas, então não se preocupe com maiúsculas.
# ---------------------------------------------------------------------------
TITLE_KEYWORDS = [
    # Instructional / Learning Design
    "instructional design", "instructional designer",
    "learning design", "learning designer",
    "learning experience design", "learning experience designer",
    "curriculum design", "curriculum developer", "curriculum designer",
    "elearning", "e-learning", "digital learning",
    "content designer learning",

    # L&D
    "learning and development", "learning & development", "l&d",
    "learning specialist", "learning manager", "learning partner",
    "learning operations", "learning technologist",
    "training specialist", "training manager", "training lead",
    "training and development", "training & development",
    "corporate trainer", "trainer",

    # Enablement / Customer Education
    "enablement", "sales enablement", "customer enablement",
    "revenue enablement", "partner enablement",
    "customer education", "customer training",
    "education specialist", "education manager",
    "onboarding specialist", "onboarding manager",

    # Change / Adoption
    "change management", "change manager", "adoption specialist",
    "organizational development",
]

# Títulos a EXCLUIR mesmo que batam acima (evita ruído)
TITLE_EXCLUDE = [
    "software", "engineer", "developer", "data scientist",
    "machine learning", "deep learning",   # "learning" que não é L&D
    "personal trainer", "fitness", "athletic",
    "intern", "internship", "estágio",
    "teacher", "professor", "tutor", "instructor k-12",
    "director of engineering", "sales representative", "account executive",
    "recruiter", "nurse", "driver",
]


# ---------------------------------------------------------------------------
# 2. ELEGIBILIDADE GEOGRÁFICA  ← o filtro mais importante
# ---------------------------------------------------------------------------

# Sinais de que a vaga PODE aceitar alguém no Brasil
GEO_POSITIVE = [
    "brazil", "brasil", "latam", "latin america", "south america",
    "americas", "worldwide", "global", "anywhere",
    "remote - global", "fully remote", "work from anywhere",
    "any location", "any timezone", "all timezones",
    "eor", "employer of record", "deel", "remote.com", "oyster", "globalization partners",
    "b2b contract", "independent contractor", "contractor",
    "we hire globally", "hire anywhere", "distributed team",
]

# Sinais de que a vaga é FECHADA para você
GEO_NEGATIVE = [
    # Autorização de trabalho nos EUA
    "legally authorized to work in the united states",
    "authorized to work in the united states",
    "must be authorized to work in the us",
    "must be legally authorized to work in the us",
    "requires us work authorization", "us work authorization required",
    "eligible to work in the united states",
    "must have us work authorization",
    # Residência exigida
    "must be located in the united states", "must reside in the united states",
    "based in united states", "must be based in the us",
    "located in the us", "residing in the united states",
    "within the united states", "must live in the united states",
    "us-based only", "u.s.-based only", "usa only", "us only", "u.s. only",
    "united states only",
    # Outros países
    "eligible to work in the uk", "right to work in the uk",
    "must be located in canada", "canada only", "based in canada",
    "eu work permit", "right to work in the eu", "eea only",
    "work authorization in the eu", "eligible to work in ireland",
    "must reside in", "must be located in", "must be based in",
    # Presencial
    "onsite", "on-site", "hybrid", "in-office", "relocation required",
    "security clearance", "w2 only", "no c2c", "c2c not accepted",
]

# Países que, quando aparecem na LOCALIZAÇÃO, travam a vaga
GEO_COUNTRY_LOCK = [
    "united states", "usa", "u.s.", "canada", "united kingdom",
    "spain", "germany", "france", "portugal", "poland", "netherlands",
    "ireland", "switzerland", "australia", "india", "philippines",
    "mexico", "colombia", "costa rica", "argentina", "chile", "peru",
    "guatemala", "el salvador", "honduras", "nicaragua", "ecuador",
    "uruguay", "panama", "japan", "singapore", "new zealand",
]

# Países LATAM que costumam aparecer em listas de elegibilidade.
# Se 2+ aparecem e o Brasil NÃO está entre eles, a vaga é bloqueada.
LATAM_COUNTRIES = [
    "mexico", "guatemala", "el salvador", "honduras", "nicaragua",
    "costa rica", "panama", "colombia", "ecuador", "peru", "bolivia",
    "chile", "argentina", "uruguay", "paraguay", "venezuela",
    "dominican republic",
]


# ---------------------------------------------------------------------------
# 3. FONTES
# ---------------------------------------------------------------------------

# Boards abertos (não precisam de lista de empresas)
USE_REMOTEOK = True
USE_REMOTIVE = True
USE_WWR = True          # We Work Remotely (RSS)
USE_HIMALAYAS = True

# Empresas no Greenhouse — o "slug" é o nome que aparece na URL do board.
# Ex: https://boards.greenhouse.io/deel  →  slug = "deel"
# Comece com esta lista e vá adicionando conforme descobrir novas.
GREENHOUSE_COMPANIES = [
    "deel", "remotecom", "gitlab", "hubspot", "docusign",
    "twilio", "cloudflare", "datadog", "elastic", "hashicorp",
    "mongodb", "gusto", "asana", "airtable", "figma",
    "notion", "loom", "webflow", "zapier", "coursera",
    "udemy", "pluralsight", "duolingo", "nubank", "wellhub",
]

# Empresas no Lever — slug da URL: https://jobs.lever.co/netlify → "netlify"
LEVER_COMPANIES = [
    "netlify", "vercel", "sourcegraph", "lattice", "mercury",
    "brex", "ramp", "rippling", "attentive",
]

# Empresas no Ashby — https://jobs.ashbyhq.com/linear → "linear"
ASHBY_COMPANIES = [
    "linear", "posthog", "supabase", "clerk",
]


# ---------------------------------------------------------------------------
# 4. SAÍDA
# ---------------------------------------------------------------------------
OUTPUT_DIR = "output"
MAX_AGE_DAYS = 21          # ignora vagas mais antigas que isso
REQUEST_TIMEOUT = 25
POLITE_DELAY = 0.4         # segundos entre requisições
