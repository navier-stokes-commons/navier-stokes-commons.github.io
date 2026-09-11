#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from playwright.sync_api import sync_playwright
from scratch import ScratchPolicyError,scratch_dir
import argparse,json,os,re,shutil,sys
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'public';CSS=(ROOT/'assets/style.css').read_text();JS=(ROOT/'assets/site.js').read_text()
try: default_out=scratch_dir('layout-integrity')/'layout_integrity.json'
except ScratchPolicyError as e: print('LAYOUT_INTEGRITY_UNAVAILABLE '+str(e),file=sys.stderr);raise SystemExit(2)
ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(default_out));ap.add_argument('--screenshots-dir',default=os.environ.get('NSC_LAYOUT_SCREENSHOTS_DIR',''));a=ap.parse_args();exe=shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome') or ''
def inline(path,js=True):
 h=path.read_text();h=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>','',h,count=1);h=re.sub(r'<link rel="stylesheet"[^>]*>', lambda _:'<style>'+CSS+'</style>',h,count=1);h=re.sub(r'<script src="[^"]+" defer></script>', lambda _:('<script>'+JS+'</script>' if js else ''),h,count=1);return h
# Geometry oracle targets text/controls and the flagship stage. It deliberately does not call itself an aesthetic pass.
selectors='h1,h2,h3,p,a,button,label,output,.stage-note,.stage-help,.visual-boundary,.hud-stat,.vortex-stage,.language-grid a,.mission-entry-link,.quest-card'
def geometry(pg):
 return pg.evaluate('''sels=>{const cw=document.documentElement.clientWidth;return [...document.querySelectorAll(sels)].map((e,i)=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {i,tag:e.tagName,cls:String(e.className||''),l:r.left,r:r.right,t:r.top,b:r.bottom,w:r.width,h:r.height,sw:e.scrollWidth,cw:e.clientWidth,vis:s.display!='none'&&s.visibility!='hidden'&&r.width>0&&r.height>0,txt:(e.textContent||'').trim().slice(0,80)}}).filter(x=>x.vis&&((x.l<-2)||(x.r>cw+2)||(x.cw>0&&x.sw>x.cw+3))) }''',selectors)
rows=[];fails=[];shotdir=Path(a.screenshots_dir) if a.screenshots_dir else None
if shotdir:shotdir.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 opts={'headless':True,'args':['--no-sandbox']};
 if exe:opts['executable_path']=exe
 b=pw.chromium.launch(**opts)
 cases=[('index.html',w,z,True) for w in (320,390,768,1280,1440) for z in (1,2)]
 cases += [('en/index.html',w,z,js) for w in (320,390,768,1280,1440) for z in (1,2) for js in (True,False)]
 cases += [(loc+'/index.html',w,z,True) for loc in ('es','ar','zh-Hans') for w in (390,1440) for z in (1,2)]
 cases += [('en/quests/index.html',390,2,True),('en/contribute/index.html',390,2,True)]
 for rel,w,z,js in cases:
  ctx=b.new_context(viewport={'width':w,'height':900 if w>500 else 844},java_script_enabled=js,reduced_motion='reduce');pg=ctx.new_page();pg.set_content(inline(P/rel,js),wait_until='domcontentloaded',timeout=15000)
  if z==2:pg.evaluate("document.documentElement.style.fontSize='200%'")
  pg.wait_for_timeout(80);cw=pg.evaluate('document.documentElement.clientWidth');sw=pg.evaluate('document.documentElement.scrollWidth');off=geometry(pg);ok=sw<=cw+2 and not off
  # No essential flagship overlay may overlap the text column; the stage clips only its own visual canvas/overlay by design.
  if rel=='en/index.html' and js:
   pair=pg.evaluate('''()=>{const a=document.querySelector('.hero-copy')?.getBoundingClientRect(),b=document.querySelector('[data-vortex-stage]')?.getBoundingClientRect();if(!a||!b)return null;return {overlap:Math.max(0,Math.min(a.right,b.right)-Math.max(a.left,b.left))*Math.max(0,Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)),a:[a.left,a.top,a.right,a.bottom],b:[b.left,b.top,b.right,b.bottom]}}''')
   if pair and pair['overlap']>2:off.append({'kind':'hero-copy-stage-overlap','area':pair['overlap']});ok=False
  row={'page':rel,'width':w,'text_scale':z,'js':js,'scroll_width':sw,'client_width':cw,'offenders':off[:12],'pass':ok};rows.append(row)
  if not ok:fails.append(row)
  if shotdir and rel in {'index.html','en/index.html','es/index.html'} and (w,z,js) in {(390,1,True),(390,2,True),(1440,1,True),(1280,2,False)}:pg.screenshot(path=str(shotdir/f'{rel.replace("/","__").replace(".html","")}__w{w}__x{z}__{("js" if js else "nojs")}.png'),full_page=True)
  ctx.close()
 # Exact RTL separator regression on root: Arabic and Chinese adjacent cells must have physical gap independent of ar dir=rtl.
 ctx=b.new_context(viewport={'width':1280,'height':900},reduced_motion='reduce');pg=ctx.new_page();pg.set_content(inline(P/'index.html',True),wait_until='domcontentloaded');pg.wait_for_timeout(50)
 sep=pg.evaluate('''()=>{const a=document.querySelector('.language-grid a[lang="ar"]')?.getBoundingClientRect(),z=document.querySelector('.language-grid a[lang="zh-Hans"]')?.getBoundingClientRect();if(!a||!z)return null;return {sameRow:Math.abs(a.top-z.top)<3,gap:z.left-a.right}}''')
 if sep and sep['sameRow'] and not(.5<=sep['gap']<=1.5):fails.append({'page':'index.html','kind':'rtl-language-separator','gap':sep['gap']})
 ctx.close();b.close()
out={'schema':'nsc-layout-integrity-v2','scope':'browser-geometry+clipping+large-text+progressive-state+rtl-separator; not aesthetic certification','states':len(rows),'rtl_separator':sep,'failures':fails,'pass':not fails};Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
if fails:
 print(f'LAYOUT_INTEGRITY_AUDIT_FAILED failures={len(fails)} states={len(rows)}',file=sys.stderr);[print(' - '+json.dumps(x,ensure_ascii=False)[:1000],file=sys.stderr) for x in fails[:12]];raise SystemExit(1)
print(f'LAYOUT_INTEGRITY_AUDIT_PASS states={len(rows)} widths=320,390,768,1280,1440 text=100,200 js_nojs=true rtl_separator=true')
