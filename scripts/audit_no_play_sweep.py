#!/usr/bin/env python3
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[1];P=R/'public';errs=[]
targets=[]
root=P/'index.html'
if root.exists(): targets.append(root)
en=P/'en'
if en.exists(): targets += sorted(en.rglob('*.html'))
for p in targets:
    txt=p.read_text(encoding='utf-8')
    if 'Play sweep' in txt:
        errs.append(f'{p.relative_to(P)} contains forbidden public English label: Play sweep')
# The two primary entrances must also contain no legacy hero debug controls.
for rel in ['index.html','en/index.html']:
    p=P/rel
    if not p.exists():
        errs.append('missing '+rel); continue
    txt=p.read_text(encoding='utf-8')
    if 'data-vortex-controls' in txt:
        errs.append(rel+' contains legacy vortex debug controls')
    if 'r17-fluid.js' not in txt:
        errs.append(rel+' missing R17 runtime')
if errs:
    print('R17_NO_PLAY_SWEEP_AUDIT_FAILED',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    raise SystemExit(1)
print(f'R17_NO_PLAY_SWEEP_AUDIT_PASS english_pages={len(targets)} legacy_label=absent legacy_debug_controls=absent')
