#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[1];errs=[]
p=subprocess.run([sys.executable,'scripts/prove2me_bridge.py','export-candidate','NS-Q005'],cwd=R,text=True,capture_output=True)
if p.returncode:errs.append('bridge exporter failed '+p.stderr)
else:
 try:d=json.loads(p.stdout)
 except Exception as e:errs.append('bridge exporter invalid json '+str(e));d={}
 for k in ['nsc_problem_id','nsc_program_id','intended_semantics','semantic_review_requirement','parent_frontier_non_implications','export_state']:
  if k not in d:errs.append('candidate missing '+k)
 if d.get('export_state')!='candidate':errs.append('unreviewed target must remain candidate')
with tempfile.TemporaryDirectory() as td:
 r=Path(td)/'r.json';r.write_text(json.dumps({'nsc_problem_id':'NS-Q005','prove2me_mission_or_theorem_url':'https://prove2.me/theorem/example','formal_statement':'theorem x : True := by trivial','lean_environment':'example','external_status':'proved','observed_at':'2026-09-12T00:00:00Z'}))
 p=subprocess.run([sys.executable,'scripts/prove2me_bridge.py','validate-import',str(r)],cwd=R,text=True,capture_output=True)
 if p.returncode:errs.append('bridge import validator failed '+p.stderr)
 else:
  x=json.loads(p.stdout)
  if x.get('nsc_import_state')!='unreviewed-external-evidence':errs.append('proved external theorem must import as unreviewed evidence')
  if x.get('automatic_parent_claim_transition') is not False:errs.append('external proof must not auto-resolve parent')
if errs:
 print('R14_PROVE2ME_BRIDGE_FAIL',file=sys.stderr);[print(' - '+x,file=sys.stderr) for x in errs];raise SystemExit(1)
print('R14_PROVE2ME_BRIDGE_PASS export_requires_semantics=true import_no_auto_elevation=true')
