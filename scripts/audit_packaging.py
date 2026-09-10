#!/usr/bin/env python3
from __future__ import annotations
import hashlib,shutil,subprocess,sys
from pathlib import Path
from scratch import scratch_dir, ScratchPolicyError
ROOT=Path(__file__).resolve().parents[1]
if not shutil.which('tar') or not shutil.which('zstd'):
    print('PACKAGING_AUDIT_UNAVAILABLE requires GNU tar and zstd',file=sys.stderr); raise SystemExit(2)
try:
    scratch=scratch_dir('package-audit',primary_env='NSC_PACKAGE_SCRATCH')
except ScratchPolicyError as e:
    print('PACKAGING_AUDIT_FAILED scratch policy: '+str(e),file=sys.stderr); raise SystemExit(2)
shutil.rmtree(scratch,ignore_errors=True); scratch.mkdir(parents=True)
def build(name,source_only=False):
    out=scratch/name
    excludes=['--exclude=.git','--exclude=__pycache__','--exclude=*.pyc']
    if source_only: excludes.extend(['--exclude=./public','--exclude=./MANIFEST.sha256'])
    tar=['tar','--sort=name','--mtime=@0','--owner=0','--group=0','--numeric-owner','--format=posix','--pax-option=delete=atime,delete=ctime',*excludes,'-C',str(ROOT),'-cf','-','.']
    p1=subprocess.Popen(tar,stdout=subprocess.PIPE)
    p2=subprocess.run(['zstd','-q','-19','-T1','-o',str(out)],stdin=p1.stdout,check=True)
    if p1.stdout: p1.stdout.close()
    rc=p1.wait()
    if rc: raise subprocess.CalledProcessError(rc,tar)
    return hashlib.sha256(out.read_bytes()).hexdigest()
a=build('full-a.tar.zst'); b=build('full-b.tar.zst'); sa=build('source-a.tar.zst',True); sb=build('source-b.tar.zst',True)
source_listing=subprocess.check_output(['tar','--zstd','-tf',str(scratch/'source-a.tar.zst')],text=True).splitlines()
source_paths={x.removeprefix('./') for x in source_listing}
shape_bad=any(x=='public' or x.startswith('public/') for x in source_paths) or 'MANIFEST.sha256' in source_paths
shutil.rmtree(scratch,ignore_errors=True)
if a!=b or sa!=sb or shape_bad:
    print('PACKAGING_AUDIT_FAILED non-deterministic archive or invalid source-only shape',file=sys.stderr); raise SystemExit(1)
print(f'PACKAGING_AUDIT_PASS full_sha256={a} source_sha256={sa} normalized_mtime=0')
