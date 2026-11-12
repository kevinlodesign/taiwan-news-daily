#!/usr/bin/env python3
"""Build the static site from data/*.json.

Usage:  python3 scripts/build.py
Output: days/YYYY-MM-DD.html for every data file, plus index.html.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DAYS = ROOT / "days"
SITE_TITLE = "台灣國際新聞摘要"
WEEKDAYS = "一二三四五六日"

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700'
    '&family=Noto+Serif+TC:wght@600;700&display=swap" rel="stylesheet">'
)

URL_RE = re.compile(r"(https?://[^\s，。、）)]+)")


def e(text):
    return html.escape(str(text or ""), quote=True)


def linkify(text):
    """Escape text, then turn bare URLs into links."""
    out, last = [], 0
    for m in URL_RE.finditer(text or ""):
        out.append(e(text[last:m.start()]))
        url = m.group(1)
        out.append(f'<a href="{e(url)}" target="_blank" rel="noopener">{e(url)}</a>')
        last = m.end()
    out.append(e((text or "")[last:]))
    return "".join(out)


def weekday(date_str):
    import datetime as dt
    d = dt.date.fromisoformat(date_str)
    return f"週{WEEKDAYS[d.weekday()]}"


def page(title, body, depth=0):
    prefix = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="zh-Hant-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
{FONTS}
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<header class="masthead">
  <a class="brand" href="{prefix}index.html">{SITE_TITLE}</a>
  <span class="tagline">每天 06:00 前更新｜世界怎麼報導台灣</span>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <p>所有摘要皆為改寫，完整內容請點原文連結。資料由 Claude 自動蒐集整理，可能有遺漏或誤差，引用前請查證原文。</p>
</footer>
</body>
</html>
"""


def render_sources(sources):
    parts = []
    for s in sources:
        time = f'<span class="time">{e(s.get("time"))}</span>' if s.get("time") else ""
        parts.append(
            f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["outlet"])}</a>{time}</li>'
        )
    return f'<ul class="sources">{"".join(parts)}</ul>'


CATEGORY_IDS = {"security", "diplomacy", "finance", "semiconductor", "tech", "society"}


def render_figure(item, cat_id):
    """Licensed photo if given, otherwise the category cover. Falls back on load error."""
    fallback = f"../assets/cat/{cat_id if cat_id in CATEGORY_IDS else 'society'}.svg"
    img = item.get("image") or {}
    if img.get("url"):
        credit = e(img.get("credit"))
        if img.get("source"):
            credit = f'<a href="{e(img["source"])}" target="_blank" rel="noopener">{credit}</a>'
        return (
            '<figure class="thumb">'
            f'<img src="{e(img["url"])}" alt="" loading="lazy" '
            f"onerror=\"this.onerror=null;this.src='{fallback}';"
            "this.parentNode.classList.add('is-fallback')\">"
            f"<figcaption>{credit}</figcaption></figure>"
        )
    return f'<figure class="thumb is-cover"><img src="{fallback}" alt="" loading="lazy"></figure>'


def render_item(item, n, cat_id):
    tags = ""
    if item.get("prc"):
        tags += '<span class="tag tag-prc">中方官媒觀點</span>'
    if item.get("tag"):
        tags += f'<span class="tag">{e(item["tag"])}</span>'
    local = ""
    for loc in item.get("local", []):
        local += (
            '<div class="local"><span class="local-label">台灣媒體對照</span>'
            f'<a href="{e(loc["url"])}" target="_blank" rel="noopener">{e(loc["outlet"])}</a>'
            f'<p>{e(loc.get("note"))}</p></div>'
        )
    note = f'<p class="note">{linkify(item["note"])}</p>' if item.get("note") else ""
    return f"""<article class="item">
  <div class="item-head"><span class="num">{n:02d}</span><h3>{e(item["title"])}</h3></div>
  <div class="item-body">
    {render_figure(item, cat_id)}
    <div class="item-text">
      {f'<div class="tags">{tags}</div>' if tags else ''}
      <p class="summary">{e(item["summary"])}</p>
      {render_sources(item.get("sources", []))}
    </div>
  </div>
  {local}
  {note}
</article>"""


def render_day(d):
    date = d["date"]
    count = sum(len(c["items"]) for c in d["categories"])
    hl = "".join(f"<li>{e(h)}</li>" for h in d.get("highlights", []))
    edition = (
        f'<p class="edition-note">{e(d["edition_note"])}</p>' if d.get("edition_note") else ""
    )
    sections, n = [], 0
    for i, cat in enumerate(d["categories"], 1):
        if not cat["items"]:
            continue
        items = []
        for it in cat["items"]:
            n += 1
            items.append(render_item(it, n, cat["id"]))
        sections.append(
            f'<section class="category" id="{e(cat["id"])}">'
            f'<h2><span class="cat-num">{i}</span>{e(cat["name"])}'
            f'<span class="cat-count">{len(cat["items"])} 則</span></h2>'
            f'{"".join(items)}</section>'
        )
    toc = "".join(
        f'<a href="#{e(c["id"])}">{e(c["name"])}</a>' for c in d["categories"] if c["items"]
    )
    notes = d.get("search_notes", {})
    notes_html = ""
    if notes.get("not_found") or notes.get("paywalled"):
        nf = "".join(f"<li>{e(x)}</li>" for x in notes.get("not_found", []))
        pw = "".join(f"<li>{e(x)}</li>" for x in notes.get("paywalled", []))
        notes_html = '<section class="search-notes"><h2>搜尋紀錄</h2>'
        if nf:
            notes_html += f"<h4>沒有找到相關報導的媒體</h4><ul>{nf}</ul>"
        if pw:
            notes_html += f"<h4>付費牆／只看得到標題或導言</h4><ul>{pw}</ul>"
        notes_html += "</section>"
    body = f"""<div class="day-head">
  <p class="dateline">{e(date)}　{weekday(date)}</p>
  <h1>今日台灣國際新聞</h1>
  <p class="meta">收錄時間：{e(d.get("window"))}｜共 {count} 則</p>
  {edition}
</div>
<section class="highlights">
  <h2>今日 3 大重點</h2>
  <ol>{hl}</ol>
</section>
<nav class="toc">{toc}</nav>
{"".join(sections)}
{notes_html}
<p class="back"><a href="../index.html">← 所有日期</a></p>"""
    return page(f"{date}｜{SITE_TITLE}", body, depth=1), count


def main():
    DAYS.mkdir(exist_ok=True)
    days = []
    for f in sorted(DATA.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        html_text, count = render_day(d)
        (DAYS / f"{d['date']}.html").write_text(html_text, encoding="utf-8")
        days.append((d, count))
    days.sort(key=lambda x: x[0]["date"], reverse=True)

    if days:
        latest, lcount = days[0]
        hl = "".join(f"<li>{e(h)}</li>" for h in latest.get("highlights", []))
        latest_html = f"""<section class="latest">
  <p class="dateline">最新一期｜{e(latest["date"])}　{weekday(latest["date"])}</p>
  <h1>今日 3 大重點</h1>
  <ol class="hl-big">{hl}</ol>
  <a class="cta" href="days/{e(latest["date"])}.html">閱讀完整 {lcount} 則 →</a>
</section>"""
    else:
        latest_html = "<p>尚無資料。</p>"
    rows = "".join(
        f'<li><a href="days/{e(d["date"])}.html"><span class="a-date">{e(d["date"])}</span>'
        f'<span class="a-wd">{weekday(d["date"])}</span>'
        f'<span class="a-hl">{e((d.get("highlights") or [""])[0])}</span>'
        f'<span class="a-count">{c} 則</span></a></li>'
        for d, c in days
    )
    body = f"""{latest_html}
<section class="archive">
  <h2>所有日期</h2>
  <ul>{rows}</ul>
</section>"""
    (ROOT / "index.html").write_text(page(SITE_TITLE, body), encoding="utf-8")
    print(f"built {len(days)} day page(s) + index.html")


if __name__ == "__main__":
    main()
