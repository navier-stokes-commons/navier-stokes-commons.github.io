#!/usr/bin/env python3
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]
css=(ROOT/'assets/style.css').read_text(); js=(ROOT/'assets/site.js').read_text(); gen=(ROOT/'scripts/build_site.py').read_text(); errs=[]
required=['--bg:','--surface:','--text:','--muted:','--primary:','--focus:','--control-min: 44px','container-type:','@container','margin-inline','padding-inline','@view-transition','prefers-color-scheme','prefers-contrast','forced-colors: active','@media print','Newsreader','Geist','Geist Mono']
for x in required:
    if x not in css: errs.append('missing design-system/platform primitive: '+x)
if len(re.findall(r'(?m)^:root\s*\{',css)) != 1: errs.append('design tokens must have exactly one global :root authority')
if re.search(r'transition\s*:\s*all\b',css): errs.append('transition: all prohibited')
# R17's scoped canvas layering uses deliberate priority overrides; retain the
# global design-system budget for all other rules.
non_r17_css=re.sub(r'\.r17[^}]*\}', '', css)
if non_r17_css.count('!important')>20: errs.append(f'excessive !important count {non_r17_css.count("!important")}')
# Local self-hosted fonts are now required; remote font/style dependencies remain prohibited.
for family in ['Newsreader Variable','Geist Variable','Geist Mono Variable']:
    if family not in css: errs.append('self-hosted @font-face missing '+family)
for url in re.findall(r'url\(([^)]+)\)',css,re.I):
    u=url.strip('"\' ')
    if re.match(r'https?://|//',u,re.I): errs.append('remote CSS asset prohibited: '+u)
# The flagship canvas is typed schematic; the exact Taylor canvas remains separately typed.
if "querySelector('[data-vortex-canvas]')" not in js: errs.append('flagship renderer not scoped to data-vortex-canvas')
if "querySelector('[data-flow-canvas]')" not in js: errs.append('exact reference renderer missing')
if gen.count('data-vortex-canvas') != 1: errs.append(f'exactly one canonical flagship canvas declaration expected in generator, found {gen.count("data-vortex-canvas")}')
if 'data-representation-status="schematic"' not in gen or 'data-quantitative-status="derived-leading-exponents"' not in gen: errs.append('flagship canvas lacks semantic truth boundary')
if errs:
    print('DESIGN_SYSTEM_AUDIT_FAILED',file=sys.stderr); [print(' - '+e,file=sys.stderr) for e in errs]; sys.exit(1)
print(f'DESIGN_SYSTEM_AUDIT_PASS css_bytes={len(css.encode())} js_bytes={len(js.encode())} canvas_contract=schematic-flagship+exact-reference fonts=self-hosted')
