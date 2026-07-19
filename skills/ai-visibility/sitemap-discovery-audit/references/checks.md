# Sitemap discovery check commands

Replace `$SITE` with the site origin and `$URL` with a representative sitemap URL entry.

## Find sitemap declarations

```bash
curl -s "$SITE/robots.txt" | grep -i "^sitemap"
curl -s -o /dev/null -w "%{http_code}\n" "$SITE/sitemap.xml"
curl -s -o /dev/null -w "%{http_code}\n" "$SITE/sitemap_index.xml"
```

## Fetch and validate sitemap structure

```bash
curl -s "$SITE/sitemap.xml" | head -c 500
curl -s "$SITE/sitemap.xml" | python3 -c "
import sys, xml.dom.minidom as m
m.parseString(sys.stdin.read())
print('well-formed XML')
"
```

## List sub-sitemaps (if this is a sitemap index) or URLs (if this is a URL set)

```bash
curl -s "$SITE/sitemap.xml" | grep -oE '<loc>[^<]+</loc>' | sed -e 's/<loc>//' -e 's/<\/loc>//'
```

## Count entries and inspect lastmod freshness

```bash
curl -s "$SITE/sitemap.xml" | grep -c '<url>'
curl -s "$SITE/sitemap.xml" | grep -oE '<lastmod>[^<]+</lastmod>' | sort -u | tail -20
```

## Check representative URLs for status, redirects, and indexability

```bash
for u in $(curl -s "$SITE/sitemap.xml" | grep -oE '<loc>[^<]+</loc>' | sed -e 's/<loc>//' -e 's/<\/loc>//' | head -20); do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$u")
  echo "$code $u"
done
```

```bash
curl -s "$URL" | grep -oiE '<meta[^>]+robots[^>]+>'
curl -s "$URL" | grep -oiE '<link[^>]+rel="canonical"[^>]*>'
```

## Cross-check coverage against navigation

Manually list the site's important nav/footer links, normalize internal links to absolute
URLs, then diff against sitemap URLs to spot omissions:

```bash
curl -s "$SITE" | grep -oE 'href="[^"]+"' | sed 's/href="//;s/"$//' | SITE="$SITE" python3 -c '
import os, sys
from urllib.parse import urljoin, urlsplit, urlunsplit

site = os.environ["SITE"].rstrip("/")
site_parts = urlsplit(site)
for href in sys.stdin:
    href = href.strip()
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        continue
    link = urlsplit(urljoin(site + "/", href))
    if link.scheme != site_parts.scheme or link.netloc != site_parts.netloc:
        continue
    print(urlunsplit((link.scheme, link.netloc, link.path, link.query, "")))
' | sort -u > /tmp/nav-links.txt
curl -s "$SITE/sitemap.xml" | grep -oE '<loc>[^<]+</loc>' | sed -e 's/<loc>//' -e 's/<\/loc>//' | sort -u > /tmp/sitemap-links.txt
comm -23 /tmp/nav-links.txt /tmp/sitemap-links.txt
```

This excludes anchors and external links before comparing only same-origin absolute URLs.

## Evidence discipline

Record each finding as: URL checked, command run, observed HTTP status or XML content, and why it is a coverage gap, redirect issue, or blocked entry. Sitemap presence is not proof of indexing — say so explicitly when reporting.
