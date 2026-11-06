"""Render a TabiHae Pinterest card (1000x1500 PNG) with no third-party photos.

Usage: python3 tools/pincard.py <card.json> <out.png>
card.json keys: kanji, kicker, title, region, season, tip, accent (optional hex)
Everything on the card is text and simple shapes drawn here, so the image is ours.
"""
import html, json, sys
from playwright.sync_api import sync_playwright

c = json.load(open(sys.argv[1], encoding="utf-8"))
e = {k: html.escape(str(v)) for k, v in c.items()}
accent = c.get("accent", "#c63a25")

page_html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0}}
body{{width:1000px;height:1500px;background:#f2f3f1;color:#121c26;font-family:"Noto Sans CJK JP","DejaVu Sans",sans-serif;overflow:hidden;position:relative}}
.top{{height:740px;background:linear-gradient(165deg,#0f2238 0%,#1f3d63 62%,#2a4f78 100%);position:relative;overflow:hidden;padding:84px 80px}}
.kanji{{position:absolute;right:-20px;bottom:-70px;font-size:440px;font-weight:300;line-height:1;color:rgba(255,255,255,.07);letter-spacing:-.04em}}
.ring{{position:absolute;border-radius:50%;border:2px solid rgba(255,255,255,.12)}}
.dot{{position:absolute;border-radius:50%;background:{accent};opacity:.9}}
.kicker{{display:flex;align-items:center;gap:16px;color:#c9d6e5;font-size:28px;font-weight:700;letter-spacing:.18em;text-transform:uppercase}}
.kicker:before{{content:"";width:16px;height:16px;background:{accent}}}
h1{{font-family:"Liberation Serif","DejaVu Serif",serif;font-weight:700;color:#fff;font-size:92px;line-height:1.04;margin-top:44px;max-width:820px;letter-spacing:-.01em}}
.region{{color:#c9d6e5;font-size:34px;margin-top:34px;font-weight:500}}
.bottom{{padding:64px 80px 0}}
.row{{display:flex;gap:28px;align-items:stretch}}
.box{{flex:1;border-top:3px solid #121c26;padding-top:22px}}
.lab{{font-size:24px;font-weight:900;letter-spacing:.16em;text-transform:uppercase;color:#74818c}}
.val{{font-size:44px;font-weight:900;margin-top:10px;line-height:1.2}}
.tip{{margin-top:48px;background:#fff;border-left:10px solid {accent};padding:34px 38px;font-size:33px;line-height:1.5;color:#2c3a47}}
.tip b{{display:block;font-size:24px;letter-spacing:.16em;text-transform:uppercase;color:{accent};margin-bottom:12px}}
.foot{{position:absolute;left:80px;right:80px;bottom:56px;display:flex;align-items:center;justify-content:space-between;border-top:1px solid rgba(18,28,38,.2);padding-top:30px}}
.brand{{display:flex;align-items:center;gap:18px;font-family:"Liberation Serif",serif;font-size:46px;font-weight:700}}
.seal{{width:58px;height:58px;border-radius:6px;background:{accent};color:#fff;display:grid;place-items:center;font-size:34px;font-weight:900;font-family:"Noto Sans CJK JP"}}
.url{{font-size:26px;color:#43515e;font-weight:500}}
</style></head><body>
<div class="top">
  <div class="ring" style="width:520px;height:520px;right:-140px;top:-160px"></div>
  <div class="ring" style="width:300px;height:300px;right:-30px;top:-50px"></div>
  <div class="dot" style="width:46px;height:46px;right:120px;top:300px"></div>
  <div class="kanji">{e['kanji']}</div>
  <div class="kicker">{e['kicker']}</div>
  <h1>{e['title']}</h1>
  <div class="region">{e['region']}</div>
</div>
<div class="bottom">
  <div class="row">
    <div class="box"><div class="lab">When</div><div class="val">{e['season']}</div></div>
    <div class="box"><div class="lab">Where</div><div class="val">{e['where']}</div></div>
  </div>
  <div class="tip"><b>Good to know</b>{e['tip']}</div>
</div>
<div class="foot"><div class="brand"><div class="seal">旅</div>TabiHae</div><div class="url">Japan trip planner · fc4405.github.io/tabihae</div></div>
</body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1000, "height": 1500}, device_scale_factor=1)
    pg.set_content(page_html)
    pg.wait_for_timeout(300)
    pg.screenshot(path=sys.argv[2])
    b.close()
print("wrote", sys.argv[2])
