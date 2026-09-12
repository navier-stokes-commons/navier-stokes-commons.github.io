#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path

KNOWN_A_TITLE='Formalize Navier-Stokes Open Problem'
KNOWN_A_URL='https://prove2.me/f/partial-differential-equations'

def validate(d):
    errs=[]
    if d.get('schema')!='nsc-prove2me-search-receipt-v1':errs.append('bad schema')
    for k in ['searched_at','queries','missions_checked','theorems_checked','decision','intended_scope']:
        if k not in d:errs.append('missing '+k)
    if len(d.get('queries',[]))<2:errs.append('insufficient catalog queries')
    decision=d.get('decision')
    if decision not in {'reuse-existing','extend-existing','create-new-nonoverlap','no-export'}:errs.append('invalid decision')
    scope=' '.join(d.get('intended_scope',[]) if isinstance(d.get('intended_scope'),list) else [str(d.get('intended_scope',''))]).lower()
    existing=' '.join(str(x) for x in d.get('existing_overlap_titles',[])).lower()
    considered=d.get('known_statement_a_mission_considered') is True
    if not considered:errs.append('existing statement-A mission was not explicitly considered')
    if decision=='create-new-nonoverlap' and re.search(r'\bstatement\s*a\b|fefferman\s*a|existence_and_smoothness_r3',scope):
        errs.append('cannot create a duplicate statement-A mission')
    if decision=='create-new-nonoverlap' and d.get('equivalent_found') is True:
        errs.append('cannot create new mission when equivalent found')
    if decision in {'reuse-existing','extend-existing'} and not d.get('selected_existing_url'):
        errs.append('reuse/extend decision missing selected existing URL')
    if errs: raise SystemExit('PROVE2ME_REUSE_GATE_FAIL '+ '; '.join(errs))
    return {'schema':'nsc-prove2me-reuse-decision-v1','decision':decision,'intended_scope':d.get('intended_scope'),'known_statement_a_mission':KNOWN_A_TITLE,'known_statement_a_catalog_url':KNOWN_A_URL,'equivalent_found':bool(d.get('equivalent_found')),'selected_existing_url':d.get('selected_existing_url'),'new_mission_allowed':decision=='create-new-nonoverlap'}

def selftest():
    base={'schema':'nsc-prove2me-search-receipt-v1','searched_at':'2026-09-12T00:00:00Z','queries':['Navier-Stokes','Fefferman'],'missions_checked':1,'theorems_checked':10,'known_statement_a_mission_considered':True,'existing_overlap_titles':[KNOWN_A_TITLE]}
    a={**base,'decision':'reuse-existing','intended_scope':['Fefferman statement A'],'equivalent_found':True,'selected_existing_url':KNOWN_A_URL}
    validate(a)
    cd={**base,'decision':'create-new-nonoverlap','intended_scope':['Fefferman statements C and D / 2026 forced blowup certificate'],'equivalent_found':False}
    validate(cd)
    bad={**base,'decision':'create-new-nonoverlap','intended_scope':['Fefferman statement A'],'equivalent_found':False}
    try:validate(bad);raise RuntimeError('duplicate A mission was allowed')
    except SystemExit:pass
    print('PROVE2ME_REUSE_GATE_SELFTEST_PASS')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('receipt',nargs='?');ap.add_argument('--selftest',action='store_true');ap.add_argument('--output');a=ap.parse_args()
    if a.selftest:selftest();return 0
    if not a.receipt:ap.error('receipt required unless --selftest')
    out=validate(json.loads(Path(a.receipt).read_text()));text=json.dumps(out,indent=2,ensure_ascii=False)+'\n'
    if a.output:Path(a.output).write_text(text)
    else:sys.stdout.write(text)
    return 0
if __name__=='__main__':raise SystemExit(main())
