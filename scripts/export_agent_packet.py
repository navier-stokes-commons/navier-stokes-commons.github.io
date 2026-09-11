#!/usr/bin/env python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text())
qdoc=load('content/public/quests.json'); graph=load('content/public/frontier_graph.json')
quest_id=sys.argv[1] if len(sys.argv)>1 else None
if not quest_id: raise SystemExit('usage: export_agent_packet.py NS-Q###')
quests={q['id']:q for q in qdoc['quests']}; q=quests.get(quest_id)
if not q: raise SystemExit('unknown problem '+quest_id)
node=next((n for n in graph['nodes'] if q['mission_id']==n['program_id']),None)
packet={'schema':'nsc-agent-work-packet-v1','problem_id':q['id'],'program_id':q['mission_id'],'title':q['title'],'task':q['task'],'deliverables':q['deliverables'],'acceptance':q['acceptance'],'review':q['review'],'sources':q.get('source_ids',[]),'dependencies':q.get('dependencies',[]),'claim_ids':q.get('claim_ids',[]),'parallel_safe':q.get('parallel_safe',False),'non_exclusive':q.get('non_exclusive',True),'frontier':({'node_id':node['id'],'lane':node['lane'],'priority':node['priority'],'key_question':node['key_question'],'agent_suitability':node['agent_suitability'],'publication_path':node['publication_path']} if node else {'lane':'unclassified','priority':'P3'}),'provenance_required':['model/provider/version or human author identity','toolchain/environment versions','exact public source/artifact versions','commands/method sufficient for reproduction','limitations, uncertainty, and conflicts'],'submission':{'attempt':'Resolve open_attempt via {{ACTIONS_ENDPOINT}}','result':'Resolve submit_result via {{ACTIONS_ENDPOINT}}','review':'Resolve review via {{ACTIONS_ENDPOINT}}','rule':'An agent result is an artifact for review, never an automatic claim elevation.'}}
print(json.dumps(packet,indent=2,ensure_ascii=False))
