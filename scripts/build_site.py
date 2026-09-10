#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, html, urllib.parse, re, math
from pathlib import Path
from nsc_model import project_view, expanded_missions, expanded_quests, expanded_claims_doc, localized_license_line, counts, capabilities, public_registry, release_policy

ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'content'/'public'
PUBLIC=ROOT/'public'
ASSETS=ROOT/'assets'
project=project_view()
registry=public_registry()
sources=json.loads((CONTENT/'sources.json').read_text())
missions=expanded_missions()
contributions=json.loads((CONTENT/'contributions.json').read_text()) if (CONTENT/'contributions.json').exists() else []
forges=json.loads((CONTENT/'forges.json').read_text()) if (CONTENT/'forges.json').exists() else {'adapters':[]}
scaling=json.loads((CONTENT/'scaling_model.json').read_text())
simulations_doc=json.loads((CONTENT/'simulations.json').read_text())
reference_benchmarks=json.loads((CONTENT/'reference_benchmarks.json').read_text())
actions_doc=json.loads((CONTENT/'actions.json').read_text())
formula_catalog=json.loads((CONTENT/'formulas.json').read_text())
quests=expanded_quests()
quests_doc={'schema':json.loads((CONTENT/'quests.json').read_text()).get('schema','nsc-quests-v1'),'quests':quests}
task_ladder=json.loads((CONTENT/'task_ladder.json').read_text())
claims_doc=expanded_claims_doc()
governance=json.loads((CONTENT/'governance.json').read_text())
founding_sprint=json.loads((CONTENT/'founding_sprint.json').read_text())
reviews=json.loads((CONTENT/'reviews.json').read_text()) if (CONTENT/'reviews.json').exists() else []
public_ssot=json.loads((ROOT/'PUBLIC_SSOT.json').read_text())
quest_by_id={q['id']:q for q in quests}
mission_by_id={m['id']:m for m in missions}
rung_by_id={r['id']:r for r in task_ladder['rungs']}
formula_by_id={f['id']:f for f in formula_catalog['formulas']}
source_by_id={s['id']:s for s in sources}
locales={loc:json.loads((CONTENT/'locales'/f'{loc}.json').read_text()) for loc in project['locales']}
mi18n={loc:json.loads((CONTENT/'mission_i18n'/f'{loc}.json').read_text()) for loc in project['locales']}
taxonomy={loc:json.loads((CONTENT/'taxonomy_i18n'/f'{loc}.json').read_text()) for loc in project['locales']}
source_i18n={loc:json.loads((CONTENT/'source_i18n'/f'{loc}.json').read_text()) for loc in project['locales']}

SITE_URL=os.getenv('SITE_URL','').rstrip('/')
GH_REPO=os.getenv('GITHUB_REPOSITORY','').strip()
GL_URL=os.getenv('CI_PROJECT_URL','').strip().rstrip('/')
FORGE_KIND=os.getenv('COMMONS_FORGE_KIND','').strip().lower()
FORGE_URL=os.getenv('COMMONS_FORGE_URL','').strip().rstrip('/')
if not FORGE_KIND:
    FORGE_KIND='github' if GH_REPO else ('gitlab' if GL_URL else 'generic')
if not FORGE_URL:
    FORGE_URL=(f'https://github.com/{GH_REPO}' if GH_REPO else GL_URL)
REPO_URL=FORGE_URL
HOST=FORGE_KIND

CATEGORY_ORDER=json.loads((CONTENT/'taxonomy.json').read_text())['category_order']

SECURITY_META="""<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"><meta name="referrer" content="no-referrer">"""

def deployed_ref(from_public_path:str, logical_site_path:str)->str:
    """Relative URL from a generated public file to one logical site-root path."""
    out=os.path.relpath(logical_site_path.lstrip('/'), start=str(Path(from_public_path).parent)).replace(os.sep,'/')
    return out+'/' if logical_site_path.endswith('/') and not out.endswith('/') else out


def esc(x): return html.escape(str(x), quote=True)
def slugify(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def rel(page:Path,target:str)->str:
    return os.path.relpath(PUBLIC/target, page.parent).replace(os.sep,'/')
def logical_target(loc:str,kind:str,slug:str|None=None)->str:
    if kind=='home': return f'{loc}/index.html'
    if kind=='mission': return f'{loc}/missions/{slug}/index.html'
    return f'{loc}/{kind}/index.html'
def repo_issue(template:str,title:str='')->str:
    if not REPO_URL:
        return ''
    kind={'claim_quest.yml':'attempt','open_attempt.yml':'attempt','side_quest.yml':'side_quest','submit_result.yml':'result','review.yml':'review'}.get(template,'contribution')
    if HOST=='github':
        q={'template':template}
        if title:q['title']=title
        return f'{REPO_URL}/issues/new?{urllib.parse.urlencode(q)}'
    if HOST=='gitlab':
        return f'{REPO_URL}/-/work_items/new?{urllib.parse.urlencode({"description_template":kind})}'
    if HOST in {'forgejo','gitea','codeberg'}:
        body=f'Contribution type: {kind}\n\nPlease include the relevant mission ID, exact claim, evidence, limitations, and reproduction instructions.'
        return f'{REPO_URL}/issues/new?{urllib.parse.urlencode({"title":title or kind,"body":body})}'
    # Bitbucket and unknown forges intentionally fall back to the repository root;
    # CONTRIBUTING.md + the public manifest schema remain the portable channel.
    return REPO_URL

def forge_label():
    return {'github':'GitHub','gitlab':'GitLab','forgejo':'Forgejo','codeberg':'Codeberg','gitea':'Gitea','bitbucket':'Bitbucket','generic':'Git repository'}.get(HOST,HOST.title())

def cat_label(loc,cat): return taxonomy[loc]['categories'].get(cat,cat)
def level_label(loc,level): return taxonomy[loc]['levels'].get(level,level)
def contrib_label(loc,name): return taxonomy[loc]['contributors'].get(name,name)

def locale_is_preview(loc:str)->bool:
    return project.get('locale_status',{}).get(loc)=='interface-preview'

def canonical_english_attrs(loc:str)->str:
    return ' lang="en" dir="ltr"' if locale_is_preview(loc) else ''

def locale_preview_notice(loc:str)->str:
    if not locale_is_preview(loc):
        return ''
    text=locales[loc].get('preview_notice','').strip()
    if not text:
        return ''
    return f'<aside class="locale-preview-notice" role="note" lang="en" dir="ltr"><div class="container"><strong>Interface preview</strong><span>{esc(text)}</span></div></aside>'

def source_links(ids, page:Path):
    out=[]
    for sid in ids:
        s=source_by_id[sid]
        out.append(f'<a class="source-inline" lang="en" dir="ltr" href="{esc(s["url"])}">{esc(s["title"])}</a>')
    return ', '.join(out)

def source_card(page:Path,loc:str,s,heading=2):
    L=locales[loc]; S=L['source_meta']
    immutable=s.get('reference_type')=='immutable-git-commit'
    ref_label=S['immutable'] if immutable else S['mutable']
    version=(f'<span><strong>{esc(S["version"])}:</strong> <code>{esc(s["version"][:12])}</code></span>' if s.get('version') else '')
    claims='; '.join(source_i18n[loc].get(s['id'],{}).get('claims_supported',s.get('claims_supported',[])))
    return f'''<article class="source-record"><div class="source-record-top"><span class="signal-dot" aria-hidden="true"></span><span class="micro">{esc(S['record'])}</span><span class="source-ref-type">{esc(ref_label)}</span></div><h{heading} lang="en" dir="ltr"><a href="{esc(s['url'])}">{esc(s['title'])}</a></h{heading}><p><strong>{esc(L['sources']['publisher'])}:</strong> {esc(s['publisher'])}</p><p lang="en" dir="ltr"><strong>{esc(L['sources']['supports'])}:</strong> {esc(claims)}</p><div class="source-record-meta"><span><strong>{esc(S['retrieved'])}:</strong> {esc(s.get('retrieved_at',';'))}</span>{version}</div></article>'''

def alternates(page:Path,kind:str,slug=None):
    bits=[]
    for loc in project['locales']:
        href=rel(page,logical_target(loc,kind,slug))
        bits.append(f'<link rel="alternate" hreflang="{esc(loc)}" href="{esc(href)}">')
    bits.append(f'<link rel="alternate" hreflang="x-default" href="{esc(rel(page,"index.html"))}">')
    return '\n'.join(bits)

def brand(page,loc):
    return f'''<a class="brand" href="{esc(rel(page,logical_target(loc,'home')))}"><span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 40 40" focusable="false"><path d="M5 21c5-12 20-16 29-6"/><path d="M7 28c9 6 22 3 27-7"/><path d="M12 13c7-3 17-1 21 6"/><circle cx="20" cy="21" r="2.5"/></svg></span><span class="brand-lockup"><strong>Navier–Stokes</strong><small>Commons</small></span></a>'''

def lang_switch(page:Path,loc:str,kind:str,slug=None):
    L=locales[loc]
    items=[]
    for x in project['locales']:
        lx=locales[x]
        current=' aria-current="true"' if x==loc else ''
        target=rel(page,logical_target(x,kind,slug))
        items.append(f'<a lang="{esc(x)}" dir="{esc(lx["dir"])}" href="{esc(target)}"{current}>{esc(lx["name"])}</a>')
    return f'''<details class="language-switcher"><summary><span aria-hidden="true">◎</span><span>{esc(L['language'])}</span></summary><div class="language-menu">{''.join(items)}</div></details>'''

def nav(page:Path,loc:str,current:str,kind:str,slug=None):
    L=locales[loc]
    links=[
        ('missions',L['nav']['missions'],'missions'),
        ('guide',L['nav'].get('guide','Guide'),'guide'),
        ('activity',L['nav'].get('activity','Contributions'),'activity'),
        ('contribute',L['nav']['contribute'],'contribute'),
        ('sources',L['nav']['sources'],'sources'),
        ('agents',L['nav']['agents'],'agents'),
    ]
    n=[]
    for key,label,target_kind in links:
        aria=' aria-current="page"' if current==key else ''
        n.append(f'<a class="nav-link" href="{esc(rel(page,logical_target(loc,target_kind)))}"{aria}>{esc(label)}</a>')
    n.insert(1,f'<a class="nav-link" lang="en" dir="ltr" href="{esc(rel(page,"en/quests/index.html"))}">Quests</a>')
    theme=f'<button class="theme-toggle enhance-only" type="button" data-theme-toggle data-label-system="{esc(L["system"])}" data-label-light="{esc(L["light"])}" data-label-dark="{esc(L["dark"])}" hidden aria-label="{esc(L["theme"])}"><span class="theme-glyph" aria-hidden="true">◐</span><span data-theme-label>{esc(L["system"])}</span></button>'
    items=''.join(n)+theme+lang_switch(page,loc,kind,slug)
    # Two responsive projections from the same generated navigation model. CSS exposes exactly one.
    mobile_items=''.join(n)+theme+lang_switch(page,loc,kind,slug)
    return f'''<header class="site-header"><div class="container header-row">{brand(page,loc)}<nav class="nav-wrap nav-desktop" aria-label="{esc(L['menu'])}">{items}</nav><details class="mobile-nav"><summary>{esc(L['menu'])}</summary><nav class="nav-wrap nav-mobile-panel" aria-label="{esc(L['menu'])}">{mobile_items}</nav></details></div></header>'''

def footer(page,loc):
    L=locales[loc]
    lic_attrs=canonical_english_attrs(loc)
    return f'''<footer class="site-footer"><div class="container footer-grid"><div>{brand(page,loc)}<p>{esc(L['tagline'])}</p></div><div><strong>{esc(L['footer']['public'])}</strong><p>{esc(L['footer']['privacy'])}</p></div><div><a href="{esc(rel(page,logical_target(loc,'accessibility')))}">{esc(L['nav']['accessibility'])}</a><p{lic_attrs}>{esc(localized_license_line(loc,L))}</p></div></div></footer>'''

def shell(page:Path,loc:str,current:str,kind:str,title:str,description:str,body:str,slug=None, extra_head=''):
    L=locales[loc]; direction=L['dir']
    asset_css=rel(page,'assets/style.css'); asset_js=rel(page,'assets/site.js')
    alt=alternates(page,kind,slug)
    canonical=''
    if SITE_URL:
        relurl=logical_target(loc,kind,slug).replace('index.html','')
        canonical=f'<link rel="canonical" href="{esc(SITE_URL+"/"+relurl)}">'
    return f'''<!doctype html>
<html lang="{esc(loc)}" dir="{esc(direction)}" data-theme="system">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)} · Navier–Stokes Commons</title>
<meta name="description" content="{esc(description)}">
{SECURITY_META}
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#071d20" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f4f7f4" media="(prefers-color-scheme: light)">
{canonical}
{alt}
<link rel="stylesheet" href="{esc(asset_css)}">
{extra_head}
</head>
<body data-page-kind="{esc(kind)}">
<a class="skip-link" href="#main">{esc(L['skip'])}</a>
{nav(page,loc,current,kind,slug)}
{locale_preview_notice(loc)}
<main id="main">{body}</main>
{footer(page,loc)}
<script src="{esc(asset_js)}" defer></script>
</body></html>'''

def write(path:str,text:str):
    p=PUBLIC/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding='utf-8')

def mission_text(loc,m):
    tr=mi18n[loc].get(m['id'],{})
    return {k:tr.get(k,m[k]) for k in ('title','summary','question')}

def formula_value(qid,tau,h):
    q=next(q for q in scaling['quantities'] if q['id']==qid)
    e=q['exponent']['constant']+q['exponent']['h']*h
    return tau**e

def ascii_core_frame(tau,h,width=23,height=11):
    aspect=formula_value('aspect',tau,h)
    inner_w=max(3,min(width-4,int(round((width-4)/(aspect**0.5)))))
    inner_h=max(3,min(height-2,int(round((height-2)*(aspect**0.5)))))
    if inner_h%2==0: inner_h-=1
    if inner_w%2==0: inner_w-=1
    canvas=[[' ']*width for _ in range(height)]
    cx,cy=width//2,height//2
    rx=max(1,inner_w//2); ry=max(1,inner_h//2)
    for y in range(height):
        for x in range(width):
            dx=(x-cx)/rx; dy=(y-cy)/ry
            v=dx*dx+dy*dy
            if 0.72 <= v <= 1.35: canvas[y][x]='#'
            elif v<0.72 and (x==cx or y==cy): canvas[y][x]='+'
    art='\n'.join(''.join(row).rstrip() for row in canvas)
    def exp_line(qid,symbol):
        value=formula_value(qid,tau,h)
        logv=math.log10(value) if value > 0 else 0
        arrow='>' if logv >= 0 else '<'
        bar=arrow*max(1,min(22,int(round(abs(logv)/2)))) if abs(logv) >= 0.2 else '.'
        return f'{symbol:<10} 10^{logv:>7.2f}  {bar}'
    return art+'\n\n'+\
        exp_line('ell_r','ell_r')+'\n'+\
        exp_line('ell_z','ell_z')+'\n'+\
        exp_line('u_theta','|u_theta|')+'\n'+\
        exp_line('energy','E_core')+'\n'+\
        exp_line('re_theta','Re_theta')

def curve_path_server(qid,h):
    q=next(q for q in scaling['quantities'] if q['id']==qid)
    e=q['exponent']['constant'] + q['exponent']['h']*h
    pts=[]
    for k in range(0,81,2):
        logv=-k*e
        x=48+(k/80)*452
        y=max(20,min(216,118-logv*2.25))
        pts.append(f'{"L" if k else "M"}{x:.1f} {y:.1f}')
    return ' '.join(pts)

def formula_tex(node):
    typ=node['type']
    if typ=='row': return ' '.join(formula_tex(x) for x in node['children']).replace(' ,',',')
    if typ=='identifier': return {'ν':r'\nu'}.get(node['value'],node['value'])
    if typ=='number': return node['value']
    if typ=='operator': return {'∂':r'\partial','·':r'\cdot','∇':r'\nabla','Δ':r'\Delta','−':'-'}.get(node['value'],node['value'])
    if typ=='subscript': return f"{formula_tex(node['base'])}_{{{formula_tex(node['sub'])}}}"
    if typ=='group': return r'\left(' + ' '.join(formula_tex(x) for x in node['children']) + r'\right)'
    if typ=='space': return r'\qquad'
    raise ValueError(f'unsupported formula node type {typ}')

def formula_mathml(node):
    typ=node['type']
    if typ=='row': return '<mrow>'+''.join(formula_mathml(x) for x in node['children'])+'</mrow>'
    if typ=='identifier': return f'<mi>{esc(node["value"])}</mi>'
    if typ=='number': return f'<mn>{esc(node["value"])}</mn>'
    if typ=='operator': return f'<mo>{esc(node["value"])}</mo>'
    if typ=='subscript': return '<msub>'+formula_mathml(node['base'])+formula_mathml(node['sub'])+'</msub>'
    if typ=='group': return '<mrow><mo>(</mo>'+''.join(formula_mathml(x) for x in node['children'])+'<mo>)</mo></mrow>'
    if typ=='space': return f'<mspace width="{float(node.get("em",1)):.1f}em"/>'
    raise ValueError(f'unsupported formula node type {typ}')

def formula_speech(node):
    typ=node['type']
    if typ=='row': return ' '.join(x for x in (formula_speech(c) for c in node['children']) if x)
    if typ=='identifier': return {'ν':'nu','u':'u','p':'p','f':'f','t':'t'}.get(node['value'],node['value'])
    if typ=='number': return node['value']
    if typ=='operator': return {'∂':'partial','·':'dot','∇':'grad','Δ':'laplacian','−':'minus','+':'plus','=':'equals',',':''}.get(node['value'],node['value'])
    if typ=='subscript': return formula_speech(node['base'])+' '+formula_speech(node['sub'])
    if typ=='group': return formula_speech({'type':'row','children':node['children']})
    if typ=='space': return ''
    raise ValueError(f'unsupported formula node type {typ}')

def equation_block():
    formula=formula_by_id['incompressible-navier-stokes-forced']
    ast=formula['ast']
    tex=formula_tex(ast)
    mathml=formula_mathml(ast)
    speech=formula_speech(ast)
    return f'''<div class="equation-line equation-object" data-formula-id="{esc(formula['id'])}" data-equation-tex="{esc(tex)}"><math display="block" aria-label="{esc(speech)}"><semantics>{mathml}<annotation encoding="application/x-tex">{esc(tex)}</annotation></semantics></math></div>'''
def scaling_lab(page,loc):
    O=locales[loc]['observatory']
    h=float(scaling['parameters']['h']['default'])
    default_k=40.0
    default_tau=10**(-default_k)
    frames=[]
    for k in (2,20,60):
        tau=10**(-k)
        frame=ascii_core_frame(tau,h)
        frames.append(f'''<div class="ascii-frame"><div class="ascii-head">tau = 10^-{k}</div><pre aria-label="{esc(O['core_aspect'])}, tau 10^-{k}">{esc(frame)}</pre></div>''')
    symbol={'ell_r':'ell_r','ell_z':'ell_z','u_theta':'|u_theta|','energy':'E_core','re_theta':'Re_theta'}
    vals=[]
    for qid in ('ell_r','ell_z','u_theta','energy','re_theta'):
        q=next(q for q in scaling['quantities'] if q['id']==qid)
        value=formula_value(qid,default_tau,h)
        logv=math.log10(value) if value > 0 else 0
        display='1' if abs(logv) < 0.005 else f'10^{logv:.2f}'
        vals.append(f'''<tr><th scope="row"><code>{esc(symbol[qid])}</code></th><td><code>{esc(q['relation'])} {esc(q['formula'])}</code></td><td data-scale-value="{esc(qid)}">{esc(display)}</td></tr>''')
    source=source_by_id.get('openai-paper')
    src=f'<a href="{esc(source["url"])}">{esc(O["paper_section"])}</a>' if source else esc(O['paper_section'])
    default_aspect=formula_value('aspect',default_tau,h)
    default_speed=math.log10(formula_value('u_theta',default_tau,h))
    default_energy=math.log10(formula_value('energy',default_tau,h))
    dirv=locales[loc].get('dir','ltr')
    coeffs={q['id']:[q['exponent']['constant'],q['exponent']['h']] for q in scaling['quantities']}
    coeff_json=json.dumps(coeffs,separators=(',',':'))
    return f'''<section class="scaling-lab" data-scaling-lab data-source="openai-paper" data-exponents="{esc(coeff_json)}" lang="{esc(loc)}" dir="{esc(dirv)}"><div class="lab-copy"><span class="micro">{esc(O['scale_kicker'])}</span><h2>{esc(O['scale_title'])}</h2><p>{esc(O['scale_body'])}</p><p class="source-line">{src}</p>{equation_block()}<div class="lab-controls enhance-only" data-lab-controls hidden><label>{esc(O['time_decades'])} <output data-k-output>{default_k:.0f}</output><input type="range" min="0.25" max="80" value="{default_k:.0f}" step="0.25" data-tau-k aria-label="{esc(O['time_decades'])}"></label><label>{esc(O['h_param'])} <output data-h-output>{h:.4f}</output><input type="range" min="0.0005" max="0.0095" value="{h}" step="0.0001" data-h aria-label="{esc(O['h_param'])}"></label><button type="button" data-lab-play data-play-label="{esc(O['play'])}" data-pause-label="{esc(O['pause'])}">{esc(O['play'])}</button></div></div><div class="lab-stage"><div class="core-viz" aria-labelledby="core-viz-title"><h3 id="core-viz-title">{esc(O['core_aspect'])}</h3><svg viewBox="0 0 420 340" role="img" aria-labelledby="core-svg-title core-svg-desc"><title id="core-svg-title">{esc(O['core_aspect'])}</title><desc id="core-svg-desc">{esc(O['table_caption'])}</desc><line x1="210" y1="24" x2="210" y2="316" class="core-axis"/><line x1="54" y1="170" x2="366" y2="170" class="core-axis"/><ellipse cx="210" cy="170" rx="{92/math.sqrt(default_aspect):.2f}" ry="{min(138,92*math.sqrt(default_aspect)):.2f}" class="core-ellipse" data-core-ellipse/><circle cx="210" cy="170" r="5" class="core-origin"/></svg><div class="core-meters"><div><span>tau</span><strong data-tau-output>10^-{default_k:.0f}</strong></div><div><span>ell_z / ell_r</span><strong data-aspect-output>{default_aspect:.2f}</strong></div><div><span>{esc(O['speed'])}</span><strong data-speed-output>10^{default_speed:.2f}</strong></div><div><span>{esc(O['energy'])}</span><strong data-energy-output>10^{default_energy:.2f}</strong></div></div></div><div class="lab-plot"><h3>{esc(O['log_trajectories'])}</h3><svg viewBox="0 0 520 250" role="img" aria-labelledby="plot-title plot-desc"><title id="plot-title">{esc(O['log_trajectories'])}</title><desc id="plot-desc">{esc(O['table_caption'])}</desc><line x1="48" y1="20" x2="48" y2="216" class="plot-axis"/><line x1="48" y1="216" x2="500" y2="216" class="plot-axis"/><path data-curve="ell_r" class="curve curve-r" d="{curve_path_server('ell_r',h)}"/><path data-curve="ell_z" class="curve curve-z" d="{curve_path_server('ell_z',h)}"/><path data-curve="u_theta" class="curve curve-u" d="{curve_path_server('u_theta',h)}"/><path data-curve="energy" class="curve curve-e" d="{curve_path_server('energy',h)}"/><line data-cursor x1="274" y1="20" x2="274" y2="216" class="plot-cursor"/><g class="plot-key"><text x="60" y="36">{esc(O['radial'])}</text><text x="170" y="36">{esc(O['axial'])}</text><text x="290" y="36">{esc(O['speed'])}</text><text x="390" y="36">{esc(O['energy'])}</text></g></svg></div></div><div class="lab-fallback"><div class="ascii-live"><span class="micro">ASCII SCALE TRACE</span><pre data-ascii-live>{esc(ascii_core_frame(default_tau,h))}</pre></div><div class="ascii-sequence">{''.join(frames)}</div><table class="scaling-table"><caption>{esc(O['table_caption'])}</caption><thead><tr><th>{esc(O['quantity'])}</th><th>{esc(O['published_scaling'])}</th><th>{esc(O['normalized_value'])}</th></tr></thead><tbody>{''.join(vals)}</tbody></table></div></section>'''
def sim_expr_eval(node, variables, parameters):
    typ=node['type']
    if typ=='number': return float(node['value'])
    if typ=='param': return float(parameters[node['name']])
    if typ=='var': return float(variables[node['name']])
    if typ!='op': raise ValueError('unsupported simulation expression node '+str(typ))
    name=node['op']; args=[sim_expr_eval(a,variables,parameters) for a in node.get('args',[])]
    if name=='add': return sum(args)
    if name=='mul': return math.prod(args)
    if name=='neg': return -args[0]
    if name=='exp': return math.exp(args[0])
    if name=='sin': return math.sin(args[0])
    if name=='cos': return math.cos(args[0])
    if name=='pow': return args[0]**args[1]
    raise ValueError('unsupported simulation expression op '+str(name))

def sim_expr_text(node):
    typ=node['type']
    if typ=='number': return str(node['value'])
    if typ in {'param','var'}: return node['name']
    name=node['op']; a=node.get('args',[])
    if name=='add': return '('+' + '.join(sim_expr_text(z) for z in a)+')'
    if name=='mul': return ' '.join(sim_expr_text(z) for z in a)
    if name=='neg': return '-('+sim_expr_text(a[0])+')'
    if name in {'exp','sin','cos'}: return name+'('+sim_expr_text(a[0])+')'
    if name=='pow': return '('+sim_expr_text(a[0])+')^('+sim_expr_text(a[1])+')'
    raise ValueError('unsupported simulation expression op '+str(name))

def flow_velocity(sim,x,y,t,A,nu):
    env={'x':x,'y':y,'t':t}; pars={'A':A,'nu':nu}; f=sim['fields']
    return sim_expr_eval(f['u_x'],env,pars),sim_expr_eval(f['u_y'],env,pars)

def flow_ascii(sim,t=0.0,A=1.0,nu=0.035,nx=21,ny=11):
    glyphs=['→','↗','↑','↖','←','↙','↓','↘']; rows=[]
    for j in range(ny):
        y=2*math.pi*j/(ny-1); row=[]
        for i in range(nx):
            x=2*math.pi*i/(nx-1); u,v=flow_velocity(sim,x,y,t,A,nu); mag=math.hypot(u,v)
            if mag<0.04*max(A,1e-12): row.append('·'); continue
            ang=(math.atan2(-v,u)%(2*math.pi)); row.append(glyphs[int(round(ang/(math.pi/4)))%8])
        rows.append(''.join(row))
    return '\n'.join(rows)

def flow_chamber(page,loc):
    if loc!='en': return ''
    sim=simulations_doc['simulations'][0]; params=sim['parameters']; A=params['A']['default']; nu=params['nu']['default']; t=params['t']['default']
    env={'x':0.0,'y':0.0,'t':t}; pars={'A':A,'nu':nu}; energy=sim_expr_eval(sim['fields']['mean_kinetic_energy'],env,pars)
    source=source_by_id[sim['source_ids'][0]]; fallback=flow_ascii(sim,t,A,nu); model_json=json.dumps(sim['fields'],separators=(',',':'))
    ux=sim_expr_text(sim['fields']['u_x']); uy=sim_expr_text(sim['fields']['u_y']); ee=sim_expr_text(sim['fields']['mean_kinetic_energy'])
    return f'''<section id="flow-chamber" class="section flow-chamber-section" lang="en" dir="ltr"><div class="container flow-chamber" data-flow-chamber data-simulation-id="{esc(sim['id'])}" data-flow-model="{esc(model_json)}" data-a="{A}" data-nu="{nu}" data-t="{t}"><div class="flow-copy"><span class="eyebrow">EXACT REFERENCE FLOW</span><h2>Watch an equation become a velocity field.</h2><p class="lede small">This chamber is an analytic two-dimensional periodic Navier-Stokes solution, rendered directly from its canonical expression tree. It is a reference flow, not a reconstruction of the 2026 three-dimensional singularity.</p><p class="flow-tracer-note" data-flow-tracer-note>The arrow field and reported energy are exact evaluations of the canonical solution. Animated dots, when enabled, are numerically integrated passive tracers for orientation only and are not proof data.</p><p class="source-line"><a href="{esc(source['url'])}">{esc(source['title'])}</a></p><div class="flow-formulas"><code>u_x = {esc(ux)}</code><code>u_y = {esc(uy)}</code><code>E_mean = {esc(ee)}</code></div><div class="flow-controls enhance-only" data-flow-controls hidden><label for="flow-time">Time <output data-flow-t-output>{t:.2f}</output><input id="flow-time" type="range" min="{params['t']['min']}" max="{params['t']['max']}" value="{t}" step="{params['t']['step']}" data-flow-t></label><label for="flow-nu">Viscosity nu <output data-flow-nu-output>{nu:.3f}</output><input id="flow-nu" type="range" min="{params['nu']['min']}" max="{params['nu']['max']}" value="{nu}" step="{params['nu']['step']}" data-flow-nu></label><button type="button" data-flow-play data-play-label="Play" data-pause-label="Pause">Play</button></div><p class="flow-state" data-flow-state aria-live="polite">At t={t:.2f}, nu={nu:.3f}, the mean kinetic energy is {energy:.4f}. The field has {esc(sim['qualitative_default'])}; {esc(sim['invariants'][0])}.</p></div><div class="flow-visual"><div class="flow-canvas-frame enhance-only" data-flow-canvas-frame hidden><canvas width="720" height="460" data-flow-canvas aria-hidden="true"></canvas><div class="flow-axis-label x">x from 0 to 2pi</div><div class="flow-axis-label y">y</div></div><figure class="flow-static"><figcaption>Static no-JavaScript velocity-direction field at the default state</figcaption><pre data-flow-static>{esc(fallback)}</pre></figure></div></div><div class="container flow-integrity"><span>Canonical expression AST</span><span>Periodic domain</span><span>No autoplay</span><span>Static fallback</span><span>Independent residual oracle</span></div></section>'''

def science_visual(loc,compact=False):
    if not compact:
        return ''
    return f'''<figure class="equation-object compact"><div class="equation-kicker">INCOMPRESSIBLE NAVIER-STOKES</div>{equation_block()}<figcaption>Exact equation form used by this site's public model.</figcaption></figure>'''

def mission_card(page,loc,m,heading=3):
    L=locales[loc]; t=mission_text(loc,m)
    search=' '.join([t['title'],t['summary'],t['question'],m['category'],cat_label(loc,m['category']),m['level']]+[contrib_label(loc,x) for x in m['contributors']])
    href=rel(page,logical_target(loc,'mission',m['slug']))
    people=' · '.join(contrib_label(loc,x) for x in m['contributors'][:2])
    en_attrs=canonical_english_attrs(loc)
    return f'''<article class="mission-entry" data-mission-card data-category="{esc(m['category'])}" data-search="{esc(search)}" data-reveal><a class="mission-entry-link" href="{esc(href)}"><span class="mission-entry-id">{esc(m['id'])}</span><span class="mission-entry-main"{en_attrs}><span class="mission-entry-title">{esc(t['title'])}</span><span class="mission-entry-summary">{esc(t['summary'])}</span></span><span class="mission-entry-meta"{en_attrs}><span>{esc(cat_label(loc,m['category']))}</span><span>{esc(level_label(loc,m['level']))}</span><span>{esc(people)}</span></span><span class="mission-entry-arrow" aria-hidden="true">↗</span></a></article>'''

def canonical_shell(page:Path,current:str,kind:str,title:str,description:str,body:str):
    loc='en'; L=locales['en']; asset_css=rel(page,'assets/style.css'); asset_js=rel(page,'assets/site.js')
    links=[
      ('home','Home','en/index.html'),('missions','Missions','en/missions/index.html'),('quests','Quests','en/quests/index.html'),
      ('sprint','Founding Sprint','en/sprint/index.html'),('activity','Contributions','en/activity/index.html'),
      ('contribute','Contribute','en/contribute/index.html'),('governance','Governance','en/governance/index.html'),('agents','For AI agents','en/agents/index.html')]
    navlinks=''.join(f'<a class="nav-link" href="{esc(rel(page,target))}"'+(' aria-current="page"' if current==key else '')+f'>{esc(label)}</a>' for key,label,target in links)
    root_href=rel(page,'index.html')
    canon_items=navlinks+f'<a class="nav-link" href="{esc(root_href)}">Languages</a>'
    header=f'''<header class="site-header"><div class="container header-row">{brand(page,'en')}<nav class="nav-wrap nav-desktop" aria-label="Main menu">{canon_items}</nav><details class="mobile-nav"><summary>Main menu</summary><nav class="nav-wrap nav-mobile-panel" aria-label="Main menu">{canon_items}</nav></details></div></header>'''
    canonical=''
    if SITE_URL:
        relurl=page.relative_to(PUBLIC).as_posix().replace('index.html','')
        canonical=f'<link rel="canonical" href="{esc(SITE_URL+"/"+relurl)}">'
    return f'''<!doctype html><html lang="en" dir="ltr" data-theme="system"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><title>{esc(title)} · Navier-Stokes Commons</title><meta name="description" content="{esc(description)}">{SECURITY_META}<meta name="color-scheme" content="light dark">{canonical}<link rel="stylesheet" href="{esc(asset_css)}"></head><body data-page-kind="{esc(kind)}"><a class="skip-link" href="#main">Skip to main content</a>{header}<main id="main">{body}</main>{footer(page,'en')}<script src="{esc(asset_js)}" defer></script></body></html>'''

def quest_issue_url(q):
    return repo_issue('claim_quest.yml',f'[Quest attempt] {q["id"]} {q["title"]}')

def quest_card(page,q,heading=3,compact=False):
    rung=rung_by_id[q['rung']]; href=rel(page,f'en/quests/{q["id"].lower()}/index.html')
    flags=[]
    if q.get('founding_sprint'): flags.append('Founding Sprint')
    if q.get('priority')=='launch': flags.append('launch priority')
    flag=' · '.join(flags)
    meta=f'''<span>{esc(q['rung'])} {esc(rung['name'])}</span><span>{esc(rung['effort'])}</span><span>{esc(q['review']['class'])}</span>'''
    extra=f'<span class="quest-flag">{esc(flag)}</span>' if flag else ''
    summary='' if compact else f'<p>{esc(q["summary"])}</p>'
    return f'''<article class="quest-card" data-quest-card data-rung="{esc(q['rung'])}" data-mission="{esc(q['mission_id'])}"><div class="quest-card-top"><code>{esc(q['id'])}</code>{extra}</div><h{heading}><a href="{esc(href)}">{esc(q['title'])}</a></h{heading}>{summary}<div class="quest-meta">{meta}</div></article>'''

def mission_quests(page,m):
    rows=[q for q in quests if q['mission_id']==m['id'] and q['status']=='open']
    if not rows: return '<p class="empty-record" lang="en" dir="ltr">No bounded quest is currently open for this mission.</p>'
    return '<div class="quest-grid" lang="en" dir="ltr">'+''.join(quest_card(page,q,heading=3,compact=True) for q in rows)+'</div>'

def quests_page():
    page=PUBLIC/'en/quests/index.html'; groups=[]
    for rung in task_ladder['rungs']:
        qs=[q for q in quests if q['status']=='open' and q['rung']==rung['id']]
        cards=''.join(quest_card(page,q) for q in qs)
        groups.append(f'''<section class="quest-rung" id="{esc(rung['id'].lower())}"><div class="quest-rung-head"><div><span class="eyebrow">{esc(rung['id'])} · {esc(rung['name'])}</span><h2>{esc(rung['effort'])}</h2><p>{esc(rung['scope'])}</p></div><p class="section-side-note">{len(qs)} open</p></div><div class="quest-grid">{cards}</div></section>''')
    sprint_href=rel(page,registry['human_routes']['founding_sprint'].lstrip('/'))
    body=f'''<section class="page-hero"><div class="container page-hero-grid"><div><span class="eyebrow">OPEN BETA · {len(quests)} BOUNDED QUESTS</span><h1>Choose work you can finish and defend.</h1><p class="lede">Quests turn the {len(missions)} research missions into independently checkable units from a 15-minute source check to frontier research. Starting one is non-exclusive.</p><div class="actions"><a class="button" href="{esc(sprint_href)}">Enter the Founding Sprint</a><a class="button secondary" href="#l0">Browse from L0</a></div></div><aside class="plain-aside"><h2>Six-rung ladder</h2><p>Difficulty is an expected scope estimate, not a prestige score. Pick the smallest quest that genuinely advances the mission.</p><p><strong>Acceptance first:</strong> read the deliverables, acceptance checks, dependencies, and reviewer requirements before starting.</p></aside></div></section><section class="section"><div class="container">{''.join(groups)}</div></section>'''
    write('en/quests/index.html',canonical_shell(page,'quests','quests','Open quests','Bounded public Navier-Stokes tasks for humans and AI agents.',body))

def quest_page(q):
    page=PUBLIC/f'en/quests/{q["id"].lower()}/index.html'; m=mission_by_id[q['mission_id']]; rung=rung_by_id[q['rung']]
    deliver=''.join(f'<li>{esc(x)}</li>' for x in q['deliverables']); accept=''.join(f'<li><span class="check-box" aria-hidden="true">□</span><span>{esc(x)}</span></li>' for x in q['acceptance'])
    deps=''.join(f'<li><a href="{esc(rel(page,f"en/quests/{d.lower()}/index.html"))}"><code>{esc(d)}</code> {esc(quest_by_id[d]["title"])}</a></li>' for d in q.get('dependencies',[])) or '<li>None.</li>'
    src=source_links(q['source_ids'],page) if q.get('source_ids') else 'No external source is required for the task as scoped.'
    claim_links=', '.join(f'<code>{esc(c)}</code>' for c in q.get('claim_ids',[])) or 'None directly.'
    benchmark_html=''
    if q.get('benchmark_set_id'):
        bhref=rel(page,registry['human_routes']['benchmarks'].lstrip('/')+'index.html')
        benchmark_html=f'<h3>Pre-registered benchmark corpus</h3><p><a href="{esc(bhref)}"><code>{esc(q["benchmark_set_id"])}</code> reference set</a></p>'
    start=quest_issue_url(q); start_html=f'<a class="button" href="{esc(start)}">Start non-exclusive attempt</a>' if start else f'<a class="button" href="{esc(rel(page,"CONTRIBUTING.md"))}">Contribution instructions</a>'
    mission_href=rel(page,f'en/missions/{m["slug"]}/index.html')
    result=repo_issue('submit_result.yml',f'[Result] {q["id"]}'); review=repo_issue('review.yml',f'[Review] {q["id"]}')
    body=f'''<section class="mission-hero"><div class="container"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="{esc(rel(page,registry['human_routes']['quests'].lstrip('/')))}">Quests</a><span>/</span><span aria-current="page">{esc(q['id'])}</span></nav><div class="quest-title-grid"><div><div class="meta"><span class="status open"><span class="signal-dot" aria-hidden="true"></span>Open quest</span><span class="field-chip">{esc(q['rung'])} {esc(rung['name'])}</span>{'<span class="field-chip">Founding Sprint</span>' if q.get('founding_sprint') else ''}</div><h1>{esc(q['title'])}</h1><p class="lede">{esc(q['summary'])}</p></div><aside class="quest-glance"><strong>{esc(rung['effort'])}</strong><span>{esc(rung['scope'])}</span></aside></div></div></section><section class="section"><div class="container mission-layout"><article class="mission-main"><section class="mission-block"><span class="section-number">01</span><div><h2>Task</h2><p class="question-text">{esc(q['task'])}</p><p>Parent mission: <a href="{esc(mission_href)}"><code>{esc(m['id'])}</code> {esc(m['title'])}</a></p></div></section><section class="mission-block"><span class="section-number">02</span><div><h2>Deliverables</h2><ul class="plain-list">{deliver}</ul></div></section><section class="mission-block acceptance-block"><span class="section-number">03</span><div><h2>Acceptance checks</h2><ol class="accept-list">{accept}</ol></div></section><section class="mission-block"><span class="section-number">04</span><div><h2>Review gate</h2><dl class="glance-list"><div><dt>Class</dt><dd>{esc(q['review']['class'])}</dd></div><div><dt>Independence</dt><dd>{esc(q['review']['independence'])}</dd></div><div><dt>Required expertise</dt><dd>{esc(q['review']['required_expertise'])}</dd></div></dl></div></section><section class="mission-block"><span class="section-number">05</span><div><h2>Dependencies and evidence</h2><h3>Dependencies</h3><ul class="plain-list">{deps}</ul><h3>Sources</h3><p class="source-line">{src}</p><h3>Claim records affected</h3><p>{claim_links}</p>{benchmark_html}</div></section><section class="mission-block take-part-block" id="take-part"><span class="section-number">06</span><div><h2>Start or review this quest</h2><p>Attempts are non-exclusive. Another contributor may independently attempt the same quest.</p><div class="actions">{start_html}{f'<a class="button secondary" href="{esc(result)}">Submit result</a>' if result else ''}{f'<a class="button ghost" href="{esc(review)}">Review or falsify</a>' if review else ''}</div></div></section></article><aside class="mission-aside"><h2>At a glance</h2><dl class="glance-list"><div><dt>Quest</dt><dd><code>{esc(q['id'])}</code></dd></div><div><dt>Mission</dt><dd><code>{esc(q['mission_id'])}</code></dd></div><div><dt>Rung</dt><dd>{esc(q['rung'])} {esc(rung['name'])}</dd></div><div><dt>Effort</dt><dd>{esc(rung['effort'])}</dd></div><div><dt>Parallel safe</dt><dd>{'yes' if q.get('parallel_safe') else 'coordinate first'}</dd></div><div><dt>Exclusive</dt><dd>no</dd></div></dl></aside></div></section>'''
    write(f'en/quests/{q["id"].lower()}/index.html',canonical_shell(page,'quests','quest',q['title'],q['summary'],body))

def sprint_page():
    page=PUBLIC/'en/sprint/index.html'; qs=[quest_by_id[x] for x in founding_sprint['quest_ids']]; cards=''.join(quest_card(page,q) for q in qs); cond=''.join(f'<li>{esc(x)}</li>' for x in founding_sprint['success_conditions'])
    body=f'''<section class="page-hero"><div class="container page-hero-grid"><div><span class="eyebrow">{esc(founding_sprint['id'])} · OPEN</span><h1>{esc(founding_sprint['title'])}</h1><p class="lede">{esc(founding_sprint['purpose'])}</p><p class="page-note">The sprint begins with publication. Its outputs strengthen the evidence state; they are not prerequisites for opening the workspace.</p></div><aside class="metric-panel"><div><strong>{len(qs)}</strong><span>launch quests</span></div><div><strong>{len(set(q['mission_id'] for q in qs))}</strong><span>missions represented</span></div></aside></div></section><section class="section"><div class="container"><span class="eyebrow">SUCCESS CONDITIONS</span><h2>What makes the sprint substantive</h2><ol class="plain-list">{cond}</ol></div></section><section class="section"><div class="container"><div class="section-head"><div><span class="eyebrow">START NOW</span><h2>Founding quests</h2></div><a class="text-link strong" href="{esc(rel(page,'en/quests/index.html'))}">All quests ↗</a></div><div class="quest-grid">{cards}</div></div></section>'''
    write('en/sprint/index.html',canonical_shell(page,'sprint','sprint',founding_sprint['title'],founding_sprint['purpose'],body))

def governance_page():
    page=PUBLIC/'en/governance/index.html'; role_html=[]
    for r in governance['roles']:
        powers=''.join(f'<li>{esc(x)}</li>' for x in r['powers']); restrictions=''.join(f'<li>{esc(x)}</li>' for x in r['restrictions'])
        role_html.append(f'''<article class="governance-role"><span class="micro">{esc(r['id'])}</span><h2>{esc(r['id'].replace('-',' ').title())}</h2><h3>May</h3><ul>{powers}</ul><h3>May not</h3><ul>{restrictions}</ul></article>''')
    rules=''.join(f'<div class="glossary-row"><dt>{esc(k.replace("_"," "))}</dt><dd>{esc(v)}</dd></div>' for k,v in governance['decision_rules'].items())
    body=f'''<section class="page-hero"><div class="container narrow"><span class="eyebrow">BOOTSTRAP OPEN BETA</span><h1>Governance that permits work without manufacturing authority.</h1><p class="lede">The repository owner can operate the beta, contributors can start immediately, and scientific status still depends on scoped independent review.</p></div></section><section class="section"><div class="container governance-grid">{''.join(role_html)}</div></section><section class="section"><div class="container"><span class="eyebrow">DECISION RULES</span><h2>Authority is typed by decision.</h2><dl class="glossary">{rules}</dl></div></section>'''
    write('en/governance/index.html',canonical_shell(page,'governance','governance','Governance','Bootstrap open-beta governance and review authority.',body))

def claims_page():
    page=PUBLIC/'en/claims/index.html'; rows=[]
    for c in claims_doc['claims']:
        src=source_links(c.get('source_ids',[]),page) if c.get('source_ids') else 'None.'
        rows.append(f'''<article class="claim-record"><div class="claim-record-top"><code>{esc(c['id'])}</code><span class="status-label">{esc(c['status'])}</span></div><h2>{esc(c['statement'])}</h2><p><strong>Type:</strong> {esc(c['type'])}</p><p class="source-line">{src}</p></article>''')
    vocab=''.join(f'<div class="glossary-row"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k,v in claims_doc['status_vocabulary'].items())
    body=f'''<section class="page-hero"><div class="container narrow"><span class="eyebrow">CLAIM AND EVIDENCE LEDGER</span><h1>Do not collapse source, derivation, reproduction, and review.</h1><p class="lede">Every status says what kind of warrant exists and what is still missing.</p></div></section><section class="section"><div class="container"><dl class="glossary">{vocab}</dl></div></section><section class="section"><div class="container claim-list">{''.join(rows)}</div></section>'''
    write('en/claims/index.html',canonical_shell(page,'claims','claims','Claim and evidence ledger','Public epistemic status of seed claims.',body))

def trust_strip(page,loc):
    L=locales[loc]; H=L['home_more']
    return f'''<section class="trust-strip"><div class="container trust-grid"><div><span class="eyebrow">{esc(H['trust_kicker'])}</span><h2>{esc(H['trust_title'])}</h2></div><p>{esc(H['trust_body'])}</p><div class="trust-links"><a href="{esc(rel(page,logical_target(loc,'known')))}">{esc(L['nav']['known'])}</a><a href="{esc(rel(page,logical_target(loc,'sources')))}">{esc(L['nav']['sources'])}</a></div></div></section>'''

def home_page(loc):
    L=locales[loc]; O=L['observatory']; page=PUBLIC/f'{loc}/index.html'
    preview=''.join(mission_card(page,loc,m) for m in missions[:6])
    facts=[(L['home']['fact1'],['openai-announcement']),(L['home']['fact2'],['openai-announcement','clay-formulation']),(L['home']['fact3'],['clay-formulation'])]
    fact_html=''.join(f'''<article class="evidence-row"><span class="evidence-index">0{i}</span><div><p>{esc(txt)}</p><p class="source-line">{source_links(ids,page)}</p></div></article>''' for i,(txt,ids) in enumerate(facts,1))
    guide_href=rel(page,logical_target(loc,'guide'))
    body=f'''<section class="hero theorem-hero"><div class="container theorem-hero-grid"><div class="hero-copy"><div class="eyebrow">NAVIER-STOKES COMMONS</div><h1>{esc(O['hero_title'])}</h1><p class="lede">{esc(O['hero_lede'])}</p><div class="hero-actions"><a class="button" lang="en" dir="ltr" href="{esc(rel(page,'en/sprint/index.html'))}">Join the Founding Sprint</a><a class="text-link strong" href="#scaling">{esc(O['explore'])}</a><a class="text-link" href="{esc(rel(page,logical_target(loc,'missions')))}">{esc(O['open_missions'])} <span aria-hidden="true">↗</span></a></div></div><aside class="hero-fact"><span class="micro">{esc(O['published_scale'])}</span><p><code>tau = 1 - t</code></p><p><code>ell_r ~ tau^(1/2)</code></p><p><code>ell_z ~ tau^(1/2-h)</code></p><p><code>|u_theta| ~ tau^(-1/2-h)</code></p><p><code>E_core ~ tau^(1/2-3h)</code></p><p class="source-line">{source_links(['openai-paper'],page)}</p></aside></div></section>
<section id="scaling" class="section observatory-section"><div class="container">{scaling_lab(page,loc)}</div></section>
{flow_chamber(page,loc)}
<section class="section evidence-section"><div class="container"><div class="section-head"><div><span class="eyebrow">{esc(O['what_public'])}</span><h2>{esc(O['facts_title'])}</h2><p>{esc(O['facts_body'])}</p></div><a class="text-link" href="{esc(rel(page,logical_target(loc,'sources')))}">{esc(O['sources'])} <span aria-hidden="true">↗</span></a></div><div class="evidence-list">{fact_html}</div></div></section>
<section class="section launch-sprint-strip"><div class="container invitation-grid" lang="en" dir="ltr"><div><span class="eyebrow">OPEN BETA · FOUNDING SPRINT</span><h2>Do not just read it. Pick one bounded quest and make the public record better.</h2></div><div><p>The Commons is open for non-exclusive attempts. Start with source checks, Lean reproduction, mathematics, numerical work, accessibility, browser testing, agent evaluation, or governance review.</p><div class="actions"><a class="button" href="{esc(rel(page,"en/sprint/index.html"))}">Founding Sprint</a><a class="text-link strong" href="{esc(rel(page,"en/quests/index.html"))}">All {len(quests)} quests <span aria-hidden="true">↗</span></a></div></div></div></section>
<section class="section mission-preview-section"><div class="container"><div class="section-head"><div><span class="eyebrow">{esc(L['section_labels']['open_frontier'])}</span><h2>{esc(L['missions']['title'])}</h2><p>{esc(O['mission_intro'])}</p></div><a class="text-link strong" href="{esc(rel(page,logical_target(loc,'missions')))}">{esc(O['view_all'])} <span aria-hidden="true">↗</span></a></div><div class="mission-list">{preview}</div></div></section>
<section class="section invitation-section"><div class="container invitation-grid"><div><span class="eyebrow">{esc(L['section_labels']['contribute'])}</span><h2>{esc(O['contribute_title'])}</h2></div><div><p>{esc(O['contribute_body'])}</p><div class="actions"><a class="button" href="{esc(rel(page,logical_target(loc,'contribute')))}">{esc(O['how_contribute'])}</a><a class="text-link" href="{esc(guide_href)}">{esc(O['how_works'])} <span aria-hidden="true">↗</span></a></div></div></div></section>'''
    write(f'{loc}/index.html',shell(page,loc,'home','home',O['hero_title'],O['hero_lede'],body))
def missions_page(loc):
    L=locales[loc]; M=L['mission_meta']; page=PUBLIC/f'{loc}/missions/index.html'
    groups=[]
    for cat in CATEGORY_ORDER:
        ms=[m for m in missions if m['category']==cat]
        if not ms: continue
        entries=''.join(mission_card(page,loc,m,heading=3) for m in ms)
        groups.append(f'''<section class="mission-group" id="field-{esc(cat)}" data-category-section="{esc(cat)}"><div class="mission-group-head"><span class="field-symbol" aria-hidden="true">{esc(str(CATEGORY_ORDER.index(cat)+1).zfill(2))}</span><div><h2>{esc(cat_label(loc,cat))}</h2><p>{len(ms)} · {esc(L['missions']['title'])}</p></div></div><div class="mission-list">{entries}</div></section>''')
    jumps=''.join(f'<a href="#field-{esc(cat)}">{esc(cat_label(loc,cat))}</a>' for cat in CATEGORY_ORDER if any(m['category']==cat for m in missions))
    chips=f'<button type="button" class="filter-chip is-active" data-category-filter="all">{esc(M["filter_all"])}</button>'+''.join(f'<button type="button" class="filter-chip" data-category-filter="{esc(cat)}">{esc(cat_label(loc,cat))}</button>' for cat in CATEGORY_ORDER if any(m['category']==cat for m in missions))
    body=f'''<section class="page-hero compact-hero"><div class="container page-hero-grid"><div><span class="eyebrow">{esc(L['section_labels']['open_frontier'])} · {len(missions)}</span><h1>{esc(L['missions']['title'])}</h1><p class="lede">{esc(L['missions']['lede'])}</p><p class="page-note" lang="en" dir="ltr">Each mission is an open public question with explicit acceptance checks. Starting one is non-exclusive.</p></div>{science_visual(loc,compact=True)}</div></section>
<section class="section mission-index"><div class="container"><nav class="category-jump" aria-label="{esc(M['category_jump'])}"><span>{esc(M['category_jump'])}</span>{jumps}</nav><div class="filter-panel enhance-only" data-filter-panel hidden><div class="search-wrap"><label for="mission-filter">{esc(L['missions']['search_label'])}</label><input id="mission-filter" data-mission-filter type="search" autocomplete="off" placeholder="{esc(L['missions']['search_placeholder'])}"></div><div class="filter-chips" aria-label="{esc(L['missions']['category'])}">{chips}</div><div class="filter-status" data-filter-status aria-live="polite"></div></div><p data-no-results hidden>{esc(L['missions']['no_results'])}</p>{''.join(groups)}</div></section>'''
    write(f'{loc}/missions/index.html',shell(page,loc,'missions','missions',L['missions']['title'],L['missions']['lede'],body))

def mission_page(loc,m):
    L=locales[loc]; M=L['mission_meta']; t=mission_text(loc,m); page=PUBLIC/f'{loc}/missions/{m["slug"]}/index.html'
    en_attrs=canonical_english_attrs(loc)
    starts=[]
    for sp in m['starting_points']:
        src=''
        if sp.get('source_ids'): src=f'<div class="source-line">{source_links(sp["source_ids"],page)}</div>'
        label=M['sourced_fact'] if sp['kind']=='sourced_fact' else M['reasoning_guard']
        cls='fact' if sp['kind']=='sourced_fact' else 'guard'
        starts.append(f'<article class="starting-card {cls}" data-reveal><span class="micro">{esc(label)}</span><p lang="en" dir="ltr">{esc(sp["text"])}</p>{src}</article>')
    accept=''.join(f'<li lang="en" dir="ltr"><span class="check-box" aria-hidden="true">□</span><span>{esc(x)}</span></li>' for x in m['acceptance'])
    contributors=''.join(f'<span class="person-chip">{esc(contrib_label(loc,x))}</span>' for x in m['contributors'])
    action=''
    attempt=repo_issue('open_attempt.yml',f'[Attempt] {m["id"]} {m["title"]}')
    result=repo_issue('submit_result.yml',f'[Result] {m["id"]}')
    review=repo_issue('review.yml',f'[Review] {m["id"]}')
    if attempt:
        action=f'<div class="actions"><a class="button" href="{esc(attempt)}">{esc(L["contribute"]["attempt"])}<span aria-hidden="true">↗</span></a><a class="button secondary" href="{esc(result)}">{esc(L["contribute"]["result"])}</a><a class="button ghost" href="{esc(review)}">{esc(L["contribute"]["review"])}</a></div>'
    else: action=f'<p class="callout">{esc(L["contribute"]["repo_missing"])}</p>'
    related=[x for x in missions if x['id']!=m['id'] and x['category']==m['category']][:3]
    if len(related)<3:
        related += [x for x in missions if x['id']!=m['id'] and x not in related][:3-len(related)]
    rel_cards=''.join(mission_card(page,loc,x,heading=3) for x in related)
    sidebar=f'''<aside class="mission-aside" aria-label="{esc(M['at_a_glance'])}"><h2>{esc(M['at_a_glance'])}</h2><dl class="glance-list"><div><dt>{esc(M['status'])}</dt><dd><span class="status open"><span class="signal-dot" aria-hidden="true"></span>{esc(L['status_open'])}</span></dd></div><div><dt>{esc(M['field'])}</dt><dd>{esc(cat_label(loc,m['category']))}</dd></div><div><dt>{esc(M['level'])}</dt><dd>{esc(level_label(loc,m['level']))}</dd></div><div><dt>{esc(M['mission_id'])}</dt><dd><code dir="ltr">{esc(m['id'])}</code></dd></div><div><dt>{esc(M['sources'])}</dt><dd>{len(m['source_ids'])}</dd></div><div><dt>{esc(M['criteria'])}</dt><dd>{len(m['acceptance'])}</dd></div></dl><a class="button aside-button" href="#take-part">{esc(M['take_part'])}</a></aside>'''
    body=f'''<section class="mission-hero"><div class="container"><nav class="breadcrumb" aria-label="{esc(L['section_labels']['breadcrumb'])}"><a href="{esc(rel(page,logical_target(loc,'missions')))}">{esc(L['nav']['missions'])}</a><span aria-hidden="true">/</span><span aria-current="page">{esc(m['id'])}</span></nav><div class="mission-title-row"><div><div class="meta"><span class="status open"><span class="signal-dot" aria-hidden="true"></span>{esc(L['status_open'])}</span><span class="field-chip"{en_attrs}>{esc(cat_label(loc,m['category']))}</span><span class="level-chip"{en_attrs}>{esc(level_label(loc,m['level']))}</span></div><h1{en_attrs}>{esc(t['title'])}</h1><p class="lede"{en_attrs}>{esc(t['summary'])}</p><p class="open-notice"><span class="signal-dot" aria-hidden="true"></span>{esc(L['not_claim'])}</p></div></div></div></section>
<section class="section mission-body"><div class="container mission-layout"><article class="mission-main"><section class="mission-block question-block" data-reveal><span class="section-number">01</span><div><h2>{esc(L['missions']['question'])}</h2><p class="question-text"{en_attrs}>{esc(t['question'])}</p></div></section><section class="mission-block" data-reveal><span class="section-number">02</span><div><h2>{esc(M['public_evidence'])}</h2><p class="section-intro">{esc(L['missions']['canonical_note']) if loc!='en' else esc(L['known']['lede'])}</p><div class="starting-grid">{''.join(starts)}</div></div></section><section class="mission-block acceptance-block" data-reveal><span class="section-number">03</span><div><h2>{esc(L['missions']['acceptance'])}</h2><p>{esc(L['missions']['canonical_note'])}</p><div class="canonical"><span class="canonical-label">{esc(L['canonical_english'])}</span><ol class="accept-list">{accept}</ol></div></div></section><section class="mission-block" data-reveal><span class="section-number">04</span><div><h2>{esc(M['audience_fit'])}</h2><div class="people-list">{contributors}</div></div></section><section class="mission-block" data-reveal><span class="section-number">05</span><div><h2>{esc(L['missions']['sources'])}</h2><div class="mini-source-list">{''.join(source_card(page,loc,source_by_id[sid],heading=3) for sid in m['source_ids'])}</div></div></section><section class="mission-block" data-reveal><span class="section-number">06</span><div lang="en" dir="ltr"><h2>Open quests</h2><p>Bounded tasks attached to this mission. Start the smallest one whose acceptance checks you can satisfy.</p>{mission_quests(page,m)}</div></section><section class="mission-block" data-reveal><span class="section-number">07</span><div><h2>{esc(L["nav"].get("activity","Contributions"))}</h2>{mission_contributions(page,loc,m)}</div></section><section class="mission-block take-part-block" id="take-part" data-reveal><span class="section-number">08</span><div><h2>{esc(M['take_part'])}</h2><p>{esc(L['contribute']['lede'])}</p>{action}</div></section></article>{sidebar}</div></section>
<section class="section related-section"><div class="container"><div class="section-head"><div><span class="eyebrow">{esc(L['section_labels']['related'])}</span><h2>{esc(M['related'])}</h2></div></div><div class="mission-grid">{rel_cards}</div></div></section>'''
    write(f'{loc}/missions/{m["slug"]}/index.html',shell(page,loc,'missions','mission',t['title'],t['summary'],body,m['slug']))

def contribution_card(page,loc,c):
    title=c.get('title') or c.get('id','Contribution')
    summary=c.get('summary','')
    role=c.get('contribution_type','contribution')
    actor=c.get('contributor',{}).get('display_name','Public contributor')
    url=c.get('artifact_url') or c.get('review_url') or ''
    t=f'<a href="{esc(url)}">{esc(title)}</a>' if url else esc(title)
    return f'<article class="contribution-record"><div class="contribution-meta"><span>{esc(role)}</span><span>{esc(actor)}</span></div><h3>{t}</h3><p>{esc(summary)}</p></article>'

def mission_contributions(page,loc,m):
    rows=[c for c in contributions if c.get('status')=='accepted' and c.get('mission_id')==m['id']]
    if not rows:
        return '<p class="empty-record">No accepted public contribution is recorded for this mission yet.</p>'
    return '<div class="contribution-list">'+''.join(contribution_card(page,loc,c) for c in rows)+'</div>'

def activity_page(loc):
    L=locales[loc]; page=PUBLIC/f'{loc}/activity/index.html'
    rows=[c for c in contributions if c.get('status')=='accepted']
    cards=''.join(contribution_card(page,loc,c) for c in rows) if rows else '<p class="empty-record">No accepted public contributions have been published yet.</p>'
    title=L['nav'].get('activity','Contributions')
    body=f'<section class="page-hero compact-hero"><div class="container"><span class="eyebrow">{esc(L['section_labels']['public_record'])}</span><h1>{esc(title)}</h1><p class="lede">Accepted contributions are generated from canonical public contribution manifests after review and merge.</p></div></section><section class="section"><div class="container contribution-list">{cards}</div></section>'
    write(f'{loc}/activity/index.html',shell(page,loc,'activity','activity',title,title,body))

def known_page(loc):
    L=locales[loc]; page=PUBLIC/f'{loc}/known/index.html'
    facts=[(L['home']['fact1'],['openai-announcement']),(L['home']['fact2'],['openai-announcement','clay-formulation']),(L['home']['fact3'],['clay-formulation']),(L['home']['fact4'],['openai-lean'])]
    items=''.join(f'<article class="evidence-card large" data-reveal><span class="evidence-index">0{i}</span><span class="micro">{esc(L["known"]["claim_label"])}</span><p>{esc(txt)}</p><p class="source-line">{source_links(ids,page)}</p></article>' for i,(txt,ids) in enumerate(facts,1))
    branches=f'''<div class="branch-diagram" aria-label="{esc(L['known']['branch_aria'])}"><div class="branch-root"><span>{esc(L['known']['branch_root'])}</span></div><div class="branch-columns"><div><strong>{esc(L['known']['branch_ab'])}</strong><span>{esc(L['known']['branch_unforced'])}</span><small>{esc(L['home']['fact3'])}</small></div><div><strong>{esc(L['known']['branch_cd'])}</strong><span>{esc(L['known']['branch_forced'])}</span><small>{esc(L['home']['fact2'])}</small></div></div></div>'''
    body=f'''<section class="page-hero"><div class="container page-hero-grid"><div><span class="eyebrow">{esc(L['section_labels']['public_record'])}</span><h1>{esc(L['known']['title'])}</h1><p class="lede">{esc(L['known']['lede'])}</p></div>{branches}</div></section><section class="section"><div class="container evidence-grid two">{items}</div></section><section class="section caution-section"><div class="container caution-card"><span class="eyebrow">{esc(L['section_labels']['boundary'])}</span><div><h2>{esc(L['known']['caution_title'])}</h2><p>{esc(L['known']['caution_body'])}</p></div></div></section>'''
    write(f'{loc}/known/index.html',shell(page,loc,'known','known',L['known']['title'],L['known']['lede'],body))

def contribute_page(loc):
    L=locales[loc]; page=PUBLIC/f'{loc}/contribute/index.html'
    steps=''.join(f'<li><span class="pipeline-index">0{i}</span><span>{esc(x)}</span></li>' for i,x in enumerate(L['contribute']['steps'],1))
    choices=[]
    urls=[
      ('claim_quest.yml','Start a quest','[Quest attempt] ','Choose a bounded quest and declare a non-exclusive attempt against its exact acceptance checks.'),
      ('open_attempt.yml',L['contribute']['attempt'],'[Attempt] ','Declare a non-exclusive route and what you intend to try when no existing quest fits.'),
      ('side_quest.yml',L['contribute']['sidequest'],'[Side quest] ','Propose a new well-scoped public question with evidence and acceptance checks.'),
      ('submit_result.yml',L['contribute']['result'],'[Result] ','Submit a public proof, analysis, dataset, implementation, review, or negative result.'),
      ('review.yml',L['contribute']['review'],'[Review] ','Reproduce, challenge, falsify, translate, or independently review existing work.'),
    ]
    for i,(tmpl,label,title,desc) in enumerate(urls,1):
        u=repo_issue(tmpl,title)
        href=u or rel(page,'CONTRIBUTING.md')
        choices.append(f'<a class="contribution-choice" href="{esc(href)}"><span class="choice-index">0{i}</span><span><strong>{esc(label)}</strong><small lang="en" dir="ltr">{esc(desc)}</small></span><span aria-hidden="true">↗</span></a>')
    worked=rel(page,logical_target(loc,'guide'))+'#worked-example'
    body=f'''<section class="page-hero"><div class="container narrow"><span class="eyebrow">{esc(L['section_labels']['open_participation'])}</span><h1>{esc(L['contribute']['title'])}</h1><p class="lede">{esc(L['contribute']['lede'])}</p><p class="page-note" lang="en" dir="ltr">You do not need to be a PDE specialist to participate. The mission page says what counts as success; the submission records what you actually did.</p></div></section>
<section class="section"><div class="container"><div class="section-head"><div><span class="eyebrow">01 · {esc(L['section_labels']['process'])}</span><h2 lang="en" dir="ltr">Choose a contribution path</h2></div><p class="section-side-note">{esc(forge_label())}</p></div><div class="contribution-choices">{''.join(choices)}</div></div></section>
<section class="section"><div class="container pipeline-layout"><div><span class="eyebrow">02 · {esc(L['section_labels']['composition'])}</span><h2>{esc(locales[loc]['home_more']['pipeline_title'])}</h2><p>{esc(locales[loc]['home_more']['pipeline_lede'])}</p></div><ol class="pipeline-list">{steps}</ol></div></section>
<section class="section"><div class="container split-layout"><div><span class="eyebrow">03 · {esc(L['section_labels']['side_quests'])}</span><h2>{esc(L['contribute']['sidequest'])}</h2><p>{esc(L['missions']['lede'])}</p><p>{esc(L['not_claim'])}</p></div><aside class="plain-aside" lang="en" dir="ltr"><h2>See a finished example</h2><p>A worked example shows the difference between an attempt, an artifact, evidence, a review, and an accepted public record.</p><a class="text-link strong" href="{esc(worked)}">Open the worked example <span aria-hidden="true">↗</span></a></aside></div></section>'''
    write(f'{loc}/contribute/index.html',shell(page,loc,'contribute','contribute',L['contribute']['title'],L['contribute']['lede'],body))

def guide_page(loc):
    L=locales[loc]; page=PUBLIC/f'{loc}/guide/index.html'
    title=L['nav'].get('guide','How this works')
    terms=[
      ('Mission','A public research question with sources, scope, suggested contributor types, and explicit acceptance checks.'),
      ('Attempt','A non-exclusive declaration that someone is working on a mission. Other independent attempts remain allowed.'),
      ('Artifact','The thing produced: a proof, formalization, dataset, program, numerical experiment, review, translation, design, or documented negative result.'),
      ('Evidence','The reproducible material showing what the artifact establishes and what it does not establish.'),
      ('Review','Independent checking, reproduction, criticism, falsification, source correction, or domain review.'),
      ('Accepted record','A reviewed contribution merged into canonical public data. The site then republishes it automatically.'),
    ]
    glossary=''.join(f'<div class="glossary-row"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k,v in terms)
    example='''<ol class="worked-example"><li><strong>Mission:</strong> independently reproduce the pinned Lean certificate.</li><li><strong>Attempt:</strong> a contributor declares a clean-room reproduction on the exact published commit.</li><li><strong>Artifact:</strong> build logs, environment manifest, axiom report, and semantic mapping notes.</li><li><strong>Evidence:</strong> commands and hashes let another person reproduce the same result.</li><li><strong>Review:</strong> an independent Lean/PDE reviewer checks the build and the statement correspondence.</li><li><strong>Accepted record:</strong> the contribution manifest is merged; mission and activity pages update automatically.</li></ol>'''
    body=f'''<section class="page-hero"><div class="container narrow"><span class="eyebrow">START HERE</span><h1>{esc(title)}</h1><p class="lede" lang="en" dir="ltr">This site is a public coordination layer around explicit Navier–Stokes questions. It does not ask visitors to trust a single verdict; it exposes what is known, what is still open, what would count as progress, and where the evidence lives.</p></div></section>
<section class="section"><div class="container guide-layout" lang="en" dir="ltr"><div><span class="eyebrow">01 · PRODUCT</span><h2>What can you actually do here?</h2><p>Read the public evidence, choose a mission, work alone or with an AI agent, submit a result or a criticism, propose a new side quest, or help explain and translate accepted work.</p><p>No mission grants exclusive ownership. Negative results and falsifications are legitimate contributions when they close a route or clarify scope.</p></div><aside class="plain-aside"><h2>Who is this for?</h2><ul class="plain-list"><li>PDE and analysis researchers</li><li>Lean/formal-methods contributors</li><li>Numerical and CFD researchers</li><li>{esc(capabilities()["student_entry_path"]["statement"])}</li><li>Designers, educators, translators, historians, economists and other specialists</li><li>Autonomous agents operating under public provenance rules</li></ul></aside></div></section>
<section class="section"><div class="container" lang="en" dir="ltr"><span class="eyebrow">02 · GLOSSARY</span><h2>The six words you need</h2><dl class="glossary">{glossary}</dl></div></section>
<section class="section" id="worked-example"><div class="container narrow" lang="en" dir="ltr"><span class="eyebrow">03 · WORKED EXAMPLE</span><h2>What a completed contribution looks like</h2><p>The example is intentionally procedural: it shows how public work becomes reusable without pretending that every artifact is automatically correct.</p>{example}</div></section>'''
    write(f'{loc}/guide/index.html',shell(page,loc,'guide','guide',title,'How Navier–Stokes Commons works for humans and AI agents.',body))

def sources_page(loc):
    L=locales[loc]; page=PUBLIC/f'{loc}/sources/index.html'
    rows=''.join(source_card(page,loc,s,heading=2) for s in sources)
    pinned=sum(1 for s in sources if s.get('reference_type')=='immutable-git-commit')
    body=f'''<section class="page-hero compact-hero"><div class="container page-hero-grid"><div><span class="eyebrow">{esc(L['section_labels']['provenance_ledger'])}</span><h1>{esc(L['sources']['title'])}</h1><p class="lede">{esc(L['sources']['lede'])}</p></div><div class="metric-panel"><div><strong>{len(sources)}</strong><span>{esc(L['sources']['title'])}</span></div><div><strong>{pinned}</strong><span>{esc(L['source_meta']['immutable'])}</span></div></div></div></section><section class="section"><div class="container source-ledger">{rows}</div></section>'''
    write(f'{loc}/sources/index.html',shell(page,loc,'sources','sources',L['sources']['title'],L['sources']['lede'],body))

def agents_page(loc):
    L=locales[loc]; page=PUBLIC/f'{loc}/agents/index.html'
    how=''.join(f'<li><span class="pipeline-index">0{i}</span><span>{esc(x)}</span></li>' for i,x in enumerate(L['agents']['how'],1))
    endpoint_keys=['quests','frontier','claims','task_ladder','taxonomy','sources','governance','founding_sprint','reviews','project_metadata','scaling_model','formulas','simulations','actions','reference_benchmarks','capabilities','authority_map','llms_index','llms_full','agent_start','agent_skill','discovery']
    endpoints=[(key,registry['machine_endpoints'][key].lstrip('/')) for key in endpoint_keys]
    eps=''.join(f'<li><a class="endpoint" href="{esc(rel(page,target))}"><code>{esc(name)}</code><span aria-hidden="true">↗</span></a></li>' for name,target in endpoints)
    discovery_route=registry['machine_endpoints']['discovery']
    starter_rung=next((r['id'] for r in task_ladder['rungs'] if r.get('starter')), task_ladder['rungs'][0]['id'])
    body=f'''<section class="page-hero"><div class="container page-hero-grid"><div><span class="eyebrow">{esc(L['section_labels']['machine_surface'])}</span><h1>{esc(L['agents']['title'])}</h1><p class="lede">{esc(L['agents']['lede'])}</p></div><div class="terminal-card" aria-hidden="true"><div class="terminal-bar"><span></span><span></span><span></span></div><code>$ fetch {esc(discovery_route)}<br>&gt; {len(missions)} missions · {len(quests)} quests<br>$ select --rung={esc(starter_rung)} --capability="..."</code></div></div></section><section class="section"><div class="container split-layout"><div><h2>{esc(locales[loc]['home_more']['pipeline_title'])}</h2><ol class="pipeline-list vertical">{how}</ol></div><aside><h2>{esc(L['agents']['machine'])}</h2><ul class="endpoint-list">{eps}</ul></aside></div></section><section class="section caution-section"><div class="container caution-card"><span class="eyebrow">{esc(L['section_labels']['boundary'])}</span><div><p>{esc(L['not_claim'])}</p></div></div></section>'''
    write(f'{loc}/agents/index.html',shell(page,loc,'agents','agents',L['agents']['title'],L['agents']['lede'],body))

def accessibility_page(loc):
    L=locales[loc]; page=PUBLIC/f'{loc}/accessibility/index.html'
    features=''.join(f'<li>{esc(x)}</li>' for x in L['accessibility']['features'])
    report=repo_issue('review.yml','[Accessibility] ')
    action=f'<a class="button" href="{esc(report)}">{esc(L["accessibility"]["report"])}</a>' if report else f'<p>{esc(L["contribute"]["repo_missing"])}</p>'
    body=f'''<section class="page-hero compact-hero"><div class="container page-hero-grid"><div><span class="eyebrow">{esc(L['section_labels']['inclusive_by_design'])}</span><h1>{esc(L['accessibility']['title'])}</h1><p class="lede">{esc(L['accessibility']['lede'])}</p></div><div class="accessibility-symbol" aria-hidden="true"><span>AA</span><small>WCAG 2.2</small></div></div></section><section class="section"><div class="container split-layout"><div><h2>{esc(L['accessibility']['status_title'])}</h2><p class="lede small">{esc(L['accessibility']['status_body'])}</p>{action}</div><div class="feature-card"><ul class="check-list">{features}</ul></div></div></section>'''
    write(f'{loc}/accessibility/index.html',shell(page,loc,'accessibility','accessibility',L['accessibility']['title'],L['accessibility']['lede'],body))

def root_page():
    page=PUBLIC/'index.html'; L=locales['en']; R=L['root']
    langs=''.join(f'<a lang="{esc(loc)}" dir="{esc(locales[loc]["dir"])}" href="{esc(rel(page,logical_target(loc,"home")))}"><span>{esc(locales[loc]["name"])}</span><small>{esc(project.get("locale_status",{}).get(loc,"preview").replace("-"," "))}</small><span aria-hidden="true">↗</span></a>' for loc in project['locales'])
    body=f'''<main id="main" class="global-landing"><section class="global-hero"><div class="global-brand"><span class="eyebrow">{esc(R['eyebrow'])}</span><h1>{esc(R['title'])}</h1><p class="lede">{esc(R['lede'])}</p><p class="hero-principle">{esc(R['principle'])}</p><div class="root-actions"><a class="button" href="{esc(rel(page,'en/quests/index.html'))}">Start a quest</a><a class="text-link strong" href="{esc(rel(page,'en/sprint/index.html'))}">Founding Sprint <span aria-hidden="true">↗</span></a><a class="text-link" href="{esc(rel(page,registry['machine_endpoints']['discovery'].lstrip('/')))}">{esc(R['machine'])} <span aria-hidden="true">↗</span></a></div></div></section><section class="language-zone" aria-labelledby="language-title"><h2 id="language-title">{esc(R['enter'])}</h2><div class="language-grid">{langs}</div></section></main>'''
    write('index.html',f'''<!doctype html><html lang="en" dir="ltr" data-theme="system"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><title>Navier–Stokes Commons</title><meta name="description" content="{esc(R['lede'])}">{SECURITY_META}<meta name="color-scheme" content="light dark"><link rel="stylesheet" href="{esc(rel(page,'assets/style.css'))}">{''.join(f'<link rel="alternate" hreflang="{esc(loc)}" href="{esc(rel(page,logical_target(loc,'home')))}">' for loc in project['locales'])}<link rel="alternate" hreflang="x-default" href="index.html"></head><body>{body}<script src="{esc(rel(page,'assets/site.js'))}" defer></script></body></html>''')

def benchmarks_page():
    page=PUBLIC/'en/benchmarks/index.html'
    dims=''.join('<article class="source-record"><div class="source-record-top"><span class="signal-dot" aria-hidden="true"></span><span class="micro">'+esc(d['id'].replace('-',' ').upper())+'</span></div><h2>'+esc(d['question'])+'</h2></article>' for d in reference_benchmarks['dimensions'])
    refs=''.join('<article class="mission-block"><span class="section-number">'+f'{i:02d}'+'</span><div><h3><a href="'+esc(r['url'])+'">'+esc(r['id'])+'</a></h3><p>'+esc(', '.join(r['roles']))+'</p><p class="micro">'+esc(r['verification'])+'</p></div></article>' for i,r in enumerate(reference_benchmarks['references'],1))
    qhref=rel(page,'en/quests/ns-q036/index.html')
    body='<section class="page-hero compact-hero"><div class="container narrow"><span class="eyebrow">PRE-REGISTERED COMPARISON CORPUS</span><h1>Reference benchmarks</h1><p class="lede">A dated comparison set for testing collaboration UX, visual craft, scientific interaction, accessibility resilience, and resource efficiency. Inclusion is not an endorsement and does not imply universal superiority or inferiority.</p><p><code>'+esc(reference_benchmarks['id'])+'</code></p><a class="button" href="'+esc(qhref)+'">Run the blinded comparison quest</a></div></section><section class="section"><div class="container"><span class="eyebrow">DIMENSIONS</span><div class="source-grid">'+dims+'</div></div></section><section class="section"><div class="container narrow"><span class="eyebrow">REFERENCE SET</span>'+refs+'</div></section>'
    write('en/benchmarks/index.html',canonical_shell(page,'guide','guide','Reference benchmarks','Pre-registered comparison references for release evaluation.',body))

def machine_files():
    frontier=[]
    for m in missions:
        frontier.append({'id':m['id'],'slug':m['slug'],'status':'open','category':m['category'],'level':m['level'],'title':m['title'],'summary':m['summary'],'question':m['question'],'acceptance':m['acceptance'],'contributors':m['contributors'],'source_ids':m['source_ids'],'url':deployed_ref('data/frontier.json',f'/en/missions/{m["slug"]}/')})
    (PUBLIC/'data').mkdir(parents=True,exist_ok=True); (PUBLIC/'.well-known').mkdir(parents=True,exist_ok=True)
    # GitHub Pages otherwise applies Jekyll's default underscore/dot-path filtering
    # to the deployment artifact, which would omit the standards discovery endpoint.
    (PUBLIC/'.nojekyll').write_text('',encoding='utf-8')
    (PUBLIC/'data/frontier.json').write_text(json.dumps({'project':project['project_id'],'generated_from_public_content':True,'missions':frontier},indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/sources.json').write_text(json.dumps(sources,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/project.json').write_text(json.dumps(project,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/contributions.json').write_text(json.dumps(contributions,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/forges.json').write_text(json.dumps(forges,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/scaling-model.json').write_text(json.dumps(scaling,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/formulas.json').write_text(json.dumps(formula_catalog,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/simulations.json').write_text(json.dumps(simulations_doc,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/reference-benchmarks.json').write_text(json.dumps(reference_benchmarks,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/actions.json').write_text(json.dumps(actions_doc,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/quests.json').write_text(json.dumps(quests_doc,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/task-ladder.json').write_text(json.dumps(task_ladder,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/taxonomy.json').write_text((CONTENT/'taxonomy.json').read_text())
    (PUBLIC/'data/claims.json').write_text(json.dumps(claims_doc,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/governance.json').write_text(json.dumps(governance,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/founding-sprint.json').write_text(json.dumps(founding_sprint,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/reviews.json').write_text(json.dumps(reviews,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/public-ssot.json').write_text(json.dumps(public_ssot,indent=2,ensure_ascii=False)+'\n')
    (PUBLIC/'data/authority-map.json').write_text((CONTENT/'authority_map.json').read_text())
    (PUBLIC/'data/release-policy.json').write_text((CONTENT/'release_policy.json').read_text())
    caps=capabilities(); (PUBLIC/'data/capabilities.json').write_text(json.dumps({'schema':'nsc-capabilities-v1','capabilities':caps},indent=2,ensure_ascii=False)+'\n')
    discovery={'schema':'commons-discovery-v4','project':project['project_id'],'name':project['name'],'reference_semantics':'Resolve every relative reference against this discovery document URL.',**{k:deployed_ref('.well-known/commons.json',v) for k,v in registry['machine_endpoints'].items()},**{f'human_{k}':deployed_ref('.well-known/commons.json',v) for k,v in registry['human_routes'].items()}}
    (PUBLIC/'.well-known/commons.json').write_text(json.dumps(discovery,indent=2)+'\n')
    skill=(ROOT/'SKILL.md')
    if skill.exists(): shutil.copy2(skill,PUBLIC/'SKILL.md')
    start=(ROOT/'start.md')
    if start.exists(): shutil.copy2(start,PUBLIC/'start.md')
    contrib=(ROOT/'CONTRIBUTING.md')
    if contrib.exists(): shutil.copy2(contrib,PUBLIC/'CONTRIBUTING.md')
    for name in ['AGENTS.md','GOVERNANCE.md','REVIEW_POLICY.md','MISSION_POLICY.md','COMMUNITY_STANDARDS.md','DCO.md','ROADMAP.md','PUBLIC_SSOT.json']:
        src=ROOT/name
        if src.exists(): shutil.copy2(src,PUBLIC/name)
    for dirname in ['schemas','references']:
        src=ROOT/dirname; dst=PUBLIC/dirname
        if src.exists(): shutil.copytree(src,dst,dirs_exist_ok=True)
    # Agent-context projections are generated from the same public source tree on every build.
    ep={k:v.lstrip('/') for k,v in registry['machine_endpoints'].items()}
    index_lines=[
      '# Navier-Stokes Commons agent index','',
      f'Release: {project["release"]}',
      f'Missions: {len(missions)}; quests: {len(quests)}; Founding Sprint: {len(founding_sprint["quest_ids"])}.','',
      f"- Start: {ep['agent_start']} - minimal cold-start protocol",
      f"- Skill: {ep['agent_skill']} - execution and evidence contract",
      f"- Discovery: {ep['discovery']} - machine endpoint registry",
      f"- Quests: {ep['quests']} - bounded work units",
      f"- Claims: {ep['claims']} - evidence/status records and derived quest links",
      f"- Sources: {ep['sources']} - public source registry",
      f"- Capabilities: {ep['capabilities']} - derived collaboration capabilities",
      f"- Authority map: {ep['authority_map']} - canonical vs derived vs independent-oracle facts",
      f"- Simulations: {ep['simulations']} - declared scientific interaction models",
      f"- Actions: {ep['actions']} - forge-mediated collaboration transactions",
      f"- Benchmarks: {ep['reference_benchmarks']} - pre-registered comparison corpus",
      f"- Governance: {ep['governance']} - roles and decision rules",
      f"- Sprint: {ep['founding_sprint']} - launch work set",'',
      f"Never infer a stronger claim status than {ep['claims']}. Attempts are non-exclusive. Negative results and falsifications are valid when they satisfy the quest acceptance contract."
    ]
    (PUBLIC/'llms.txt').write_text('\n'.join(index_lines)+'\n')
    full_parts=['\n'.join(index_lines)]
    for rel in ['start.md','SKILL.md','AGENTS.md','GOVERNANCE.md','MISSION_POLICY.md','REVIEW_POLICY.md','CONTRIBUTING.md','PUBLIC_SSOT.json']:
        src=PUBLIC/rel
        if src.exists(): full_parts.append(f'\n\n# FILE: {rel}\n\n'+src.read_text())
    for rel in ['data/capabilities.json','data/claims.json','data/quests.json','data/sources.json','data/founding-sprint.json','data/authority-map.json','data/simulations.json','data/actions.json','data/reference-benchmarks.json']:
        src=PUBLIC/rel; full_parts.append(f'\n\n# FILE: {rel}\n\n'+src.read_text())
    (PUBLIC/'llms-full.txt').write_text(''.join(full_parts))
    (PUBLIC/'robots.txt').write_text('User-agent: *\nAllow: /\n')

def main():
    if PUBLIC.exists(): shutil.rmtree(PUBLIC)
    PUBLIC.mkdir(parents=True)
    (PUBLIC/'assets').mkdir()
    shutil.copy2(ASSETS/'style.css',PUBLIC/'assets/style.css'); shutil.copy2(ASSETS/'site.js',PUBLIC/'assets/site.js')
    root_page()
    for loc in project['locales']:
        home_page(loc); missions_page(loc); guide_page(loc); known_page(loc); contribute_page(loc); activity_page(loc); sources_page(loc); agents_page(loc); accessibility_page(loc)
        for m in missions: mission_page(loc,m)
    quests_page()
    for q in quests: quest_page(q)
    sprint_page(); governance_page(); claims_page(); benchmarks_page()
    machine_files()
    print(f'Built {sum(1 for _ in PUBLIC.rglob("*.html"))} HTML pages in {PUBLIC}')

if __name__=='__main__': main()
