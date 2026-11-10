#!/usr/bin/env python3
"""Regenerate search-index.json, sitemap.xml and rss.xml from the posts/
directory. Run this after adding new posts (the daily publishing routine
runs it as its final step before committing).

Usage: python3 scripts/rebuild_indexes.py
"""
import html
import pathlib
import re
import datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
POSTS = ROOT / "posts"
SITE_URL = "https://thesouthernwire.netlify.app"  # update once a custom domain is live

TITLE_RE = re.compile(r"<h1>(.*?)</h1>", re.S)
TAG_RE = re.compile(r'<span class="tag"[^>]*>(.*?)</span>', re.S)
DESC_RE = re.compile(r'<p class="dek">(.*?)</p>', re.S)

def strip_tags(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

def parse_post(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    m = TITLE_RE.search(text)
    title = strip_tags(m.group(1)) if m else path.stem
    t = TAG_RE.search(text)
    category = strip_tags(t.group(1)) if t else "News"
    # date comes from the filename prefix: YYYY-MM-DD-slug.html
    date_match = re.match(r"(\d{4})-(\d{2})-(\d{2})-", path.name)
    date_iso = "-".join(date_match.groups()) if date_match else ""
    return {
        "title": title,
        "category": category,
        "date": date_iso,
        "url": f"posts/{path.name}",
    }

def build_search_index(posts):
    import json
    (ROOT / "search-index.json").write_text(
        json.dumps(posts, ensure_ascii=False, indent=0), encoding="utf-8"
    )

def build_sitemap(posts):
    urls = ["", "crime.html", "politics.html", "business.html", "sport.html",
            "tech.html", "screen.html", "world.html", "weather.html",
            "lifestyle.html", "about.html", "privacy.html", "terms.html",
            "contact.html", "archive/index.html"]
    urls += [p["url"] for p in posts]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append(f"  <url><loc>{SITE_URL}/{u}</loc></url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")

def build_rss(posts):
    latest = sorted(posts, key=lambda p: p["date"], reverse=True)[:30]
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    items = []
    for p in latest:
        items.append(
            "  <item>\n"
            f"    <title>{html.escape(p['title'])}</title>\n"
            f"    <link>{SITE_URL}/{p['url']}</link>\n"
            f"    <guid>{SITE_URL}/{p['url']}</guid>\n"
            f"    <category>{html.escape(p['category'])}</category>\n"
            f"    <pubDate>{p['date']}</pubDate>\n"
            "  </item>"
        )
    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>\n'
        "  <title>The Southern Wire</title>\n"
        f"  <link>{SITE_URL}/</link>\n"
        "  <description>Daily South African, African and world news commentary.</description>\n"
        f"  <lastBuildDate>{now}</lastBuildDate>\n"
        + "\n".join(items) +
        "\n</channel></rss>\n"
    )
    (ROOT / "rss.xml").write_text(rss, encoding="utf-8")

def main():
    posts = [parse_post(p) for p in sorted(POSTS.glob("*.html"))]
    build_search_index(posts)
    build_sitemap(posts)
    build_rss(posts)
    print(f"Indexed {len(posts)} posts -> search-index.json, sitemap.xml, rss.xml")

if __name__ == "__main__":
    main()
