#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,shutil,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];CFG=ROOT/'audit/review-system-v2';CID=re.compile(r'^RC-\d{8}-\d{3}$')
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-id',required=True);ap.add_argument('--id',required=True);ap.add_argument('--modality',required=True);ap.add_argument('--file',required=True);ap.add_argument('--notes',default='');a=ap.parse_args()
 if not CID.fullmatch(a.candidate_id):raise SystemExit('invalid candidate id')
 src=Path(a.file)
 if not src.is_file():raise SystemExit('evidence file missing')
 destdir=CFG/'evidence'/a.candidate_id;destdir.mkdir(parents=True,exist_ok=True)
 safe=re.sub(r'[^A-Za-z0-9._-]+','-',a.id);dest=destdir/(safe+src.suffix.lower());shutil.copy2(src,dest);digest=sha(dest)
 manifest=destdir/'MANIFEST.json';doc={'schema':'nsc-evidence-manifest-v2','candidate_id':a.candidate_id,'items':[]}
 if manifest.exists():doc=json.loads(manifest.read_text())
 items=[x for x in doc.get('items',[]) if x.get('id')!=a.id];items.append({'id':a.id,'modality':a.modality,'sha256':digest,'uri':'repo://'+dest.relative_to(ROOT).as_posix(),'local_ref':dest.relative_to(ROOT).as_posix(),'release_equivalent':True,'notes':a.notes});doc['items']=sorted(items,key=lambda x:x['id']);manifest.write_text(json.dumps(doc,indent=2)+'\n')
 print(f'REVIEW_EVIDENCE_REGISTERED candidate={a.candidate_id} id={a.id} modality={a.modality} sha256={digest} path={dest.relative_to(ROOT)}')
if __name__=='__main__':main()
