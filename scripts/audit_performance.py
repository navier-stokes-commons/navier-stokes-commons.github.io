#!/usr/bin/env python3
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re,sys
ROOT=Path(__file__).resolve().parents[1]; PUBLIC=ROOT/'public'
errs=[]; warnings=[]
CSS=ROOT/'assets/style.css'; JS=ROOT/'assets/site.js'
limits={'css':55*1024,'js':35*1024,'html':100*1024}
if CSS.stat().st_size>limits['css']: errs.append(f'CSS {CSS.stat().st_size} > {limits["css"]}')
if JS.stat().st_size>limits['js']: errs.append(f'JS {JS.stat().st_size} > {limits["js"]}')
css=CSS.read_text(); js=JS.read_text()
if re.search(r'@import\s',css,re.I): errs.append('CSS @import prohibited')
if re.search(r'@font-face\b',css,re.I): errs.append('bundled/custom font-face prohibited in public seed')
if re.search(r'url\(["\']?https?://',css,re.I): errs.append('remote CSS asset prohibited')
if re.search(r'transition\s*:\s*all\b',css,re.I): errs.append('transition: all prohibited')
if 'setInterval(' in js: errs.append('setInterval prohibited for persistent decorative motion')
if len(re.findall(r'requestAnimationFrame\(',js))>8: warnings.append('high number of requestAnimationFrame call sites')
class P(HTMLParser):
    def __init__(self): super().__init__(); self.remote_runtime=[]; self.scripts=[]; self.styles=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script' and a.get('src'):
            self.scripts.append(a['src'])
            if urlsplit(a['src']).scheme: self.remote_runtime.append(('script',a['src']))
        if tag=='link' and a.get('rel')=='stylesheet' and a.get('href'):
            self.styles.append(a['href'])
            if urlsplit(a['href']).scheme: self.remote_runtime.append(('stylesheet',a['href']))
max_html=(0,None); pages=0
for page in PUBLIC.rglob('*.html'):
    pages+=1; size=page.stat().st_size
    if size>max_html[0]: max_html=(size,page)
    if size>limits['html']: errs.append(f'{page.relative_to(PUBLIC)} HTML {size} > {limits["html"]}')
    p=P(); p.feed(page.read_text(encoding='utf-8'))
    if p.remote_runtime: errs.append(f'{page.relative_to(PUBLIC)} remote runtime asset {p.remote_runtime[:2]}')
    if len(p.scripts)>1: warnings.append(f'{page.relative_to(PUBLIC)} has {len(p.scripts)} scripts')
if errs:
    print('PERFORMANCE_AUDIT_FAILED',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    sys.exit(1)
print(f'PERFORMANCE_AUDIT_PASS pages={pages} css_bytes={CSS.stat().st_size} js_bytes={JS.stat().st_size} max_html_bytes={max_html[0]} max_html={max_html[1].relative_to(PUBLIC) if max_html[1] else "none"}')
for w in warnings[:20]: print(' warning:',w)
