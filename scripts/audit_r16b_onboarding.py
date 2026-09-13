#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
guide=ROOT/'public/en/guide/index.html'
start=ROOT/'start.md'
status=ROOT/'content/public/clay_problem_status.json'
sources=ROOT/'content/public/sources.json'
sponsor=ROOT/'docs/SPONSORSHIP_AND_AFFILIATE_POLICY.md'
errors=[]

def need(text, needle, label):
    if needle not in text:
        errors.append(f"{label}: missing {needle!r}")

if not guide.exists():
    errors.append("missing public/en/guide/index.html; run build_site.py first")
else:
    g=guide.read_text(encoding='utf-8')
    for needle in [
        'What do you have?',
        'Never used a coding agent?',
        'Read the long-form GPT-5.6 Sol deep dive',
        'https://chatgpt.com/s/t_6aa685d089588191af3c3917b8af59fd',
        'This is an explanatory aid, not a canonical scientific source.',
        'I have an AI subscription or API credits',
        'I have spare CPU/GPU',
        'I know Lean',
        'I know CFD / numerical methods',
        'I am skeptical',
        'apparently been settled',
    ]:
        need(g, needle, 'guide')

s=start.read_text(encoding='utf-8') if start.exists() else ''
need(s, 'New here?', 'start.md')
need(s, '.well-known/commons.json', 'start.md')
need(s, 'chatgpt.com/s/t_6aa685d089588191af3c3917b8af59fd', 'start.md')

doc=json.loads(status.read_text())
inst=doc['official_problem']['institutional_status']
if inst.get('state')!='cmi-apparently-settled-evaluation-pending':
    errors.append('clay status state not updated')
need(inst.get('note',''), 'apparently been settled', 'clay status note')
need(inst.get('note',''), 'deliberately unhurried', 'clay status note')

src=json.loads(sources.read_text())
if 'clay-2026-announcement' not in {x.get('id') for x in src}:
    errors.append('missing clay-2026-announcement source')

p=sponsor.read_text(encoding='utf-8') if sponsor.exists() else ''
need(p, 'no sponsors, no ads, no affiliate links', 'sponsor policy')
need(p, 'rel="sponsored noopener noreferrer"', 'sponsor policy')
need(p, 'must never affect', 'sponsor policy')

if errors:
    print('R16B_ONBOARDING_FAIL')
    for e in errors:
        print('-',e)
    raise SystemExit(1)
print('R16B_ONBOARDING_PASS')
