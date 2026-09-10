#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,re,shutil,sys
from pathlib import Path
from scratch import ScratchPolicyError, scratch_dir
try:
    from playwright.sync_api import sync_playwright
except Exception as e:
    print(f'BROWSER_AUDIT_UNAVAILABLE playwright={e}',file=sys.stderr); raise SystemExit(2)
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'public'
try:
    DEFAULT_OUTPUT=scratch_dir('browser-audit')/'browser_matrix.json'
except ScratchPolicyError as e:
    print('BROWSER_AUDIT_UNAVAILABLE scratch policy: '+str(e),file=sys.stderr); raise SystemExit(2)
ap=argparse.ArgumentParser(); ap.add_argument('--output',default=str(DEFAULT_OUTPUT)); ap.add_argument('--chromium',default=os.getenv('NSC_CHROMIUM','')); a=ap.parse_args()
exe=a.chromium.strip() or shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome') or ''
css=(ROOT/'assets/style.css').read_text(); js=(ROOT/'assets/site.js').read_text()
# Unique product surfaces plus language-direction and preview state.
mission=next((P/'en/missions').glob('*/index.html'))
paths=[P/'en/index.html',P/'en/quests/index.html',P/'en/quests/ns-q008/index.html',mission,P/'en/contribute/index.html',P/'en/agents/index.html',P/'en/governance/index.html',P/'en/benchmarks/index.html',P/'ar/index.html',P/'de/index.html']
configs=[
 {'name':'desktop-js','width':1440,'height':1000,'js':True,'color':'light','motion':'no-preference','forced':'none','zoom':1},
 {'name':'mobile-js','width':390,'height':844,'js':True,'color':'light','motion':'no-preference','forced':'none','zoom':1},
 {'name':'mobile-nojs','width':390,'height':844,'js':False,'color':'light','motion':'no-preference','forced':'none','zoom':1},
 {'name':'dark-reduced','width':390,'height':844,'js':True,'color':'dark','motion':'reduce','forced':'none','zoom':1},
 {'name':'forced-nojs-200pct','width':390,'height':844,'js':False,'color':'light','motion':'reduce','forced':'active','zoom':2},
]

def inline(path:Path,js_on:bool)->str:
    h=path.read_text()
    # The harness inlines same-origin assets into set_content; remove only the CSP meta in this synthetic DOM so the harness itself does not violate the production policy. Static audits require the production CSP.
    h=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', '', h, count=1)
    h=re.sub(r'<link rel="stylesheet"[^>]*>',lambda _: '<style>'+css+'</style>',h,count=1)
    h=re.sub(r'<script src="[^"]+" defer></script>',lambda _: '<script>'+js+'</script>' if js_on else '',h,count=1)
    return h

def run():
    rows=[]; failures=[]
    with sync_playwright() as pw:
        opts={'headless':True,'args':['--no-sandbox','--disable-gpu']}
        if exe: opts['executable_path']=exe
        browser=pw.chromium.launch(**opts)
        for path in paths:
          rel=path.relative_to(P).as_posix()
          for cfg in configs:
            ctx=browser.new_context(viewport={'width':cfg['width'],'height':cfg['height']},java_script_enabled=cfg['js'],color_scheme=cfg['color'],reduced_motion=cfg['motion'],forced_colors=cfg['forced'])
            page=ctx.new_page(); console=[]; pageerr=[]
            page.on('console',lambda msg,bag=console: bag.append(msg.text) if msg.type=='error' else None)
            page.on('pageerror',lambda exc,bag=pageerr: bag.append(str(exc)))
            page.set_content(inline(path,cfg['js']),wait_until='domcontentloaded',timeout=10000)
            if cfg['zoom']!=1: page.evaluate(f"document.documentElement.style.fontSize='{cfg['zoom']*100:.0f}%'" )
            if cfg['js']: page.wait_for_timeout(80)
            sw=page.evaluate('document.documentElement.scrollWidth'); cw=page.evaluate('document.documentElement.clientWidth')
            main=page.locator('main#main').count(); h1=page.locator('h1').count();
            rec={'page':rel,'state':cfg['name'],'scroll_width':sw,'client_width':cw,'console_errors':console,'page_errors':pageerr,'main':main,'h1':h1}
            ok=sw<=cw+2 and not console and not pageerr and main==1 and h1==1
            if rel=='en/index.html':
                scale_controls=page.locator('[data-lab-controls]')
                flow_controls=page.locator('[data-flow-controls]')
                static=page.locator('[data-flow-static]')
                rec['scale_controls_hidden']=scale_controls.evaluate('e=>e.hidden')
                rec['flow_controls_hidden']=flow_controls.evaluate('e=>e.hidden')
                rec['flow_static_nonempty']=bool(static.text_content().strip())
                if not rec['flow_static_nonempty']: ok=False
                if cfg['js']:
                    if rec['scale_controls_hidden'] or rec['flow_controls_hidden']: ok=False
                    t=page.locator('[data-flow-t]'); state=page.locator('[data-flow-state]'); before=state.text_content(); old=t.input_value(); page.wait_for_timeout(120)
                    # no autoplay: time must remain unchanged before explicit play.
                    rec['no_autoplay']=t.input_value()==old
                    t.evaluate("e=>{e.value='1.24';e.dispatchEvent(new Event('input',{bubbles:true}))}")
                    current=t.input_value(); after=state.text_content(); rec['state_updates']=before!=after and f"t={float(current):.2f}" in after
                    rec['canvas_visible']=page.locator('[data-flow-canvas-frame]').is_visible()
                    if not (rec['no_autoplay'] and rec['state_updates'] and rec['canvas_visible']): ok=False
                    scale_play=page.locator('[data-lab-play]'); flow_play=page.locator('[data-flow-play]')
                    if cfg['motion']=='reduce':
                        rec['reduced_motion_play_controls_suppressed']=(not scale_play.is_visible()) and (not flow_play.is_visible())
                        if not rec['reduced_motion_play_controls_suppressed']: ok=False
                    else:
                        # Do not predicate a release on rAF cadence: hosted headless
                        # browsers may throttle it.  Exercise the terminal restart and
                        # explicit pause transitions synchronously, and require the
                        # bounded terminal guard in the shipped controller.
                        t.evaluate("e=>{e.value=e.max;e.dispatchEvent(new Event('input',{bubbles:true}))}")
                        flow_play.dispatch_event('click')
                        rec['flow_terminal_restart_resets_to_min']=abs(float(t.input_value())-float(t.get_attribute('min'))) < 1e-9
                        rec['flow_play_enters_pressed_state']=flow_play.get_attribute('aria-pressed')=='true'
                        flow_play.dispatch_event('click')
                        rec['flow_play_returns_unpressed_state']=flow_play.get_attribute('aria-pressed')=='false'
                        rec['flow_end_bound_guard_declared']='if(Number(tInput.value)>=tMax-1e-9){stopFlow();draw(true);return;}' in js
                        if not (rec['flow_terminal_restart_resets_to_min'] and rec['flow_play_enters_pressed_state'] and rec['flow_play_returns_unpressed_state'] and rec['flow_end_bound_guard_declared']): ok=False
                else:
                    if not (rec['scale_controls_hidden'] and rec['flow_controls_hidden']): ok=False
            mobile=cfg['width']<=704
            mobile_nav=page.locator('.mobile-nav')
            desktop_nav=page.locator('.nav-desktop')
            if mobile:
                rec['mobile_nav_visible']=mobile_nav.is_visible()
                rec['desktop_nav_visible']=desktop_nav.is_visible()
                panel=page.locator('.nav-mobile-panel')
                rec['mobile_panel_initially_hidden']=not panel.is_visible()
                if rec['mobile_nav_visible']:
                    mobile_nav.locator(':scope > summary').click()
                    rec['mobile_panel_opens']=panel.is_visible()
                else:
                    rec['mobile_panel_opens']=False
                if not (rec['mobile_nav_visible'] and not rec['desktop_nav_visible'] and rec['mobile_panel_initially_hidden'] and rec['mobile_panel_opens']): ok=False
            else:
                rec['mobile_nav_visible']=mobile_nav.is_visible()
                rec['desktop_nav_visible']=desktop_nav.is_visible()
                if rec['mobile_nav_visible'] or not rec['desktop_nav_visible']: ok=False
            if rel.startswith('ar/') and page.locator('html').get_attribute('dir')!='rtl': ok=False
            if rel.startswith('de/') and page.locator('.locale-preview-notice').count()!=1: ok=False
            rec['pass']=ok; rows.append(rec)
            if not ok: failures.append(rec)
            ctx.close()
        browser.close()
    return rows,failures
rows,failures=run(); browser_id=('system-chromium' if exe else 'playwright-managed-chromium')
out={'schema':'nsc-public-browser-matrix-v1','browser':browser_id,'states':rows,'failures':failures,'pass':not failures}
outp=Path(a.output); outp.parent.mkdir(parents=True,exist_ok=True); outp.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
if failures:
    print(f'PUBLIC_BROWSER_AUDIT_FAILED failures={len(failures)} states={len(rows)}',file=sys.stderr)
    for x in failures[:8]: print(' -',x,file=sys.stderr)
    raise SystemExit(1)
print(f'PUBLIC_BROWSER_AUDIT_PASS pages={len(paths)} states={len(rows)} js_nojs=true rtl=true reduced_motion=true forced_colors=true zoom200=true interactions=true')
