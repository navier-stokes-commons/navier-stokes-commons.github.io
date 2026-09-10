# Deploy the public site

## 1. Verify the exact release

From repository root, use the canonical gate rather than a hand-maintained subset:

```sh
python3 scripts/bootstrap_audit_env.py
python3 scripts/run_all_checks.py
```

For a source checkout, `public/` is generated and ignored by Git. For a full release archive, verify `MANIFEST.sha256` before the canonical gate.

## 2. Canonical GitHub Pages deployment

The canonical repository is `Aletheia-Prime/navier-stokes-commons-public`. For the first public cutover, keep it private while replacing the staging source and while CI validates the exact commit. Change visibility only after that CI run succeeds.

1. Replace the staging branch with the exact source-only release tree.
2. Wait for **Public site CI** on that exact commit and require success.
3. Change repository visibility to public.
4. Create or update the GitHub Pages site with build type `workflow`.
5. Dispatch **Deploy public site to GitHub Pages** and require success.
6. Smoke-test the deployed release identity plus the project-subpath-safe machine discovery document at `.well-known/commons.json`.
7. From an English and a non-English mission page, test Start an attempt, Submit a result, and Review or falsify.
8. From the contribution page, test Propose a side quest.
9. Check the Arabic edition for right-to-left layout.
10. Test keyboard navigation, 200% text enlargement, reduced motion, and the exact-flow/scaling interactions before making stronger accessibility claims.

The Pages workflow uses `actions/configure-pages` to obtain the actual deployment base URL and builds with that value. Human links are relative. Machine discovery references are document-relative so GitHub project subpaths are preserved.

## 3. GitLab Pages

The repository ships a GitLab Pages configuration that invokes the same shared audit-environment bootstrap and canonical suite. It is a **configured, unexercised adapter**, not a turnkey claim. Promote it to turnkey only after a live GitLab deployment is independently exercised and recorded.

## 4. Custom domain

Configure the domain at the hosting provider and supply the canonical `SITE_URL` to the build. The generated site uses relative internal links and document-relative machine discovery references, so it works at a domain root or project subpath. When `SITE_URL` is set, canonical page metadata is emitted from that deployment base.

## 5. Production accessibility sign-off

Automated checks are release gates, not a substitute for assistive-technology testing. Complete the manual matrix in `ACCESSIBILITY.md`, record findings publicly, fix failures, and rerun the full release gate before making a formal conformance statement.
