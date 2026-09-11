#!/usr/bin/env python3
"""Aggregate pre-recorded synthetic-review evidence without pretending it is human data.

This tool never calls an LLM. It is deliberately conservative:
- deterministic hard vetoes are evaluated before preferences;
- numeric objective vectors define the measured Pareto archive;
- pairwise reviews must be mirrored A/B + B/A within one block;
- development evidence is separated from a held-out confirmation split;
- held-out claims require more than one judge/model family;
- Wilson intervals describe repeated synthetic-instrument behavior only.

The tool cannot establish human-population preference or global design optimality.
"""
from __future__ import annotations
import argparse,json,math,sys
from collections import defaultdict
from pathlib import Path

DEFAULT_EQ=[0.45,0.55]

def wilson(wins:int,n:int,z:float=1.959963984540054):
    if n<=0:return [0.0,1.0]
    p=wins/n; d=1+z*z/n; c=(p+z*z/(2*n))/d
    h=z*math.sqrt((p*(1-p)+z*z/(4*n))/n)/d
    return [max(0.0,c-h),min(1.0,c+h)]

def dominates(a,b,directions,eps=1e-12):
    """True iff a is no worse everywhere and strictly better somewhere."""
    better=False
    for k,dirn in directions.items():
        if k not in a or k not in b:return False
        av,bv=float(a[k]),float(b[k])
        if dirn=='max':
            if av < bv-eps:return False
            if av > bv+eps:better=True
        elif dirn=='min':
            if av > bv+eps:return False
            if av < bv-eps:better=True
        else:raise ValueError(f'bad direction {dirn!r} for {k}')
    return better

def summarize_pairwise(rows,eq,min_holdout_families):
    # A block is one judge instance viewing the same comparison in both orders.
    # Keeping family/id in the key prevents two different judges from being
    # accidentally treated as an order-mirrored pair.
    groups=defaultdict(list)
    for r in rows:
        split=r.get('split','development')
        key=(split,r.get('challenger'),r.get('reference'),r.get('dimension'),r.get('judge_family'),r.get('judge_id'),r.get('block_id'))
        groups[key].append(r)
    raw=defaultdict(lambda:{'stable_wins':0,'stable_losses':0,'stable_ties':0,'unstable_blocks':0,'blocks':0,'families':defaultdict(lambda:{'w':0,'l':0,'t':0,'u':0,'b':0})})
    for (split,chall,ref,dim,fam,jid,bid),rs in groups.items():
        key=(split,chall,ref,dim); out=raw[key]; out['blocks']+=1; f=out['families'][fam or 'UNKNOWN'];f['b']+=1
        orders={r.get('order') for r in rs}
        if orders!={'AB','BA'} or len(rs)!=2:
            out['unstable_blocks']+=1;f['u']+=1;continue
        winners=[r.get('winner') for r in rs]
        if winners[0]!=winners[1]:
            out['unstable_blocks']+=1;f['u']+=1;continue
        w=winners[0]
        if w==chall:out['stable_wins']+=1;f['w']+=1
        elif w==ref:out['stable_losses']+=1;f['l']+=1
        elif w=='tie':out['stable_ties']+=1;f['t']+=1
        else:out['unstable_blocks']+=1;f['u']+=1
    result=[]
    for (split,chall,ref,dim),x in sorted(raw.items()):
        n=x['stable_wins']+x['stable_losses'];ci=wilson(x['stable_wins'],n)
        fam_rows=[]; informative_fams=0
        for fam,d in sorted(x['families'].items()):
            fn=d['w']+d['l']; fci=wilson(d['w'],fn)
            if fn: informative_fams+=1
            fam_rows.append({'family':fam,'stable_wins':d['w'],'stable_losses':d['l'],'stable_ties':d['t'],'unstable_blocks':d['u'],'blocks':d['b'],'non_tie_n':fn,'wilson95':fci})
        if n==0: status='insufficient_or_tied'
        elif ci[0]>eq[1]:status='challenger_advantage'
        elif ci[1]<eq[0]:status='challenger_disadvantage'
        else:status='equivalent_or_uncertain'
        # A hold-out "advantage" from one model family is a family-specific result,
        # not robust synthetic confirmation. Downgrade it explicitly.
        robust=status
        if split=='holdout' and status in {'challenger_advantage','challenger_disadvantage'} and informative_fams<min_holdout_families:
            robust='insufficient_family_diversity'
        result.append({
            'split':split,'challenger':chall,'reference':ref,'dimension':dim,
            'stable_wins':x['stable_wins'],'stable_losses':x['stable_losses'],'stable_ties':x['stable_ties'],
            'unstable_blocks':x['unstable_blocks'],'blocks':x['blocks'],'non_tie_n':n,'wilson95':ci,
            'judge_families_informative':informative_fams,'family_breakdown':fam_rows,
            'synthetic_status':status,'robust_synthetic_status':robust,
        })
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('--output');a=ap.parse_args()
    doc=json.loads(Path(a.input).read_text())
    incumbent=doc['incumbent'];candidates=doc['candidates'];dirs=doc.get('objective_directions',{})
    eq=doc.get('synthetic_equivalence',DEFAULT_EQ);rows=doc.get('pairwise',[])
    min_fams=int(doc.get('min_holdout_families',2));errs=[]
    if incumbent not in candidates:errs.append('incumbent missing from candidates')
    if not (isinstance(eq,list) and len(eq)==2 and 0<=eq[0]<.5<eq[1]<=1):errs.append('invalid synthetic_equivalence interval')
    if min_fams<2:errs.append('min_holdout_families must be >=2 for material held-out preference claims')
    eligible={}
    for cid,c in candidates.items():
        veto=c.get('hard_vetoes',{})
        eligible[cid]=bool(veto) and all(v is True for v in veto.values())
        if not veto:errs.append(f'{cid}: no hard veto evidence')
    frontier=[]
    for cid,c in candidates.items():
        if not eligible.get(cid):continue
        obj=c.get('objectives',{})
        if not dirs or not all(k in obj for k in dirs):continue
        if not any(eligible.get(oid) and dominates(candidates[oid].get('objectives',{}),obj,dirs) for oid in candidates if oid!=cid):frontier.append(cid)
    pairwise=summarize_pairwise(rows,eq,min_fams)
    # If preference evidence is supplied for a material decision, force an explicit
    # held-out split; otherwise repeated optimization can overfit the judge pool.
    if rows and not any(r.get('split')=='holdout' for r in rows):errs.append('pairwise evidence supplied without a heldout split')
    for r in rows:
        for key in ['challenger','reference','dimension','block_id','judge_family','judge_id','order','winner','split']:
            if not r.get(key):errs.append(f'pairwise row missing {key}')
        if r.get('order') not in {'AB','BA'}:errs.append('pairwise order must be AB or BA')
        if r.get('split') not in {'development','holdout'}:errs.append('pairwise split must be development or holdout')
    inc_obj=candidates.get(incumbent,{}).get('objectives',{})
    challengers=[]
    for cid,c in candidates.items():
        if cid==incumbent:continue
        obj=c.get('objectives',{})
        challengers.append({
            'candidate':cid,
            'hard_veto_pass':eligible.get(cid,False),
            'pareto_dominates_incumbent':eligible.get(cid,False) and eligible.get(incumbent,False) and bool(dirs) and dominates(obj,inc_obj,dirs),
            'dominated_by_incumbent':eligible.get(cid,False) and eligible.get(incumbent,False) and bool(dirs) and dominates(inc_obj,obj,dirs),
        })
    stop=not any(x['pareto_dominates_incumbent'] for x in challengers)
    if errs:
        print('PARETO_REVIEW_INPUT_FAILED',file=sys.stderr);[print(' - '+e,file=sys.stderr) for e in sorted(set(errs))];return 2
    result={
      'schema':'nsc-pareto-review-result-v2','incumbent':incumbent,'eligible':eligible,
      'measured_pareto_frontier':sorted(frontier),'challengers':challengers,
      'synthetic_pairwise':pairwise,'synthetic_equivalence':eq,'min_holdout_families':min_fams,
      'synthetic_interval_scope':'repeated synthetic-judge instrument only; not human-population inference',
      'holdout_policy':'development judges may guide search; material pairwise confirmation must include the heldout split and >=min_holdout_families informative families',
      'candidate_stop_signal':stop,
    }
    txt=json.dumps(result,indent=2)+'\n'
    if a.output:Path(a.output).write_text(txt)
    print(txt,end='');return 0
if __name__=='__main__':raise SystemExit(main())
