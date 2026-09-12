#!/usr/bin/env python3
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];d=json.loads((R/'content/public/source_watch.json').read_text());errs=[]
if d.get('policy')!='detect-only-never-auto-elevate':errs.append('source watch policy drift')
for x in d.get('deltas',[]):
 if x.get('required_effect') not in {None,'review-candidate-only'}:errs.append('source delta may only create review candidate')
if not (R/'scripts/watch_sources.py').exists():errs.append('watcher missing')
if errs:
 print('R14_SOURCE_WATCH_AUDIT_FAIL',file=sys.stderr);[print(' - '+x,file=sys.stderr) for x in errs];raise SystemExit(1)
print(f'R14_SOURCE_WATCH_AUDIT_PASS observations={len(d.get("observations",{}))} automatic_claim_changes=0')
