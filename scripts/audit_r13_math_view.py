#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import re,sys,urllib.parse
R=Path(__file__).resolve().parents[1]
p=R/'public/en/math/index.html'; errs=[]
if not p.is_file():
    print('R13_MATH_VIEW_AUDIT_FAIL\n - missing public/en/math/index.html',file=sys.stderr);raise SystemExit(1)
s=p.read_text(encoding='utf-8')
low=s.lower()
if low.count('<main')!=1: errs.append('mathematics view must contain exactly one main landmark')
for token in ['<script','<canvas','<svg','rel="stylesheet"','class="button"','<button']:
    if token in low: errs.append('forbidden rich/UI dependency: '+token)
for phrase in ['founding sprint','start a quest','open missions','join us','explore the scaling','one hard problem. many legitimate ways to help']:
    if phrase in low: errs.append('persuasion/gamified phrase present: '+phrase)
required=['OpenAI','A','B','C','D','A/B','C/D','CMI recognition','Research frontier','Claim and review state','Machine-readable interface','requires no JavaScript']
for x in required:
    if x not in s: errs.append('required mathematics-view content missing: '+x)
# Plain-page ceiling: keep it information-dense and resistant to campaign-copy accretion.
words=re.findall(r"\b[\w'–-]+\b",re.sub(r'<[^>]+>',' ',s))
if len(words)>3200: errs.append(f'mathematics view too verbose: {len(words)} words')
# Internal relative links must resolve against the generated tree. Directory URLs map to index.html.
class P(HTMLParser):
    def __init__(self): super().__init__();self.hrefs=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            d=dict(attrs);h=d.get('href')
            if h: self.hrefs.append(h)
q=P();q.feed(s)
for href in q.hrefs:
    u=urllib.parse.urlsplit(href)
    if u.scheme or href.startswith('#') or href.startswith('//'): continue
    target=(p.parent/u.path).resolve()
    try: target.relative_to((R/'public').resolve())
    except ValueError: errs.append('relative link escapes public tree: '+href);continue
    if u.path.endswith('/') or target.is_dir(): target=target/'index.html'
    if not target.exists(): errs.append('broken internal math-view link: '+href)
if errs:
    print('R13_MATH_VIEW_AUDIT_FAIL',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    raise SystemExit(1)
print('R13_MATH_VIEW_AUDIT_PASS no_js=true no_css=true single_main=true internal_links=true')
