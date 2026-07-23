"""Gera o relatório HTML que você abre no navegador."""
import html
import os
from datetime import datetime

import config

CSS = """
*{box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
     margin:0;padding:32px 20px;background:#f4f5f7;color:#1a1a1a;line-height:1.55}
.wrap{max-width:980px;margin:0 auto}
h1{font-size:26px;margin:0 0 4px}
.sub{color:#666;font-size:14px;margin-bottom:24px}
.stats{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:28px}
.stat{background:#fff;border:1px solid #e2e4e8;border-radius:8px;padding:12px 16px;min-width:104px}
.stat b{display:block;font-size:22px}
.stat span{font-size:11px;color:#666;text-transform:uppercase;letter-spacing:.5px}
h2{font-size:17px;margin:34px 0 6px;padding-bottom:8px;border-bottom:2px solid #d8dade}
.hint{font-size:13px;color:#666;margin-bottom:14px}
.job{background:#fff;border:1px solid #e2e4e8;border-radius:10px;padding:16px 18px;margin-bottom:12px}
.job.top{border-left:4px solid #2e7d32}
.job.loc{border-left:4px solid #b0851f}
.jt{font-size:16px;font-weight:600;margin-bottom:3px;padding-right:44px}
.jt a{color:#12326b;text-decoration:none}
.jt a:hover{text-decoration:underline}
.jm{font-size:13px;color:#555;margin-bottom:9px}
.tags{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:8px}
.tag{font-size:11px;background:#eef1f5;color:#33415c;padding:2px 8px;border-radius:10px}
.tag.geo{background:#e6f4ea;color:#1b5e20}
.tag.warn{background:#fdf3e0;color:#8a5a00}
.tag.pay{background:#e8eefc;color:#1c3f80}
.score{float:right;font-size:12px;font-weight:700;color:#2e7d32}
.snip{font-size:13px;color:#444;border-top:1px solid #eef0f2;padding-top:8px;margin-top:4px}
.diag{background:#fff;border:1px solid #e2e4e8;border-radius:10px;padding:14px 18px;font-size:13px}
.diag div{padding:3px 0}
.ok{color:#1b5e20}.fail{color:#a52222}
footer{margin-top:36px;font-size:12px;color:#888;text-align:center}
"""


def _card(j, style=""):
    e = html.escape
    tags = "".join(f'<span class="tag">{e(s)}</span>' for s in j["signals"][:9])

    geo_cls = "geo" if j["geo_status"] == "open" else "warn"
    geo_tag = f'<span class="tag {geo_cls}">{e(j["geo_reason"])}</span>'

    pay_tag = ""
    if j.get("pay_status") == "local":
        pay_tag = f'<span class="tag warn">{e(j["pay_reason"])}</span>'
    elif j.get("pay_status") == "foreign":
        pay_tag = f'<span class="tag pay">{e(j["pay_reason"])}</span>'

    return f"""
    <div class="job {style}">
      <span class="score">{j['score']}</span>
      <div class="jt"><a href="{e(j['url'])}" target="_blank">{e(j['title'])}</a></div>
      <div class="jm">{e(j['company'])} &middot; {e(j['location'] or 'Remote')} &middot; {e(j['source'])}</div>
      <div class="tags">{geo_tag}{pay_tag}{tags}</div>
      <div class="snip">{e(j['description'][:280])}...</div>
    </div>"""


def _section(titulo, dica, jobs, style="", limite=25):
    corpo = "".join(_card(j, style) for j in jobs[:limite])
    if not corpo:
        corpo = "<p>Nada nesta categoria hoje.</p>"
    return (f"<h2>{titulo} — {len(jobs)}</h2>"
            f'<div class="hint">{dica}</div>{corpo}')


def build(priority, local, maybe, stats, diagnostics):
    now = datetime.now().strftime("%d/%m/%Y às %H:%M")

    diag_rows = "".join(
        f'<div class="{"ok" if d["ok"] else "fail"}">'
        f'{"✓" if d["ok"] else "✗"} {html.escape(d["source"])} '
        f'{html.escape(d["detail"])}</div>'
        for d in diagnostics)

    body = f"""<!doctype html><html lang="pt-BR"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>JobRadar — {now}</title><style>{CSS}</style></head><body><div class="wrap">
<h1>JobRadar</h1>
<div class="sub">Gerado em {now}</div>

<div class="stats">
  <div class="stat"><b>{stats['bruto']}</b><span>Coletadas</span></div>
  <div class="stat"><b>{stats['match_titulo']}</b><span>Da sua área</span></div>
  <div class="stat"><b>{stats['prioridade']}</b><span>Prioridade</span></div>
  <div class="stat"><b>{stats['local']}</b><span>Local BR</span></div>
  <div class="stat"><b>{stats['talvez']}</b><span>Talvez</span></div>
  <div class="stat"><b>{stats['bloqueadas']}</b><span>Bloqueadas</span></div>
</div>

{_section("Prioridade",
          "Elegível para contratação e com sinal de pagamento em moeda forte "
          "(USD/EUR, contractor, EOR). Comece por aqui.",
          priority, "top")}

{_section("Verificar manualmente",
          "Sem sinal claro de elegibilidade. Vale abrir e conferir antes de "
          "investir tempo.",
          maybe, "", 20)}

{_section("Contratação local no Brasil",
          "Elegível, mas provavelmente folha local em reais. Fora do objetivo "
          "de ganhar em moeda estrangeira — mantido apenas para visibilidade.",
          local, "loc", 10)}

<h2>Diagnóstico das fontes</h2>
<div class="diag">{diag_rows}</div>

<footer>JobRadar &middot; {stats['bloqueadas']} vagas bloqueadas por elegibilidade</footer>
</div></body></html>"""

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    path = os.path.join(config.OUTPUT_DIR, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    return path
