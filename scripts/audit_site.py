#!/usr/bin/env python3
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json,re,sys,os
ROOT=Path(__file__).resolve().parents[1]; PUBLIC=ROOT/'public'
from nsc_model import project_view
project=project_view()
locales=set(project['locales'])
errs=[]
class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.ids=[]; self.hrefs=[]; self.srcs=[]; self.targets=[]; self.h=[]; self.html_attrs={}; self.main_ids=[]; self.h1=0; self.skip=False; self.inputs=[]; self.labels=set(); self.empty_interactive=[]; self._stack=[]; self.alternates=[]; self.positive_tab=[]; self.autoplay=[]; self.img_missing_alt=[]; self.duplicate_attrs=[]
    def handle_starttag(self,tag,attrs):
        names=[k for k,_ in attrs];
        if len(names)!=len(set(names)): self.duplicate_attrs.append(tag)
        a=dict(attrs); self._stack.append([tag,a,False])
        if tag=='html': self.html_attrs=a
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a':
            if 'href' in a:self.hrefs.append(a['href'])
            if a.get('href')=='#main':self.skip=True
            if a.get('target')=='_blank':self.targets.append('_blank')
        if tag in ('script','img','link') and 'src' in a:self.srcs.append(a['src'])
        if tag=='link' and a.get('rel')=='alternate': self.alternates.append((a.get('hreflang'),a.get('href')))
        if tag=='main':self.main_ids.append(a.get('id'))
        if re.fullmatch(r'h[1-6]',tag):
            n=int(tag[1]); self.h.append(n); self.h1 += n==1
        if tag=='input': self.inputs.append((a.get('id'),a.get('aria-label')))
        if tag=='label' and a.get('for'): self.labels.add(a['for'])
        if a.get('tabindex','').lstrip('+').isdigit() and int(a['tabindex'])>0:self.positive_tab.append((tag,a['tabindex']))
        if 'autoplay' in a:self.autoplay.append(tag)
        if tag=='img' and 'alt' not in a:self.img_missing_alt.append(a.get('src',''))
    def handle_data(self,data):
        if data.strip():
            for x in self._stack: x[2]=True
    def handle_endtag(self,tag):
        for i in range(len(self._stack)-1,-1,-1):
            if self._stack[i][0]==tag:
                t,a,has_text=self._stack.pop(i)
                if t in {'a','button','summary'} and not has_text and not a.get('aria-label'):
                    self.empty_interactive.append(t)
                break

def check_local(page:Path,u:str,kind:str):
    if not u or u.startswith(('#','mailto:','tel:','data:')):return
    parts=urlsplit(u)
    if parts.scheme or parts.netloc:return
    path=parts.path
    if not path:return
    target=(page.parent/path).resolve()
    if path.endswith('/') or target.is_dir():target=target/'index.html'
    if not target.exists():errs.append(f'{page.relative_to(PUBLIC)}: broken {kind} {u}')

for page in PUBLIC.rglob('*.html'):
    txt=page.read_text(encoding='utf-8'); p=P(); p.feed(txt)
    if 'Content-Security-Policy' not in txt: errs.append(f'{page.relative_to(PUBLIC)}: missing CSP meta policy')
    if '<meta name="referrer" content="no-referrer">' not in txt: errs.append(f'{page.relative_to(PUBLIC)}: missing no-referrer policy')
    relp=page.relative_to(PUBLIC)
    if len(p.ids)!=len(set(p.ids)):errs.append(f'{relp}: duplicate ids')
    if p.h1!=1:errs.append(f'{relp}: expected exactly one h1, got {p.h1}')
    if p.main_ids.count('main')!=1:errs.append(f'{relp}: expected main#main exactly once')
    if relp.as_posix()!='index.html' and not p.skip:errs.append(f'{relp}: missing skip link')
    if p.targets:errs.append(f'{relp}: target=_blank prohibited')
    if p.positive_tab:errs.append(f'{relp}: positive tabindex present')
    if p.autoplay:errs.append(f'{relp}: autoplay present')
    if p.img_missing_alt:errs.append(f'{relp}: image without alt')
    if p.duplicate_attrs:errs.append(f'{relp}: duplicate HTML attributes')
    if p.empty_interactive:errs.append(f'{relp}: empty interactive element')
    for iid,aria in p.inputs:
        if not aria and (not iid or iid not in p.labels):errs.append(f'{relp}: unlabeled input {iid}')
    for prev,nxt in zip(p.h,p.h[1:]):
        if nxt>prev+1:errs.append(f'{relp}: heading level jumps h{prev}->h{nxt}')
    for u in p.hrefs:check_local(page,u,'href')
    for u in p.srcs:check_local(page,u,'src')
    parts=relp.parts
    if parts and parts[0] in locales:
        loc=parts[0]; expected_dir='rtl' if loc=='ar' else 'ltr'
        if p.html_attrs.get('lang')!=loc:errs.append(f'{relp}: html lang mismatch')
        if p.html_attrs.get('dir')!=expected_dir:errs.append(f'{relp}: html dir mismatch')
        canonical_only = loc=='en' and (relp.as_posix().startswith('en/quests/') or relp.as_posix() in {'en/quests/index.html','en/sprint/index.html','en/governance/index.html','en/claims/index.html','en/benchmarks/index.html','en/reference-flow/index.html','en/context/index.html'})
        if not canonical_only:
            hreflangs={x for x,_ in p.alternates}
            needed=set(project['locales'])|{'x-default'}
            if not needed.issubset(hreflangs):errs.append(f'{relp}: incomplete hreflang alternates')
# Machine endpoints
for req in ['data/frontier.json','data/sources.json','data/project.json','data/contributions.json','data/forges.json','.well-known/commons.json','SKILL.md','start.md','assets/style.css']:
    if not (PUBLIC/req).exists():errs.append(f'missing public endpoint {req}')
if errs:
    print('SITE_AUDIT_FAILED',file=sys.stderr)
    for e in errs[:200]:print(' - '+e,file=sys.stderr)
    if len(errs)>200:print(f' ... {len(errs)-200} more',file=sys.stderr)
    sys.exit(1)
print(f'SITE_AUDIT_PASS html_pages={sum(1 for _ in PUBLIC.rglob("*.html"))}')
