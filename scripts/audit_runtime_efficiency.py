#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re,sys
R=Path(__file__).resolve().parents[1]
css=(R/'assets/style.css').read_text(); js=(R/'assets/site.js').read_text(); errs=[]
# Static payload budgets: generous enough for the selected experience but small
# enough that visual polish cannot silently turn into a framework-sized runtime.
limits={'css':55*1024,'js':64*1024,'fonts':260*1024}
if len(css.encode())>limits['css']: errs.append(f'CSS bytes {len(css.encode())} > {limits["css"]}')
if len(js.encode())>limits['js']: errs.append(f'JS bytes {len(js.encode())} > {limits["js"]}')
font_dir=R/'assets/fonts'; font_bytes=sum(p.stat().st_size for p in font_dir.glob('*.woff2')) if font_dir.exists() else 0
if font_bytes>limits['fonts']: errs.append(f'font bytes {font_bytes} > {limits["fonts"]}')
# The realtime renderer must retain explicit bounded-compute and graceful-degrade signals.
required=[
 'navigator.connection?.saveData','navigator.deviceMemory','navigator.hardwareConcurrency',
 "matchMedia('(max-width: 680px)')",'Math.min(devicePixelRatio||1,lowPower?1.25:1.7)',
 "getContext('webgl2'", "getContext('2d')", "webglcontextlost",
 "document.addEventListener('visibilitychange'", 'cancelAnimationFrame(raf)',
]
for token in required:
    if token not in js: errs.append('runtime efficiency/resilience marker missing: '+token)
# Geometry budget is deliberately statically recoverable from the source.
m=re.search(r'const\s+STREAMS=lowPower\?(\d+):(\d+),STEPS=lowPower\?(\d+):(\d+),N=STREAMS\*STEPS',js)
if not m: errs.append('bounded stream/step geometry declaration missing')
else:
    ls,ds,lstep,dstep=map(int,m.groups()); desktop=ds*dstep; low=ls*lstep
    if desktop>10000: errs.append(f'desktop geometry vertices {desktop} > 10000')
    if low>=desktop: errs.append(f'low-power geometry {low} is not lower than desktop {desktop}')
# A settled page may schedule on input/visibility, but must not have an unconditional perpetual loop.
if 'setInterval(' in js: errs.append('setInterval prohibited in public runtime')
if re.search(r'function\s+frame\([^)]*\)\s*\{[^}]*requestAnimationFrame\(frame\)[^}]*\}',js,re.S):
    errs.append('unconditional perpetual frame loop detected')
for page in (R/'public').rglob('*.html'):
    if re.search(r'<script[^>]+src=["\']https?://',page.read_text(),re.I):
        errs.append('remote runtime script reached public HTML: '+str(page.relative_to(R/'public'))); break
if errs:
    print('RUNTIME_EFFICIENCY_AUDIT_FAILED',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    raise SystemExit(1)
print(f'RUNTIME_EFFICIENCY_AUDIT_PASS css_bytes={len(css.encode())} js_bytes={len(js.encode())} font_bytes={font_bytes} geometry_desktop={ds*dstep if m else "?"} geometry_low_power={ls*lstep if m else "?"} low_power_signals=saveData+viewport+deviceMemory+hardwareConcurrency context_loss=static-fallback')
