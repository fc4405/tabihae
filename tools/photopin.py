"""Put a title over a photo to make a 1000x1500 Pinterest pin (PNG/JPEG).

Usage: python3 tools/photopin.py <photo.jpg> <pin.json> <out.jpg>
pin.json keys: kicker (e.g. "KYOTO · AUTUMN"), title (2-3 short lines max),
               sub (optional, e.g. "Best: mid-Nov – early Dec"), credit (e.g. "Photo: Name / Pexels")
The photo is cropped to 2:3 (centre, or "focus": "top"/"bottom" in pin.json).
"""
import base64, html, json, mimetypes, pathlib, sys
from playwright.sync_api import sync_playwright

photo, spec, out = sys.argv[1:4]
c = json.load(open(spec, encoding="utf-8"))
e = {k: html.escape(str(v)) for k, v in c.items()}
mime = mimetypes.guess_type(photo)[0] or "image/jpeg"
data = base64.b64encode(pathlib.Path(photo).read_bytes()).decode()
pos = {"top": "center 20%", "bottom": "center 80%"}.get(c.get("focus"), "center")

page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;box-sizing:border-box}}
body{{width:1000px;height:1500px;position:relative;overflow:hidden;background:#111;font-family:"Noto Sans CJK JP","DejaVu Sans",sans-serif}}
.ph{{position:absolute;inset:0;background:url(data:{mime};base64,{data}) {pos}/cover no-repeat}}
.shade{{position:absolute;inset:0;background:linear-gradient(to bottom,rgba(0,0,0,.55) 0%,rgba(0,0,0,.12) 32%,rgba(0,0,0,0) 55%,rgba(0,0,0,.25) 78%,rgba(0,0,0,.6) 100%)}}
.top{{position:absolute;left:70px;right:70px;top:80px;color:#fff;text-shadow:0 2px 18px rgba(0,0,0,.45)}}
.kicker{{display:inline-block;background:#c63a25;color:#fff;font-size:26px;font-weight:900;letter-spacing:.16em;padding:10px 18px;text-shadow:none}}
h1{{font-family:"Liberation Serif","DejaVu Serif",serif;font-size:96px;line-height:1.02;font-weight:700;margin-top:28px;letter-spacing:-.01em}}
.sub{{font-size:36px;font-weight:700;margin-top:24px}}
.foot{{position:absolute;left:70px;right:70px;bottom:60px;display:flex;align-items:flex-end;justify-content:space-between;color:#fff}}
.brand{{display:flex;align-items:center;gap:16px;font-family:"Liberation Serif",serif;font-size:44px;font-weight:700;text-shadow:0 2px 12px rgba(0,0,0,.5)}}
.seal{{width:54px;height:54px;border-radius:6px;background:#c63a25;display:grid;place-items:center;font-family:"Noto Sans CJK JP";font-size:32px;font-weight:900}}
.credit{{font-size:20px;opacity:.85;text-align:right;max-width:420px}}
</style></head><body><div class="ph"></div><div class="shade"></div>
<div class="top"><span class="kicker">{e['kicker']}</span><h1>{e['title']}</h1>{f'<div class="sub">{e["sub"]}</div>' if c.get('sub') else ''}</div>
<div class="foot"><div class="brand"><div class="seal">旅</div>TabiHae</div><div class="credit">{e.get('credit','')}</div></div>
</body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1000, "height": 1500})
    pg.set_content(page)
    pg.wait_for_timeout(300)
    pg.screenshot(path=out, type="jpeg" if out.lower().endswith((".jpg", ".jpeg")) else "png", **({"quality": 88} if out.lower().endswith((".jpg", ".jpeg")) else {}))
    b.close()
print("wrote", out)
