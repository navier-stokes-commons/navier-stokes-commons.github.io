#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from urllib.parse import urljoin,urlparse
import json,os,sys
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/'content/public'; P=ROOT/'public'; errs=[]
load=lambda p:json.loads(p.read_text())
reg=load(C/'public_registry.json')
contract=reg.get('discovery_contract') or {}
if contract.get('kind')!='project-local-custom': errs.append('discovery contract must explicitly be project-local-custom')
if contract.get('iana_well_known_registered') is not False: errs.append('project must not claim RFC 8615/IANA well-known registration')
me=reg.get('machine_endpoints',{})
for required in ['discovery','openapi','frontier','quests','claims','sources','research_context','actions','agent_start','agent_skill','agent_index','llms_index','llms_full']:
    if required not in me: errs.append('machine registry missing '+required)
# Resolve the configured output paths without duplicating endpoint literals.
def output_for(logical): return P/logical.lstrip('/')
for key,logical in me.items():
    p=output_for(logical)
    if not p.exists(): errs.append(f'machine endpoint missing output: {key} -> {logical}')
# OpenAPI is descriptive for static GET resources.
op_path=output_for(me.get('openapi','/__missing__')); op=load(op_path) if op_path.exists() else {}
if op.get('openapi')!='3.1.2': errs.append('OpenAPI document must declare 3.1.2')
paths=op.get('paths',{}) if isinstance(op,dict) else {}
for key,logical in me.items():
    if logical not in paths: errs.append(f'OpenAPI paths missing registry endpoint {key}')
    else:
        get=paths[logical].get('get',{}) if isinstance(paths[logical],dict) else {}
        if 'responses' not in get or '200' not in get.get('responses',{}): errs.append(f'OpenAPI endpoint {key} lacks GET 200 contract')
# Discovery must expose both endpoint refs and the honest contract metadata.
disc_path=output_for(me.get('discovery','/__missing__')); disc=load(disc_path) if disc_path.exists() else {}
if disc.get('discovery_contract')!=contract: errs.append('public discovery does not expose canonical discovery_contract metadata')
# Validate the research-context object with the shipped Draft 2020-12 schema.
rc=load(C/'research_context.json'); schema=load(ROOT/'schemas/research-context.schema.json')
for e in Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(rc): errs.append('research-context schema: '+e.message)
rc_out=output_for(me.get('research_context','/__missing__'))
if rc_out.exists() and load(rc_out)!=rc: errs.append('public research-context endpoint differs from canonical content')
# Core agent context must remain non-empty and publicly reachable.
for key in ['agent_start','agent_skill','agent_index','llms_index','llms_full']:
    p=output_for(me.get(key,'/__missing__'))
    if not p.exists() or not p.read_text().strip(): errs.append('empty/missing agent context '+key)
# Host-bound builds should advertise a sitemap without making it canonical state.
site=os.getenv('SITE_URL','').rstrip('/')
if site:
    sitemap=P/'sitemap.xml'; robots=P/'robots.txt'
    if not sitemap.is_file() or '<urlset' not in sitemap.read_text(): errs.append('SITE_URL build missing sitemap.xml')
    if not robots.is_file() or ('Sitemap: '+site+'/sitemap.xml') not in robots.read_text(): errs.append('robots.txt missing host-bound Sitemap declaration')
    if sitemap.is_file():
        sm=sitemap.read_text()
        for rel in ['','en/','en/quests/','en/context/']:
            if '<loc>'+site+'/'+rel+'</loc>' not in sm: errs.append('sitemap missing core route '+rel)
# Current llms.txt v2 discoverability is an informal proposal, not a standard.
# Require the project to expose it via the describedby link relation without
# changing the canonical endpoint registry semantics.
for hp in [P/'index.html',P/'en/index.html']:
    if hp.is_file():
        h=hp.read_text()
        if 'rel="describedby"' not in h or 'llms.txt' not in h: errs.append(str(hp.relative_to(P))+' missing llms.txt describedby hint')

# Project-subpath resolution: every discovery ref must remain within the synthetic base.
base='https://example.test/project/'; durl=urljoin(base,me['discovery'].lstrip('/'))
for key in list(me):
    ref=disc.get(key)
    if not isinstance(ref,str): errs.append('discovery missing projected ref '+key); continue
    if ref.startswith('/'): errs.append('origin-root discovery ref unsafe for project Pages: '+key)
    if not urljoin(durl,ref).startswith(base): errs.append('discovery ref escapes project base: '+key)
if errs:
    print('MACHINE_LEGIBILITY_AUDIT_FAILED',file=sys.stderr)
    for e in errs[:200]: print(' - '+e,file=sys.stderr)
    raise SystemExit(1)
print(f'MACHINE_LEGIBILITY_AUDIT_PASS endpoints={len(me)} openapi=3.1.2 json_schema=2020-12 discovery=project-local-custom agent_context=true sitemap={bool(site)}')
