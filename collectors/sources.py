"""
Coletores. Cada função retorna uma lista de dicionários no formato padrão:
{title, company, location, url, description, source, posted}
Nenhuma delas levanta exceção: em caso de erro, registra e devolve lista vazia.
"""
import json
import re
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import config

UA = "Mozilla/5.0 (compatible; JobRadar/1.0)"

# Registro de diagnóstico preenchido durante a execução
DIAGNOSTICS = []


def _log(source, ok, detail=""):
    DIAGNOSTICS.append({"source": source, "ok": ok, "detail": detail})
    mark = "OK  " if ok else "FALHOU"
    print(f"  [{mark}] {source} {detail}")


def _get(url, as_json=True):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json, text/xml, */*",
    })
    with urllib.request.urlopen(req, timeout=config.REQUEST_TIMEOUT) as r:
        raw = r.read()
    return json.loads(raw) if as_json else raw


def _clean(html_text):
    """
    Remove HTML de forma robusta.
    Precisa decodificar entidades ANTES de tirar as tags, senão conteúdo
    que veio escapado (&lt;div&gt;) sobrevive e aparece cru no relatório.
    Roda duas vezes porque algumas APIs escapam em dois níveis.
    """
    if not html_text:
        return ""

    text = html_text
    for _ in range(2):
        # 1. decodificar entidades
        text = _unescape(text)
        # 2. remover tags
        text = re.sub(r"<script[^>]*>.*?</script>", " ", text,
                      flags=re.S | re.I)
        text = re.sub(r"<style[^>]*>.*?</style>", " ", text,
                      flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)

    text = _unescape(text)
    return " ".join(text.split())


def _unescape(text):
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                 ("&quot;", '"'), ("&#39;", "'"), ("&apos;", "'"),
                 ("&nbsp;", " "), ("&#x27;", "'"), ("&#x2F;", "/"),
                 ("&rsquo;", "'"), ("&ldquo;", '"'), ("&rdquo;", '"'),
                 ("&mdash;", "—"), ("&ndash;", "–"), ("&hellip;", "…")):
        text = text.replace(a, b)
    return text


def _job(title, company, location, url, description, source, posted=None):
    return {
        "title": (title or "").strip(),
        "company": (company or "").strip(),
        "location": (location or "").strip(),
        "url": (url or "").strip(),
        "description": _clean(description)[:6000],
        "source": source,
        "posted": posted or "",
    }


# --------------------------------------------------------------------------
# Boards abertos
# --------------------------------------------------------------------------

def remoteok():
    try:
        data = _get("https://remoteok.com/api")
        jobs = []
        for it in data:
            if not isinstance(it, dict) or "position" not in it:
                continue
            jobs.append(_job(
                it.get("position"), it.get("company"),
                it.get("location") or "Remote",
                it.get("url") or it.get("apply_url"),
                it.get("description"), "RemoteOK", it.get("date", "")))
        _log("RemoteOK", True, f"({len(jobs)} vagas)")
        return jobs
    except Exception as e:
        _log("RemoteOK", False, repr(e)[:120])
        return []


def remotive():
    try:
        data = _get("https://remotive.com/api/remote-jobs?limit=800")
        jobs = []
        for it in data.get("jobs", []):
            jobs.append(_job(
                it.get("title"), it.get("company_name"),
                it.get("candidate_required_location") or "Remote",
                it.get("url"), it.get("description"),
                "Remotive", it.get("publication_date", "")))
        _log("Remotive", True, f"({len(jobs)} vagas)")
        return jobs
    except Exception as e:
        _log("Remotive", False, repr(e)[:120])
        return []


def weworkremotely():
    feeds = [
        "https://weworkremotely.com/categories/remote-management-and-finance-jobs.rss",
        "https://weworkremotely.com/categories/remote-customer-support-jobs.rss",
        "https://weworkremotely.com/categories/remote-marketing-jobs.rss",
        "https://weworkremotely.com/remote-jobs.rss",
    ]
    jobs = []
    ok_any = False
    for url in feeds:
        try:
            raw = _get(url, as_json=False)
            root = ET.fromstring(raw)
            for item in root.iter("item"):
                def tx(tag):
                    el = item.find(tag)
                    return el.text if el is not None and el.text else ""
                title = tx("title")
                company = ""
                if ":" in title:
                    company, title = title.split(":", 1)
                jobs.append(_job(title, company, tx("region") or "Remote",
                                 tx("link"), tx("description"),
                                 "WeWorkRemotely", tx("pubDate")))
            ok_any = True
            time.sleep(config.POLITE_DELAY)
        except Exception:
            continue
    _log("WeWorkRemotely", ok_any, f"({len(jobs)} vagas)")
    return jobs


def himalayas():
    try:
        data = _get("https://himalayas.app/jobs/api?limit=500")
        jobs = []
        for it in data.get("jobs", []):
            locs = it.get("locationRestrictions") or []
            jobs.append(_job(
                it.get("title"), it.get("companyName"),
                ", ".join(locs) if locs else "Worldwide",
                it.get("applicationLink") or it.get("guid"),
                it.get("description"), "Himalayas",
                str(it.get("pubDate", ""))))
        _log("Himalayas", True, f"({len(jobs)} vagas)")
        return jobs
    except Exception as e:
        _log("Himalayas", False, repr(e)[:120])
        return []


def workingnomads():
    """
    Working Nomads — agregador com filtro nativo por região.
    Consulta o feed geral e também os recortes LATAM e Brasil.
    """
    urls = [
        "https://www.workingnomads.com/api/exposed_jobs/",
        "https://www.workingnomads.com/api/exposed_jobs/?category=education",
        "https://www.workingnomads.com/api/exposed_jobs/?category=hr",
    ]
    jobs, ok_any = [], False
    for url in urls:
        try:
            data = _get(url)
            items = data if isinstance(data, list) else data.get("results", [])
            for it in items:
                jobs.append(_job(
                    it.get("title"), it.get("company_name") or it.get("company"),
                    it.get("location") or "Remote",
                    it.get("url") or it.get("apply_url"),
                    it.get("description"), "WorkingNomads",
                    str(it.get("pub_date", ""))))
            ok_any = True
        except Exception:
            pass
        time.sleep(config.POLITE_DELAY)
    _log("WorkingNomads", ok_any, f"({len(jobs)} vagas)")
    return jobs


def jobicy():
    """Jobicy — API pública com filtro por região geográfica."""
    urls = [
        "https://jobicy.com/api/v2/remote-jobs?count=100",
        "https://jobicy.com/api/v2/remote-jobs?count=50&geo=latam",
        "https://jobicy.com/api/v2/remote-jobs?count=50&geo=anywhere",
        "https://jobicy.com/api/v2/remote-jobs?count=50&industry=hr",
    ]
    jobs, ok_any = [], False
    for url in urls:
        try:
            data = _get(url)
            for it in data.get("jobs", []):
                geo = it.get("jobGeo") or "Remote"
                jobs.append(_job(
                    it.get("jobTitle"), it.get("companyName"), geo,
                    it.get("url"),
                    it.get("jobDescription") or it.get("jobExcerpt"),
                    "Jobicy", it.get("pubDate", "")))
            ok_any = True
        except Exception:
            pass
        time.sleep(config.POLITE_DELAY)
    _log("Jobicy", ok_any, f"({len(jobs)} vagas)")
    return jobs


# --------------------------------------------------------------------------
# ATS por empresa
# --------------------------------------------------------------------------

def greenhouse(companies):
    jobs, ok, fail = [], 0, []
    for slug in companies:
        try:
            url = (f"https://boards-api.greenhouse.io/v1/boards/{slug}"
                   f"/jobs?content=true")
            data = _get(url)
            for it in data.get("jobs", []):
                jobs.append(_job(
                    it.get("title"), slug,
                    (it.get("location") or {}).get("name", ""),
                    it.get("absolute_url"), it.get("content"),
                    "Greenhouse", it.get("updated_at", "")))
            ok += 1
        except Exception:
            fail.append(slug)
        time.sleep(config.POLITE_DELAY)
    _log("Greenhouse", ok > 0,
         f"({ok}/{len(companies)} empresas, {len(jobs)} vagas)"
         + (f" sem resposta: {', '.join(fail[:5])}" if fail else ""))
    return jobs


def lever(companies):
    jobs, ok, fail = [], 0, []
    last_err = ""
    for slug in companies:
        try:
            data = _get(f"https://api.lever.co/v0/postings/{slug}?mode=json")
            for it in data:
                cat = it.get("categories") or {}
                jobs.append(_job(
                    it.get("text"), slug, cat.get("location", ""),
                    it.get("hostedUrl"),
                    (it.get("descriptionPlain") or it.get("description")),
                    "Lever", str(it.get("createdAt", ""))))
            ok += 1
        except Exception as e:
            fail.append(slug)
            last_err = repr(e)[:70]
        time.sleep(config.POLITE_DELAY)
    detail = f"({ok}/{len(companies)} empresas, {len(jobs)} vagas)"
    if fail:
        detail += f" sem resposta: {', '.join(fail[:4])}"
        if ok == 0 and last_err:
            detail += f" | erro: {last_err}"
    _log("Lever", ok > 0, detail)
    return jobs


def ashby(companies):
    jobs, ok, fail = [], 0, []
    for slug in companies:
        try:
            url = ("https://api.ashbyhq.com/posting-api/job-board/"
                   f"{slug}?includeCompensation=true")
            data = _get(url)
            for it in data.get("jobs", []):
                jobs.append(_job(
                    it.get("title"), slug, it.get("location", ""),
                    it.get("jobUrl"), it.get("descriptionPlain", ""),
                    "Ashby", it.get("publishedAt", "")))
            ok += 1
        except Exception:
            fail.append(slug)
        time.sleep(config.POLITE_DELAY)
    _log("Ashby", ok > 0,
         f"({ok}/{len(companies)} empresas, {len(jobs)} vagas)"
         + (f" sem resposta: {', '.join(fail[:5])}" if fail else ""))
    return jobs


def workable(companies):
    """Workable — muito usado por EdTech e empresas médias europeias."""
    jobs, ok, fail = [], 0, []
    for slug in companies:
        try:
            url = (f"https://apply.workable.com/api/v1/widget/accounts/"
                   f"{slug}?details=true")
            data = _get(url)
            for it in data.get("jobs", []):
                loc = it.get("location") or {}
                loc_str = ", ".join(filter(None, [
                    loc.get("city"), loc.get("region"), loc.get("country")]))
                if it.get("telecommuting"):
                    loc_str = f"Remote - {loc_str}" if loc_str else "Remote"
                jobs.append(_job(
                    it.get("title"), slug, loc_str,
                    it.get("url") or it.get("shortlink"),
                    (it.get("description", "") + " " +
                     it.get("requirements", "")),
                    "Workable", it.get("published_on", "")))
            ok += 1
        except Exception:
            fail.append(slug)
        time.sleep(config.POLITE_DELAY)
    detail = f"({ok}/{len(companies)} empresas, {len(jobs)} vagas)"
    if fail:
        detail += f" sem resposta: {', '.join(fail[:4])}"
    _log("Workable", ok > 0, detail)
    return jobs


def recruitee(companies):
    """Recruitee — comum em empresas europeias."""
    jobs, ok, fail = [], 0, []
    for slug in companies:
        try:
            data = _get(f"https://{slug}.recruitee.com/api/offers/")
            for it in data.get("offers", []):
                loc_str = ", ".join(filter(None, [
                    it.get("city"), it.get("country")]))
                if it.get("remote"):
                    loc_str = f"Remote - {loc_str}" if loc_str else "Remote"
                jobs.append(_job(
                    it.get("title"), slug, loc_str,
                    it.get("careers_url") or it.get("url"),
                    (it.get("description", "") + " " +
                     it.get("requirements", "")),
                    "Recruitee", it.get("published_at", "")))
            ok += 1
        except Exception:
            fail.append(slug)
        time.sleep(config.POLITE_DELAY)
    detail = f"({ok}/{len(companies)} empresas, {len(jobs)} vagas)"
    if fail:
        detail += f" sem resposta: {', '.join(fail[:4])}"
    _log("Recruitee", ok > 0, detail)
    return jobs


def collect_all():
    print("\nColetando vagas...\n")
    jobs = []
    if config.USE_REMOTEOK:
        jobs += remoteok()
    if config.USE_REMOTIVE:
        jobs += remotive()
    if config.USE_WWR:
        jobs += weworkremotely()
    if config.USE_HIMALAYAS:
        jobs += himalayas()
    if getattr(config, "USE_WORKINGNOMADS", False):
        jobs += workingnomads()
    if getattr(config, "USE_JOBICY", False):
        jobs += jobicy()
    if config.GREENHOUSE_COMPANIES:
        jobs += greenhouse(config.GREENHOUSE_COMPANIES)
    if config.LEVER_COMPANIES:
        jobs += lever(config.LEVER_COMPANIES)
    if config.ASHBY_COMPANIES:
        jobs += ashby(config.ASHBY_COMPANIES)
    if getattr(config, "WORKABLE_COMPANIES", None):
        jobs += workable(config.WORKABLE_COMPANIES)
    if getattr(config, "RECRUITEE_COMPANIES", None):
        jobs += recruitee(config.RECRUITEE_COMPANIES)
    print(f"\nTotal bruto coletado: {len(jobs)} vagas")
    return jobs
