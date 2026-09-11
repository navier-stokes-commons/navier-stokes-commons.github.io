#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,sys
R=Path(__file__).resolve().parents[1]; errs=[]
for q in ['NS-Q005','NS-Q018','NS-Q032']:
    p=subprocess.run([sys.executable,'scripts/export_agent_packet.py',q],cwd=R,text=True,capture_output=True)
    if p.returncode: errs.append(q+' exporter failed: '+p.stderr); continue
    try:d=json.loads(p.stdout)
    except Exception as e: errs.append(q+' invalid json '+str(e)); continue
    for k in ['task','deliverables','acceptance','review','sources','dependencies','frontier','submission']:
        if k not in d: errs.append(q+' missing '+k)
    if q=='NS-Q032' and d['frontier'].get('priority')!='P0': errs.append('Q032 packet must expose P0 frontier priority')
    if d.get('submission',{}).get('rule','').find('never')<0: errs.append(q+' missing no-auto-elevation rule')
if errs: print('R11_AGENT_PACKET_AUDIT_FAIL');print('\n'.join(errs));raise SystemExit(1)
print('R11_AGENT_PACKET_AUDIT_PASS representative_packets=3')
