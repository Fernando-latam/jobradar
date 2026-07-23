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
    "change consultant", "organizational change",
    "adoption specialist", "adoption manager",
    "organizational development",

    # Localização / conteúdo multilíngue
    "localization", "localisation", "content localization",
    "localization specialist", "localization manager",
    "translation manager", "multilingual content",

    # Contract / freelance na própria descrição do cargo
    "learning consultant", "training contractor",
    "freelance instructional", "contract instructional",
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

# Países que BLOQUEIAM pela localização: NENHUM.
# Qualquer país fora do Brasil é de interesse. O que exclui uma vaga é
# restrição explícita de residência/visto (GEO_NEGATIVE) ou exigência de
# um idioma que você não fala (LANGUAGE_BLOCK, abaixo).
GEO_COUNTRY_LOCK = [
    # Deixe vazio para não bloquear nenhum país pela localização.
    # Se quiser voltar a bloquear algum, adicione aqui em minúsculas.
]

# Países cuja localização manda a vaga para "verificar manualmente".
# Não bloqueiam — só sinalizam que vale conferir o modelo de contratação.
GEO_COUNTRY_REVIEW = [
    "united states", "usa", "u.s.", "canada", "united kingdom",
    "australia", "new zealand", "india", "philippines", "japan",
    "singapore", "china", "korea",
    "mexico", "colombia", "costa rica", "argentina", "chile", "peru",
    "guatemala", "el salvador", "honduras", "nicaragua", "ecuador",
    "uruguay", "panama", "bolivia", "paraguay", "dominican republic",
    "spain", "germany", "france", "portugal", "poland", "netherlands",
    "ireland", "switzerland", "italy", "sweden", "norway", "denmark",
    "finland", "belgium", "austria", "czech", "romania", "greece",
    "estonia", "lithuania", "bulgaria", "hungary",
    "israel", "uae", "dubai", "south africa", "turkey",
]


# ---------------------------------------------------------------------------
# 2b. IDIOMA  ← o que realmente bloqueia agora
# Você fala Português, Inglês e Espanhol. Vaga que exige outro idioma
# como requisito é bloqueada.
# ---------------------------------------------------------------------------

# Frases que indicam EXIGÊNCIA de idioma que você não domina
LANGUAGE_BLOCK = [
    # Alemão
    "german language", "fluent in german", "fluency in german",
    "native german", "german speaking", "deutschkenntnisse",
    "sehr gute deutschkenntnisse", "verhandlungssicheres deutsch",
    "german is required", "german required", "german c1", "german c2",
    # Francês
    "french language", "fluent in french", "fluency in french",
    "native french", "french speaking", "maîtrise du français",
    "french is required", "french required", "french c1", "french c2",
    # Holandês
    "dutch language", "fluent in dutch", "native dutch",
    "dutch speaking", "nederlands", "dutch is required",
    # Nórdicos
    "swedish language", "fluent in swedish", "native swedish",
    "norwegian language", "fluent in norwegian",
    "danish language", "fluent in danish",
    "finnish language", "fluent in finnish",
    # Italiano
    "italian language", "fluent in italian", "native italian",
    "italian is required", "madrelingua italiana",
    # Eslavos / outros
    "polish language", "fluent in polish", "native polish",
    "czech language", "fluent in czech",
    "romanian language", "fluent in romanian",
    "hungarian language", "fluent in hungarian",
    "russian language", "fluent in russian", "native russian",
    "ukrainian language", "fluent in ukrainian",
    "greek language", "fluent in greek",
    "turkish language", "fluent in turkish",
    "hebrew language", "fluent in hebrew",
    "arabic language", "fluent in arabic", "native arabic",
    # Asiáticos
    "japanese language", "fluent in japanese", "native japanese",
    "business level japanese", "japanese is required",
    "mandarin", "cantonese", "fluent in chinese", "native chinese",
    "korean language", "fluent in korean", "native korean",
    "hindi language", "fluent in hindi",
    "tagalog", "thai language", "vietnamese language",
]

# Sinais de que a vaga é escrita em idioma que você não domina.
# Aparecem no TÍTULO — indicam vaga local não-anglófona.
FOREIGN_TITLE_MARKERS = [
    # alemão
    "mitarbeiter", "mitarbeiterin", "referent", "referentin",
    "berater", "beraterin", "leiter", "leiterin", "fachkraft",
    "mediengestalter", "ausbildung", "bildungs", "schulung",
    "trainer/in", " für ", " und ", "m/w/d", "w/m/d",
    # francês
    "chargé", "chargée", "responsable", "formateur", "formatrice",
    "concepteur", "conceptrice", "ingénieur",
    # holandês
    "medewerker", "adviseur", "opleider",
    # italiano
    "responsabile", "progettista", "formatore",
    # polonês
    "specjalista", "kierownik", "trener",
]


# Marcadores de localização US.
# Não bloqueiam mais — servem para mandar a vaga a "verificar manualmente".
US_LOCATION_MARKERS = [
    "remote - us", "remote-us", "remote, us", "us remote", "usa remote",
    "remote (us", "remote us", "united states", "u.s.",
]

# Abreviações de estados — só valem no FIM da string ("Austin, TX")
US_STATE_SUFFIXES = [
    "ny", "ca", "tx", "fl", "wa", "ma", "il", "co", "ga", "nc", "va",
    "az", "oh", "pa", "mn", "or", "nj", "ut", "tn", "mo", "md", "wi",
    "in", "sc", "mi", "nv", "ks", "ia", "ct", "ok", "ar", "ms", "ne",
    "id", "nm", "wv", "nh", "me", "ri", "mt", "de", "sd", "nd", "ak",
    "vt", "wy", "hi", "dc", "ky", "al", "la",
]

# Lista fechada de países LATAM numa vaga.
# Se 3 ou mais aparecem e o Brasil NÃO está entre eles, é uma lista de
# elegibilidade que exclui você de propósito (ex.: a vaga da Viva Talent).
# Com 2 ou menos, pode ser menção casual — vai para revisão manual.
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

# Você aceita part-time e trabalho por projeto — esses termos são um
# BÔNUS no score, não um filtro de exclusão.
PROJECT_WORK_SIGNALS = [
    "part-time", "part time", "freelance", "freelancer",
    "contract", "contractor", "fractional", "project-based",
    "project based", "consultant", "consulting", "interim",
    "temporary", "fixed-term", "retainer", "hourly",
    "6-month", "12-month", "3-month", "short-term engagement",
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
USE_WORKINGNOMADS = True   # tem filtro nativo por LATAM e por Brasil
USE_JOBICY = True          # agregador com filtro de região

# Greenhouse — slug de https://boards.greenhouse.io/SLUG
# Priorizadas empresas com função de Customer Education / Enablement forte,
# EdTech, e consultorias de aprendizagem — onde vagas de L&D realmente saem.
GREENHOUSE_COMPANIES = [
    # SaaS com Customer Education / Enablement
    "twilio", "cloudflare", "datadog", "elastic", "mongodb",
    "gitlab", "hubspot", "asana", "airtable", "figma",
    "gusto", "webflow", "samsara", "affirm", "stripe",
    "instacart", "doordash", "robinhood", "reddit", "discord",
    "atlassian", "databricks", "snowflake", "confluent", "hashicorp",
    "amplitude", "mixpanel", "segment", "braze", "klaviyo",
    "zendesk", "intercom", "front", "miro", "canva",
    "okta", "auth0", "1password", "sentry", "postman",
    # EdTech / Learning
    "coursera", "udemy", "duolingo", "guild", "multiverse",
    "newsela", "nearpod", "quizlet", "chegg", "skillshare",
    # Remote-first / EOR
    "oysterhr", "andela", "turing", "crossover",
    # LATAM
    "nubank", "wellhub", "rappi", "kavak",
]

# Lever — slug de https://jobs.lever.co/SLUG
LEVER_COMPANIES = [
    "plaid", "sardine", "kraken", "gopuff", "veeva",
    "leapsome", "showpad", "seismic", "highspot",
]

# Ashby — slug de https://jobs.ashbyhq.com/SLUG
ASHBY_COMPANIES = [
    "linear", "posthog", "supabase", "clerk",
    "ramp", "deel", "mercury", "vanta", "openai",
    "notion", "loom", "runway", "replit",
]

# Workable — slug de https://apply.workable.com/SLUG
# Muito usado por EdTech e empresas médias europeias.
WORKABLE_COMPANIES = [
    "docebo", "360learning", "easygenerator", "learnworlds",
    "talentlms", "kahoot", "sanalabs", "howspace",
    "valamis", "cornerstone", "gomolearning",
]

# Recruitee — slug de https://SLUG.recruitee.com
RECRUITEE_COMPANIES = [
    "lepaya", "studytube", "gp-strategies",
]


# ---------------------------------------------------------------------------
# 5. SAÍDA
# ---------------------------------------------------------------------------
# Bloquear vagas que exigem idioma que você não domina?
BLOCK_BY_LANGUAGE = True

OUTPUT_DIR = "output"
MAX_AGE_DAYS = 21
REQUEST_TIMEOUT = 25
POLITE_DELAY = 0.4
