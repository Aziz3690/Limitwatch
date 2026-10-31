#!/usr/bin/env python3
"""Fetch each pricing page, extract visible text, diff against last snapshot.
Usage: python3 scripts/watch.py   (exit code 1 if any change detected)"""
import json, pathlib, re, sys, difflib, datetime, urllib.request
from bs4 import BeautifulSoup
R=pathlib.Path(__file__).resolve().parent.parent; S=R/"snapshots"; S.mkdir(exist_ok=True)
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) Chrome/130 LimitWatch/0.1"}
def stamp_last_check():
    date=datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    p=R/"data"/"watch.json"
    data={"last_check":date}
    if p.exists():
        try:
            old=json.loads(p.read_text())
            if isinstance(old, dict):
                old["last_check"]=date; data=old
        except json.JSONDecodeError:
            pass
    p.write_text(json.dumps(data, indent=2)+"\n")
    return date
changed=False; report=[]; fetched=0
for t in json.load(open(R/"data/tools.json"))["tools"]:
    try:
        raw=urllib.request.urlopen(urllib.request.Request(t["url"],headers=UA),timeout=30).read().decode("utf-8","ignore")
    except Exception as ex:
        report.append(f"!! {t['id']}: fetch failed ({ex})"); continue
    s=BeautifulSoup(raw,"html.parser")
    for x in s(["script","style","noscript","svg"]): x.decompose()
    lines=[l.strip() for l in re.sub(r"[ \t]+"," ",s.get_text("\n")).splitlines() if l.strip()]
    if len(lines)<15 or "Just a moment" in raw[:2000]: report.append(f"?? {t['id']}: page looks blocked/JS-only ({len(lines)} lines) — check manually")
    f=S/f"{t['id']}.txt"; new="\n".join(lines)
    if f.exists():
        old=f.read_text().splitlines()
        d=list(difflib.unified_diff(old,lines,"previous","current",lineterm="",n=0))
        if d:
            changed=True; report.append(f"** {t['id']}: CHANGED\n"+"\n".join(d[:80]))
            (S/f"{t['id']}.{datetime.date.today()}.diff").write_text("\n".join(d))
        else: report.append(f"ok {t['id']}: no change")
    else: report.append(f"++ {t['id']}: first snapshot saved")
    f.write_text(new); fetched+=1
if fetched: report.append(f"last_check {stamp_last_check()}")
else: report.append("last_check unchanged (no pricing page fetched)")
print("\n".join(report)); sys.exit(1 if changed else 0)
