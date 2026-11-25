"""Regenerate the two static GitHub Pages documents."""
import argparse
import json
from pathlib import Path
from html import escape as esc

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--site-url", help="Published base URL, including any repository path")
location = parser.parse_args().site_url
languages = {
    "en": ("English", "index.html", "index.html"),
    "ja": ("日本語", "ja.html", "ja.html"),
}

for lang, page in json.loads((root / "content.json").read_text(encoding="utf-8")).items():
    h1, intro, hw, date, status, passed, pending, sections, footer = (page[k] for k in ("title", "intro", "hardware", "date", "status", "passed", "pending", "sections", "footer"))
    photos = "".join(f'<figure><a href="{esc(path)}"><img src="{esc(path)}" width="{w}" height="{h}" alt="{esc(caption,quote=True)}" decoding="async"></a><figcaption><strong>{esc(title)}</strong> {esc(caption)}</figcaption></figure>' for path,w,h,title,caption in page.get("photos", []))
    metadata = ''
    if location:
        origin = esc(location.rstrip('/'), quote=True)
        page_url = origin + ("/" if lang == "en" else "/ja.html")
        metadata = f'''<link rel="canonical" href="{page_url}">
<link rel="alternate" hreflang="en" href="{origin}/">
<link rel="alternate" hreflang="ja" href="{origin}/ja.html">
<meta property="og:type" content="article"><meta property="og:url" content="{page_url}">
<meta property="og:title" content="{esc(h1, quote=True)}">
<meta property="og:description" content="{esc(intro, quote=True)}">
<meta property="og:image" content="{origin}/images/r2-desktop.jpeg">
<meta name="twitter:card" content="summary_large_image">'''
    nav = "".join(f'<a href="#{key}">{esc(title)}</a>' for key,title,_ in sections)
    main = "".join(f'<section id="{key}"><h2>{esc(title)}</h2>{"".join(f"<p>{p}</p>" for p in paras)}</section>' for key,title,paras in sections)
    badges = "".join(f'<li><b>{esc(h)}</b></li>' for h in hw)
    lists = lambda xs: "".join(f"<li>{esc(s)}</li>" for s in xs)
    switch = "".join(
        f'<span aria-current="page">{name}</span>' if code == lang
        else f'<a href="{url}" lang="{code}" hreflang="{code}">{name}</a>'
        for code, (name, url, _) in languages.items()
    )
    html = f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(h1)}</title><meta name="description" content="{esc(intro,quote=True)}">{metadata}<link rel="stylesheet" href="style.css"></head>
<body><header><div class="wrap"><div class="label">OMARCHY / FIELD NOTES</div><nav class="lang" aria-label="Language">{switch}</nav></div></header>
<div class="hero"><div class="wrap"><div class="eyebrow">{esc(date)}</div><h1>{esc(h1)}</h1><p class="intro">{esc(intro)}</p><ul class="spec">{badges}</ul></div></div>
<main class="wrap"><div class="comparison">{photos}</div><nav class="toc" aria-label="Contents">{nav}</nav><div class="article"><article>{main}</article><aside class="callouts"><h2>{esc(status[0])}</h2><h3>{esc(status[1])}</h3><ul>{lists(passed)}</ul><h3 class="pending">{esc(status[2])}</h3><ul>{lists(pending)}</ul></aside></div></main>
<footer><div class="wrap">{esc(footer)}</div></footer></body></html>"""
    _, _, filename = languages[lang]
    (root / "docs" / filename).write_text(html + "\n", encoding="utf-8")
