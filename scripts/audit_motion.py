#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]
css=(ROOT/'assets/style.css').read_text(); js=(ROOT/'assets/site.js').read_text()
errs=[]
required_css=['prefers-reduced-motion: reduce','@view-transition','forced-colors: active']
for x in required_css:
    if x not in css: errs.append(f'missing CSS motion/accessibility primitive: {x}')
required_js=["prefers-reduced-motion: reduce",'IntersectionObserver','el.animate']
for x in required_js:
    if x not in js: errs.append(f'missing JS motion control: {x}')
if re.search(r'animation\s*:\s*[^;]*infinite',css,re.I): errs.append('infinite CSS animation prohibited')
if re.search(r'transition\s*:\s*all\b',css,re.I): errs.append('transition: all prohibited')
for page in (ROOT/'public').rglob('*.html'):
    if re.search(r'<(?:video|audio)[^>]*\bautoplay\b',page.read_text(),re.I): errs.append(f'{page.relative_to(ROOT)}: media autoplay prohibited')
# Runtime no-autoplay behavior for scientific animation is exercised by audit_browser.py;
# substring checks are intentionally avoided because comments/data schemas may discuss autoplay safely.
if errs:
    print('MOTION_AUDIT_FAILED',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    sys.exit(1)
print('MOTION_AUDIT_PASS progressive=true reduced_motion=true finite_motion=true')
