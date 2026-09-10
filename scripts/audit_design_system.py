#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
css=(ROOT/'assets/style.css').read_text()
js=(ROOT/'assets/site.js').read_text()
gen=(ROOT/'scripts/build_site.py').read_text()
sims=json.loads((ROOT/'content/public/simulations.json').read_text()).get('simulations',[])
errs=[]
required=['--bg:','--surface:','--text:','--muted:','--primary:','--focus:','--control-min: 44px','container-type:','@container','margin-inline','padding-inline','@view-transition','prefers-color-scheme','prefers-contrast','forced-colors: active','@media print']
for x in required:
    if x not in css: errs.append(f'missing design-system/platform primitive: {x}')
if '@font-face' in css or re.search(r'https?://',css): errs.append('remote/custom font dependency in CSS')
if re.search(r'transition\s*:\s*all\b',css): errs.append('transition: all prohibited')
if css.count('!important')>20: errs.append(f'excessive !important count {css.count("!important")}')

# Canvas is permitted only as progressive rendering for a declared scientific
# simulation. This replaces the obsolete blanket ban that made an exact,
# provenance-bound scientific visualization impossible.
canvas_decls=list(re.finditer(r'<canvas\b[^>]*>',gen,re.I))
if canvas_decls:
    declared_ids={s.get('id') for s in sims}
    if declared_ids != {'taylor-vortex-array-2d'}:
        errs.append(f'unexpected declared canvas simulation set: {sorted(x for x in declared_ids if x)}')
    for m in canvas_decls:
        tag=m.group(0)
        if 'data-flow-canvas' not in tag or 'aria-hidden="true"' not in tag:
            errs.append('canvas must be the declared exact-flow progressive rendering and aria-hidden')
    if gen.count('<canvas') != 1:
        errs.append(f'exactly one declared canvas renderer expected, found {gen.count("<canvas")}')
    for token in [
        'data-simulation-id="{esc(sim[\'id\'])}"',
        'data-flow-static',
        'data-flow-state',
        'No autoplay',
    ]:
        if token not in gen: errs.append('scientific canvas contract missing '+token)
    # Runtime must address that declared canvas rather than generic canvas nodes.
    if "querySelector('[data-flow-canvas]')" not in js:
        errs.append('canvas runtime is not scoped to the declared scientific renderer')
    if re.search(r"querySelector(?:All)?\(\s*['\"]canvas",js):
        errs.append('generic canvas runtime selector prohibited')
    if js.count("getContext('2d'") != 1:
        errs.append('unexpected number of 2D canvas runtimes')
else:
    if 'getContext(' in js:
        errs.append('canvas runtime exists without a declared canvas object')

if 'data-eq-term' not in js or 'equation-object' not in css: errs.append('actual mathematical-object enhancement missing')
if errs:
    print('DESIGN_SYSTEM_AUDIT_FAILED',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    sys.exit(1)
print(f'DESIGN_SYSTEM_AUDIT_PASS css_bytes={len(css.encode())} js_bytes={len(js.encode())} canvas_contract=declared-scientific-only')
