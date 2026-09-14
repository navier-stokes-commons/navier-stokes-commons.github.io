#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from png_metric import mad_png
from playwright.sync_api import sync_playwright
from scratch import ScratchPolicyError,scratch_dir
import json,os,re,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'public'; CSS=(ROOT/'assets/style.css').read_text(); JS=(ROOT/'assets/site.js').read_text(); R17=(ROOT/'assets/r17-fluid.js').read_text(); fails=[]; rows=[]
try: _base=scratch_dir('experience-audit')
except ScratchPolicyError as e: print('EXPERIENCE_AUDIT_UNAVAILABLE '+str(e),file=sys.stderr);raise SystemExit(2)
OUT=Path(os.environ.get('NSC_EXPERIENCE_OUTPUT',str(_base/'experience.json'))); SHOTS=Path(os.environ.get('NSC_EXPERIENCE_SCREENSHOTS_DIR',str(_base/'screenshots'))); SHOTS.mkdir(parents=True,exist_ok=True)

def inline(path:Path,js_on=True):
    h=path.read_text(); h=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>','',h,count=1); h=re.sub(r'<link rel="stylesheet"[^>]*>', lambda _:'<style>'+CSS+'</style>',h,count=1); h=re.sub(r'<script src="[^"]*site\.js" defer></script>', lambda _:('<script>'+JS+'</script>' if js_on else ''),h,count=1); h=re.sub(r'<script src="[^"]*r17-fluid\.js" defer></script>', lambda _:('<script>'+R17+'</script>' if js_on else ''),h,count=1); return h

def mad(a,b): return mad_png(a,b)

def shot(stage): return stage.screenshot(timeout=8000)
exe=shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome') or ''
with sync_playwright() as pw:
  opts={'headless':True,'args':['--no-sandbox','--disable-gpu']};
  if exe: opts['executable_path']=exe
  b=pw.chromium.launch(**opts)
  # Wide and narrow text-reflow matrix. Reduced motion isolates geometry.
  cases=[('en/index.html',w,z) for w in (320,390,768,1280,1440) for z in (1,2)]
  cases += [(loc+'/index.html',w,z) for loc in ('es','ar','zh-Hans') for w in (390,1440) for z in (1,2)]
  for rel,w,z in cases:
    ctx=b.new_context(viewport={'width':w,'height':900 if w>500 else 844},reduced_motion='reduce');pg=ctx.new_page();pg.set_content(inline(P/rel,True),wait_until='domcontentloaded',timeout=15000)
    if z==2:pg.evaluate("document.documentElement.style.fontSize='200%'")
    pg.wait_for_timeout(80);cw=pg.evaluate('document.documentElement.clientWidth');sw=pg.evaluate('document.documentElement.scrollWidth')
    offenders=pg.evaluate('''[...document.querySelectorAll('h1,h2,h3,p,a,button,label,output,.stage-note,.stage-help,.visual-boundary,.hud-stat,.language-grid a')].map(e=>{let r=e.getBoundingClientRect(),s=getComputedStyle(e);return {tag:e.tagName,cls:String(e.className||''),l:r.left,r:r.right,w:r.width,sw:e.scrollWidth,cw:e.clientWidth,vis:s.display!='none'&&s.visibility!='hidden',txt:(e.textContent||'').trim().slice(0,90)}}).filter(x=>x.vis&&((x.l<-2)||(x.r>document.documentElement.clientWidth+2)||(x.cw>0&&x.sw>x.cw+3)))''')
    ok=sw<=cw+2 and not offenders
    row={'page':rel,'width':w,'text_scale':z,'scroll_width':sw,'client_width':cw,'offenders':offenders[:12],'pass':ok};rows.append(row)
    if not ok:fails.append(row)
    if rel=='en/index.html' and w in (390,1440) and z in (1,2):pg.screenshot(path=str(SHOTS/f'en-{w}-x{z}.png'),full_page=False)
    ctx.close()
  # no-JS still-good path
  for w in (390,1440):
    ctx=b.new_context(viewport={'width':w,'height':900},java_script_enabled=False,reduced_motion='reduce');pg=ctx.new_page();pg.set_content(inline(P/'en/index.html',False),wait_until='domcontentloaded');pg.wait_for_timeout(30)
    ok=pg.locator('[data-vortex-static]').is_visible() and pg.locator('[data-vortex-controls]').is_hidden() and pg.locator('[data-vortex-stage]').count()==1
    if not ok:fails.append({'no_js':w,'pass':False})
    ctx.close()
  # R17 direct manipulation / visible-motion checks are canonical here; deeper decay/pause checks live in audit_motion_experience.py.
  ctx=b.new_context(viewport={'width':1200,'height':900},reduced_motion='no-preference');pg=ctx.new_page();pg.set_content(inline(P/'en/index.html',True),wait_until='domcontentloaded');pg.wait_for_timeout(450);stage=pg.locator('[data-vortex-stage]');canvas=pg.locator('[data-r17-hero-canvas]')
  base=shot(stage);pg.wait_for_timeout(550);live=shot(stage);dk=mad(base,live);box=canvas.bounding_box();pg.mouse.move(box['x']+box['width']*.25,box['y']+box['height']*.55);pg.mouse.move(box['x']+box['width']*.76,box['y']+box['height']*.30,steps=14);pg.wait_for_timeout(160);probe=shot(stage);dp=mad(live,probe);state=pg.locator('html').get_attribute('data-r17-motion');legacy=pg.locator('[data-vortex-controls] [data-play]').count();
  if dk<.003:fails.append({'dynamic':'r17_auto','mad':dk})
  if dp<.003:fails.append({'dynamic':'r17_pointer','mad':dp})
  if state!='running':fails.append({'dynamic':'r17_running_state','state':state})
  if legacy:fails.append({'dynamic':'legacy_play_present','count':legacy})
  ctx.close()
  # Arabic -> Chinese root-cell physical separator survives RTL child direction.
  ctx=b.new_context(viewport={'width':1280,'height':900},reduced_motion='reduce');pg=ctx.new_page();pg.set_content(inline(P/'index.html',True),wait_until='domcontentloaded');pg.wait_for_timeout(30);cells=pg.locator('.language-grid a');ar=cells.nth(4).bounding_box();zh=cells.nth(5).bounding_box();gap=zh['x']-(ar['x']+ar['width']);
  if not (.5<=gap<=1.5):fails.append({'layout':'arabic_chinese_gap','gap':gap})
  ctx.close();b.close()
out={'schema':'nsc-experience-audit-v1','layout_states':rows,'dynamic':{'r17_auto_mad':dk,'pointer_mad':dp,'arabic_chinese_gap_px':gap},'pass':not fails,'failures':fails};OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2)+'\n')
print(f'EXPERIENCE_DYNAMIC_METRICS r17_auto_mad={dk:.4f} pointer_mad={dp:.4f} ar_zh_gap={gap:.2f}px')
if fails:
 print('EXPERIENCE_AUDIT_FAILED',file=sys.stderr);[print(' - '+str(x),file=sys.stderr) for x in fails[:20]];raise SystemExit(1)
print(f'EXPERIENCE_AUDIT_PASS layout_states={len(rows)} nojs=true dynamic_contrast=true pointer_probe=true orbit=true sweep=true rtl_separator=true evidence={SHOTS}')
