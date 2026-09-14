#!/usr/bin/env python3
from pathlib import Path
import re,sys
R=Path(__file__).resolve().parents[1];css=(R/'assets/style.css').read_text();site=(R/'assets/site.js').read_text();r17=(R/'assets/r17-fluid.js').read_text();errs=[]
limits={'css':60*1024,'site_js':48*1024,'r17_js':27*1024,'rich_js':64*1024,'fonts':260*1024}
if len(css.encode())>limits['css']:errs.append(f'CSS bytes {len(css.encode())} > {limits["css"]}')
if len(site.encode())>limits['site_js']:errs.append(f'base JS bytes {len(site.encode())} > {limits["site_js"]}')
if len(r17.encode())>limits['r17_js']:errs.append(f'R17 JS bytes {len(r17.encode())} > {limits["r17_js"]}')
if len(site.encode())+len(r17.encode())>limits['rich_js']:errs.append(f'combined rich JS bytes {len(site.encode())+len(r17.encode())} > {limits["rich_js"]}')
font_dir=R/'assets/fonts';font_bytes=sum(p.stat().st_size for p in font_dir.glob('*.woff2')) if font_dir.exists() else 0
if font_bytes>limits['fonts']:errs.append(f'font bytes {font_bytes} > {limits["fonts"]}')
# Translated surfaces still use the bounded legacy renderer; keep its resilience contract until migration.
for token in ['navigator.connection?.saveData','navigator.deviceMemory','navigator.hardwareConcurrency',"getContext('webgl2'",'webglcontextlost',"document.addEventListener('visibilitychange'",'cancelAnimationFrame(raf)']:
 if token not in site:errs.append('legacy runtime efficiency/resilience marker missing: '+token)
m=re.search(r'const\s+STREAMS=lowPower\?(\d+):(\d+),STEPS=lowPower\?(\d+):(\d+),N=STREAMS\*STEPS',site)
if not m:errs.append('bounded legacy stream/step geometry declaration missing')
else:
 ls,ds,lstep,dstep=map(int,m.groups());desktop=ds*dstep;low=ls*lstep
 if desktop>10000:errs.append(f'legacy desktop geometry vertices {desktop} > 10000')
 if low>=desktop:errs.append(f'legacy low-power geometry {low} is not lower than desktop {desktop}')
# R17 English rich surfaces use a separate, bounded Canvas2D runtime.
for token in ['saveData','navigator.deviceMemory','navigator.hardwareConcurrency','frameInterval','heroVisible','drawHeroStatic','static-fallback','1000 : 3400']:
 if token not in r17:errs.append('R17 efficiency/fallback marker missing: '+token)
m2=re.search(r'const N = ctx \? \(lowPower \? (\d+) : (\d+)\) : 0',r17)
if not m2:errs.append('R17 particle budget declaration missing')
else:
 low17,desktop17=map(int,m2.groups())
 if desktop17>4000:errs.append(f'R17 desktop particles {desktop17} > 4000')
 if low17>=desktop17:errs.append('R17 low-power particle budget is not smaller')
if 'setInterval(' in site+r17:errs.append('setInterval prohibited in public runtime')
# A requestAnimationFrame loop is permitted only behind the R17 effective-motion state and bounded cadence.
if 'if (now - lastRender < frameInterval)' not in r17 or 'if (run) schedule();' not in r17:errs.append('R17 render loop lacks cadence/run guards')
for page in (R/'public').rglob('*.html'):
 if re.search(r'<script[^>]+src=["\']https?://',page.read_text(),re.I):errs.append('remote runtime script reached public HTML: '+str(page.relative_to(R/'public')));break
if errs:
 print('RUNTIME_EFFICIENCY_AUDIT_FAILED',file=sys.stderr);[print(' - '+e,file=sys.stderr) for e in errs];raise SystemExit(1)
print(f'RUNTIME_EFFICIENCY_AUDIT_PASS css_bytes={len(css.encode())} site_js_bytes={len(site.encode())} r17_js_bytes={len(r17.encode())} rich_js_bytes={len(site.encode())+len(r17.encode())} font_bytes={font_bytes} legacy_geometry={ds*dstep if m else "?"} r17_particles={desktop17 if m2 else "?"} low_power_r17={low17 if m2 else "?"}')
