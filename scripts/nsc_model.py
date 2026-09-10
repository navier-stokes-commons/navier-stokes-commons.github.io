#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
C=ROOT/'content'/'public'

def load_json(path:Path): return json.loads(path.read_text())
def raw_project(): return load_json(C/'project.json')
def locale_registry(): return load_json(C/'locale_registry.json')
def locale_codes(): return [x['code'] for x in locale_registry()['locales']]
def locale_policy(code:str):
    return next(x for x in locale_registry()['locales'] if x['code']==code)

def locale_content_digest(code:str)->str:
    h=hashlib.sha256()
    for rel in [f'locales/{code}.json',f'mission_i18n/{code}.json',f'taxonomy_i18n/{code}.json',f'source_i18n/{code}.json']:
        p=C/rel; h.update(rel.encode()); h.update(b'\0'); h.update(p.read_bytes()); h.update(b'\n')
    return h.hexdigest()

def locale_review_receipts(code:str):
    out=[]; d=C/'locale_reviews'
    if not d.exists(): return out
    for p in sorted(d.glob('*.json')):
        try: r=load_json(p)
        except Exception: continue
        if r.get('schema')=='nsc-locale-review-v2' and r.get('locale')==code: out.append(r)
    return out

def locale_status(code:str)->str:
    scope=locale_policy(code)['translation_scope']
    if scope=='canonical': return 'canonical'
    if scope=='interface-preview': return 'interface-preview'
    if scope!='full-translation': raise ValueError(f'unsupported translation_scope {scope!r} for {code}')
    digest=locale_content_digest(code)
    matching=[r for r in locale_review_receipts(code) if r.get('content_digest_sha256')==digest]
    if any(r.get('verdict')=='fail' for r in matching):
        return 'full-translation-review-pending'
    passed={role:set() for role in ('native-language','subject-domain')}
    for r in matching:
        if r.get('verdict')!='pass' or r.get('review_role') not in passed: continue
        reviewer=r.get('reviewer') or {}; rid=reviewer.get('id') if isinstance(reviewer,dict) else None
        if rid: passed[r['review_role']].add(rid)
    independently_dual=any(a!=b for a in passed['native-language'] for b in passed['subject-domain'])
    return 'scientific-reviewed' if independently_dual else 'full-translation-review-pending'

def locale_statuses(): return {c:locale_status(c) for c in locale_codes()}
def version(): return (ROOT/'VERSION').read_text().strip()
def release_id(): return 'public-web-v'+version()
def project_view():
    p=raw_project(); p['release']=release_id(); p['locales']=locale_codes(); p['locale_status']=locale_statuses(); return p

def missions(): return load_json(C/'missions.json')
def quest_doc(): return load_json(C/'quests.json')
def quests(): return quest_doc()['quests']
def claims_doc(): return load_json(C/'claims.json')
def claims(): return claims_doc()['claims']
def reviews_doc(): return load_json(C/'reviews.json')
def reviews(): return reviews_doc().get('records',[])

def _reviewer_id(r:dict):
    x=r.get('reviewer') or {}
    return x.get('id') if isinstance(x,dict) else None

def canonical_json_digest(value)->str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def claim_digest(claim:dict)->str:
    return canonical_json_digest(claim)

def review_record_valid_for_claim(r:dict,claim:dict)->bool:
    reviewer=r.get('reviewer') or {}; independence=r.get('independence') or {}
    return (
      r.get('target_id')==claim['id'] and
      r.get('target_digest_sha256')==claim_digest(claim) and
      isinstance(reviewer,dict) and bool(reviewer.get('id')) and str(reviewer.get('profile_url','')).startswith('https://') and
      isinstance(independence,dict) and independence.get('independent') is True and len(str(independence.get('basis','')))>=10 and
      str(r.get('evidence_url','')).startswith('https://') and bool(r.get('checks'))
    )

def claim_status(claim:dict)->str:
    baseline=claim['baseline_status']
    relevant=[r for r in reviews() if review_record_valid_for_claim(r,claim)]
    if any(r.get('verdict') in {'reject','request-changes'} for r in relevant):
        return 'disputed'
    req=claim.get('review_requirement')
    if req:
        classes=set(req.get('review_classes',[])); need=int(req.get('independent_accepts',1))
        accepted={_reviewer_id(r) for r in relevant if r.get('verdict')=='accept' and r.get('review_class') in classes and _reviewer_id(r)}
        if len(accepted)>=need: return 'independently-reviewed'
    return baseline
def sources(): return load_json(C/'sources.json')
def task_ladder(): return load_json(C/'task_ladder.json')
def taxonomy(): return load_json(C/'taxonomy.json')
def sprint(): return load_json(C/'founding_sprint.json')
def sprint_ids(): return list(sprint()['quest_ids'])
def is_sprint_quest(qid:str)->bool: return qid in set(sprint_ids())
def quest_ids_for_mission(mid:str): return [q['id'] for q in quests() if q['mission_id']==mid]
def quest_ids_for_claim(cid:str): return [q['id'] for q in quests() if cid in q.get('claim_ids',[])]
def expanded_missions():
    return [dict(m,quest_ids=quest_ids_for_mission(m['id'])) for m in missions()]
def expanded_quests():
    s=set(sprint_ids()); return [dict(q,founding_sprint=q['id'] in s) for q in quests()]
def expanded_claims_doc():
    d=claims_doc(); d['claims']=[dict(c,status=claim_status(c),target_quest_ids=quest_ids_for_claim(c['id'])) for c in d['claims']]; return d

def counts():
    return {'missions':len(missions()),'sources':len(sources()),'quests':len(quests()),'founding_sprint_quests':len(sprint_ids()),'tracked_claims':len(claims()),'locales':len(locale_codes())}

def license_display_token(spdx:str)->str:
    return {'Apache-2.0':'Apache-2.0','CC-BY-4.0':'CC BY 4.0','CC0-1.0':'CC0'}.get(spdx,spdx)
def localized_license_line(code:str, locale_doc:dict|None=None)->str:
    p=raw_project(); locale_doc=locale_doc or load_json(C/'locales'/f'{code}.json')
    labels=locale_doc.get('footer',{}).get('license_labels',{})
    lic=p['license']
    parts=[]
    for key,default in [('software','Software'),('original_content','Original content'),('metadata','Metadata')]:
        parts.append(f"{labels.get(key,default)} {license_display_token(lic[key])}")
    return ' · '.join(parts)

def capabilities():
    qs=quests(); ladder=task_ladder()['rungs']; rung_ids=[r['id'] for r in ladder]; starter_ids={r['id'] for r in ladder if r.get('starter')}
    by_rung={rid:sum(q['rung']==rid and q['status']=='open' for q in qs) for rid in rung_ids}
    bounded=bool(ladder) and len(starter_ids)>=1 and all(by_rung[rid]>=1 for rid in starter_ids)
    cold=any(q['status']=='open' and q['rung'] in starter_ids and not q.get('dependencies') for q in qs)
    student_entries=[q['id'] for q in qs if q['status']=='open' and q['rung'] in starter_ids and not q.get('dependencies') and 'students' in q.get('contributors',[])]
    return {
      'bounded_participation_ladder':{'satisfied':bounded,'open_quests_by_rung':by_rung,
        'statement':f'A {len(ladder)}-rung bounded quest ladder is live, from short checks and reproduction through mapping, implementation, analysis, and frontier research.'},
      'student_entry_path':{'satisfied':len(student_entries)>=2,'quest_ids':student_entries,
        'statement':f"{len(student_entries)} open dependency-free quests on starter rungs {('/'.join(rung_ids_ for rung_ids_ in rung_ids if rung_ids_ in starter_ids))} explicitly list students as suitable contributors; later-rung work may require specialist expertise."},
      'agent_cold_start':{'satisfied':cold,'statement':f"An agent can discover canonical machine endpoints and select an open dependency-free quest on a declared starter rung ({'/'.join(r for r in rung_ids if r in starter_ids)}) without private context."},
      'parallel_attempts':{'satisfied':all(q.get('non_exclusive') for q in qs),'statement':'Quest attempts are non-exclusive; independent parallel attempts are permitted.'}
    }


def public_registry(): return load_json(C/'public_registry.json')
def release_policy(): return load_json(C/'release_policy.json')
