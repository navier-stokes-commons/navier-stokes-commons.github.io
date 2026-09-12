#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import json, subprocess, sys
from nsc_model import public_registry

R=Path(__file__).resolve().parents[1]
errs=[]
endpoints=public_registry()['machine_endpoints']
quests_path=R/('public'+endpoints['quests'])
agent_packets_rel=endpoints['agent_packets'].lstrip('/')
agent_packets_dir=agent_packets_rel.rsplit('/',1)[0]
expected_operations={'attempt':'claim_quest','result':'submit_result','review':'request_review'}
action_ids={x['id'] for x in json.loads((R/'content/public/actions.json').read_text())['operations']}

def check_packet(packet, label):
    for key in ['task','deliverables','acceptance','review','sources','dependencies','frontier','submission']:
        if key not in packet: errs.append(label+' missing '+key)
    submission=packet.get('submission',{})
    if submission.get('actions')!='../actions.json': errs.append(label+' unresolved submission endpoint')
    if not submission.get('reference_semantics'): errs.append(label+' missing reference semantics')
    if '{{' in json.dumps(submission): errs.append(label+' unresolved submission placeholder')
    if 'never' not in submission.get('rule',''): errs.append(label+' missing no-auto-elevation rule')
    for key,value in expected_operations.items():
        if submission.get(key)!=value or value not in action_ids: errs.append(label+' invalid operation '+key)

index_path=R/'public'/agent_packets_rel
if not index_path.is_file():
    print('R11_AGENT_PACKET_AUDIT_FAIL missing built index; run build_site.py first')
    raise SystemExit(1)
index=json.loads(index_path.read_text())
if not index.get('reference_semantics'): errs.append('index missing reference semantics')
expected_ids={q['id'] for q in json.loads(quests_path.read_text())['quests']}
items=index.get('packets',[])
if {item.get('problem_id') for item in items}!=expected_ids or len(items)!=len(expected_ids):
    errs.append('index must include every research problem exactly once')
built={}
for item in items:
    qid=item['problem_id']; reference=item.get('url','')
    if reference!=qid+'.json':
        errs.append(qid+' index URL must be document-relative'); continue
    packet_path=index_path.parent/reference
    if not packet_path.is_file(): errs.append(qid+' missing built packet'); continue
    packet=json.loads(packet_path.read_text()); built[qid]=packet
    check_packet(packet,qid+' built')
    if packet.get('problem_id')!=qid: errs.append(qid+' packet identity mismatch')
    for base in ['https://example.github.io/project/','https://example.gitlab.io/project/','https://example.org/']:
        index_url=urljoin(base,agent_packets_rel)
        packet_url=urljoin(index_url,reference)
        actions_url=urljoin(packet_url,packet.get('submission',{}).get('actions',''))
        if packet_url!=urljoin(base,agent_packets_dir+'/'+qid+'.json'): errs.append(qid+' escaped deployment base')
        if actions_url!=urljoin(base,'data/actions.json'): errs.append(qid+' actions escaped deployment base')
        target=R/'public'/urlsplit(actions_url).path.removeprefix(urlsplit(base).path)
        if not target.is_file(): errs.append(qid+' actions endpoint missing from built tree')
for qid in ['NS-Q005','NS-Q018','NS-Q032']:
    result=subprocess.run([sys.executable,'scripts/export_agent_packet.py',qid],cwd=R,text=True,capture_output=True)
    if result.returncode: errs.append(qid+' exporter failed: '+result.stderr); continue
    try: packet=json.loads(result.stdout)
    except ValueError: errs.append(qid+' invalid CLI JSON'); continue
    check_packet(packet,qid+' CLI')
    if qid=='NS-Q032' and packet.get('frontier',{}).get('priority')!='P0': errs.append('Q032 must expose P0 priority')
    if packet.get('submission')!=built.get(qid,{}).get('submission'): errs.append(qid+' CLI/built submission mismatch')
if errs:
    print('R11_AGENT_PACKET_AUDIT_FAIL'); print('\n'.join(errs)); raise SystemExit(1)
print(f'R11_AGENT_PACKET_AUDIT_PASS representative_packets=3 built_packets={len(items)} deployment_bases=3 submission_actions=true')
