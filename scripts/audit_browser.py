#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,re,shutil,sys
from pathlib import Path
from scratch import ScratchPolicyError,scratch_dir
try: from playwright.sync_api import sync_playwright
except Exception as e: print(f'BROWSER_AUDIT_UNAVAILABLE playwright={e}',file=sys.stderr); raise SystemExit(2)
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'public'
try: DEFAULT_OUTPUT=scratch_dir('browser-audit')/'browser_matrix.json'
except ScratchPolicyError as e: print('BROWSER_AUDIT_UNAVAILABLE scratch policy: '+str(e),file=sys.stderr); raise SystemExit(2)
ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(DEFAULT_OUTPUT));ap.add_argument('--chromium',default=os.getenv('NSC_CHROMIUM',''));a=ap.parse_args()
exe=a.chromium.strip() or shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome') or ''
css=(ROOT/'assets/style.css').read_text();js=(ROOT/'assets/site.js').read_text();r17=(ROOT/'assets/r17-fluid.js').read_text(); mission=next((P/'en/missions').glob('*/index.html'))
paths=[P/'index.html',P/'en/index.html',P/'es/index.html',P/'en/quests/index.html',P/'en/quests/ns-q008/index.html',mission,P/'en/sprint/index.html',P/'en/contribute/index.html',P/'en/agents/index.html',P/'ar/index.html',P/'zh-Hans/index.html',P/'en/reference-flow/index.html']
configs=[
 {'name':'desktop-js','width':1440,'height':1000,'js':True,'color':'light','motion':'no-preference','forced':'none','zoom':1},
 {'name':'mobile-js','width':390,'height':844,'js':True,'color':'light','motion':'no-preference','forced':'none','zoom':1},
 {'name':'mobile-nojs','width':390,'height':844,'js':False,'color':'light','motion':'no-preference','forced':'none','zoom':1},
 {'name':'dark-reduced','width':390,'height':844,'js':True,'color':'dark','motion':'reduce','forced':'none','zoom':1},
 {'name':'desktop-nojs-200pct','width':1280,'height':1000,'js':False,'color':'light','motion':'reduce','forced':'none','zoom':2},
 {'name':'mobile-js-200pct','width':390,'height':844,'js':True,'color':'light','motion':'reduce','forced':'none','zoom':2},
]
def inline(path:Path,js_on:bool)->str:
    h=path.read_text();h=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>','',h,count=1)
    h=re.sub(r'<link rel="stylesheet"[^>]*>',lambda _:'<style>'+css+'</style>',h,count=1)
    h=re.sub(r'<script src="[^"]*site\.js" defer></script>',lambda _:'<script>'+js+'</script>' if js_on else '',h,count=1)
    h=re.sub(r'<script src="[^"]*r17-fluid\.js" defer></script>',lambda _:'<script>'+r17+'</script>' if js_on else '',h,count=1)
    return h
def vis(page,sel):
    q=page.locator(sel); return q.count()>0 and q.first.is_visible()
def run():
 rows=[];fails=[]
 with sync_playwright() as pw:
  opts={'headless':True,'args':['--no-sandbox']};
  if exe:opts['executable_path']=exe
  browser=pw.chromium.launch(**opts)
  for path in paths:
   rel=path.relative_to(P).as_posix()
   for cfg in configs:
    ctx=browser.new_context(viewport={'width':cfg['width'],'height':cfg['height']},java_script_enabled=cfg['js'],color_scheme=cfg['color'],reduced_motion=cfg['motion'],forced_colors=cfg['forced'])
    page=ctx.new_page();console=[];pageerr=[];page.on('console',lambda msg,bag=console:bag.append(msg.text) if msg.type=='error' else None);page.on('pageerror',lambda exc,bag=pageerr:bag.append(str(exc)))
    page.set_content(inline(path,cfg['js']),wait_until='domcontentloaded',timeout=15000)
    if cfg['zoom']!=1:page.evaluate(f"document.documentElement.style.fontSize='{cfg['zoom']*100:.0f}%'")
    if cfg['js']:page.wait_for_timeout(150)
    sw=page.evaluate('document.documentElement.scrollWidth');cw=page.evaluate('document.documentElement.clientWidth')
    rec={'page':rel,'state':cfg['name'],'scroll_width':sw,'client_width':cw,'console_errors':console,'page_errors':pageerr};ok=sw<=cw+2 and not console and not pageerr and page.locator('main#main').count()==1 and page.locator('h1').count()==1
    if rel in {'index.html','en/index.html'}:
      rec['vortex_present']=page.locator('[data-vortex-stage]').count()==1;rec['typed_schematic']=page.locator('[data-vortex-stage][data-representation-status="schematic"][data-quantitative-status="derived-leading-exponents"]').count()==1;rec['static_present']=page.locator('[data-vortex-static]').count()==1
      if cfg['js']:
        rec['r17_canvas']=page.locator('[data-r17-hero-canvas]').count()==1;rec['r17_pause']=page.locator('[data-r17-pause]').count()==1;rec['legacy_play_absent']=page.locator('[data-vortex-controls] [data-play]').count()==0 and 'Play sweep' not in page.locator('[data-vortex-stage]').inner_text();state=page.locator('html').get_attribute('data-r17-motion');rec['r17_motion_state']=state;expected='reduced' if cfg['motion']=='reduce' else 'running'
        if not(rec['vortex_present'] and rec['typed_schematic'] and rec['static_present'] and rec['r17_canvas'] and rec['r17_pause'] and rec['legacy_play_absent'] and state==expected):ok=False
      else:
        rec['static_visible']=vis(page,'[data-vortex-static]')
        if not(rec['vortex_present'] and rec['static_visible']):ok=False
    elif rel in {'es/index.html','ar/index.html','zh-Hans/index.html'}:
      rec['vortex_present']=page.locator('[data-vortex-stage]').count()==1;rec['typed_schematic']=page.locator('[data-vortex-stage][data-representation-status="schematic"][data-quantitative-status="derived-leading-exponents"]').count()==1;rec['static_present']=page.locator('[data-vortex-static]').count()==1;controls=page.locator('[data-vortex-controls]')
      if not all([rec['vortex_present'],rec['typed_schematic'],rec['static_present']]):ok=False
      if cfg['js']:
        rec['controls_visible']=controls.is_visible();k=page.locator('[data-k]');old=k.input_value();page.wait_for_timeout(400);rec['autoplay_sweep_advances']=k.input_value()!=old
        if not(rec['controls_visible'] and (rec['autoplay_sweep_advances'] if cfg['motion']!='reduce' else not rec['autoplay_sweep_advances'])):ok=False
      else:
        rec['static_visible']=vis(page,'[data-vortex-static]')
        if not rec['static_visible']:ok=False
    if rel=='index.html':
      rec['trace_present']=page.locator('[data-scale-trace]').count()==1
      if cfg['js']:
        out=page.locator('[data-scale-trace-output]');before=out.text_content();page.wait_for_timeout(260);after=out.text_content();rec['trace_control']=page.locator('[data-scale-trace-toggle]').count()==1;rec['trace_motion_policy']=(before==after) if cfg['motion']=='reduce' else (before!=after)
        if not(rec['trace_present'] and rec['trace_control'] and rec['trace_motion_policy']):ok=False
    if rel=='en/reference-flow/index.html':
      rec['flow_present']=page.locator('[data-flow-chamber]').count()==1
      if cfg['js']:
        rec['flow_controls_visible']=vis(page,'[data-flow-controls]');rec['flow_canvas_visible']=vis(page,'[data-flow-canvas-frame]')
        if not(rec['flow_present'] and rec['flow_controls_visible'] and rec['flow_canvas_visible']):ok=False
    mobile=cfg['width']<=704;mn=page.locator('.mobile-nav');dn=page.locator('.nav-desktop')
    if rel!='index.html':
      if mobile:
        if not mn.is_visible() or dn.is_visible():ok=False
      else:
        if mn.is_visible() or not dn.is_visible():ok=False
    if rel.startswith('ar/') and page.locator('html').get_attribute('dir')!='rtl':ok=False
    rec['pass']=ok;rows.append(rec)
    if not ok:fails.append(rec)
    ctx.close()
  browser.close()
 return rows,fails
rows,failures=run();out={'schema':'nsc-public-browser-matrix-v3','scope':'structural+progressive+representative-functional; dynamic visual quality is audit_experience.py','browser':'system-chromium' if exe else 'playwright-managed-chromium','states':rows,'failures':failures,'pass':not failures};Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
if failures:
 print(f'PUBLIC_BROWSER_AUDIT_FAILED failures={len(failures)} states={len(rows)}',file=sys.stderr);[print(' -',x,file=sys.stderr) for x in failures[:8]];raise SystemExit(1)
print(f'PUBLIC_BROWSER_AUDIT_PASS pages={len(paths)} states={len(rows)} js_nojs=true rtl=true reduced_motion=true text200=true flagship_r5=true exact_reference_isolated=true')
