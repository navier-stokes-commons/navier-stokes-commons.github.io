#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
C=ROOT/'content'/'public'
errs=[]
from nsc_model import project_view
project=project_view()
sources=json.loads((C/'sources.json').read_text())
missions=json.loads((C/'missions.json').read_text())
source_ids={s['id'] for s in sources}
if len(source_ids)!=len(sources): errs.append('duplicate source id')
for s in sources:
    if not str(s.get('url','')).startswith('https://'): errs.append(f"source {s.get('id')} is not HTTPS")
    if not s.get('retrieved_at'): errs.append(f"source {s.get('id')} missing retrieval date")
    rt=s.get('reference_type')
    allowed_ref={'mutable-public-url','versioned-or-content-address-like-url','immutable-git-commit'}
    if rt not in allowed_ref: errs.append(f"source {s.get('id')} invalid reference_type {rt}")
    if rt=='immutable-git-commit':
        v=str(s.get('version',''))
        import re as _re
        if not _re.fullmatch(r'[0-9a-f]{40}',v): errs.append(f"source {s.get('id')} immutable git source missing 40-hex version")
        elif v not in str(s.get('url','')): errs.append(f"source {s.get('id')} immutable git URL does not contain version")
mission_ids=set()
for m in missions:
    mid=m.get('id')
    if mid in mission_ids: errs.append(f'duplicate mission id {mid}')
    mission_ids.add(mid)
    if m.get('status')!='open': errs.append(f'{mid}: public seed missions must be open questions')
    if not m.get('question') or not m.get('acceptance'): errs.append(f'{mid}: missing question/acceptance')
    missing=set(m.get('source_ids',[]))-source_ids
    if missing: errs.append(f'{mid}: unknown mission source ids {sorted(missing)}')
    for sp in m.get('starting_points',[]):
        kind=sp.get('kind'); ids=sp.get('source_ids',[])
        if kind not in {'sourced_fact','reasoning_guard'}: errs.append(f'{mid}: invalid starting point kind {kind}')
        if kind=='sourced_fact' and not ids: errs.append(f'{mid}: sourced_fact without source')
        if kind=='reasoning_guard' and ids: errs.append(f'{mid}: reasoning_guard should not masquerade as sourced fact')
        if set(ids)-source_ids: errs.append(f'{mid}: unknown starting point source')
for loc in project['locales']:
    lf=C/'locales'/f'{loc}.json'; mf=C/'mission_i18n'/f'{loc}.json'
    if not lf.exists() or not mf.exists(): errs.append(f'{loc}: missing localization files'); continue
    L=json.loads(lf.read_text()); T=json.loads(mf.read_text())
    tf=C/'taxonomy_i18n'/f'{loc}.json'
    sf=C/'source_i18n'/f'{loc}.json'
    if not tf.exists(): errs.append(f'{loc}: missing taxonomy localization'); continue
    if not sf.exists(): errs.append(f'{loc}: missing source localization'); continue
    TX=json.loads(tf.read_text()); SX=json.loads(sf.read_text())
    expected_cats={m['category'] for m in missions}; expected_levels={m['level'] for m in missions}; expected_contrib={c for m in missions for c in m['contributors']}
    if expected_cats-set(TX.get('categories',{})): errs.append(f'{loc}: incomplete category taxonomy')
    if expected_levels-set(TX.get('levels',{})): errs.append(f'{loc}: incomplete level taxonomy')
    if expected_contrib-set(TX.get('contributors',{})): errs.append(f'{loc}: incomplete contributor taxonomy')
    if source_ids-set(SX): errs.append(f'{loc}: incomplete source localization')
    if set(SX)-source_ids: errs.append(f'{loc}: unknown source localization ids {sorted(set(SX)-source_ids)}')
    for sid in source_ids:
        if not SX.get(sid,{}).get('claims_supported'): errs.append(f'{loc}/{sid}: missing localized source claims')
    required_section={'paths_in','public_evidence','open_frontier','composition','contribute','public_record','boundary','open_participation','process','side_quests','provenance_ledger','machine_surface','inclusive_by_design','related','breadcrumb'}
    if required_section-set(L.get('section_labels',{})): errs.append(f'{loc}: incomplete section-label localization')
    for k in ('sourced_fact','reasoning_guard'):
        if not L.get('mission_meta',{}).get(k): errs.append(f'{loc}: missing mission label {k}')
    for k in ('branch_aria','branch_root','branch_ab','branch_cd','branch_unforced','branch_forced'):
        if not L.get('known',{}).get(k): errs.append(f'{loc}: missing known-page label {k}')
    if L.get('dir') not in {'ltr','rtl'}: errs.append(f'{loc}: invalid dir')
    if loc=='ar' and L.get('dir')!='rtl': errs.append('Arabic must be rtl')
    missing=mission_ids-set(T)
    extra=set(T)-mission_ids
    if missing: errs.append(f'{loc}: missing mission translations {sorted(missing)}')
    if extra: errs.append(f'{loc}: unknown mission translations {sorted(extra)}')
    for mid,t in T.items():
        for k in ('title','summary','question'):
            if not str(t.get(k,'')).strip(): errs.append(f'{loc}/{mid}: missing {k}')
# Fail if non-public content roots are accidentally introduced.
allowed_top={'content','assets','scripts','.github','.gitlab','docs','public','standards','audit','templates','schemas','references'}
for p in ROOT.iterdir():
    if p.name.startswith('.') and p.name not in {'.github','.gitlab','.gitignore'}: continue
    if p.is_dir() and p.name not in allowed_top and p.name!='__pycache__':
        errs.append(f'unexpected top-level directory {p.name}')
if errs:
    print('PUBLIC_CONTENT_AUDIT_FAILED',file=sys.stderr)
    for e in errs: print(' - '+e,file=sys.stderr)
    sys.exit(1)
print(f'PUBLIC_CONTENT_AUDIT_PASS missions={len(missions)} sources={len(sources)} locales={len(project["locales"])}')
