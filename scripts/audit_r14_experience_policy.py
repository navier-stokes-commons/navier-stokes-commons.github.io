#!/usr/bin/env python3
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[1];P=R/'public';errs=[]
h=(P/'en/index.html').read_text();root=(P/'index.html').read_text();math=(P/'en/math/index.html').read_text();js=(R/'assets/site.js').read_text();css=(R/'assets/style.css').read_text()
for name,text in [('root',root),('en',h)]:
 for tok in ['class="r14-hero"','data-vortex-stage','class="r14-abcd-strip"','data-ambient-field','>Mathematics<']:
  if tok not in text:errs.append(name+' missing '+tok)
 # Vortex must be in the rich hero, not introduced only after the status surface.
 if text.find('data-vortex-stage')>text.find('class="r14-abcd-strip"'):errs.append(name+' scientific visual must precede status strip')
if '<script' in math.lower() or '<link rel="stylesheet"' in math.lower() or '<style' in math.lower():errs.append('Mathematics projection must remain stylesheet/JS independent')
for tok in ['R14 ambient glyph field','nsc:ambient-motion','ambient||','Pause motion']:
 if tok not in js:errs.append('runtime missing '+tok)
if '/* === R14 RICH DEFAULT / MATHEMATICS ISOLATION === */' not in css:errs.append('R14 CSS marker missing')
if errs:
 print('R14_EXPERIENCE_POLICY_FAIL',file=sys.stderr);[print(' - '+x,file=sys.stderr) for x in errs];raise SystemExit(1)
print('R14_EXPERIENCE_POLICY_PASS rich_default=true vortex_first=true ambient=true math_isolated=true')
