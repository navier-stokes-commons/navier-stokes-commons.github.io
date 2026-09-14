# R17 terminal SSOT reconciliation

This additive correction does not alter the R17 renderer, interaction model, thresholds, browser evidence, or visual acceptance contract.

The live beta.7 repository state had a narrower state-drift defect: `content/public/release_policy.json` and its root `RELEASE.json` projection still described GitHub Pages as `configured-live-smoke-pending` and GitLab Pages as `configured-unexercised`, even though the deployment paths had already been exercised. The final R17 package correctly updates release identity to beta.8, but intentionally does not touch those adapter-state fields.

The terminal correction therefore records both adapters as `configured-live-path-exercised` and keeps `turnkey_static_deployment_adapters` empty. That distinction is deliberate. The existing `audit_host_configs.py` treats "turnkey" as a stronger certification that requires canonical provider evidence; the current v1 release-policy schema has no such evidence object. Successful prior deployments justify "path exercised", not an invented stronger guarantee.

The terminal release rule remains unchanged: beta.8 is not complete until the exact committed source SHA has passed the complete inherited suite, GitHub Pages, the fast-forward GitLab mirror/pipeline, both live hosts, and same-source parity.
