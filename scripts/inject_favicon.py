#!/usr/bin/env python3
"""Idempotently insert a favicon <link> into every HTML page."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

def process(path: pathlib.Path, prefix: str):
    text = path.read_text(encoding="utf-8")
    if "favicon.svg" in text:
        return False
    marker = f'<link rel="stylesheet" href="{prefix}assets/widgets.css">'
    if marker not in text:
        print(f"SKIP (no widgets.css link found): {path}")
        return False
    favicon_tag = f'<link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg">\n{marker}'
    text = text.replace(marker, favicon_tag, 1)
    path.write_text(text, encoding="utf-8")
    return True

def main():
    changed = 0
    root_pages = ["index.html", "crime.html", "politics.html", "business.html", "sport.html",
                  "tech.html", "screen.html", "world.html", "weather.html", "lifestyle.html",
                  "about.html", "privacy.html", "terms.html", "contact.html"]
    for name in root_pages:
        p = ROOT / name
        if p.exists() and process(p, ""):
            changed += 1
    for p in sorted((ROOT / "archive").glob("*.html")):
        if process(p, "../"):
            changed += 1
    for p in sorted((ROOT / "posts").glob("*.html")):
        if process(p, "../"):
            changed += 1
    print(f"Updated {changed} files.")

if __name__ == "__main__":
    main()
