#!/usr/bin/env python3
from pathlib import Path
import json,sys,re
R=Path(__file__).resolve().parents[1]; P=R/'public'; errs=[]
site=(R/'assets/site.js').read_text(); r17=(R/'assets/r17-fluid.js').read_text(); css=(R/'assets/style.css').read_text(); gen=(R/'scripts/build_site.py').read_text(); pol=json.loads((R/'content/public/experience_policy.json').read_text());
for s in ["if(document.querySelector('[data-r14-rich-hero]')) return;","if(document.documentElement.lang==='en') return;","R14 ambient glyph field"]:
    if s not in site: errs.append('legacy runtime guard/marker missing: '+s)
if 'NSC R16 fluid hero overlay' in site: errs.append('failed R16 overlay remains in site.js')
for s in ['NSC R17 unified fluid interaction system','sessionStorage','pageRawVx','pageRawVy','pageEnergy','drawHeroStatic','frameInterval','r17-renderer-ready','data-r17-pause','resetPointerWhileInactive']:
    if s not in r17: errs.append('R17 runtime contract missing: '+s)
for bad in ['localStorage.setItem(storageKey','derived.open = true','Play sweep']:
    if bad in r17: errs.append('R17 prohibited runtime token: '+bad)
for s in ['NSC R17 unified fluid visual system','touch-action:pan-y pinch-zoom!important','r17-ambient-field','r17-cursor-fluid','r17-global-pause']:
    if s not in css: errs.append('R17 CSS contract missing: '+s)
for s in ['assets/r17-fluid.js','r17_script','Take an open problem','Put spare compute to work','en/quests/index.html','Interactive exploratory UI field when JavaScript is available']:
    if s not in gen: errs.append('generator integration missing: '+s)
for rel in ['index.html','en/index.html']:
    p=P/rel
    if not p.exists(): errs.append('missing built '+rel); continue
    h=p.read_text()
    if 'r17-fluid.js' not in h: errs.append(rel+' missing R17 script')
    if 'Play sweep' in h: errs.append(rel+' still exposes Play sweep')
    if 'data-vortex-controls' in h: errs.append(rel+' still contains legacy debug controls')
    if 'data-vortex-static' not in h: errs.append(rel+' missing no-JS static fallback')
for rel in ['en/guide/index.html','en/quests/index.html','en/agents/index.html','en/frontier/index.html']:
    p=P/rel
    if not p.exists(): errs.append('missing built '+rel); continue
    h=p.read_text()
    if 'r17-fluid.js' not in h: errs.append(rel+' missing page-wide R17 runtime')
    if 'data-ambient-field' not in h: errs.append(rel+' missing page-wide ambient canvas')
math=P/'en/math/index.html'
if math.exists():
    h=math.read_text().lower()
    if '<script' in h or 'rel="stylesheet"' in h or '<style' in h: errs.append('Mathematics projection is no longer plain')
rh=pol.get('rich_home',{})
required={'interaction_system':'r17-unified-fluid-field','runtime_delivery':'split-english-rich-pages','pagewide_pointer_wake':True,'pointer_velocity_response':True,'pointer_velocity_decay':True,'first_pointer_sample_zero_velocity':True,'legacy_vortex_renderer_on_en':False,'debug_controls_first_viewport':False,'canvas_failure_falls_back_static':True,'mobile_touch_allows_vertical_scroll':True}
for k,v in required.items():
    if rh.get(k)!=v: errs.append(f'policy {k}={rh.get(k)!r}, wanted {v!r}')
if rh.get('motion_stop_semantics')!=['explicit_user_pause','prefers-reduced-motion']: errs.append('wrong motion stop semantics')
if pol.get('mathematics_projection')!='/en/math/': errs.append('math projection changed')
if errs:
    print('R17_FLUID_SYSTEM_AUDIT_FAILED',file=sys.stderr)
    [print(' - '+e,file=sys.stderr) for e in errs]
    raise SystemExit(1)
print('R17_FLUID_SYSTEM_AUDIT_PASS single_authority=true split_runtime=true pagewide_pointer_wake=true fallback=true r16_removed=true math_isolated=true')
