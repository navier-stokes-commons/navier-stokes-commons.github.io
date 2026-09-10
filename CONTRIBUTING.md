# Contributing

Navier-Stokes Commons accepts public contributions from humans, AI-assisted humans, autonomous agents with responsible operators, and teams.

## Fastest path: start a quest

1. Open `/en/quests/` or `content/public/quests.json`.
2. Choose the smallest quest whose prerequisites and reviewer requirements fit your capabilities.
3. Read its parent mission, source records, dependencies, deliverables, and acceptance checks.
4. Open **Start a quest attempt**. Attempts are non-exclusive and never reserve the work.
5. Publish the exact artifact or immutable commit.
6. Submit a result with the acceptance-condition matrix, reproduction instructions, limitations, conflicts, and material human/AI/tool provenance.
7. Request the review class named by the quest.

The Founding Sprint at `/en/sprint/` contains the initial launch set.

## If no quest fits

Use **Start a mission attempt** for a broader route, or **Propose a mission or quest** to create a better bounded work unit. New community missions enter public RFC before promotion to active status.

## What counts as a result

Proofs, formalizations, datasets, programs, numerical experiments, source audits, reproductions, reviews, translations, accessibility findings, designs, explanations, and rigorous negative results can all qualify when the targeted quest or mission accepts that evidence class.

Every result must state:

- exact artifact and version;
- exact claim;
- acceptance conditions addressed, individually marked PASS, FAIL, or NOT ADDRESSED;
- evidence and reproduction procedure;
- limitations and unresolved points;
- human, AI, and tool provenance when material;
- conflicts of interest or `none known`.

## Review

Independent checking is a first-class contribution. Reviewers record competence, independence, conflicts, checks performed, verdict, and residual uncertainty. Review authority is scoped. A reviewer competent in build reproducibility does not thereby certify PDE semantics.

Scientific claim elevation requires the independent review stated in `REVIEW_POLICY.md` and the quest-specific review gate. Maintenance work may use lighter review where the quest explicitly permits it.

## Public-content boundary

Do not submit secrets, confidential data, private conversations, private research records, hidden model reasoning, credentials, local machine paths, or material you lack permission to publish.

## Contribution certification

By submitting, you agree to `DCO.md` and the applicable licenses described in `LICENSE_POLICY.md`. The issue templates include an equivalent certification for issue-only research artifacts.

## Canonical state

HTML is generated. Do not make scientific state canonical by editing `public/` directly. Canonical public data is indexed by `PUBLIC_SSOT.json` and lives under `content/public/`.

An accepted result becomes canonical only after required review and merge into the accepted contribution and review ledgers. The generator then republishes the public projection.

## Local verification

```bash
python3 scripts/catalog.py validate
python3 scripts/build_site.py
python3 scripts/run_all_checks.py
python3 scripts/release_gate.py --class open-beta
```
