#!/usr/bin/env python3
from pathlib import Path
import re,sys
R=Path(__file__).resolve().parents[1]
css=(R/'assets/style.css').read_text(); js=(R/'assets/site.js').read_text(); gen=(R/'scripts/build_site.py').read_text(); public=R/'public'; errs=[]
# This is not an aesthetic oracle. It enforces scientific visual typing, product identity,
# and prevents historical representations from silently returning.
flagships=[public/x for x in ['en/index.html','es/index.html','ar/index.html','zh-Hans/index.html']]
rendered='\n'.join(p.read_text() for p in flagships if p.exists())
for bad in ['participation-orbit','Decorative flow field','flow-orbits','orbit-breathe','core-stream','data-mechanism-atlas','data-mechanism-figure','ascii-sequence','data-ascii-live']:
    if bad in rendered: errs.append('retired flagship primitive reached public output: '+bad)
for tok in ['data-vortex-stage','data-vortex-static','data-vortex-canvas','data-flow-probe','data-vortex-controls','data-representation-status="schematic"','data-quantitative-status="derived-leading-exponents"']:
    if tok not in rendered: errs.append('immersive flagship primitive missing: '+tok)
# The exact Taylor flow is deliberately isolated from the 2026 schematic.
en=(public/'en/index.html').read_text()
ref=(public/'en/reference-flow/index.html').read_text() if (public/'en/reference-flow/index.html').exists() else ''
if 'data-flow-chamber' in en: errs.append('exact Taylor reference flow conflated with flagship 2026 mechanism')
if 'data-flow-chamber' not in ref or 'data-simulation-id="taylor-vortex-array-2d"' not in ref: errs.append('dedicated exact reference flow missing')
# Canvas is allowed for exactly two typed families: schematic flagship renderer and exact reference flow.
for p in public.rglob('*.html'):
    txt=p.read_text()
    for m in re.finditer(r'<canvas\b[^>]*>',txt,re.I):
        tag=m.group(0)
        if 'data-vortex-canvas' in tag:
            if 'data-vortex-stage' not in txt or 'data-representation-status="schematic"' not in txt: errs.append(f'{p.relative_to(public)} untyped schematic canvas')
        elif 'data-flow-canvas' in tag:
            if 'data-simulation-id="taylor-vortex-array-2d"' not in txt: errs.append(f'{p.relative_to(public)} untyped exact-flow canvas')
        else: errs.append(f'{p.relative_to(public)} undeclared canvas')
# Direct-manipulation contract must be real code, not prose.
for tok in ["getContext('webgl2'", "getContext('2d'", "addEventListener('pointermove'", "addEventListener('pointerdown'", "addEventListener('wheel'", "stage.dataset.renderer='webgl2'", "stage.dataset.renderer='canvas2d'"]:
    if tok not in js: errs.append('realtime renderer/direct-manipulation primitive missing: '+tok)
# Strong logarithmic-time visual encoding is an implementation invariant; dynamic discrimination is audited elsewhere.
if '1.25+19*Math.pow(s,.72)' not in js: errs.append('strong k-dependent twist-density encoding missing')
# One global token authority only; scientific night surfaces are component scoped.
if len(re.findall(r'(?m)^:root\s*\{',css))!=1: errs.append('multiple global design-token authorities')
if re.search(r'(?m)^html\s*\{[^}]*--(?:paper|ink)',css,re.S): errs.append('scientific component palette leaked into global html')
# Anti-template budgets are tripwires, never evidence of beauty.
metrics={'pill_radius_rules':len(re.findall(r'border-radius\s*:\s*999px',css)),'linear_gradients':css.count('linear-gradient('),'radial_gradients':css.count('radial-gradient('),'backdrop_blur_rules':len(re.findall(r'backdrop-filter\s*:\s*blur\(',css))}
limits={'pill_radius_rules':2,'linear_gradients':5,'radial_gradients':4,'backdrop_blur_rules':1}
for k,v in metrics.items():
    if v>limits[k]: errs.append(f'anti-template budget exceeded: {k}={v} limit={limits[k]}')
for token in ['Newsreader','Geist','Geist Mono','--math:','@view-transition']:
    if token not in css: errs.append('production visual/typography primitive missing: '+token)
if re.search(r'url\(["\']?https?://',css,re.I) or re.search(r'@import\s+url\(["\']?https?://',css,re.I): errs.append('remote CSS/font runtime dependency introduced')
if errs:
    print('VISUAL_INTEGRITY_AUDIT_FAILED',file=sys.stderr); [print(' - '+e,file=sys.stderr) for e in errs]; print('METRICS',metrics,file=sys.stderr); sys.exit(1)
print('VISUAL_INTEGRITY_AUDIT_PASS scope=scientific-typing+realtime-identity+historical-regressions+token-authority metrics='+','.join(f'{k}={v}' for k,v in metrics.items()))
