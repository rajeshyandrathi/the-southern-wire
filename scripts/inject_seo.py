#!/usr/bin/env python3
"""Idempotently add SEO tags to every HTML page, inside a marked block
placed right after the <title> line:

  * <link rel="canonical"> for the page's own URL
  * a meta description, og:title/description/url/type/site_name and
    twitter:card -- only where the page does not already have its own
  * structured data (JSON-LD): NewsArticle on posts, WebSite + Organization
    on the homepage

Re-running recomputes the block from the page as it is now, so run it after
every build (the homepage and archive snapshots are copies of each other and
need different canonical URLs).

Usage: python3 scripts/inject_seo.py
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://thesouthernwire.co.za"
NAME = "The Southern Wire"
LOGO = SITE + "/assets/brand/x-avatar-1200.png"
BLOCK_RE = re.compile(r"<!-- seo \(sw-seo\) -->.*?<!-- /seo \(sw-seo\) -->\n", re.S)


def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def clip(s, n=158):
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0].rstrip(",;:—-")
    return cut + "…"


def attr(s):
    return html.escape(s, quote=True)


def has(text, pattern):
    return re.search(pattern, text) is not None


def page_url(rel):
    if rel == "index.html":
        return SITE + "/"
    return f"{SITE}/{rel}"


def describe(text):
    for pat in (r'<p class="dek">(.*?)</p>', r'<p class="lede">(.*?)</p>',
                r'<meta property="og:description" content="([^"]*)"',
                r"<article[^>]*>.*?<p>(.*?)</p>", r'<p class="summary">(.*?)</p>'):
        m = re.search(pat, text, re.S)
        if m and strip_tags(m.group(1)):
            return clip(strip_tags(m.group(1)))
    return f"{NAME}: South African and world news, explained clearly every day."


def process(path):
    rel = path.relative_to(ROOT).as_posix()
    original = path.read_text(encoding="utf-8")
    text = BLOCK_RE.sub("", original)
    if "<title>" not in text:
        return False
    url = page_url(rel)
    title_m = re.search(r"<title>(.*?)</title>", text, re.S)
    page_title = strip_tags(title_m.group(1)) if title_m else NAME
    h1 = re.search(r"<h1>(.*?)</h1>", text, re.S)
    headline = strip_tags(h1.group(1)) if h1 else page_title
    desc = describe(text)
    is_post = rel.startswith("posts/")

    lines = [f'<link rel="canonical" href="{attr(url)}">']
    if not has(text, r'<meta name="description"'):
        lines.append(f'<meta name="description" content="{attr(desc)}">')
    if not has(text, r'property="og:title"'):
        lines.append(f'<meta property="og:title" content="{attr(headline if is_post else page_title)}">')
    if not has(text, r'property="og:description"'):
        lines.append(f'<meta property="og:description" content="{attr(desc)}">')
    if not has(text, r'property="og:url"'):
        lines.append(f'<meta property="og:url" content="{attr(url)}">')
    if not has(text, r'property="og:type"'):
        lines.append(f'<meta property="og:type" content="{"article" if is_post else "website"}">')
    if not has(text, r'property="og:site_name"'):
        lines.append(f'<meta property="og:site_name" content="{NAME}">')
    if not has(text, r'name="twitter:card"'):
        lines.append('<meta name="twitter:card" content="summary_large_image">')

    publisher = {"@type": "Organization", "name": NAME, "url": SITE + "/",
                 "logo": {"@type": "ImageObject", "url": LOGO}}
    data = None
    if is_post:
        img = re.search(r'<meta property="og:image" content="([^"]+)"', text)
        date = re.match(r"(\d{4}-\d{2}-\d{2})-", path.name)
        byline = re.search(r'<div class="byline">([^<]*)', text)
        section = re.search(r'<span class="tag"[^>]*>(.*?)</span>', text, re.S)
        data = {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": clip(headline, 110),
            "description": desc,
            "mainEntityOfPage": {"@type": "WebPage", "@id": url},
            "url": url,
            "author": {"@type": "Organization",
                       "name": f"{NAME} {strip_tags(byline.group(1))}" if byline and strip_tags(byline.group(1)) else NAME,
                       "url": SITE + "/about.html"},
            "publisher": publisher,
            "inLanguage": "en-ZA",
        }
        if img:
            data["image"] = [html.unescape(img.group(1))]
        if date:
            data["datePublished"] = data["dateModified"] = date.group(1)
        if section:
            data["articleSection"] = strip_tags(section.group(1))
    elif rel == "index.html":
        data = {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "WebSite", "name": NAME, "url": SITE + "/", "inLanguage": "en-ZA"},
                dict(publisher, **{"@type": "NewsMediaOrganization",
                                   "email": "thesouthernwireza@gmail.com",
                                   "publishingPrinciples": SITE + "/about.html"}),
            ],
        }
    if data:
        js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        lines.append(f'<script type="application/ld+json">{js}</script>')

    block = "<!-- seo (sw-seo) -->\n" + "\n".join(lines) + "\n<!-- /seo (sw-seo) -->\n"
    new = re.sub(r"(<title>.*?</title>[^\n]*\n)", lambda m: m.group(1) + block, text, count=1, flags=re.S)
    if new != original:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main():
    pages = sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("posts/*.html")) + sorted(ROOT.glob("archive/*.html"))
    changed = sum(process(p) for p in pages)
    print(f"SEO: {changed} pages updated, {len(pages)} pages checked")


if __name__ == "__main__":
    main()
