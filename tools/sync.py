"""Copy the TabiHae artifact HTML into index.html for the public site.

Usage: python3 tools/sync.py <artifact.html>
Adds search/share metadata after the viewport tag, then writes index.html
and refreshes sitemap.xml's lastmod. Prints CHANGED or UNCHANGED.
"""
import datetime, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = "https://fc4405.github.io/tabihae/"
META = (
    '<meta name="description" content="Plan a photogenic Japan trip: curated spots by mood and season, '
    'ready-made routes, live seasonal notes, and etiquette tips in English, Japanese, Korean, '
    'Traditional Chinese and Thai.">'
    '<meta property="og:title" content="TabiHae — photogenic Japan trip planner">'
    '<meta property="og:description" content="Curated Japan spots by mood and season, with ready-made '
    'routes and live seasonal notes.">'
    f'<meta property="og:type" content="website"><meta property="og:url" content="{URL}">'
    f'<meta name="twitter:card" content="summary_large_image"><link rel="canonical" href="{URL}">'
)
ANCHOR = 'viewport-fit=cover">'

src = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
if 'og:title' not in src:
    if ANCHOR not in src:
        sys.exit("viewport tag not found; artifact layout changed")
    src = src.replace(ANCHOR, ANCHOR + META, 1)
if "TabiHae" not in src[:20000]:
    sys.exit("TabiHae title not found; refusing to overwrite")

out = ROOT / "index.html"
old = out.read_text(encoding="utf-8") if out.exists() else ""
if old == src:
    print("UNCHANGED")
    sys.exit(0)
out.write_text(src, encoding="utf-8")
today = datetime.date.today().isoformat()
(ROOT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    f'<url><loc>{URL}</loc><lastmod>{today}</lastmod></url></urlset>\n', encoding="utf-8")
print("CHANGED")
