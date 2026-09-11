#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
from nsc_model import ROOT,C,project_view,counts,locale_statuses,release_policy,public_registry,version,release_id

def render_release():
    p=project_view(); n=counts(); pol=release_policy(); forges=json.loads((C/'forges.json').read_text())
    reg=public_registry()
    machine=list(reg['machine_endpoints'].values())
    machine=list(dict.fromkeys(machine))
    d={
      'release':release_id(),'version':version(),'product':pol['product'],'content_scope':pol['content_scope'],
      'locales':p['locales'],'locale_status':p['locale_status'],'rtl_locales':[x for x in p['locales'] if json.loads((C/'locales'/f'{x}.json').read_text()).get('dir')=='rtl'],
      'missions':n['missions'],'public_sources_and_standards':n['sources'],'accessibility_target':p['accessibility_target'],'accessibility_claim':pol['accessibility_claim'],
      'runtime_third_party_scripts':pol['runtime_third_party_scripts'],'analytics_or_cookies_by_default':pol['analytics_or_cookies_by_default'],
      'forge_contribution_adapters':[x['label'] for x in forges.get('adapters',[])],
      'turnkey_static_deployment_adapters':pol['turnkey_static_deployment_adapters'],'configured_static_deployment_adapters':pol.get('configured_static_deployment_adapters',[]),'machine_endpoints':machine,'machine_endpoint_path_semantics':'Logical site-root paths only. On deployed project-subpath hosts, use the relative references emitted by .well-known/commons.json and resolve them against the discovery document URL.',
      'licenses':p['license'],'release_gates':pol['release_gates'],'release_id':release_id(),'status':p['release_stage'],'notes':pol['notes'],
      'quests':n['quests'],'founding_sprint_quests':n['founding_sprint_quests'],'tracked_claims':n['tracked_claims']
    }
    return json.dumps(d,ensure_ascii=False,indent=2)+'\n'

def render_ssot():
    p=project_view(); reg=public_registry()
    d={'schema':'nsc-public-ssot-v2','project_id':p['project_id'],'release':release_id(),'release_stage':p['release_stage'],'participation_status':p['participation_status'],
       'canonical_data':reg['canonical_data'],'public_protocols':reg['public_protocols'],'machine_endpoints':reg['machine_endpoints'],'human_routes':reg['human_routes'],'path_semantics':'Registry paths are logical site-root paths. Deployed agents MUST resolve the relative references emitted by .well-known/commons.json against that discovery document URL; this preserves GitHub/GitLab project subpaths.',
       'work_model':{
         'mission':'longer-lived research program or question','quest':'bounded independently checkable unit of work attached to exactly one mission',
         'attempt':'non-exclusive public declaration of work on a mission or quest','result':'artifact plus exact claim, evidence, limitations, provenance, and reproduction instructions',
         'review':'independent scoped evaluation of a result or decision','accepted_record':'canonical public contribution merged only after required gates'},
       'invariants':[
         'Open questions are never rendered as established facts.','Starting a quest is non-exclusive and does not reserve it.',
         'Scientific claim elevation requires independent competent review.','Negative results, corrections, and falsifications may be accepted artifacts.',
         'Public canonical data contains no private research history or orchestration material.','The open beta may be published with zero accepted contributions when the launch predicate passes.',
         'Maturity gates may block stronger claims or version 1.0 without blocking open participation.',
         'Writable relationship state has one canonical direction; reverse indexes are generated.',
         'Locale scientific-review status is derived from translation scope and exact-content review receipts.',
         'Release summaries and public projections are generated and checked against canonical data.',
         'Collaboration actions are specified as forge-neutral logical transactions and projected through forge adapters.',
         'Comparative visual claims require a dated pre-registered benchmark set and independent human review.'
       ],'canonical_repository':p['repository_url']}
    return json.dumps(d,ensure_ascii=False,indent=2)+'\n'

def render_citation():
    p=project_view()
    return ("cff-version: 1.2.0\n"
      "title: Navier-Stokes Commons\n"
      'message: "Cite the exact release or repository commit used. For scientific claims, cite the underlying primary source or accepted contribution rather than the Commons alone."\n'
      "type: software\n"
      f"license: {p['license']['software']}\n"
      f"version: {version()}\n"
      f"repository-code: \"{p['repository_url']}\"\n")

def replace_block(text,name,body):
    start=f'<!-- GENERATED:{name}:start -->'; end=f'<!-- GENERATED:{name}:end -->'
    block=start+'\n'+body.rstrip()+'\n'+end
    rx=re.compile(re.escape(start)+r'.*?'+re.escape(end),re.S)
    if rx.search(text): return rx.sub(block,text)
    return block+'\n\n'+text

def license_label(spdx):
    return {'Apache-2.0':'Apache License 2.0','CC-BY-4.0':'Creative Commons Attribution 4.0 International','CC0-1.0':'Creative Commons CC0 1.0 Universal'}.get(spdx,spdx)

def render_license_file():
    spdx=project_view()['license']['software']
    src=ROOT/'references'/'licenses'/f'{spdx}.txt'
    if not src.exists(): raise SystemExit(f'No canonical license text template for {spdx}: {src}')
    return src.read_text()

def docs_outputs():
    n=counts(); p=project_view()
    readme=(ROOT/'README.md').read_text()
    summary=(f"**Current release:** `{release_id()}`\n"
             f"**Stage:** {p['release_stage']}\n"
             f"**Participation:** {p['participation_status']}\n"
             f"**Seed research programs:** {n['missions']} missions\n"
             f"**Bounded work units:** {n['quests']} quests\n"
             f"**Initial Independent Review Portfolio:** {n['founding_sprint_quests']} quests")
    # Remove legacy writable copy when first migrating.
    readme=re.sub(r'\*\*Current release:\*\*.*?\*\*Bounded work units:\*\*.*?\n', '', readme, count=1, flags=re.S)
    readme=replace_block(readme,'release-summary',summary)
    guide=(ROOT/'docs/PRODUCT_GUIDE.md').read_text()
    caps=__import__('nsc_model').capabilities(); cap=caps['bounded_participation_ladder']['statement']+' '+caps['student_entry_path']['statement']
    guide=re.sub(r'Student participation now includes a six-rung bounded quest ladder,.*?frontier research\.', '', guide)
    guide=replace_block(guide,'participation-capability',cap)
    ann=(ROOT/'docs/LAUNCH_ANNOUNCEMENT.md').read_text()
    launch=f"The current release includes {n['missions']} research missions and {n['quests']} bounded quests. {n['founding_sprint_quests']} quests are in the Initial Independent Review Portfolio."
    ann=re.sub(r'The first release includes \d+ research missions and \d+ bounded quests[^\n]*\n', '', ann)
    ann=replace_block(ann,'launch-counts',launch)
    # Release-critical license selections and machine entrypoints are projections, never writable prose copies.
    lic=p['license']
    license_summary=f"Software: {lic['software']}. Original content: {license_label(lic['original_content'])}. Metadata: {lic['metadata']}. See `LICENSE_POLICY.md`, `CONTENT_LICENSE.md`, and `DCO.md`."
    readme=replace_block(readme,'license-summary',license_summary)
    sprint=json.loads((C/'founding_sprint.json').read_text())
    readme=replace_block(readme,'sprint-id',f"**Initial Independent Review Portfolio:** `{sprint['id']}`")
    reg=public_registry(); ep=reg['machine_endpoints']; href=lambda x:x.lstrip('/')
    readme=replace_block(readme,'agent-entrypoints',f"Humans may use the rendered site and repository issue forms. Agents should fetch `{href(ep['discovery'])}`, then read `{href(ep['agent_start'])}`, `{href(ep['agent_skill'])}`, `{href(ep['quests'])}`, `{href(ep['frontier'])}`, `{href(ep['claims'])}`, and `{href(ep['actions'])}` plus the relevant source records before acting.")
    lp=(ROOT/'LICENSE_POLICY.md').read_text()
    lp_body=(f"- **Software and build tooling:** {license_label(lic['software'])} (`{lic['software']}`).\n"
             f"- **Original human-readable editorial/scientific content and original site media:** {license_label(lic['original_content'])} (`{lic['original_content']}`).\n"
             f"- **Factual/catalog metadata intended for machine reuse:** {license_label(lic['metadata'])} (`{lic['metadata']}`).")
    lp=replace_block(lp,'license-policy',lp_body)
    cl=(ROOT/'CONTENT_LICENSE.md').read_text()
    cl_body=(f"Unless a file or source record states otherwise, original prose and original site media use **{license_label(lic['original_content'])}** (`{lic['original_content']}`).\n\n"
             f"Machine-oriented factual/catalog metadata explicitly identified as metadata uses **{license_label(lic['metadata'])}** (`{lic['metadata']}`).")
    cl=replace_block(cl,'content-license-summary',cl_body)
    start=(ROOT/'start.md').read_text()
    start=replace_block(start,'agent-fastest-path',f"Agent fastest path: fetch `{href(ep['discovery'])}`, then `{href(ep['agent_skill'])}`, `{href(ep['quests'])}`, and `{href(ep['actions'])}`.\n\nCanonical public state is indexed by `{href(ep['public_ssot'])}`. Generated HTML is not the source of truth.")
    skill=(ROOT/'SKILL.md').read_text()
    skill=replace_block(skill,'agent-discovery',"Fetch `{}.`".format(ep['discovery']).replace('`.`','`.') if False else f"Fetch `{href(ep['discovery'])}`. Then fetch `{href(ep['quests'])}`, `{href(ep['frontier'])}`, `{href(ep['sources'])}`, `{href(ep['claims'])}`, `{href(ep['task_ladder'])}`, `{href(ep['actions'])}`, `{href(ep['reference_benchmarks'])}`, and `{href(ep['governance'])}` as needed.")
    skill=replace_block(skill,'claims-endpoint',f"Do not infer that compilation proves semantic correspondence, that a numerical result proves an analytic theorem, or that a source-reported claim is independently reviewed. Use statuses from `{href(ep['claims'])}` exactly.")
    agents=(ROOT/'AGENTS.md').read_text()
    order=[href(ep[x]) for x in ['discovery','agent_start','agent_skill','quests','actions','frontier','sources','claims']]
    agents=replace_block(agents,'agent-start-order','\n'.join(f"{i}. `{x}`" for i,x in enumerate(order,1))+f"\n{len(order)+1}. the exact quest and parent mission selected")
    statuses=locale_statuses()
    from collections import Counter
    sc=Counter(statuses.values())
    wcag=(ROOT/'docs/WCAG_SELF_ASSESSMENT.md').read_text()
    wcag_body=(f"Configured locale surfaces: {len(statuses)}. Canonical scientific language: {sc.get('canonical',0)}. Full translations awaiting qualifying native-language plus subject-domain receipts: {sc.get('full-translation-review-pending',0)}. Interface-preview locales: {sc.get('interface-preview',0)}. Locale status is evidence-derived from exact-content digests, not manually promoted.")
    wcag=replace_block(wcag,'locale-assurance-status',wcag_body)
    sprint_doc=json.loads((C/'founding_sprint.json').read_text())
    quest_lookup={q['id']:q for q in json.loads((C/'quests.json').read_text())['quests']}
    sprint_lines='\n'.join(f"- `{qid}`: {quest_lookup[qid]['title']}" for qid in sprint_doc['quest_ids'])
    sprint_text=(f"# Initial Independent Review Portfolio `{sprint_doc['id']}`\n\n{sprint_doc['purpose']}\n\n"
                 f"The launch cohort contains **{len(sprint_doc['quest_ids'])} quests**. Participation is non-exclusive; multiple independent attempts are permitted.\n\n"
                 f"## Canonical quest set\n\n{sprint_lines}\n\n"
                 "## Completion semantics\n\nThe sprint is public work, not a pre-launch blocker. Its success conditions are the canonical conditions in `content/public/founding_sprint.json`, evaluated from public artifacts and review records. The first accepted contribution should exercise the complete lifecycle: attempt, artifact, evidence, independent review, canonical record, deterministic rebuild, and public projection.\n")
    release_notes=(f"# {version()}: collaboration beta with systemic assurance\n\n"
      f"This release contains {n['missions']} seed research missions, {n['quests']} bounded quests, a six-rung task ladder, {n['founding_sprint_quests']} Initial Independent Review Portfolio quests, {n['tracked_claims']} tracked claim records, and {len(p['locales'])} locale surfaces.\n\n"
      "## Structural guarantees\n\n- Release-critical facts have one writable authority. Derived projections are reconciled and checked.\n- Locale and claim elevation states are evidence-derived from exact-content review records.\n- Mission-to-quest, claim-to-quest, and sprint membership reverse indexes are generated rather than manually duplicated.\n- Public browser rendering is exercised in CI, including JavaScript and no-JavaScript paths, narrow layouts, RTL, reduced motion, forced colors, and zoom.\n- Scientific interaction is limited to declared models with static fallbacks and independent mathematical oracles.\n- Collaboration transactions are machine-readable and forge-mediated rather than coupled to one host.\n- Comparative visual claims are evaluated against a pre-registered reference corpus rather than asserted by a synthetic aesthetic score.\n\n"
      "## Open-beta semantics\n\nOpen participation does not wait for independent certification of every scientific or institutional claim. Stronger claim states remain gated by the evidence class that can justify them. Negative results, reproductions, corrections, accessibility findings, design findings, and falsifications are first-class contributions when they satisfy their quest contract.\n")
    return {'README.md':readme,'docs/PRODUCT_GUIDE.md':guide,'docs/LAUNCH_ANNOUNCEMENT.md':ann,'docs/WCAG_SELF_ASSESSMENT.md':wcag,'docs/FOUNDING_SPRINT.md':sprint_text,'RELEASE_NOTES.md':release_notes,'LICENSE_POLICY.md':lp,'CONTENT_LICENSE.md':cl,'start.md':start,'SKILL.md':skill,'AGENTS.md':agents}

def expected():
    out={'RELEASE.json':render_release(),'PUBLIC_SSOT.json':render_ssot(),'CITATION.cff':render_citation(),'LICENSE':render_license_file()}; out.update(docs_outputs()); return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); a=ap.parse_args(); bad=[]
    for rel,text in expected().items():
        p=ROOT/rel
        if a.check:
            if not p.exists() or p.read_text()!=text: bad.append(rel)
        else:
            p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text)
    if bad:
        print('PROJECTION_RECONCILIATION_FAILED stale='+','.join(bad),file=sys.stderr); return 1
    print('PROJECTION_RECONCILIATION_PASS' if a.check else 'PROJECTION_RECONCILIATION_UPDATED')
    return 0
if __name__=='__main__': raise SystemExit(main())
