#!/usr/bin/env python3
from pathlib import Path
import re,sys,json
R=Path(__file__).resolve().parents[1]; css=(R/'assets/style.css').read_text(); js=(R/'assets/site.js').read_text(); gen=(R/'scripts/build_site.py').read_text(); public=R/'public'; errs=[]
# This gate is intentionally NOT called an aesthetic pass. It checks visual honesty,
# anti-template regressions, and the existence of project-specific scientific objects.
source_blob='\n'.join([gen,js])
for bad in ['participation-orbit','Decorative flow field','flow-orbits','orbit-breathe','core-stream']:
    if bad in source_blob: errs.append(f'rejected pseudo-scientific/decorative motif remains: {bad}')
rendered='\n'.join((public/x).read_text() for x in ['en/index.html','en/contribute/index.html','ar/index.html'] if (public/x).exists())
for pat in [r'participation-orbit',r'Decorative flow field',r'core-stream']:
    if re.search(pat,rendered,re.I): errs.append(f'rejected visual motif reached public output: {pat}')
# Any canvas must be tied to a declared scientific simulation with fallback and accessible state.
for m in re.finditer(r'<canvas\b[^>]*>',rendered,re.I):
    if 'data-flow-canvas' not in m.group(0): errs.append('undeclared canvas reached flagship public output')
if '<canvas' in rendered:
    for tok in ['data-flow-chamber','data-simulation-id="taylor-vortex-array-2d"','data-flow-static','data-flow-state']:
        if tok not in rendered: errs.append('scientific canvas missing required semantic binding '+tok)
# Anti-template budgets are tripwires, not beauty metrics.
metrics={'pill_radius_rules':len(re.findall(r'border-radius\s*:\s*999px',css)),'linear_gradients':css.count('linear-gradient('),'radial_gradients':css.count('radial-gradient('),'backdrop_blur_rules':len(re.findall(r'backdrop-filter\s*:\s*blur\(',css))}
limits={'pill_radius_rules':2,'linear_gradients':4,'radial_gradients':2,'backdrop_blur_rules':1}
for k,v in metrics.items():
    if v>limits[k]: errs.append(f'anti-template budget exceeded: {k}={v} limit={limits[k]}')
m=re.search(r'\.button\s*\{[^}]*border-radius\s*:\s*([^;]+)',css,re.S)
if not m: errs.append('button visual rule missing')
elif '999' in m.group(1) or '50%' in m.group(1): errs.append('primary buttons are pill/capsule shaped')
for token in ['equation-object','data-scaling-lab','data-ascii-live','scaling-table','data-flow-chamber','data-flow-static']:
    if token not in gen and token not in css: errs.append('project-specific scientific visual primitive missing: '+token)
if 'scaling-model.json' not in gen or 'formulas.json' not in gen or 'simulations.json' not in gen: errs.append('scientific visual models not wired to generator')
if 'contribution-choices' not in gen or 'worked-example' not in gen: errs.append('real contribution lifecycle object missing')
if '@view-transition' not in css: errs.append('native view-transition enhancement missing')
if '--sans:' not in css or '--math:' not in css: errs.append('explicit editorial + mathematical typography system missing')
if re.search(r'https?://[^)\s]+\.(?:woff2?|ttf|otf)',css,re.I): errs.append('remote font dependency introduced')
if errs:
    print('VISUAL_INTEGRITY_AUDIT_FAILED',file=sys.stderr); [print(' - '+e,file=sys.stderr) for e in errs]; print('METRICS',metrics,file=sys.stderr); sys.exit(1)
print('VISUAL_INTEGRITY_AUDIT_PASS machine_scope=honesty+identity+anti-template metrics='+','.join(f'{k}={v}' for k,v in metrics.items()))
