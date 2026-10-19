#!/usr/bin/env python3
"""Generate static site in dist/ from data/*.json."""
import json, html, pathlib, shutil
R=pathlib.Path(__file__).resolve().parent.parent; D=R/"dist"
T=json.load(open(R/"data/tools.json")); C=sorted(json.load(open(R/"data/changes.json")),key=lambda c:c["date"],reverse=True)
e=html.escape
CSS="""*{box-sizing:border-box}body{margin:0;font:16px/1.5 system-ui,sans-serif;color:#1a1a1a;background:#fafafa}
header{background:#111;color:#fff;padding:14px 20px;display:flex;gap:20px;flex-wrap:wrap;align-items:center}
header a{color:#fff;text-decoration:none}header .b{font-weight:700;font-size:1.2em}main{max-width:1100px;margin:auto;padding:20px}
.t{overflow-x:auto}table{border-collapse:collapse;width:100%;background:#fff}th,td{border:1px solid #e3e3e3;padding:8px;text-align:left;vertical-align:top;font-size:.93em}
th{background:#f1f1f1}.u{color:#a15c00}.m{color:#666;font-size:.85em}form{background:#fff;border:1px solid #ddd;padding:16px;border-radius:8px;margin-top:30px}
input{padding:8px;width:min(320px,100%)}button{padding:8px 14px;background:#111;color:#fff;border:0;border-radius:4px}
footer{text-align:center;color:#777;font-size:.85em;padding:30px}"""
def mark(s): s=e(s); return s.replace("unknown",'<span class="u">unknown</span>')
def page(title,body,depth=0):
    p="../"*depth
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · LimitWatch</title><link rel="stylesheet" href="{p}style.css"></head><body>
<header><a class="b" href="{p}index.html">LimitWatch</a><a href="{p}index.html">Compare</a><a href="{p}changes.html">What changed</a><a href="{p}index.html#subscribe">Newsletter</a></header>
<main>{body}</main><footer>Data checked {T['checked']}. Always verify on the vendor's official page. Not affiliated with any vendor.</footer></body></html>"""
SUB="""<form id="subscribe" action="https://buttondown.com/api/emails/embed-subscribe/r44e44" method="post" target="popupwindow" onsubmit="window.open('https://buttondown.com/r44e44', 'popupwindow')">
<h3>Get alerts when plans or limits change</h3><input type="email" name="email" required placeholder="you@example.com"> <input type="hidden" name="embed" value="1"> <button>Subscribe</button><p class="m">Weekly email when AI coding plans change. Free, unsubscribe anytime.</p></form>"""
if D.exists(): shutil.rmtree(D)
(D/"tools").mkdir(parents=True); (D/"style.css").write_text(CSS)
rows=""
for t in T["tools"]:
    paid=[p for p in t["plans"] if p["price"] not in("$0","$0/mo")]
    rows+=f"<tr><td><a href='tools/{t['id']}.html'><b>{e(t['name'])}</b></a><br><span class=m>{e(t['category'])}</span></td><td>{'<br>'.join(e(p['name']+': '+p['price']) for p in t['plans'])}</td><td>{mark(t['reset'])}</td><td>{mark(t['overage'])}</td><td class=m><a href='{e(t['url'])}'>source</a><br>{t['checked']}</td></tr>"
home=f"<h1>AI coding tool plans, limits &amp; reset windows</h1><p>Prices, credits and rate limits for {len(T['tools'])} AI coding tools, sourced from official pricing pages. Items we couldn't verify are marked <span class=u>unknown</span>.</p><div class=t><table><tr><th>Tool</th><th>Plans &amp; prices</th><th>Limits reset</th><th>Overage</th><th>Source</th></tr>{rows}</table></div><h2>Latest changes</h2><ul>"+"".join(f"<li><b>{c['date']}</b> {e(c['tool'])}: {e(c['summary'])}</li>" for c in C[:5])+"</ul><a href='changes.html'>All changes →</a>"+SUB
(D/"index.html").write_text(page("Compare",home))
for t in T["tools"]:
    pr="".join(f"<tr><td>{e(p['name'])}</td><td>{mark(p['price'])}</td><td>{mark(p['limits'])}</td></tr>" for p in t["plans"])
    ch="".join(f"<li><b>{c['date']}</b> {e(c['summary'])} <a href='{e(c['source'])}'>source</a></li>" for c in C if c["tool"].split()[0].lower() in t["name"].lower()) or "<li>No sourced changes recorded yet.</li>"
    b=f"<h1>{e(t['name'])}</h1><p>{mark(t['notes'])}</p><p><b>Reset window:</b> {mark(t['reset'])}<br><b>Overage:</b> {mark(t['overage'])}</p><div class=t><table><tr><th>Plan</th><th>Price</th><th>Included usage / limits</th></tr>{pr}</table></div><p class=m>Source: <a href='{e(t['url'])}'>{e(t['url'])}</a> · checked {t['checked']}</p><h2>Change history</h2><ul>{ch}</ul>"+SUB
    (D/"tools"/f"{t['id']}.html").write_text(page(t["name"],b,1))
cl="<h1>What changed</h1><div class=t><table><tr><th>Date</th><th>Tool</th><th>Change</th><th>Source</th></tr>"+"".join(f"<tr><td>{c['date']}</td><td>{e(c['tool'])}</td><td>{e(c['summary'])}</td><td><a href='{e(c['source'])}'>link</a></td></tr>" for c in C)+"</table></div>"
(D/"changes.html").write_text(page("What changed",cl))
print("built", len(list(D.rglob('*.html'))), "pages ->", D)
