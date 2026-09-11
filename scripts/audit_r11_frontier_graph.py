#!/usr/bin/env python3
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]; g=json.loads((R/'content/public/frontier_graph.json').read_text()); u=json.loads((R/'content/public/frontier_updates.json').read_text()); m=json.loads((R/'content/public/missions.json').read_text()); q=json.loads((R/'content/public/quests.json').read_text())
M={x['id'] for x in m}; Q={x['id'] for x in q['quests']}; N={x['id']:x for x in g['nodes']}; errs=[]
if len(N)!=len(g['nodes']): errs.append('duplicate frontier node ids')
for n in N.values():
    if n['program_id'] not in M: errs.append('unknown program '+n['program_id'])
    for x in n['problem_ids']:
        if x not in Q: errs.append('unknown problem '+x)
    if n['priority'] in {'P0','P1'} and (not n.get('review_class') or not n.get('publication_path')): errs.append('high-priority node lacks review/publication path '+n['id'])
if N.get('FG-01',{}).get('program_id')!='NS-M05' or N['FG-01']['priority']!='P0': errs.append('forced-to-unforced must remain explicit P0 strategic frontier')
U={x['id']:x for x in u['updates']}
for k in ['FU-2026-09-09-CAO-CHI-TORUS','FU-2026-09-09-CAO-CHI-R3']:
    if k not in U: errs.append('missing current frontier update '+k)
    elif not any('fixed-force' in s for s in U[k]['does_not_establish']): errs.append(k+' must preserve fixed-force limitation')
# dependency edges must reference nodes
for e in g['edges']:
    if e['from'] not in N or e['to'] not in N: errs.append('edge refers to unknown node')
if errs: print('R11_FRONTIER_AUDIT_FAIL'); print('\n'.join(errs)); raise SystemExit(1)
print(f'R11_FRONTIER_AUDIT_PASS nodes={len(N)} updates={len(U)} p0={sum(n["priority"]=="P0" for n in N.values())}')
