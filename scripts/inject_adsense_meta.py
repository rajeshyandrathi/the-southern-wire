#!/usr/bin/env python3
"""Idempotently insert the Google AdSense site-verification <meta> tag
into every HTML page."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
META_TAG = '<meta name="google-adsense-account" content="ca-pub-2954954234821721">'

def process(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    if "google-adsense-account" in text:
        return False
    marker = "<head>"
    if marker not in text:
        print(f"SKIP (no <head> found): {path}")
        return False
    text = text.replace(marker, marker + "\n" + META_TAG, 1)
    path.write_text(text, encoding="utf-8")
    return True

def main():
    changed = 0
    root_pages = ["index.html", "crime.html", "politics.html", "business.html", "sport.html",
                  "tech.html", "screen.html", "world.html", "weather.html", "lifestyle.html",
                  "about.html", "privacy.html", "terms.html", "contact.html"]
    for name in root_pages:
        p = ROOT / name
        if p.exists() and process(p):
            changed += 1
    for p in sorted((ROOT / "archive").glob("*.html")):
        if process(p):
            changed += 1
    for p in sorted((ROOT / "posts").glob("*.html")):
        if process(p):
            changed += 1
    print(f"Updated {changed} files.")

if __name__ == "__main__":
    main()
