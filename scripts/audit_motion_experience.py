#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright
import re,shutil,sys
R=Path(__file__).resolve().parents[1];P=R/'public';css=(R/'assets/style.css').read_text();site=(R/'assets/site.js').read_text();r17=(R/'assets/r17-fluid.js').read_text()
exe=shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome') or ''

def inline(path,js=True,ctxfail=False):
 h=path.read_text();h=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>','',h,count=1);h=re.sub(r'<link rel="stylesheet"[^>]*>',lambda _:'<style>'+css+'</style>',h,count=1)
 h=re.sub(r'<script src="[^"]*site\.js" defer></script>',lambda _:('<script>'+site+'</script>' if js else ''),h,count=1)
 patch=''
 if js and ctxfail:patch="<script>const _gc=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(t,o){if(this.hasAttribute('data-vortex-canvas'))return null;return _gc.call(this,t,o)}</script>"
 h=re.sub(r'<script src="[^"]*r17-fluid\.js" defer></script>',lambda _:(patch+'<script>'+r17+'</script>' if js else ''),h,count=1)
 return h

def sample(pg,sel,step=12):
 return pg.eval_on_selector(sel,f"""c=>{{const x=c.getContext('2d'),d=x.getImageData(0,0,c.width,c.height).data,a=[];for(let y=0;y<c.height;y+={step})for(let z=0;z<c.width;z+={step}){{let i=(y*c.width+z)*4;a.push(d[i],d[i+1],d[i+2])}}return a}}""")
def mad(a,b):
 if len(a)!=len(b) or not a:return 1.0
 return sum(abs(x-y) for x,y in zip(a,b))/(len(a)*255.0)
def density(a):
 if not a:return 0.0
 n=len(a)//3;return sum(1 for i in range(0,len(a),3) if max(a[i:i+3])>25)/max(1,n)

def state(pg):return pg.locator('html').get_attribute('data-r17-motion')

with sync_playwright() as p:
 o={'headless':True,'args':['--no-sandbox','--disable-gpu']};
 if exe:o['executable_path']=exe
 b=p.chromium.launch(**o)
 # Home: autoplay, pointer velocity wake, bounded cadence, explicit pause, no hidden wake accumulation.
 c=b.new_context(viewport={'width':1200,'height':850},reduced_motion='no-preference');g=c.new_page();g.set_content(inline(P/'en/index.html'),wait_until='domcontentloaded');g.wait_for_timeout(450)
 assert state(g)=='running';assert g.locator('[data-r17-pause]').inner_text()=='Pause motion'
 a=sample(g,'[data-r17-hero-canvas]');n0=int(g.locator('[data-vortex-stage]').get_attribute('data-r17-render-count') or 0);g.wait_for_timeout(1200);bb=sample(g,'[data-r17-hero-canvas]');n1=int(g.locator('[data-vortex-stage]').get_attribute('data-r17-render-count') or 0);auto=mad(a,bb);fps=(n1-n0)/1.2
 box=g.locator('[data-r17-hero-canvas]').bounding_box();g.mouse.move(box['x']+box['width']*.34,box['y']+box['height']*.46);g.wait_for_timeout(80);first=float(g.locator('html').get_attribute('data-r17-page-speed') or 0);g.mouse.move(box['x']+box['width']*.78,box['y']+box['height']*.24,steps=16);g.wait_for_timeout(200);pp=sample(g,'[data-r17-hero-canvas]');pointer=mad(bb,pp);peak=float(g.locator('html').get_attribute('data-r17-page-speed') or 0);g.wait_for_timeout(1200);decay=float(g.locator('html').get_attribute('data-r17-page-speed') or 0)
 g.locator('[data-r17-mode="viscous"]').click();assert state(g)=='running'
 g.locator('[data-r17-pause]').click();g.wait_for_timeout(120);s0=sample(g,'[data-r17-hero-canvas]');q0=sample(g,'.r17-ambient-field');g.mouse.move(100,700);g.wait_for_timeout(550);s1=sample(g,'[data-r17-hero-canvas]');q1=sample(g,'.r17-ambient-field');paused=max(mad(s0,s1),mad(q0,q1));paused_speed=float(g.locator('html').get_attribute('data-r17-page-speed') or 0);assert state(g)=='paused'
 before=sample(g,'[data-r17-hero-canvas]');g.locator('[data-r17-reset]').click();g.wait_for_timeout(60);after=sample(g,'[data-r17-hero-canvas]');reset_delta=mad(before,after);assert state(g)=='paused'
 # Resume must restart actual field evolution while retaining zero stale pointer-wake velocity.
 resume0=sample(g,'[data-r17-hero-canvas]');g.locator('[data-r17-pause]').click();g.wait_for_timeout(600);resume1=sample(g,'[data-r17-hero-canvas]');resume_visual=mad(resume0,resume1);resume_wake_speed=float(g.locator('html').get_attribute('data-r17-page-speed') or 0);assert state(g)=='running';c.close()
 # Fresh browsing context autoplays: pause preference is intentionally session-scoped.
 c=b.new_context(viewport={'width':1200,'height':850},reduced_motion='no-preference');g=c.new_page();g.set_content(inline(P/'en/index.html'),wait_until='domcontentloaded');g.wait_for_timeout(140);fresh=state(g);c.close()
 # Reduced motion: stable but visibly populated hero.
 c=b.new_context(viewport={'width':1200,'height':850},reduced_motion='reduce');g=c.new_page();g.set_content(inline(P/'en/index.html'),wait_until='domcontentloaded');g.wait_for_timeout(220);r0=sample(g,'[data-r17-hero-canvas]');den=density(r0);g.wait_for_timeout(550);r1=sample(g,'[data-r17-hero-canvas]');reduced=mad(r0,r1);reduced_state=state(g);ambient_hidden=g.locator('.r17-ambient-field').is_hidden();c.close()
 # Non-home English rich page: page-wide field really persists throughout browsing and can be paused.
 c=b.new_context(viewport={'width':1200,'height':850},reduced_motion='no-preference');g=c.new_page();g.set_content(inline(P/'en/quests/index.html'),wait_until='domcontentloaded');g.wait_for_timeout(350);assert g.locator('[data-r17-hero-canvas]').count()==0;assert state(g)=='running';assert g.locator('.r17-global-pause').is_visible();aa=sample(g,'.r17-ambient-field',16);g.wait_for_timeout(650);ab=sample(g,'.r17-ambient-field',16);page_auto=mad(aa,ab);g.mouse.move(180,260);g.mouse.move(940,560,steps=18);g.wait_for_timeout(160);ac=sample(g,'.r17-ambient-field',16);page_pointer=mad(ab,ac);g.locator('.r17-global-pause').click();g.wait_for_timeout(100);p0=sample(g,'.r17-ambient-field',16);g.wait_for_timeout(500);p1=sample(g,'.r17-ambient-field',16);page_paused=mad(p0,p1);c.close()
 # Canvas2D hero failure must leave the static fallback instead of a blank panel; ambient may still enhance the page.
 c=b.new_context(viewport={'width':1200,'height':850});g=c.new_page();g.set_content(inline(P/'en/index.html',True,True),wait_until='domcontentloaded');g.wait_for_timeout(100);ctxfail_static=g.locator('[data-vortex-static]').is_visible();ctxfail_renderer=g.locator('[data-vortex-stage]').get_attribute('data-r17-renderer');c.close();b.close()

print(f'R17_MOTION_METRICS auto={auto:.5f} pointer={pointer:.5f} fps={fps:.1f} first_speed={first:.5f} peak={peak:.5f} decay={decay:.5f} paused={paused:.5f} paused_speed={paused_speed:.5f} resume_visual={resume_visual:.5f} resume_wake_speed={resume_wake_speed:.5f} reset={reset_delta:.5f} reduced={reduced:.5f} density={den:.3f} page_auto={page_auto:.5f} page_pointer={page_pointer:.5f} page_paused={page_paused:.5f} fresh={fresh}')
if auto<.01 or pointer<.01 or not(12<=fps<=45) or first>.02 or peak<.004 or decay>=peak*.45 or paused>.002 or paused_speed>.002 or resume_visual<.01 or resume_wake_speed>.01 or reset_delta<.002 or reduced>.002 or den<.02 or fresh!='running' or reduced_state!='reduced' or not ambient_hidden or page_auto<.00015 or page_pointer<.00015 or page_paused>.002 or not ctxfail_static or ctxfail_renderer!='static-fallback':raise SystemExit('R17_MOTION_EXPERIENCE_AUDIT_FAILED')
print('R17_MOTION_EXPERIENCE_AUDIT_PASS auto=true fps_bounded=true no_first_pointer_spike=true pointer_wake=true wake_decays=true pause_static=true pause_no_hidden_accumulation=true resume_visual=true resume_no_stale_wake=true reset_paused=true reduced_static=true fresh_session_autoplay=true pagewide_across_routes=true canvas_fallback=true')
