# Publish Navier-Stokes Commons

This runbook publishes the open-beta source tree without weakening the scientific or governance gates.

## Publication object

Publish only this public repository tree. Never publish the private design program, local audit scratch data, private prompts, machine paths, credentials, or unpublished research history.

The repository is source-of-truth driven. `PUBLIC_SSOT.json` indexes canonical public data and policy. `public/` is generated output.

## Before the first push

Run from the repository root:

```sh
python3 scripts/release_gate.py --class open-beta
```

Publication is allowed only if the command exits successfully and `OPEN_BETA_RELEASE_RECEIPT.json` says `status: PASS`.

Then verify the source manifest:

```sh
python3 scripts/audit_manifest.py
```

Do not edit generated HTML to make a failing gate pass. Correct canonical source or policy, rebuild, and rerun the gate.

## Canonical GitHub target

The configured canonical repository is `timperelman/navier-stokes-commons-public`. The source tree may be staged there while private, but collaboration launch begins only when repository visibility is public and the deployed smoke tests below pass.

## GitHub publication

1. Use the configured canonical repository `timperelman/navier-stokes-commons-public`; do not create a competing canonical repository.
2. Keep the repository private during the exact source cutover and the first CI validation.
3. Push the exact source-only release tree to `main` and require **Public site CI** to pass on that exact commit.
4. Change repository visibility to public only after CI succeeds.
5. Create or update GitHub Pages with build type `workflow`, then dispatch the pinned Pages workflow.
6. Verify the deployed root, `en/quests/`, `en/sprint/`, and `.well-known/commons.json` relative to the actual Pages base URL.
7. Resolve the discovery document relative references against the discovery document URL and verify that every advertised machine endpoint remains inside the Pages project subpath.
8. Open one quest attempt through the deployed interface. Confirm the generated issue preserves the quest ID.
9. Open one result and one review form far enough to verify their mission/quest identifiers and required fields.
10. Announce the Initial Independent Review Portfolio only after these smoke tests pass.

When GitHub Actions builds the site, the generator reads the repository identity supplied by the host and produces repository-native contribution links.

## GitLab publication

1. Create or select the public project and enable Issues plus CI/CD.
2. Push this source tree.
3. The included pipeline runs the same public gates and builds Pages.
4. Verify the deployed root, quest board, Initial Independent Review Portfolio, machine discovery endpoint, and issue-template routing.
5. Announce only after the smoke tests pass.

## Any other forge

The canonical scientific and collaboration data are forge-neutral. `content/public/forge_adapters.json` defines contribution-routing support for GitHub, GitLab, Forgejo, Codeberg, Gitea, Bitbucket, and a generic fallback. Other hosts can invoke the same deterministic build and gate commands.

GitHub Pages and GitLab Pages configurations are shipped as configured adapters. Do not promote either to the `turnkey_static_deployment_adapters` list until its live deployment path has actually been exercised and recorded.

## First maintainer actions after publication

Publication begins the Initial Independent Review Portfolio. It does not wait for the sprint to finish.

1. Create a public announcement from `docs/LAUNCH_ANNOUNCEMENT.md` and link the quest board plus Initial Independent Review Portfolio.
2. Start or sponsor at least one small starter-rung quest so newcomers can observe the complete attempt -> artifact -> review lifecycle.
3. Invite independent contributors toward the launch quests in `content/public/founding_sprint.json` rather than asking for vague help.
4. Route scientific review requests only to reviewers whose competence and independence fit the quest's declared review class.
5. Merge accepted contribution manifests only after the acceptance criteria and review policy are satisfied.
6. Rebuild and publish after every accepted canonical record.
7. Record corrections and reversals; do not erase public evidence history.

## What may be claimed at open beta

It is accurate to say that Navier-Stokes Commons is an open public collaboration workspace with seeded missions and bounded quests, machine-readable interfaces, forge-native contribution flows, explicit review rules, and reproducible release gates.

It is not accurate to claim that the Commons independently validates the 2026 mathematical result, certifies WCAG conformance, provides scientifically reviewed translations in every locale, or has mature institutional governance unless the corresponding evidence has been completed and accepted.

Those are not prerequisites for opening the workspace. They are themselves tracked maturity and evidence tasks.

## Release identity after the public repository exists

The canonical repository URL is already part of canonical project metadata and is projected into `CITATION.cff`. If the repository identity ever changes, edit only `content/public/project.json`, run `python3 scripts/reconcile.py`, and rerun the complete release gate.
