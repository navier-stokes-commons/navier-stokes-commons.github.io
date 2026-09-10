#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]; C=ROOT/'content/public'; P=ROOT/'public'
from nsc_model import project_view
project=project_view(); missions=json.loads((C/'missions.json').read_text()); sources=json.loads((C/'sources.json').read_text())
errs=[]
for loc in project['locales']:
    L=json.loads((C/'locales'/f'{loc}.json').read_text()); S=json.loads((C/'source_i18n'/f'{loc}.json').read_text())
    if loc=='ar' and L.get('dir')!='rtl': errs.append('Arabic dir must be rtl')
    if project.get('locale_status',{}).get(loc)=='interface-preview':
        if not L.get('preview_notice'): errs.append(f'{loc}: interface preview missing disclosure')
    if loc!='ar' and L.get('dir')!='ltr': errs.append(f'{loc} dir must be ltr')
    if set(S)!={s['id'] for s in sources}: errs.append(f'{loc}: source localization ID mismatch')
    # Residual English UI labels that are not scientific canonical-English blocks are prohibited in non-English generated pages.
    if loc!='en' and project.get('locale_status',{}).get(loc)!='interface-preview':
        forbidden=['>OPEN FRONTIER<','>PUBLIC RECORD<','>BOUNDARY<','>OPEN PARTICIPATION<','>PROCESS<','>SIDE QUESTS<','>PROVENANCE LEDGER<','>MACHINE SURFACE<','>INCLUSIVE BY DESIGN<','aria-label="Breadcrumb"','>Sourced fact<','>Reasoning guard<','>smooth forcing permitted<','>Clay formulation<']
        for page in (P/loc).rglob('*.html'):
            txt=page.read_text()
            for bad in forbidden:
                if bad in txt: errs.append(f'{page.relative_to(P)} residual English UI label {bad}')
    # Canonical acceptance criteria must remain explicitly English/LTR when locale != en.
    for m in missions:
        txt=(P/loc/'missions'/m['slug']/'index.html').read_text()
        if loc!='en' and 'class="accept-list"' in txt:
            block=txt.split('class="accept-list"',1)[1].split('</ol>',1)[0]
            if 'lang="en" dir="ltr"' not in block: errs.append(f'{loc}/{m["id"]}: canonical acceptance lost language boundary')
# Machine frontier canonical content must be English and locale-neutral.
frontier=json.loads((P/'data/frontier.json').read_text())
if len(frontier.get('missions',[]))!=len(missions): errs.append('machine frontier mission count mismatch')
if errs:
    print('I18N_AUDIT_FAILED',file=sys.stderr)
    for e in errs[:200]: print(' - '+e,file=sys.stderr)
    sys.exit(1)
print(f'I18N_AUDIT_PASS locales={len(project["locales"])} source_records={len(sources)} mission_pages={len(missions)*len(project["locales"])}')
