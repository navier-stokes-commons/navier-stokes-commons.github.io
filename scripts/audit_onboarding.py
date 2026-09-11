#!/usr/bin/env python3
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'public'; errs=[]
class A(HTMLParser):
    def __init__(self): super().__init__(); self.routes=0; self.hrefs=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='article' and 'entry-route' in d.get('class','').split(): self.routes+=1
        if tag=='a' and d.get('href'): self.hrefs.append(d['href'])

def check(path):
    p=A(); p.feed(path.read_text()); return p
for loc in ['en','es']:
    page=P/loc/'index.html'
    if not page.exists(): errs.append(f'{loc} home missing'); continue
    p=check(page)
    if p.routes!=6: errs.append(f'{loc} home expected 6 entry routes, got {p.routes}')
    txt=page.read_text()
    for token in (['You do not need to believe the announcement to contribute.','Context / credit'] if loc=='en' else ['No tienes que creer el anuncio para contribuir.','Leer contexto / crédito']):
        if token not in txt: errs.append(f'{loc} home missing onboarding token {token}')
root=P/'index.html'
if root.exists() and 'Context / credit' not in root.read_text(): errs.append('global landing missing context/credit route')
ctx=P/'en/context/index.html'
if not ctx.exists(): errs.append('context route missing')
else:
    txt=ctx.read_text()
    for token in ['Find a review quest','Public sources','Participation does not require endorsing']:
        if token not in txt: errs.append('context route missing action: '+token)
if errs:
    print('ONBOARDING_AUDIT_FAILED',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    raise SystemExit(1)
print('ONBOARDING_AUDIT_PASS routes=en:6,es:6 context=true skeptic_route=true agent_route=true')
