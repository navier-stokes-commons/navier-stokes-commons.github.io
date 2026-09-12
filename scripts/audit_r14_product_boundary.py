#!/usr/bin/env python3
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];C=R/'content/public';errs=[]
ex=json.loads((C/'external_executors.json').read_text());p=next((x for x in ex.get('executors',[]) if x.get('id')=='prove2me'),None)
if not p:errs.append('Prove2Me executor missing')
else:
 if p.get('skill_version')!='0.10.3':errs.append('Prove2Me skill pin is not 0.10.3')
 if p.get('workspace_commit')!='8d697eeda2f65d396209a9b4f888602de1f55fbf':errs.append('Prove2Me workspace pin drift')
 if 'semantic' not in p.get('authority_boundary','').lower():errs.append('semantic authority boundary missing')
links=json.loads((C/'formalization_links.json').read_text())
for x in links.get('records',[]):
 if x.get('executor_id')!='prove2me':errs.append('unexpected formal executor in R14 bridge')
 if x.get('nsc_import_state')=='accepted':errs.append('formal executor may not directly create accepted NSC state')
# Explicitly reject accidental construction of a competing generic theorem service.
for rel in ['content/public/external_executors.json','docs/PROVE2ME_INTEROP.md']:
 txt=(R/rel).read_text().lower()
 if 'second general lean' not in txt and 'not a second' not in txt:errs.append(rel+' must make non-duplication boundary explicit')
if errs:
 print('R14_PRODUCT_BOUNDARY_FAIL',file=sys.stderr);[print(' - '+x,file=sys.stderr) for x in errs];raise SystemExit(1)
print('R14_PRODUCT_BOUNDARY_PASS complementary=true generic_lean_duplication=false semantic_boundary=true')
