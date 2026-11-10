#!/usr/bin/env python3
"""Idempotently insert <link>/<script> tags for the shared assets
(widgets.css, config.js, site.js) into every existing HTML page that
doesn't already have them. Safe to re-run: skips files that already
reference assets/site.js.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

def process(path: pathlib.Path, prefix: str):
    text = path.read_text(encoding="utf-8")
    if "assets/site.js" in text:
        return False
    if "<style>" not in text or "</body>" not in text:
        print(f"SKIP (no <style> or </body>): {path}")
        return False

    css_tag = f'<link rel="stylesheet" href="{prefix}assets/widgets.css">\n<style>'
    text = text.replace("<style>", css_tag, 1)

    scripts = (
        f'<script src="{prefix}assets/config.js"></script>\n'
        f'<script src="{prefix}assets/site.js"></script>\n'
        "</body>"
    )
    # Replace the LAST occurrence of </body>
    idx = text.rfind("</body>")
    text = text[:idx] + scripts + text[idx + len("</body>"):]

    path.write_text(text, encoding="utf-8")
    return True

def main():
    changed = 0
    root_pages = ["crime.html", "politics.html", "business.html", "sport.html",
                  "tech.html", "screen.html", "world.html", "weather.html", "lifestyle.html"]
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
