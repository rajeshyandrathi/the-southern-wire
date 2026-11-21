#!/usr/bin/env python3
"""Idempotently insert Vercel Web Analytics script tags into every HTML page.
Following the official Vercel Analytics documentation for static HTML sites:
https://vercel.com/docs/analytics/quickstart

The script adds:
1. Inline script to initialize window.va function
2. Deferred script to load the analytics library from /_vercel/insights/script.js

This is safe to re-run: skips files that already have Vercel Analytics.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Vercel Analytics inline script (minified version)
ANALYTICS_INLINE = '''<script>
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
</script>'''

# Vercel Analytics deferred script
ANALYTICS_SCRIPT = '<script defer src="/_vercel/insights/script.js"></script>'

def process(path: pathlib.Path):
    """Inject Vercel Analytics scripts into an HTML file if not already present."""
    text = path.read_text(encoding="utf-8")
    
    # Skip if already has Vercel Analytics
    if "_vercel/insights/script.js" in text or "window.va" in text:
        return False
    
    # Ensure we have a </head> tag to inject before
    if "</head>" not in text:
        print(f"SKIP (no </head> found): {path}")
        return False
    
    # Inject both scripts right before </head>
    injection = f"{ANALYTICS_INLINE}\n{ANALYTICS_SCRIPT}\n</head>"
    text = text.replace("</head>", injection, 1)
    
    path.write_text(text, encoding="utf-8")
    return True

def main():
    changed = 0
    
    # Root level pages
    root_pages = [
        "index.html", "crime.html", "politics.html", "business.html", 
        "sport.html", "tech.html", "screen.html", "world.html", 
        "weather.html", "lifestyle.html", "about.html", "privacy.html", 
        "terms.html", "contact.html"
    ]
    
    for name in root_pages:
        p = ROOT / name
        if p.exists() and process(p):
            print(f"✓ Updated: {name}")
            changed += 1
    
    # Archive pages
    for p in sorted((ROOT / "archive").glob("*.html")):
        if process(p):
            print(f"✓ Updated: {p.relative_to(ROOT)}")
            changed += 1
    
    # Post pages (if they exist)
    posts_dir = ROOT / "posts"
    if posts_dir.exists():
        for p in sorted(posts_dir.glob("*.html")):
            if process(p):
                print(f"✓ Updated: {p.relative_to(ROOT)}")
                changed += 1
    
    print(f"\n✅ Vercel Analytics injected into {changed} files.")
    if changed == 0:
        print("   All files already have Vercel Analytics configured.")

if __name__ == "__main__":
    main()
