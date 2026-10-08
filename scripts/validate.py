#!/usr/bin/env python3
"""Validação leve do site estático (sem dependências). Falha com exit 1 se algo estiver errado."""
import json, os, re, sys
from html.parser import HTMLParser
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []

html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.refs, self.local, self.ld, self._ld, self.imgs = set(), [], [], [], False, []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a: self.ids.add(a["id"])
        if tag == "script" and a.get("type") == "application/ld+json": self._ld = True
        if tag == "img": self.imgs.append(a)
        for k in ("href", "src"):
            v = a.get(k)
            if not v: continue
            if v.startswith("#"): self.refs.append(v[1:])
            elif not re.match(r"^(https?:|mailto:|tel:|data:)", v): self.local.append(v)
    def handle_endtag(self, tag):
        if tag == "script": self._ld = False
    def handle_data(self, d):
        if self._ld: self.ld.append(d)

p = P(); p.feed(html)
for r in p.refs:
    if r and r not in p.ids: errors.append(f"âncora #{r} sem id correspondente")
for f in p.local:
    if not os.path.exists(os.path.join(ROOT, f.split("?")[0])): errors.append(f"arquivo local ausente: {f}")
for img in p.imgs:
    if "alt" not in img: errors.append(f"<img> sem alt: {img.get('src')}")
try: json.loads("".join(p.ld))
except Exception as e: errors.append(f"JSON-LD inválido: {e}")
# IDs de tracking placeholder só podem existir dentro de comentário HTML
visible = re.sub(r"<!--.*?-->", "", html, flags=re.S)
if re.search(r"G-XXXXXXXXXX|XXXXXXXXXXXXXXX", visible): errors.append("ID de analytics placeholder fora de comentário")
if not re.search(r'<html[^>]+lang="', html): errors.append("<html> sem lang")
if "<title>" not in html: errors.append("sem <title>")
if len(re.findall(r"<(?:main|section|div|form|nav|header|footer)\b", visible)) != len(re.findall(r"</(?:main|section|div|form|nav|header|footer)>", visible)):
    errors.append("tags de bloco desbalanceadas")

try: ET.parse(os.path.join(ROOT, "sitemap.xml"))
except Exception as e: errors.append(f"sitemap.xml inválido: {e}")
if "Sitemap:" not in open(os.path.join(ROOT, "robots.txt")).read(): errors.append("robots.txt sem Sitemap")

for e in errors: print("ERRO:", e)
print("OK" if not errors else f"{len(errors)} erro(s)")
sys.exit(1 if errors else 0)
