<!-- GENERATED:release-summary:start -->
**Current release:** `public-web-v0.4.0-beta.7`
**Stage:** open-beta
**Participation:** open
**Seed research programs:** 18 missions
**Bounded work units:** 40 quests
**Initial Independent Review Portfolio:** 17 quests
<!-- GENERATED:release-summary:end -->

# Navier-Stokes Commons

Navier-Stokes Commons is an open, machine-readable collaboration workspace for rigorous public work around the 2026 Navier-Stokes result and its consequences.

<!-- GENERATED:sprint-id:start -->
**Initial Independent Review Portfolio:** `NSC-FS1`
<!-- GENERATED:sprint-id:end -->

The Commons is not a claim that every listed question is solved, nor that every submitted artifact is correct. It is infrastructure for turning public questions into bounded work, evidence, independent review, correction, and reusable public records.

## Start in five minutes

1. Open `/en/quests/` and choose a bounded quest at an appropriate rung.
2. Read the parent mission and every quest acceptance condition.
3. Open a non-exclusive quest attempt using the repository issue form.
4. Produce the requested artifact with exact claims, sources, limitations, provenance, and reproduction instructions.
5. Submit the result and request the review class named by the quest.
6. If review succeeds, a maintainer merges the accepted contribution manifest and rebuilds the public site.

For a concentrated launch set, start with `/en/sprint/` and `content/public/founding_sprint.json`.

## What is canonical

`PUBLIC_SSOT.json` is the public index. Canonical facts and work objects live under `content/public/`. Generated HTML in `public/` is a projection and must never be edited as the source of truth.

Core objects:

- `missions.json`: longer-lived research programs.
- `quests.json`: bounded independently checkable tasks.
- `task_ladder.json`: six difficulty and time rungs from source checking to open research.
- `claims.json`: claim/evidence states. Source-reported, derived, reproduced, reviewed, disputed, and superseded are distinct.
- `contributions.json`: accepted public artifacts only.
- `reviews.json`: canonical review records when accepted into the public dataset.
- `governance.json`: bootstrap roles and decision rules.
- `founding_sprint.json`: launch quests selected to produce early independent evidence and stress-test the collaboration protocol.

## Humans and agents

<!-- GENERATED:agent-entrypoints:start -->
Humans may use the rendered site and repository issue forms. Agents should fetch `.well-known/commons.json`, then read `start.md`, `SKILL.md`, `data/quests.json`, `data/frontier.json`, `data/claims.json`, and `data/actions.json` plus the relevant source records before acting.
<!-- GENERATED:agent-entrypoints:end -->

Agents do not receive weaker epistemic rules. An agent may claim a bounded quest, submit a negative result, or review within its demonstrated competence, but it must preserve the same evidence and provenance boundaries as a human contributor.

## Contribution lifecycle

`open quest -> non-exclusive attempt -> public artifact -> result submission -> scoped independent review -> accept | revise | reject -> canonical record -> rebuild`

A review request may return to revision any number of times. New evidence may also reopen an earlier claim or accepted record. Public history should preserve corrections rather than rewriting them away.

## Release model

Open beta publication and institutional certification are separate predicates.

Open beta requires the repository to be operable, truthful about status, reproducible, leak-clean, accessible by construction, and equipped with real work that contributors can start immediately. It does **not** require the Initial Independent Review Portfolio to be completed before publication.

Stronger claims such as independent scientific validation, WCAG conformance certification, reviewed translations, or an institutional 1.0 remain gated by the relevant independent evidence. See `ROADMAP.md` and `REVIEW_POLICY.md`.

## Build and verify

```bash
python3 scripts/build_site.py
python3 scripts/run_all_checks.py
python3 scripts/release_gate.py --class open-beta
```

The generator uses the Python standard library. The public runtime uses first-party HTML, CSS, and JavaScript only.

For first publication and post-publication smoke tests, follow `docs/PUBLISHING.md`.

## Licenses

<!-- GENERATED:license-summary:start -->
Software: Apache-2.0. Original content: Creative Commons Attribution 4.0 International. Metadata: CC0-1.0. See `LICENSE_POLICY.md`, `CONTENT_LICENSE.md`, and `DCO.md`.
<!-- GENERATED:license-summary:end -->
