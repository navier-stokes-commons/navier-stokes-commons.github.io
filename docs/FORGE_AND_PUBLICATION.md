# Forge-neutral contribution and automatic publication

The public website is not semantically tied to GitHub or GitLab.

`COMMONS_FORGE_KIND` selects the adapter (`github`, `gitlab`, `forgejo`, `codeberg`, `gitea`, `bitbucket`, or `generic`) and `COMMONS_FORGE_URL` supplies the canonical repository URL. Host-native issue/work-item URLs are conveniences, not the scientific data model.

The portable transaction object is a contribution manifest. Accepted manifests live in `content/public/contributions.json` (a later service may project the same schema from a database/event log). The generator consumes those manifests and automatically emits:

- the relevant mission's accepted-contribution section;
- the locale activity/contribution ledger;
- `public/data/contributions.json` for agents and other clients.

Therefore an accepted contribution does **not** require manual HTML changes. Review/merge changes canonical public data; CI executes `scripts/run_all_checks.py`; the site is rebuilt; publication follows automatically.

A future forge adapter may be added without changing mission semantics, evidence semantics, or the frontend content model.
