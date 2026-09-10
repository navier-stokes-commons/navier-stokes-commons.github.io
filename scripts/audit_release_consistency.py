#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json,re,sys
from nsc_model import ROOT,C,project_view,locale_codes,locale_statuses,localized_license_line,release_id,version,counts,locale_content_digest,locale_review_receipts
P=ROOT/'public'; project=project_view(); release=json.loads((ROOT/'RELEASE.json').read_text()); errs=[]
if release.get('version')!=version(): errs.append('RELEASE.json version differs from VERSION')
if release.get('release')!=release_id() or release.get('release_id')!=release_id(): errs.append('RELEASE.json release identity differs from VERSION')
if project.get('release')!=release_id(): errs.append('derived project release differs from VERSION')
if release.get('locale_status')!=locale_statuses(): errs.append('RELEASE.json locale_status differs from evidence-derived locale status')
if release.get('locales')!=locale_codes(): errs.append('RELEASE.json locales differ from locale registry')
if release.get('licenses')!=project.get('license'): errs.append('RELEASE.json license tuple differs from canonical project license')
n=counts()
for rk,nk in [('missions','missions'),('quests','quests'),('founding_sprint_quests','founding_sprint_quests'),('tracked_claims','tracked_claims')]:
    if release.get(rk)!=n[nk]: errs.append(f'RELEASE.json {rk} is not derived count')
preview=[loc for loc,status in locale_statuses().items() if status=='interface-preview']

# Review receipts are evidence, not labels. Validate the current receipt contract and
# ensure any scientific-reviewed state is supported by two distinct reviewers.
for loc in locale_codes():
    digest=locale_content_digest(loc); matching=[]
    for r in locale_review_receipts(loc):
        reviewer=r.get('reviewer') or {}
        required={'schema','review_id','locale','review_role','reviewer','reviewed_at','content_digest_sha256','review_artifact_url','independence_statement','verdict'}
        if set(r)<required: errs.append(f'{loc}: malformed locale review receipt {r.get("review_id","?")}')
        if not isinstance(reviewer,dict) or not reviewer.get('id') or not str(reviewer.get('profile_url','')).startswith('https://'): errs.append(f'{loc}: review receipt lacks public reviewer identity')
        if not str(r.get('review_artifact_url','')).startswith('https://'): errs.append(f'{loc}: review receipt lacks public review artifact URL')
        if len(str(r.get('independence_statement',''))) < 20: errs.append(f'{loc}: review independence statement too weak')
        if r.get('content_digest_sha256')==digest: matching.append(r)
    if locale_statuses()[loc]=='scientific-reviewed':
        passes=[r for r in matching if r.get('verdict')=='pass']
        roles={r.get('review_role') for r in passes}
        reviewers={r.get('reviewer',{}).get('id') for r in passes if isinstance(r.get('reviewer'),dict)}
        if roles!={'native-language','subject-domain'} or len(reviewers)<2 or any(r.get('verdict')=='fail' for r in matching):
            errs.append(f'{loc}: scientific-reviewed status lacks independent dual exact-content evidence')
for loc in locale_codes():
    L=json.loads((C/'locales'/f'{loc}.json').read_text())
    if 'license' in L.get('footer',{}): errs.append(f'{loc}: canonical locale source duplicates license value')
    expected=localized_license_line(loc,L)
    pages=sorted((P/loc).rglob('*.html'))
    if not pages: errs.append(f'{loc}: no generated pages')
    for page in pages:
        txt=page.read_text()
        if expected not in txt: errs.append(f'{page.relative_to(P)}: generated footer differs from canonical license tuple')
    if loc in preview:
        notice=L.get('preview_notice','').strip()
        if not notice: errs.append(f'{loc}: preview source missing preview_notice')
        for page in pages:
            txt=page.read_text()
            if 'class="locale-preview-notice"' not in txt or notice not in txt: errs.append(f'{page.relative_to(P)}: preview disclosure missing/mismatched')
            if 'class="locale-preview-notice" role="note" lang="en" dir="ltr"' not in txt: errs.append(f'{page.relative_to(P)}: preview disclosure language boundary missing')
        for m in json.loads((C/'missions.json').read_text()):
            txt=(P/loc/'missions'/m['slug']/'index.html').read_text()
            for pattern,label in [(r'<h1 lang="en" dir="ltr">','mission title'),(r'<p class="lede" lang="en" dir="ltr">','mission summary'),(r'<p class="question-text" lang="en" dir="ltr">','mission question')]:
                if not re.search(pattern,txt): errs.append(f'{loc}/{m["id"]}: {label} missing canonical-English boundary')
# Legacy contradictory software license may not survive.
for base in [C,P]:
    for path in base.rglob('*'):
        if path.is_file() and path.suffix.lower() in {'.json','.md','.html','.txt'}:
            try: txt=path.read_text()
            except UnicodeDecodeError: continue
            if 'Code MIT' in txt or 'Software MIT' in txt: errs.append(f'{path.relative_to(ROOT)}: stale MIT license claim')
if errs:
    print('RELEASE_CONSISTENCY_AUDIT_FAILED',file=sys.stderr)
    for e in errs[:300]: print(' - '+e,file=sys.stderr)
    sys.exit(1)
print(f'RELEASE_CONSISTENCY_AUDIT_PASS version={version()} preview_locales={len(preview)} locales={len(locale_codes())} status_source=evidence-derived')
