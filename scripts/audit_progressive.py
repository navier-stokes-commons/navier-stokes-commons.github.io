#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]; PUBLIC=ROOT/'public'
missions=json.loads((ROOT/'content/public/missions.json').read_text())
from nsc_model import project_view
project=project_view()
css=(ROOT/'assets/style.css').read_text(); js=(ROOT/'assets/site.js').read_text()
errs=[]
# Essential content must never depend on JS-only hidden-state classes.
for bad in [r'\.enhanced\s+\[data-reveal\].*opacity\s*:\s*0',r'\.enhanced\s+\[data-reveal\].*display\s*:\s*none']:
    if re.search(bad,css,re.S): errs.append('core reveal content is hidden by enhancement CSS')
home=(PUBLIC/'en/index.html').read_text()
if 'equation-object' not in home: errs.append('mathematical hero baseline missing')
if 'data-flow-canvas' in home and ('data-flow-chamber' not in home or 'data-simulation-id="taylor-vortex-array-2d"' not in home or 'data-flow-static' not in home): errs.append('canvas lacks provenance-bound exact-simulation fallback')
if 'data-flow-canvas' in home and 'data-flow-tracer-note' not in home: errs.append('exact flow lacks explicit exact-field vs numerical-tracer disclosure')
if "document.documentElement" not in js: errs.append('enhancement script not explicitly scoped')
# Every locale mission index must statically contain every mission link; every mission detail must contain question, acceptance and take-part section.
for loc in project['locales']:
    idx=(PUBLIC/loc/'missions/index.html').read_text()
    for m in missions:
        if f'missions/{m["slug"]}/index.html' not in idx and f'{m["slug"]}/' not in idx:
            errs.append(f'{loc}: mission {m["id"]} absent from static mission index')
    for m in missions:
        page=PUBLIC/loc/'missions'/m['slug']/'index.html'; txt=page.read_text()
        for token,label in [('class="question-text"','question'),('class="accept-list"','acceptance'),('id="take-part"','take-part')]:
            if token not in txt: errs.append(f'{page.relative_to(PUBLIC)} missing static {label}')
        if '<script ' not in txt or ' defer' not in txt: errs.append(f'{page.relative_to(PUBLIC)} enhancement script must be deferred')
# JS failures must not remove content; prohibited DOM body replacement/eval patterns.
for pat,label in [(r'document\.body\.innerHTML\s*=','body replacement'),(r'\beval\s*\(','eval'),(r'new Function\s*\(','dynamic Function')]:
    if re.search(pat,js): errs.append(f'prohibited JS pattern: {label}')
if errs:
    print('PROGRESSIVE_AUDIT_FAILED',file=sys.stderr)
    for e in errs[:200]: print(' - '+e,file=sys.stderr)
    sys.exit(1)
print(f'PROGRESSIVE_AUDIT_PASS locales={len(project["locales"])} missions={len(missions)}')
