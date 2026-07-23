"""
JobRadar - Configuração central
Edite ESTE arquivo para ajustar sua busca. Não precisa mexer no resto.

O filtro faz DUAS perguntas diferentes sobre cada vaga:
  1. ELEGIBILIDADE — posso legalmente ser contratado nessa vaga?
  2. PAGAMENTO     — paga em moeda forte, ou é folha local em reais?

Uma vaga em São Paulo contratada por entidade brasileira passa em (1)
e falha em (2). O relatório separa as duas coisas.
"""

# ---------------------------------------------------------------------------
# 1. TÍTULOS QUE INTERESSAM
# ---------------------------------------------------------------------------
TITLE_KEYWORDS = [
    # Instructional / Learning Design
    "instructional design", "instructional designer",
    "learning design", "learning designer",
    "learning experience design", "learning experience designer",
    "curriculum design", "curriculum developer", "curriculum designer",
    "elearning", "e-learning", "digital learning", "learning content",

    # L&D
    "learning and development", "learning & development", "l&d",
    "learning specialist", "learning manager", "learning partner",
    "learning operations", "learning technologist", "learning consultant",
    "training specialist", "training manager", "training lead",
    "training and development", "training & development",
    "training consultant", "corporate trainer",

    # Enablement / Customer Education
    "enablement", "sales enablement", "customer enablement",
    "revenue enablement", "partner enablement", "technical enablement",
    "customer education", "customer training", "product education",
    "education specialist", "education manager", "education program",
    "onboarding specialist", "onboarding manager",

    # Change / Adoption
    "change management", "change manager", "change lead",
    "adoption specialist", "organizational development",
]

TITLE_EXCLUDE = [
    "software engineer", "software developer", "backend", "frontend",
    "full stack", "fullstack", "data scientist", "data engineer",
    "machine learning", "deep learning", "ml engineer",
    "devops", "sre", "platform engineer", "security engineer",
    "solutions architect", "solutions engineer",
    "personal trainer", "fitness", "athletic", "yoga",
    "intern", "internship", "estágio", "apprentice", "graduate program",
    "teacher", "professor", "tutor", "lecturer", "faculty",
    "recruiter", "talent acquisition", "nurse", "driver",
    "account executive", "sales representative", "sales development",
    "customer support", "customer service representative",
]


# ---------------------------------------------------------------------------
# 2. ELEGIBILIDADE GEOGRÁFICA
# ---------------------------------------------------------------------------

GEO_NEGATIVE = [
    "legally authorized to work in the united states",
    "authorized to work in the united states",
    "must be authorized to work in the us",
    "must be legally authorized to work in the us",
    "requires us work authorization", "us work authorization required",
    "eligible to work in the united states",
    "must have us work authorization", "without sponsorship",
    "must be located in the united states", "must reside in the united states",
    "based in united states", "must be based in the us",
    "located in the us", "residing in the united states",
    "within the united states", "must live in the united states",
    "us-based only", "u.s.-based only", "usa only", "us only", "u.s. only",
    "united states only", "us residents only",
    "eligible to work in the uk", "right to work in the uk",
    "must be located in canada", "canada only", "based in canada",
    "eu work permit", "right to work in the eu", "eea only",
    "work authorization in the eu", "eligible to work in ireland",
    "must reside in", "must be located in", "must be based in",
    "onsite", "on-site", "hybrid", "in-office", "relocation required",
    "security clearance", "w2 only", "no c2c", "c2c not accepted",
]

GEO_COUNTRY_LOCK = [
    "united states", "usa", "u.s.", "canada", "united kingdom",
    "spain", "germany", "france", "portugal", "poland", "netherlands",
    "ireland", "switzerland", "australia", "india", "philippines",
    "mexico", "colombia", "costa rica", "argentina", "chile", "peru",
    "guatemala", "el salvador", "honduras", "nicaragua", "ecuador",
    "uruguay", "panama", "japan", "singapore", "new zealand",
    "italy", "sweden", "norway", "denmark", "finland", "belgium",
    "austria", "czech", "romania", "greece", "israel", "uae", "dubai",
]

# Marcadores de localização US — pegam "Remote - US", "Austin, TX", etc.
US_LOCATION_MARKERS = [
    "remote - us", "remote-us", "remote, us", "us remote", "usa remote",
    "remote (us", "remote us", "- us", ", us", "united states", "u.s.",
    ", ny", ", ca", ", tx", ", fl", ", wa", ", ma", ", il", ", co",
    ", ga", ", nc", ", va", ", az", ", oh", ", pa", ", mn", ", or",
    ", nj", ", ut", ", tn", ", mo", ", md", ", wi", ", in", ", sc",
]

LATAM_COUNTRIES = [
    "mexico", "guatemala", "el salvador", "honduras", "nicaragua",
    "costa rica", "panama", "colombia", "ecuador", "peru", "bolivia",
    "chile", "argentina", "uruguay", "paraguay", "venezuela",
    "dominican republic",
]

# Sinais REAIS de contratação global.
# Precisam ser frases inequívocas: palavras soltas como "worldwide" ou
# "global" aparecem em texto institucional de qualquer empresa.
GEO_POSITIVE = [
    "work from anywhere", "hire from anywhere", "hire anywhere",
    "we hire globally", "hire globally", "globally distributed",
    "anywhere in the world", "from anywhere in the world",
    "remote - worldwide", "remote worldwide", "remote (worldwide)",
    "remote - global", "remote global", "remote (global)",
    "fully distributed", "100% remote worldwide",
    "any location", "any timezone", "all timezones", "any country",
    "employer of record", "employer-of-record",
    "independent contractor", "b2b contract", "contractor agreement",
    "no location restrictions", "location independent",
    "open to candidates worldwide", "candidates from any country",
]

GEO_BRAZIL = ["brazil", "brasil"]
GEO_LATAM_OPEN = ["latam", "latin america", "south america"]


# ---------------------------------------------------------------------------
# 3. MOEDA / TIPO DE CONTRATAÇÃO
# ---------------------------------------------------------------------------

LOCAL_HIRE_SIGNALS = [
    "clt", "carteira assinada", "vale refeição", "vale transporte",
    "plano de saúde", "regime clt", "consolidação das leis",
    "brazilian labor", "local contract", "local payroll",
    "local benefits", "brazilian entity", "brazilian subsidiary",
    "vale alimentação", "auxílio", "salário", "reais",
]

BR_CITIES = [
    "são paulo", "sao paulo", "rio de janeiro", "belo horizonte",
    "curitiba", "porto alegre", "brasília", "brasilia", "campinas",
    "recife", "salvador", "florianópolis", "florianopolis", "fortaleza",
    "barueri", "osasco", "santos", "goiânia", "goiania",
]

STRONG_CURRENCY_SIGNALS = [
    "usd", "us$", "$/hr", "$ per hour", "usd/hour", "paid in usd",
    "eur", "gbp", "day rate", "daily rate", "hourly rate",
    "employer of record", "independent contractor",
    "b2b", "contractor", "1099", "invoice", "annual salary usd",
]


# ---------------------------------------------------------------------------
# 4. FONTES
# ---------------------------------------------------------------------------
USE_REMOTEOK = True
USE_REMOTIVE = True
USE_WWR = True
USE_HIMALAYAS = True

# Greenhouse — slug de https://boards.greenhouse.io/SLUG
GREENHOUSE_COMPANIES = [
    # SaaS com Customer Education / Enablement forte
    "twilio", "cloudflare", "datadog", "elastic", "mongodb",
    "gitlab", "hubspot", "asana", "airtable", "figma",
    "gusto", "webflow", "zapier", "samsara", "affirm",
    "instacart", "doordash", "robinhood", "reddit", "discord",
    # EdTech / Learning
    "coursera", "udemy", "duolingo", "pluralsight", "guild",
    "articulate", "360learning", "docebo",
    # Remote-first / EOR
    "oysterhr", "andela", "toptal",
    # LATAM
    "nubank", "wellhub",
]

# Lever — slug de https://jobs.lever.co/SLUG
LEVER_COMPANIES = [
    "plaid", "benchling", "attentive", "matterport",
    "voiceflow", "sardine", "kraken", "gopuff",
]

# Ashby — slug de https://jobs.ashbyhq.com/SLUG
ASHBY_COMPANIES = [
    "linear", "posthog", "supabase", "clerk",
    "ramp", "deel", "mercury", "vanta",
]


# ---------------------------------------------------------------------------
# 5. SAÍDA
# ---------------------------------------------------------------------------
OUTPUT_DIR = "output"
MAX_AGE_DAYS = 21
REQUEST_TIMEOUT = 25
POLITE_DELAY = 0.4
