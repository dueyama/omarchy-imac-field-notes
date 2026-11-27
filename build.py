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


def render_chapters(sections, chapters):
    by_id = {key: (title, paragraphs) for key, title, paragraphs in sections}
    chapter_ids = [key for key, _, _ in chapters]
    note_ids = [key for _, _, keys in chapters for key in keys]
    if (len(by_id) != len(sections) or len(note_ids) != len(sections)
            or set(note_ids) != set(by_id) or len(set(chapter_ids)) != len(chapter_ids)
            or set(chapter_ids) & by_id.keys()):
        raise ValueError("Chapter and note IDs must be unique and cover all sections")

    contents = []
    article = []
    for chapter, title, keys in chapters:
        links = "".join(f'<li><a href="#{esc(key)}">{esc(by_id[key][0])}</a></li>' for key in keys)
        contents.append(f'<div class="toc-group"><a class="toc-heading" href="#{esc(chapter)}">'
                        f'{esc(title)}</a><ul>{links}</ul></div>')
        article.append(f'<section class="chapter" id="{esc(chapter)}"><h2>{esc(title)}</h2>')
        for key in keys:
            heading, paragraphs = by_id[key]
            body = "\n".join(f"<p>{paragraph}</p>" for paragraph in paragraphs)
            article.append(f'<section id="{esc(key)}"><h3>{esc(heading)}</h3>\n{body}\n</section>')
        article.append("</section>")
    return "\n".join(contents), "\n".join(article)


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
    nav, main = render_chapters(sections, page["chapters"])
    badges = "".join(f'<li><b>{esc(h)}</b></li>' for h in hw)
    lists = lambda xs: "".join(f"<li>{esc(s)}</li>" for s in xs)
    switch = "".join(
        f'<span aria-current="page">{name}</span>' if code == lang
        else f'<a href="{url}" lang="{code}" hreflang="{code}">{name}</a>'
        for code, (name, url, _) in languages.items()
    )
    nav_label = "サイトナビゲーション" if lang == "ja" else "Site navigation"
    contents_label = "目次" if lang == "ja" else "Contents"
    html = f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(h1)}</title><meta name="description" content="{esc(intro,quote=True)}">{metadata}<link rel="stylesheet" href="style.css"></head>
<body><header><div class="wrap"><div class="label">OMARCHY / FIELD NOTES</div><nav class="lang" aria-label="{nav_label}"><a href="https://github.com/dueyama/omarchy-imac-field-notes">GitHub</a>{switch}</nav></div></header>
<div class="hero"><div class="wrap"><div class="eyebrow">{esc(date)}</div><h1>{esc(h1)}</h1><p class="intro">{esc(intro)}</p><ul class="spec">{badges}</ul></div></div>
<main class="wrap"><div class="comparison">{photos}</div><nav class="toc" aria-label="{contents_label}">{nav}</nav><div class="article"><article>{main}</article><aside class="callouts"><h2>{esc(status[0])}</h2><h3>{esc(status[1])}</h3><ul>{lists(passed)}</ul><h3 class="pending">{esc(status[2])}</h3><ul>{lists(pending)}</ul></aside></div></main>
<footer><div class="wrap">{esc(footer)}</div></footer></body></html>"""
    _, _, filename = languages[lang]
    (root / "docs" / filename).write_text(html + "\n", encoding="utf-8")
