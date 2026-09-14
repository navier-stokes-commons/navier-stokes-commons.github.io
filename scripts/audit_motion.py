#!/usr/bin/env python3
from pathlib import Path
import re,sys
R=Path(__file__).resolve().parents[1];css=(R/'assets/style.css').read_text();site=(R/'assets/site.js').read_text();r17=(R/'assets/r17-fluid.js').read_text();errs=[]
for x in ['prefers-reduced-motion: reduce','forced-colors: active']:
 if x not in css:errs.append('missing CSS motion/accessibility primitive '+x)
for x in ['prefers-reduced-motion: reduce','NSC R17 unified fluid interaction system','sessionStorage','pageRawVx','pageRawVy','frameInterval']:
 if x not in r17:errs.append('missing R17 motion primitive '+x)
if 'NSC R16 fluid hero overlay' in site:errs.append('R16 runtime remains in site.js')
if "if(document.querySelector('[data-r14-rich-hero]')) return;" not in site:errs.append('legacy R5 rich-home guard missing')
if "if(document.documentElement.lang==='en') return;" not in site:errs.append('legacy ambient English guard missing')
if re.search(r'animation\s*:\s*[^;]*infinite',css,re.I):errs.append('infinite CSS animation prohibited')
if re.search(r'transition\s*:\s*all\b',css,re.I):errs.append('transition: all prohibited')
if errs:print('MOTION_AUDIT_FAILED',errs,file=sys.stderr);raise SystemExit(1)
print('MOTION_AUDIT_PASS progressive=true reduced_motion=true split_r17_runtime=true single_authority=true pagewide_pointer_wake=true')
