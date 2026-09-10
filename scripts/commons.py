#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from nsc_model import C, expanded_quests, expanded_claims_doc, project_view, capabilities, public_registry

def main():
    ap=argparse.ArgumentParser(description='Navier-Stokes Commons zero-dependency catalog CLI')
    sp=ap.add_subparsers(dest='cmd',required=True)
    sp.add_parser('discover')
    lp=sp.add_parser('list-quests'); lp.add_argument('--rung'); lp.add_argument('--mission'); lp.add_argument('--sprint',action='store_true')
    sh=sp.add_parser('show-quest'); sh.add_argument('quest_id')
    dr=sp.add_parser('draft-attempt'); dr.add_argument('quest_id'); dr.add_argument('--mode',choices=['human','ai','human-ai'],default='human')
    sp.add_parser('validate')
    a=ap.parse_args(); qs=expanded_quests()
    if a.cmd=='discover':
        ep=public_registry()['machine_endpoints']; print(json.dumps({'project':project_view()['name'],'release':project_view()['release'],'capabilities':capabilities(),'start':ep['agent_start'],'discovery':ep['discovery']},indent=2)); return 0
    if a.cmd=='list-quests':
        rows=[q for q in qs if (not a.rung or q['rung']==a.rung) and (not a.mission or q['mission_id']==a.mission) and (not a.sprint or q['founding_sprint'])]
        for q in rows: print(f"{q['id']}\t{q['rung']}\t{q['mission_id']}\t{q['status']}\t{q['title']}")
        return 0
    if a.cmd in {'show-quest','draft-attempt'}:
        q=next((x for x in qs if x['id']==a.quest_id),None)
        if not q: print('unknown quest',a.quest_id,file=sys.stderr); return 2
        if a.cmd=='show-quest': print(json.dumps(q,indent=2,ensure_ascii=False)); return 0
        print(f"# Attempt: {q['id']} {q['title']}\n\nContributor mode: {a.mode}\nStatus: draft\n\n## Plan\n\n## Evidence / source locators\n\n## Tool and model provenance\n\n## Limitations\n\n## Reproduction\n\nAcceptance checklist:\n"+'\n'.join('- [ ] '+x for x in q['acceptance']))
        return 0
    if a.cmd=='validate':
        import subprocess
        return subprocess.run([sys.executable,str(Path(__file__).with_name('catalog.py')),'validate']).returncode
    return 2
if __name__=='__main__': raise SystemExit(main())
