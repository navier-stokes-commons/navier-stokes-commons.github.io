#!/usr/bin/env python3
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1]
js=(R/'assets/site.js').read_text(); css=(R/'assets/style.css').read_text(); b=(R/'scripts/build_site.py').read_text(); p=json.loads((R/'content/public/experience_policy.json').read_text())
errs=[]
for s in ['NSC R16 fluid hero overlay','data-r16-motion','Flow response','pointer.rawVx','pointer.energy','r16MotionRunning','Deliberately DO NOT stop automatic motion']:
    if s not in js: errs.append('missing JS contract '+s)
for s in ['NSC R16 fluid hero visual system','r16-fluid-canvas','r16-fluid-controls','r16-participation-line']:
    if s not in css: errs.append('missing CSS contract '+s)
for s in ['Take an open problem','Put spare compute to work','Bring mathematical skill, spare compute, or an inference subscription']:
    if s not in b: errs.append('missing generated rich-home copy '+s)
rh=p.get('rich_home',{})
if rh.get('motion_stop_semantics')!=['explicit_user_pause','prefers-reduced-motion']: errs.append('motion stop semantics not canonical')
for k in ['pointer_interaction_preserves_running_intent','parameter_changes_preserve_running_intent','visibility_suspends_without_changing_running_intent','fluid_wake_pointer_velocity','dominant_wireframe_hourglass_prohibited','advanced_parameters_subordinate','spare_compute_primary_cta']:
    if rh.get(k) is not True: errs.append('experience policy missing '+k)
if '/en/math/' != p.get('mathematics_projection'): errs.append('math projection changed')
# Regression tripwires: old public CTA/copy must not remain in generator.
if 'Work on an open problem' in b: errs.append('old CTA remains')
if 'Give an agent a research problem' in b: errs.append('old agent CTA remains')
if errs:
    print('R16_FLUID_HERO_AUDIT_FAILED',file=sys.stderr)
    [print(' - '+e,file=sys.stderr) for e in errs]
    raise SystemExit(1)
print('R16_FLUID_HERO_AUDIT_PASS autoplay_contract=true pointer_velocity_wake=true stop_semantics=explicit_pause_or_reduced advanced_controls=subordinate spare_compute_cta=true math_isolated=true')
