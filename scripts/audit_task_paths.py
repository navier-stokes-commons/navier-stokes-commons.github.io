#!/usr/bin/env python3
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
from collections import deque
import json,sys
R=Path(__file__).resolve().parents[1]; P=R/'public'; errs=[]
class Links(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self._a=None; self._text=[]
    def handle_starttag(self,t,a):
        if t=='a': self._a=dict(a).get('href',''); self._text=[]
    def handle_data(self,d):
        if self._a is not None:self._text.append(d)
    def handle_endtag(self,t):
        if t=='a' and self._a is not None:
            self.links.append((self._a,' '.join(''.join(self._text).split())));self._a=None;self._text=[]
def parse(path):
    x=Links();x.feed(path.read_text());return x.links
def local_target(page,href):
    if not href or href.startswith(('#','mailto:','tel:')):return None
    q=urlsplit(href)
    if q.scheme or q.netloc:return None
    t=(page.parent/unquote(q.path)).resolve() if q.path else page
    try:t.relative_to(P.resolve())
    except ValueError:return None
    if q.path.endswith('/') or t.is_dir():t=t/'index.html'
    return t if t.is_file() and t.suffix=='.html' else None
# Build human link graph.
pages=list(P.rglob('*.html')); graph={p:[] for p in pages}
for p in pages:
    for href,text in parse(p):
        t=local_target(p,href)
        if t in graph:graph[p].append((t,text,href))
def dist(src,dst,maxd=4):
    q=deque([(src,0)]);seen={src}
    while q:
        p,d=q.popleft()
        if p==dst:return d
        if d>=maxd:continue
        for t,_,_ in graph.get(p,[]):
            if t not in seen:seen.add(t);q.append((t,d+1))
    return None
root=P/'index.html'; home=P/'en/index.html'
core={'quests':P/'en/quests/index.html','missions':P/'en/missions/index.html','sprint':P/'en/sprint/index.html','agents':P/'en/agents/index.html','context':P/'en/context/index.html','contribute':P/'en/contribute/index.html'}
for label,dst in core.items():
    if not dst.is_file():errs.append('missing core human route '+label);continue
    d=dist(root,dst,3)
    if d is None or d>2:errs.append(f'root -> {label} click depth {d} exceeds 2')
# English flagship must give direct information scent to frontier and missions.
for label in ['quests','missions']:
    if dist(home,core[label],1)!=1:errs.append(f'en home lacks direct route to {label}')
# Quest discovery -> detail -> collaboration transaction.
quest_index=core['quests']; qlinks=[t for t,_,_ in graph.get(quest_index,[]) if '/en/quests/' in t.as_posix() and t!=quest_index]
if not qlinks:errs.append('quest index exposes no quest-detail links')
else:
    qpage=sorted(set(qlinks))[0]; links=parse(qpage); text=' '.join(t for _,t in links).lower()
    if 'start non-exclusive attempt' not in text and 'contribution instructions' not in text:errs.append('quest detail lacks start-attempt action')
    if 'submit result' not in text:errs.append('quest detail lacks submit-result action')
    if 'review or falsify' not in text:errs.append('quest detail lacks review/falsify action')
# Context page must expose lineage/provenance in visible text rather than metadata only.
ctx=core['context'].read_text().lower() if core['context'].is_file() else ''
for token in ['lineage','openai','buckmaster','córdoba']:
    if token not in ctx:errs.append('context page lacks visible trust/lineage token '+token)
# Machine path objective: public-only cold-start receipt must exist and pass after its independent audit.
receipt=R/'audit/open-beta/agent_cold_start.json'
if not receipt.is_file():errs.append('agent cold-start receipt missing')
else:
    try:d=json.loads(receipt.read_text())
    except Exception:d={}
    if d.get('pass') is not True or d.get('private_context_used') is not False:errs.append('agent cold-start receipt does not prove public-only success')
if errs:
    print('TASK_PATH_AUDIT_FAILED',file=sys.stderr)
    for e in errs:print(' - '+e,file=sys.stderr)
    raise SystemExit(1)
print('TASK_PATH_AUDIT_PASS root_to_core<=2 home_to_frontier=1 quest_to_transactions=true context_lineage=true agent_public_only=true')
