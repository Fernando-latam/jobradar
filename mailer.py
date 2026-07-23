"""
Monta e envia o digest diário por email (Yahoo SMTP).

Configuração via variáveis de ambiente / GitHub Secrets:
  YAHOO_EMAIL         seu endereço
  YAHOO_APP_PASSWORD  senha de app de 16 caracteres (não a senha da conta)
"""
import html
import os
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage

SMTP_HOST = "smtp.mail.yahoo.com"
SMTP_PORT = 465

COR = {
    "elegivel": ("#e6f4ea", "#1b5e20", "Elegível"),
    "incerto": ("#fdf3e0", "#8a5a00", "Verificar"),
    "inviavel": ("#fdeaea", "#8a2222", "Inviável"),
}


def configurado():
    return bool(os.environ.get("YAHOO_EMAIL")
                and os.environ.get("YAHOO_APP_PASSWORD"))


def _card(j, i):
    e = html.escape
    nota = j.get("ai_nota", j.get("score", 0))
    eleg = j.get("ai_elegibilidade", "incerto")
    bg, fg, rotulo = COR.get(eleg, COR["incerto"])

    lacunas = ""
    if j.get("ai_lacunas"):
        itens = ", ".join(e(str(x)) for x in j["ai_lacunas"][:4])
        lacunas = (f'<div style="font-size:13px;color:#8a2222;'
                   f'margin-top:6px">Pede o que você não tem: {itens}</div>')

    fit = e(j.get("ai_fit", "")) or e(j["description"][:200] + "...")
    acao = ""
    if j.get("ai_acao"):
        acao = (f'<div style="font-size:13px;color:#333;margin-top:8px;'
                f'padding-top:8px;border-top:1px solid #eee">'
                f'<b>Ação:</b> {e(j["ai_acao"])}</div>')

    return f"""
<tr><td style="padding:0 0 14px 0">
 <table width="100%" cellpadding="0" cellspacing="0"
        style="background:#fff;border:1px solid #e2e4e8;border-radius:8px">
  <tr><td style="padding:16px 18px">
   <table width="100%"><tr>
     <td style="font-size:16px;font-weight:600;padding-bottom:2px">
       <a href="{e(j['url'])}" style="color:#12326b;text-decoration:none">{e(j['title'])}</a>
     </td>
     <td align="right" style="font-size:18px;font-weight:700;color:#2e7d32;
         width:44px;vertical-align:top">{nota}</td>
   </tr></table>
   <div style="font-size:13px;color:#555;padding-bottom:9px">
     {e(j['company'])} &middot; {e(j['location'] or 'Remote')} &middot; {e(j['source'])}
   </div>
   <span style="display:inline-block;font-size:11px;background:{bg};color:{fg};
         padding:3px 9px;border-radius:10px;margin-bottom:8px">
     {rotulo} &middot; {e(j.get('ai_motivo_eleg', j.get('geo_reason', '')))}
   </span>
   <div style="font-size:14px;color:#333;line-height:1.5">{fit}</div>
   {lacunas}
   {acao}
   <div style="margin-top:10px">
     <a href="{e(j['url'])}" style="font-size:13px;color:#12326b">Abrir vaga &rarr;</a>
   </div>
  </td></tr>
 </table>
</td></tr>"""


def montar_html(destaques, outras, stats, pages_url=""):
    hoje = datetime.now().strftime("%d/%m/%Y")

    cards_top = "".join(_card(j, i) for i, j in enumerate(destaques))
    if not cards_top:
        cards_top = ('<tr><td style="padding:16px;background:#fff;'
                     'border-radius:8px;color:#666">Nenhuma vaga nova com bom '
                     'fit hoje. Isso é normal — o mercado é pequeno.</td></tr>')

    linhas_outras = ""
    for j in outras[:15]:
        nota = j.get("ai_nota", j.get("score", 0))
        linhas_outras += (
            f'<tr><td style="padding:5px 0;font-size:13px;border-bottom:'
            f'1px solid #eee">'
            f'<span style="color:#888">{nota}</span> &nbsp;'
            f'<a href="{html.escape(j["url"])}" style="color:#12326b;'
            f'text-decoration:none">{html.escape(j["title"][:58])}</a>'
            f' <span style="color:#888">&middot; {html.escape(j["company"][:22])}</span>'
            f'</td></tr>')

    bloco_outras = ""
    if linhas_outras:
        bloco_outras = f"""
        <tr><td style="padding:22px 0 8px 0;font-size:15px;font-weight:600">
          Outras {len(outras)} vagas novas
        </td></tr>
        <tr><td><table width="100%">{linhas_outras}</table></td></tr>"""

    link_pages = ""
    if pages_url:
        link_pages = (f'<a href="{pages_url}" style="color:#12326b">'
                      f'Ver relatório completo</a> &middot; ')

    return f"""<!doctype html><html><body style="margin:0;padding:20px;
background:#f4f5f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',
Roboto,Arial,sans-serif;color:#1a1a1a">
<table width="100%" cellpadding="0" cellspacing="0">
<tr><td align="center">
<table width="620" cellpadding="0" cellspacing="0" style="max-width:620px">

  <tr><td style="padding-bottom:4px;font-size:22px;font-weight:700">JobRadar</td></tr>
  <tr><td style="padding-bottom:18px;font-size:13px;color:#666">
    {hoje} &middot; {stats['bruto']} vagas varridas &middot;
    {stats['match_titulo']} da sua área &middot; {len(destaques)} destaques
  </td></tr>

  <tr><td style="padding-bottom:10px;font-size:15px;font-weight:600">
    Destaques de hoje
  </td></tr>
  {cards_top}
  {bloco_outras}

  <tr><td style="padding-top:24px;font-size:12px;color:#888;
      border-top:1px solid #ddd">
    {link_pages}Gerado automaticamente pelo JobRadar.
  </td></tr>

</table>
</td></tr></table>
</body></html>"""


def enviar(destaques, outras, stats, pages_url=""):
    if not configurado():
        print("  YAHOO_EMAIL / YAHOO_APP_PASSWORD não configurados — email não enviado")
        return False

    endereco = os.environ["YAHOO_EMAIL"]
    senha = os.environ["YAHOO_APP_PASSWORD"]

    n = len(destaques)
    if n:
        topo = destaques[0]
        assunto = f"JobRadar: {n} vaga{'s' if n > 1 else ''} — {topo['title'][:44]}"
    else:
        assunto = "JobRadar: nenhuma vaga nova hoje"

    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = endereco
    msg["To"] = endereco
    msg.set_content(
        "Seu leitor de email não suporta HTML. "
        "Veja o relatório completo no GitHub Pages.")
    msg.add_alternative(montar_html(destaques, outras, stats, pages_url),
                        subtype="html")

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as s:
            s.login(endereco, senha)
            s.send_message(msg)
        print(f"  email enviado para {endereco}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("  ERRO de autenticação. Verifique se YAHOO_APP_PASSWORD é uma "
              "senha de app (16 caracteres), não a senha normal da conta.")
        return False
    except Exception as e:
        print(f"  ERRO ao enviar email: {repr(e)[:160]}")
        return False
