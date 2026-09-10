#!/usr/bin/env python3
from pathlib import Path
from html import unescape
import json,os,re,sys
from nsc_model import public_registry
ROOT=Path(__file__).resolve().parents[1]
errs=[]
cat=json.loads((ROOT/'content/public/formulas.json').read_text())
if cat.get('schema')!='nsc-formula-ast-v1': errs.append('formula catalog schema mismatch')
forms={f['id']:f for f in cat.get('formulas',[])}
formula=forms.get('incompressible-navier-stokes-forced')
if not formula: errs.append('canonical forced incompressible Navier-Stokes formula missing')

def tex(node):
    typ=node['type']
    if typ=='row': return ' '.join(tex(x) for x in node['children']).replace(' ,',',')
    if typ=='identifier': return {'ν':r'\nu'}.get(node['value'],node['value'])
    if typ=='number': return node['value']
    if typ=='operator': return {'∂':r'\partial','·':r'\cdot','∇':r'\nabla','Δ':r'\Delta','−':'-'}.get(node['value'],node['value'])
    if typ=='subscript': return f"{tex(node['base'])}_{{{tex(node['sub'])}}}"
    if typ=='group': return r'\left('+' '.join(tex(x) for x in node['children'])+r'\right)'
    if typ=='space': return r'\qquad'
    raise ValueError(typ)

expected=tex(formula['ast']) if formula else ''
if r'\nu \Delta u' not in expected: errs.append(f'canonical AST viscosity term invalid: {expected!r}')
registry=public_registry(); formula_route=registry['machine_endpoints']['formulas']; discovery_route=registry['machine_endpoints']['discovery']
endpoint=ROOT/'public'/formula_route.lstrip('/')
if not endpoint.exists(): errs.append('public formula catalog endpoint missing')
elif_data=json.loads(endpoint.read_text()) if endpoint.exists() else None
if elif_data is not None and elif_data!=cat: errs.append('public formula endpoint differs from canonical catalog')
for loc in ('en','es','pt-BR','fr','ar','zh-Hans','de','ja'):
    p=ROOT/'public'/loc/'index.html'
    if not p.exists(): errs.append(f'missing {loc} home'); continue
    s=p.read_text()
    attrs=[unescape(x) for x in re.findall(r'data-equation-tex="([^"]+)"',s)]
    anns=[unescape(x) for x in re.findall(r'<annotation encoding="application/x-tex">(.*?)</annotation>',s,re.S)]
    ids=re.findall(r'data-formula-id="([^"]+)"',s)
    if not attrs or not anns or not ids:
        errs.append(f'{loc}: formula representations missing'); continue
    if any(x!=expected for x in attrs): errs.append(f'{loc}: data TeX drift')
    if any(x!=expected for x in anns): errs.append(f'{loc}: annotation TeX drift')
    if any(x!='incompressible-navier-stokes-forced' for x in ids): errs.append(f'{loc}: formula id drift')
    if '<mi>ν</mi><mo>Δ</mo><mi>u</mi>' not in s: errs.append(f'{loc}: visible MathML viscosity term missing')
disc=json.loads((ROOT/'public'/discovery_route.lstrip('/')).read_text())
expected_disc=os.path.relpath(formula_route.lstrip('/'),start='.well-known').replace(os.sep,'/')
if disc.get('formulas')!=expected_disc: errs.append('discovery document missing deployment-relative formula endpoint')
if errs:
    print('MATH_REPRESENTATION_AUDIT_FAILED',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    sys.exit(1)
print(f'MATH_REPRESENTATION_AUDIT_PASS formulas={len(forms)} canonical_tex={expected}')
