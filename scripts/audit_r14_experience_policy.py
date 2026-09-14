#!/usr/bin/env python3
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];P=R/'public';errs=[]
h=(P/'en/index.html').read_text();root=(P/'index.html').read_text();math=(P/'en/math/index.html').read_text();site=(R/'assets/site.js').read_text();r17=(R/'assets/r17-fluid.js').read_text();css=(R/'assets/style.css').read_text();pol=json.loads((R/'content/public/experience_policy.json').read_text()).get('rich_home',{})
if pol.get('interaction_system')!='r17-unified-fluid-field':errs.append('rich-home interaction authority is not R17')
if pol.get('motion_stop_semantics')!=['explicit_user_pause','prefers-reduced-motion']:errs.append('experience policy contradicts R17 stop semantics')
for name,text in [('root',root),('en',h)]:
 for tok in ['class="r14-hero"','data-vortex-stage','class="r14-abcd-strip"','>Mathematics<','r17-fluid.js']:
  if tok not in text:errs.append(name+' missing '+tok)
 if text.find('data-vortex-stage')>text.find('class="r14-abcd-strip"'):errs.append(name+' scientific visual must precede status strip')
 if 'Play sweep' in text or 'data-vortex-controls' in text:errs.append(name+' exposes superseded legacy hero controls')
if '<script' in math.lower() or '<link rel="stylesheet"' in math.lower() or '<style' in math.lower():errs.append('Mathematics projection must remain stylesheet/JS independent')
for tok in ['NSC R17 unified fluid interaction system','sessionStorage','pageRawVx','pageRawVy','Pause motion']:
 if tok not in r17:errs.append('R17 runtime missing '+tok)
for tok in ["if(document.querySelector('[data-r14-rich-hero]')) return;","if(document.documentElement.lang==='en') return;",'R14 ambient glyph field']:
 if tok not in site:errs.append('legacy runtime not guarded/preserved for translated pages: '+tok)
for rel in ['en/guide/index.html','en/quests/index.html','en/agents/index.html']:
 p=P/rel
 if not p.exists() or 'r17-fluid.js' not in p.read_text():errs.append(rel+' missing English page-wide R17 runtime')
if '/* === R14 RICH DEFAULT / MATHEMATICS ISOLATION === */' not in css:errs.append('R14 rich-layout CSS authority marker missing')
if errs:
 print('RICH_EXPERIENCE_POLICY_FAIL',file=sys.stderr);[print(' - '+x,file=sys.stderr) for x in errs];raise SystemExit(1)
print('RICH_EXPERIENCE_POLICY_PASS rich_default=true r17_single_authority=true auto=true pagewide_wake=true math_isolated=true')
