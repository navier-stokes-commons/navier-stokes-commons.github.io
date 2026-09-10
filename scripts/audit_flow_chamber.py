#!/usr/bin/env python3
from __future__ import annotations
import json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/'content/public'; P=ROOT/'public'; errs=[]
doc=json.loads((C/'simulations.json').read_text()); sims=doc.get('simulations',[])
if len(sims)!=1 or sims[0].get('id')!='taylor-vortex-array-2d': errs.append('canonical exact flow simulation missing or ambiguous')
sim=sims[0] if sims else {}; srcids={s['id'] for s in json.loads((C/'sources.json').read_text())}
if set(sim.get('source_ids',[]))-srcids: errs.append('simulation source reference missing')

def expr(node,variables,parameters):
    typ=node['type']
    if typ=='number': return float(node['value'])
    if typ=='param': return float(parameters[node['name']])
    if typ=='var': return float(variables[node['name']])
    args=[expr(a,variables,parameters) for a in node.get('args',[])]
    if node['op']=='add': return sum(args)
    if node['op']=='mul': return math.prod(args)
    if node['op']=='neg': return -args[0]
    if node['op']=='exp': return math.exp(args[0])
    if node['op']=='sin': return math.sin(args[0])
    if node['op']=='cos': return math.cos(args[0])
    if node['op']=='pow': return args[0]**args[1]
    raise ValueError('unknown op '+str(node.get('op')))

def canonical_fields(x,y,t,A,nu):
    f=sim['fields']; vars={'x':x,'y':y,'t':t}; pars={'A':A,'nu':nu}
    return expr(f['u_x'],vars,pars),expr(f['u_y'],vars,pars),expr(f['p'],vars,pars)

def canonical_energy(t,A,nu): return expr(sim['fields']['mean_kinetic_energy'],{'x':0,'y':0,'t':t},{'A':A,'nu':nu})
def oracle_energy(t,A,nu): return (A*A/4)*math.exp(-4*nu*t)
def oracle_fields(x,y,t,A,nu):
    decay=math.exp(-2*nu*t)
    return A*decay*math.sin(x)*math.cos(y),-A*decay*math.cos(x)*math.sin(y),(A*A/4)*math.exp(-4*nu*t)*(math.cos(2*x)+math.cos(2*y))
def d1(f,z,h=2e-5): return (f(z+h)-f(z-h))/(2*h)
def d2(f,z,h=5e-4): return (f(z+h)-2*f(z)+f(z-h))/(h*h)
for T in [0.0,.6,2.1]:
  for X,Y in [(.31,.79),(1.2,2.4),(2.8,5.1)]:
    got=canonical_fields(X,Y,T,1.17,.043); want=oracle_fields(X,Y,T,1.17,.043)
    if max(abs(a-b) for a,b in zip(got,want))>2e-12: errs.append('canonical expression AST differs from independent Taylor-vortex oracle')
A=1.17; nu=.043
worst_div=worst_res=0.0
for t in [0.0,.6,2.1,5.0]:
  for x,y in [(.31,.79),(1.2,2.4),(2.8,5.1),(5.4,3.3)]:
    u,v,p=canonical_fields(x,y,t,A,nu)
    ux=d1(lambda X:canonical_fields(X,y,t,A,nu)[0],x); uy=d1(lambda Y:canonical_fields(x,Y,t,A,nu)[0],y)
    vx=d1(lambda X:canonical_fields(X,y,t,A,nu)[1],x); vy=d1(lambda Y:canonical_fields(x,Y,t,A,nu)[1],y)
    ut=d1(lambda T:canonical_fields(x,y,T,A,nu)[0],t); vt=d1(lambda T:canonical_fields(x,y,T,A,nu)[1],t)
    px=d1(lambda X:canonical_fields(X,y,t,A,nu)[2],x); py=d1(lambda Y:canonical_fields(x,Y,t,A,nu)[2],y)
    lapu=d2(lambda X:canonical_fields(X,y,t,A,nu)[0],x)+d2(lambda Y:canonical_fields(x,Y,t,A,nu)[0],y)
    lapv=d2(lambda X:canonical_fields(X,y,t,A,nu)[1],x)+d2(lambda Y:canonical_fields(x,Y,t,A,nu)[1],y)
    div=ux+vy; ru=ut+u*ux+v*uy+px-nu*lapu; rv=vt+u*vx+v*vy+py-nu*lapv
    worst_div=max(worst_div,abs(div)); worst_res=max(worst_res,abs(ru),abs(rv))
if worst_div>2e-7: errs.append(f'divergence residual too large: {worst_div}')
if worst_res>3e-6: errs.append(f'momentum residual too large: {worst_res}')
# Independent energy oracle from spatial quadrature, not the JSON formula string.
for t in [0,.75,3.25]:
    n=96; total=0.0
    for j in range(n):
      y=2*math.pi*(j+.5)/n
      for i in range(n):
        x=2*math.pi*(i+.5)/n; u,v,_=canonical_fields(x,y,t,A,nu); total += .5*(u*u+v*v)
    mean=total/(n*n); expected=oracle_energy(t,A,nu)
    if abs(canonical_energy(t,A,nu)-expected)>2e-12: errs.append(f'canonical energy AST differs from independent oracle at t={t}')
    if abs(mean-expected)>2e-12: errs.append(f'energy oracle mismatch at t={t}: {mean} vs {expected}')
# Generated representation requirements.
home=(P/'en/index.html').read_text()
for token,label in [('data-flow-chamber','simulation root'),('data-flow-model','canonical expression model'),('data-flow-canvas','progressive canvas'),('data-flow-static','static fallback'),('data-flow-state','parallel textual state'),('data-flow-controls','controls'),('not a reconstruction of the 2026 three-dimensional singularity','scope boundary')]:
    if token not in home: errs.append('generated home missing '+label)
if '<canvas' in home and 'aria-hidden="true"' not in home: errs.append('canvas must not substitute for accessible state')
out=json.loads((P/'data/simulations.json').read_text()) if (P/'data/simulations.json').exists() else None
if out!=doc: errs.append('machine simulation endpoint differs from canonical source')
if errs:
    print('FLOW_CHAMBER_AUDIT_FAILED',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    sys.exit(1)
print(f'FLOW_CHAMBER_AUDIT_PASS worst_div={worst_div:.2e} worst_momentum_residual={worst_res:.2e} energy_quadrature=exact-within-tolerance')
