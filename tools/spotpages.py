"""Build one landing page per spot (spots/<id>/index.html), a spot index (spots/index.html)
and sitemap.xml from the site's own data in index.html.

Usage: python3 tools/spotpages.py
Reads index.html (SPOTS, SPOT_DETAIL, SPOT_PHOTOS, KLOOK data via tools/extract.js) and pins.md
(the Pexels photo used for each spot's Pinterest pin, so the landing page shows the same photo).
Prints CHANGED or UNCHANGED.
"""
import datetime, html, json, pathlib, re, subprocess, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://fc4405.github.io/tabihae/"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]

data = json.loads(subprocess.run(["node", str(ROOT / "tools/extract.js"), str(ROOT / "index.html")],
                                 check=True, capture_output=True, text=True).stdout)
SPOTS, DETAIL, PHOTOS = data["SPOTS"], data["SPOT_DETAIL"] or {}, data["SPOT_PHOTOS"] or {}
KCITY, R2K, MOODS = data["KLOOK_CITY"] or {}, data["REGION_TO_KLOOK"] or {}, data["MOOD_META"] or {}

# Latest scheduled Pexels photo per spot from pins.md
pexels = {}
for line in (ROOT / "pins.md").read_text(encoding="utf-8").splitlines():
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) >= 6 and cells[5].startswith("予約済み"):
        m = re.match(r"Pexels (\d+)（([^）]+)）", cells[3])
        if m:
            pexels[cells[1]] = (m.group(1), m.group(2))

e = lambda s: html.escape(str(s), quote=True)
en = lambda v: (v.get("en") if isinstance(v, dict) else v) if v is not None else None


def klook_url(region):
    city = KCITY.get(R2K.get(region, ""))
    if not city:
        return None
    prefix = "p" if city["type"] == "place" else "c"
    return (f"https://www.klook.com/en-US/destination/{prefix}{city['id']}-{city['slug']}/1-things-to-do/"
            "?aid=136969")


def next_month(months, today):
    if not months:
        return today.month
    ms = sorted(months)
    return next((m for m in ms if m >= today.month), ms[0])


def photo_for(sp):
    if sp["id"] in pexels:
        pid, who = pexels[sp["id"]]
        return {"src": f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=1200",
                "credit": f"Photo: {who} / Pexels", "link": f"https://www.pexels.com/photo/{pid}/"}
    arr = PHOTOS.get(sp["id"]) or []
    if arr:
        return {"src": arr[0]["url"].replace("width=640", "width=1200"),
                "credit": "Photo: Wikimedia Commons (see license)", "link": arr[0]["credit"]}
    return None


CSS = """
:root{--paper:#f2f3f1;--card:#fff;--ink:#121c26;--soft:#43515e;--faint:#74818c;--seal:#c63a25;--on-seal:#fff;
--indigo:#1f3d63;--line:rgba(18,28,38,.14);--gold:#9a6a0b;--gold-soft:#f1e6cb;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#0d141b;--card:#17212b;--ink:#eef2f5;
--soft:#b3bec8;--faint:#7f8c97;--seal:#f06a52;--on-seal:#1d0a06;--indigo:#8fb1e3;--line:rgba(255,255,255,.14);
--gold:#e6b657;--gold-soft:#3a2e14;color-scheme:dark}}
:root[data-theme="dark"]{--paper:#0d141b;--card:#17212b;--ink:#eef2f5;--soft:#b3bec8;--faint:#7f8c97;--seal:#f06a52;
--on-seal:#1d0a06;--indigo:#8fb1e3;--line:rgba(255,255,255,.14);--gold:#e6b657;--gold-soft:#3a2e14;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);
font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI","Hiragino Sans",sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--indigo)}.top{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 16px;
max-width:860px;margin:0 auto}.brand{font-family:"Shippori Mincho",Georgia,serif;font-weight:800;font-size:22px;
color:var(--ink);text-decoration:none;display:flex;align-items:center;gap:8px}.brand i{width:26px;height:26px;border-radius:4px;
background:var(--seal);color:var(--on-seal);display:grid;place-items:center;font-style:normal;font-size:15px}
.hero{max-width:860px;margin:0 auto;position:relative}.hero img{width:100%;max-height:72vh;object-fit:cover;display:block;
border-radius:0}@media (min-width:880px){.hero img{border-radius:8px}}.credit{font-size:12px;color:var(--faint);
padding:6px 16px 0;max-width:860px;margin:0 auto}.credit a{color:var(--faint)}
main{max-width:860px;margin:0 auto;padding:18px 16px 56px}h1{font-family:"Shippori Mincho",Georgia,serif;
font-size:clamp(30px,6vw,46px);line-height:1.15;margin:6px 0 10px;letter-spacing:-.01em}
.kicker{font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--seal);margin:0}
.hook{font-size:19px;color:var(--soft);margin:0 0 18px}.chips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 22px;padding:0;list-style:none}
.chips li{font-size:13px;font-weight:700;border:1px solid var(--line);border-radius:99px;padding:4px 12px;color:var(--soft)}
.cta{display:flex;flex-wrap:wrap;gap:10px;margin:8px 0 30px}.btn{display:inline-block;background:var(--seal);color:var(--on-seal);
text-decoration:none;font-weight:800;font-size:14px;padding:13px 20px;border-radius:4px}.btn.alt{background:transparent;
color:var(--ink);border:1px solid var(--line)}h2{font-family:"Shippori Mincho",Georgia,serif;font-size:24px;margin:32px 0 8px}
p{margin:0 0 12px}ul.list{padding-left:20px;margin:0 0 12px}ul.list li{margin:4px 0}
.note{background:var(--gold-soft);color:var(--gold);border-radius:6px;padding:12px 14px;font-size:14.5px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px;padding:0;list-style:none}
.grid a{display:block;background:var(--card);border:1px solid var(--line);border-radius:6px;padding:14px;text-decoration:none;color:var(--ink)}
.grid b{display:block}.grid span{font-size:13px;color:var(--faint)}footer{max-width:860px;margin:0 auto;padding:24px 16px 40px;
font-size:12.5px;color:var(--faint);border-top:1px solid var(--line)}
"""


def page(title, desc, url, body, image=None):
    og = f'<meta property="og:image" content="{e(image)}">' if image else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{e(url)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="article"><meta property="og:url" content="{e(url)}">{og}
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@700;800&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<header class="top"><a class="brand" href="{BASE}"><i>旅</i>TabiHae</a><a href="{BASE}spots/">All spots</a></header>
{body}
<footer>TabiHae is an independent Japan trip planner. Some links (marked Klook) are affiliate links: we may earn a
commission at no extra cost to you. Opening hours, prices and seasonal dates change, so check official sources before you go.</footer>
</body></html>
"""


today = datetime.date.today()
files = {}
for sp in SPOTS:
    d = DETAIL.get(sp["id"], {})
    url = f"{BASE}spots/{sp['id']}/"
    ph = photo_for(sp)
    hook = en(d.get("hook")) or sp.get("blurb", "")
    months = sp.get("months") or []
    month_names = ", ".join(MONTHS[m - 1] for m in sorted(months)) if len(months) < 12 else "All year"
    moods = [en(MOODS[m]) for m in sp.get("moods", []) if m in MOODS]
    nm = next_month(months, today)
    mood = (sp.get("moods") or [""])[0]
    planner = f"{BASE}?utm_source=pinterest#b2m{nm}n3ouslenv{mood}"
    k = klook_url(sp.get("region", ""))
    parts = []
    if ph:
        parts.append(f'<div class="hero"><img src="{e(ph["src"])}" alt="{e(sp["name"])}, {e(sp["region"])}" '
                     f'fetchpriority="high"></div><p class="credit"><a href="{e(ph["link"])}" rel="noopener">{e(ph["credit"])}</a></p>')
    parts.append("<main>")
    parts.append(f'<p class="kicker">{e(sp["region"])} · {e(sp.get("ja", ""))}</p><h1>{e(sp["name"])}</h1>'
                 f'<p class="hook">{e(hook)}</p>')
    chips = [f"Best: {month_names}"] + moods
    if en(d.get("time")):
        chips.append(f"Time: {en(d.get('time'))}")
    parts.append('<ul class="chips">' + "".join(f"<li>{e(c)}</li>" for c in chips) + "</ul>")
    cta = f'<a class="btn" href="{e(planner)}">Plan a {MONTHS[nm - 1]} route with this spot</a>'
    if k:
        cta += f'<a class="btn alt" href="{e(k)}" rel="sponsored noopener">Tours &amp; tickets nearby (Klook)</a>'
    parts.append(f'<div class="cta">{cta}</div>')
    story = en(d.get("story")) or sp.get("blurb", "")
    parts.append(f"<h2>Why go</h2><p>{e(story)}</p>")
    hl = en(d.get("highlights"))
    if hl:
        parts.append("<h2>What to do</h2><ul class='list'>" + "".join(f"<li>{e(x)}</li>" for x in hl) + "</ul>")
    if en(d.get("access")):
        parts.append(f"<h2>Getting there</h2><p>{e(en(d.get('access')))}</p>")
    if en(d.get("best")):
        parts.append(f"<h2>When to visit</h2><p>{e(en(d.get('best')))}</p>")
    pt = en(d.get("photoTips"))
    if pt:
        parts.append("<h2>Photo tips</h2><ul class='list'>" + "".join(f"<li>{e(x)}</li>" for x in pt) + "</ul>")
    nb = en(d.get("nearby"))
    if nb:
        parts.append("<h2>Nearby</h2><ul class='list'>" + "".join(f"<li>{e(x)}</li>" for x in nb) + "</ul>")
    tips = [x for x in [en(d.get("tip")), en(sp.get("etiquette"))] if x]
    if tips:
        parts.append("<h2>Good to know</h2>" + "".join(f'<p class="note">{e(x)}</p>' for x in tips))
    maps = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(f"{sp['name']} {sp.get('ja', '')}")
    parts.append(f'<p><a href="{e(maps)}" rel="noopener">Open in Google Maps</a></p>')
    parts.append(f'<div class="cta"><a class="btn" href="{e(planner)}">Build your Japan itinerary on TabiHae</a></div></main>')
    title = f"{sp['name']}, {sp['region']}: Japan Travel Guide | TabiHae"
    desc = f"{hook} Best months, how to get there, photo tips and etiquette for {sp['name']}."[:300]
    files[f"spots/{sp['id']}/index.html"] = page(title, desc, url, "\n".join(parts), ph["src"] if ph else None)

items = "".join(f'<li><a href="{BASE}spots/{s["id"]}/"><b>{e(s["name"])}</b><span>{e(s["region"])}</span></a></li>'
                for s in sorted(SPOTS, key=lambda s: (s["region"], s["name"])))
files["spots/index.html"] = page("Japan Travel Spots by Region | TabiHae",
                                 "Guides to photogenic places across Japan: best months, access, photo tips and etiquette.",
                                 f"{BASE}spots/", f'<main><h1>Japan spots</h1><ul class="grid">{items}</ul></main>')

urls = [BASE, f"{BASE}spots/"] + [f"{BASE}spots/{s['id']}/" for s in SPOTS]
files["sitemap.xml"] = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                        + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>\n")

changed = False
for rel, content in files.items():
    p = ROOT / rel
    if not p.exists() or p.read_text(encoding="utf-8") != content:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        changed = True
print("CHANGED" if changed else "UNCHANGED")
