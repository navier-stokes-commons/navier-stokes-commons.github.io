#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,sys
try:
    from jsonschema import Draft202012Validator, FormatChecker
except Exception as e:
    print(f'R11_SCHEMA_AUDIT_UNAVAILABLE jsonschema={e}',file=sys.stderr); raise SystemExit(2)
R=Path(__file__).resolve().parents[1]; C=R/'content/public'; S=R/'schemas'; errs=[]
def load(p): return json.loads(p.read_text())
def check(label,schema_name,obj):
    v=Draft202012Validator(load(S/schema_name),format_checker=FormatChecker())
    for e in sorted(v.iter_errors(obj),key=lambda x:list(x.path)):
        path='.'.join(str(x) for x in e.path) or '<root>'; errs.append(f'{label}:{path}: {e.message}')
check('clay-status','clay-problem-status.schema.json',load(C/'clay_problem_status.json'))
check('frontier-graph','frontier-graph.schema.json',load(C/'frontier_graph.json'))
check('frontier-updates','frontier-updates.schema.json',load(C/'frontier_updates.json'))
# Validate representative generated packets against the public packet schema.
for q in ['NS-Q005','NS-Q032','NS-Q037','NS-Q040']:
    p=subprocess.run([sys.executable,'scripts/export_agent_packet.py',q],cwd=R,text=True,capture_output=True)
    if p.returncode: errs.append(q+': exporter failed: '+p.stderr.strip()); continue
    try: obj=json.loads(p.stdout)
    except Exception as e: errs.append(q+': invalid JSON '+str(e)); continue
    check('agent-packet:'+q,'agent-work-packet.schema.json',obj)
if errs:
    print('R11_SCHEMA_AUDIT_FAIL',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    raise SystemExit(1)
print('R11_SCHEMA_AUDIT_PASS clay=true frontier=true updates=true agent_packets=true')
