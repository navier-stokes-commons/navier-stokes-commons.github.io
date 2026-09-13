#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re,sys
ROOT=Path(__file__).resolve().parents[1]; PUBLIC=ROOT/'public'; CSS=ROOT/'assets/style.css'; JS=ROOT/'assets/site.js'; FONTS=ROOT/'assets/fonts'; errs=[]; warnings=[]
# R16's authored fluid renderer is bundled locally; retain bounded payload
# limits while accounting for its CSS/JS overlay.
limits={'css':60*1024,'js':56*1024,'html':110*1024,'fonts_total':420*1024}
if CSS.stat().st_size>limits['css']: errs.append(f'CSS {CSS.stat().st_size} > {limits["css"]}')
if JS.stat().st_size>limits['js']: errs.append(f'JS {JS.stat().st_size} > {limits["js"]}')
css=CSS.read_text(); js=JS.read_text()
if re.search(r'@import\s',css,re.I): errs.append('CSS @import prohibited')
if re.search(r'url\(["\']?https?://',css,re.I): errs.append('remote CSS asset prohibited')
if re.search(r'transition\s*:\s*all\b',css,re.I): errs.append('transition: all prohibited')
if 'setInterval(' in js: errs.append('setInterval prohibited for persistent decorative motion')
font_bytes=sum(p.stat().st_size for p in FONTS.glob('*.woff2')) if FONTS.exists() else 0
if font_bytes>limits['fonts_total']: errs.append(f'font WOFF2 total {font_bytes} > {limits["fonts_total"]}')
class P(HTMLParser):
    def __init__(self): super().__init__(); self.remote=[]; self.scripts=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script' and a.get('src'):
            self.scripts.append(a['src'])
            if urlsplit(a['src']).scheme:self.remote.append(('script',a['src']))
        if tag=='link' and a.get('rel')=='stylesheet' and a.get('href') and urlsplit(a['href']).scheme:self.remote.append(('stylesheet',a['href']))
max_html=(0,None); pages=0
for page in PUBLIC.rglob('*.html'):
    pages+=1; size=page.stat().st_size
    if size>max_html[0]:max_html=(size,page)
    if size>limits['html']:errs.append(f'{page.relative_to(PUBLIC)} HTML {size} > {limits["html"]}')
    p=P();p.feed(page.read_text())
    if p.remote:errs.append(f'{page.relative_to(PUBLIC)} remote runtime asset {p.remote[:2]}')
if errs:
    print('PERFORMANCE_AUDIT_FAILED',file=sys.stderr);[print(' - '+e,file=sys.stderr) for e in errs];sys.exit(1)
print(f'PERFORMANCE_AUDIT_PASS pages={pages} css_bytes={CSS.stat().st_size} js_bytes={JS.stat().st_size} font_bytes={font_bytes} max_html_bytes={max_html[0]} max_html={max_html[1].relative_to(PUBLIC) if max_html[1] else "none"}')
