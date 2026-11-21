#!/usr/bin/env python3
"""Idempotently insert the Google tag (GTM-N4N2HFHM) and Google Analytics
(G-ZT1G607EB3) immediately after <head> on every HTML page.

Consent Mode v2: everything defaults to "denied" until the reader clicks
Accept on the cookie notice (assets/site.js then sends a consent update).
Readers who accepted on an earlier visit are granted straight away.
Re-running replaces the block, so IDs can be changed here and re-applied.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
GTM_ID = "GTM-N4N2HFHM"
GA_ID = "G-ZT1G607EB3"

BLOCK = f"""<!-- Google tag (sw-google-tag) -->
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('consent', 'default', {{ad_storage:'denied', ad_user_data:'denied', ad_personalization:'denied', analytics_storage:'denied', wait_for_update:500}});
  try {{ if (localStorage.getItem('sw_consent') === 'accepted') gtag('consent', 'update', {{ad_storage:'granted', ad_user_data:'granted', ad_personalization:'granted', analytics_storage:'granted'}}); }} catch (e) {{}}
  dataLayer.push({{'gtm.start': new Date().getTime(), event: 'gtm.js'}});
</script>
<script async src="https://www.googletagmanager.com/gtm.js?id={GTM_ID}"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
</script>
<!-- /Google tag (sw-google-tag) -->
"""

PAT = re.compile(r"<!-- Google tag \(sw-google-tag\) -->.*?<!-- /Google tag \(sw-google-tag\) -->\n", re.S)


def process(path: pathlib.Path) -> bool:
    text = path.read_text(encoding="utf-8")
    # keep the charset declaration first in <head> (must be in the first 1024 bytes)
    text0 = text
    text = re.sub(r'(?m)^<meta charset="utf-8">\n', '', text)
    if PAT.search(text):
        new = PAT.sub(lambda m: BLOCK, text, count=1)
    else:
        new = text.replace("<head>\n", "<head>\n" + BLOCK, 1)
    new = new.replace("<head>\n", '<head>\n<meta charset="utf-8">\n', 1)
    if new != text0:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main():
    pages = list(ROOT.glob("*.html")) + list(ROOT.glob("posts/*.html")) + list(ROOT.glob("archive/*.html"))
    changed = sum(process(p) for p in pages)
    missing = [str(p) for p in pages if "sw-google-tag" not in p.read_text(encoding="utf-8")]
    print(f"Google tag: {changed} pages updated, {len(pages)} pages checked, {len(missing)} missing")
    for m in missing:
        print("  missing:", m)


if __name__ == "__main__":
    main()
