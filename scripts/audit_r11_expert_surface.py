#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,json
R=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,'scripts/build_site.py'],cwd=R,check=True)
errs=[]
def txt(p):
    f=R/'public'/p
    if not f.exists(): errs.append('missing '+p); return ''
    return f.read_text(errors='replace')
h=txt('en/index.html'); root=txt('index.html'); fr=txt('en/frontier/index.html'); rv=txt('en/review/index.html'); ex=txt('en/explain/index.html'); probs=txt('en/quests/index.html'); guide=txt('en/guide/index.html'); agents=txt('en/agents/index.html')
for needle in ['OpenAI claims C and D','A and B remain open','Review C/D']:
    if needle not in h and needle not in root: errs.append('missing expert-first thesis/action '+needle)
if not (('Take an open problem' in h or 'Take an open problem' in root) or ('Work on an open problem' in h or 'Work on an open problem' in root)):
    errs.append('missing expert-first thesis/action open-problem CTA')
if not (('Put spare compute to work' in h or 'Put spare compute to work' in root) or ('Give an agent a research problem' in h or 'Give an agent a research problem' in root)):
    errs.append('missing expert-first thesis/action spare-compute CTA')
for bad in ['One hard problem. Many legitimate ways to help.','Start a quest','Research Sprint']:
    if bad in h or bad in root: errs.append('legacy general-public/gamified first-surface copy remains: '+bad)
for label,doc in [('frontier',fr),('review',rv),('explain',ex)]:
    if doc.count('<main')!=1: errs.append(label+' must contain exactly one main landmark')
    for fake in ['/fr/'+label+'/', '/es/'+label+'/', '/ar/'+label+'/', '/zh-Hans/'+label+'/']:
        if fake in doc: errs.append(label+' advertises non-existent localized hreflang '+fake)
for bad in ['Bounded quests','Open quests','Start a quest','Research Sprint']:
    if bad in probs or bad in guide or bad in agents: errs.append('legacy casual research vocabulary remains on expert workflow: '+bad)
for needle in ['Forced → unforced','Independent analytic proof audit','Lean certificate','The frontier already moved']:
    if needle not in fr: errs.append('frontier route missing '+needle)
if 'Review is part of the research' not in rv: errs.append('review lifecycle not visible')
if 'A / B / C / D' not in ex: errs.append('ABCD explainer missing')
for p in ['data/clay-problem-status.json','data/frontier-graph.json','data/frontier-updates.json','data/agent-packets/index.json','openapi.json','.well-known/commons.json']:
    if not (R/'public'/p).exists(): errs.append('machine projection missing '+p)
if errs: print('R11_EXPERT_SURFACE_AUDIT_FAIL');print('\n'.join(errs));raise SystemExit(1)
print('R11_EXPERT_SURFACE_AUDIT_PASS thesis=true frontier=true review=true agent_packets=true')
