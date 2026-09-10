#!/usr/bin/env python3
from __future__ import annotations
import re,sys
from pathlib import Path
css=(Path(__file__).resolve().parents[1]/'assets/style.css').read_text()
def vals(name): return re.findall(rf'--{re.escape(name)}:\s*(#[0-9a-fA-F]{{6}})',css)
def rgb(h): return [int(h[i:i+2],16)/255 for i in (1,3,5)]
def lum(h):
    c=[]
    for x in rgb(h):c.append(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4)
    return .2126*c[0]+.7152*c[1]+.0722*c[2]
def ratio(a,b):
    x,y=lum(a),lum(b); return (max(x,y)+.05)/(min(x,y)+.05)
keys=['bg','surface','text','muted','border','primary','on-primary','focus']
V={k:vals(k) for k in keys}
if any(len(V[k])<2 for k in keys):
    print('CONTRAST_AUDIT_FAILED missing light/dark token',file=sys.stderr);sys.exit(1)
errs=[]
for i,mode in enumerate(['light','dark']):
    tests=[('text/bg','text','bg',4.5),('muted/bg','muted','bg',4.5),('text/surface','text','surface',4.5),('border/surface','border','surface',3.0),('primary/bg','primary','bg',3.0),('button','on-primary','primary',4.5),('focus/bg','focus','bg',3.0)]
    for label,a,b,minimum in tests:
        r=ratio(V[a][i],V[b][i])
        if r+1e-9<minimum:errs.append(f'{mode} {label}: {r:.2f} < {minimum}')

# Component-level overrides are independent contrast surfaces and must be audited
# explicitly; global token checks cannot detect a low-contrast local override.
def selector_hex(selector, prop='color'):
    m=re.search(rf'{re.escape(selector)}\s*\{{[^}}]*?{re.escape(prop)}\s*:\s*(#[0-9a-fA-F]{{6}})',css,re.S)
    return m.group(1) if m else None
ink=vals('ink')[-1] if vals('ink') else None
for selector,minimum in [('.flow-copy .lede',4.5),('.flow-copy .source-line a',4.5)]:
    fg=selector_hex(selector)
    if not (ink and fg): errs.append(f'missing explicit flow contrast surface: {selector}')
    else:
        r=ratio(fg,ink)
        if r+1e-9<minimum: errs.append(f'{selector}/flow-bg: {r:.2f} < {minimum}')

if '--control-min: 44px' not in css:errs.append('primary control minimum is not 44px')
if ':focus-visible' not in css:errs.append('missing visible focus rule')
if 'prefers-reduced-motion: reduce' not in css:errs.append('missing reduced-motion rule')
if errs:
    print('CONTRAST_AUDIT_FAILED',file=sys.stderr); [print(' - '+e,file=sys.stderr) for e in errs];sys.exit(1)
print('CONTRAST_AUDIT_PASS')
