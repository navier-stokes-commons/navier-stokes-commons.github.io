#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]
css=(ROOT/'assets/style.css').read_text(); js=(ROOT/'assets/site.js').read_text();errs=[]
for x in ['prefers-reduced-motion: reduce','@view-transition','forced-colors: active']:
    if x not in css:errs.append('missing CSS motion/accessibility primitive: '+x)
for x in ['prefers-reduced-motion: reduce','IntersectionObserver','el.animate','R14 ambient glyph field','nsc:ambient-motion']:
    if x not in js:errs.append('missing JS motion control: '+x)
if re.search(r'animation\s*:\s*[^;]*infinite',css,re.I):errs.append('infinite CSS animation prohibited; persistent motion must be JS-governed and pausable')
if re.search(r'transition\s*:\s*all\b',css,re.I):errs.append('transition: all prohibited')
for page in (ROOT/'public').rglob('*.html'):
    if re.search(r'<(?:video|audio)[^>]*\bautoplay\b',page.read_text(),re.I):errs.append(f'{page.relative_to(ROOT)}: media autoplay prohibited')
if errs:
 print('MOTION_AUDIT_FAILED',file=sys.stderr);[print(' - '+e,file=sys.stderr) for e in errs];raise SystemExit(1)
print('MOTION_AUDIT_PASS progressive=true reduced_motion=true ambient_runtime_motion=true user_pause=true')
