# Prove2Me reuse-first plan for the Navier–Stokes Commons

## Existing overlap: do not duplicate statement A

As observed 2026-09-12, Prove2Me already exposes a reviewed public mission:

- title: `Formalize Navier-Stokes Open Problem`
- field: Partial Differential Equations
- captain: `korbonits`
- public catalog: `https://prove2.me/f/partial-differential-equations`
- intended goal: Fefferman statement A on R^3
- explicit scope boundary: statements B, C, D and Euler are out of scope

Before creating ANY new Navier–Stokes Prove2Me mission, authenticated R15 execution MUST enumerate the current Prove2Me catalog and theorem search, identify exact overlaps, and record a reuse/search receipt. This observation is a search seed, not a substitute for a current authenticated catalog lookup.

## Canonical decision tree

For each NSC formal leaf:

1. identify the exact informal/source statement and reviewed intended semantics;
2. search Prove2Me fields, missions, theorems and relevant milestone history;
3. if a faithful existing theorem/mission exists, link/reuse it;
4. if an existing mission is the right parent but the needed theorem/milestone is absent, contribute there or coordinate with its captain rather than creating a duplicate mission;
5. create a new mission proposal only when the formal target is materially non-overlapping and mission-coherent;
6. import Prove2Me verification only as typed external formal evidence until NSC semantic/domain review.

## Highest-value new candidate: 2026 C/D certificate

A new Prove2Me mission is justified only after the current catalog search confirms there is still no equivalent mission.

Candidate mission:

- working title: `Finite-Time Blowup for Forced Navier-Stokes - 2026 C/D Certificate`
- mission type: `ResearchPaper`
- analytic source: OpenAI, `Finite time blowup for Navier–Stokes` (2026)
- formal source: `openai/NavierStokesAndEuler`
- pinned source commit: `8937a8f4cbc7abaab5e9e97d1cc7f5d2319d9538`
- NSC parents: primarily FG-03 (Lean ↔ Clay semantics), with consequences for FG-02 and downstream frontier nodes

Because a compiling Lean project already exists, use Prove2Me's `upload_full_project` playbook rather than manually recreating theorem statements. Select the relevant terminal theorem(s), compute the exact declaration dependency closure, mechanically preserve source statements, and validate the exact uploaded types against the original.

## Required C/D proposal gates

Do not ask the human to submit until all pass:

1. current Prove2Me mission/theorem search performed and saved;
2. existing statement-A mission explicitly recognized and not duplicated;
3. no equivalent C/D mission/theorem graph found, or exact reason why the new mission is not a duplicate recorded;
4. terminal C/D theorem(s) and source locators identified;
5. exact OpenAI repository commit pinned;
6. target Prove2Me Lean/mathlib environment checked for compatibility;
7. generated Prove2Me project builds locally/server-side as appropriate;
8. elaborated original vs staged theorem types compared mechanically;
9. independent read-back of goal and core milestone statements completed;
10. attribution/license/source metadata preserved;
11. NSC semantic mapping packet written, explicitly listing what Prove2Me verification does NOT establish;
12. NSC `formalization_links` candidate record prepared without falsely claiming domain acceptance.

Then stop at `PROVE2ME_HUMAN_SELF_AUDIT_SUBMIT_REQUIRED` with the proposal URL/ID, read-back packet, exact items needing confirmation, and no secrets.

## Later candidates

- Statement B: do not create now merely because the current A mission excludes it. Reuse infrastructure from A first; reassess after the A mission has matured.
- Cao–Chi 2026 follow-up papers: good future `ResearchPaper` candidates after independent semantic review of the source statements.
- FG-01, FG-02, FG-03, FG-08, FG-11 and FG-12 remain primarily NSC-native; export only exact formal leaves when appropriate.

## Bidirectional link semantics

Prove2Me mission descriptions should link back to the relevant NSC research-program/frontier context without implying NSC owns the Prove2Me mission.

NSC records should link to Prove2Me theorem/mission IDs and current formal status, while preserving:

`Prove2Me proved` -> `NSC external formal evidence`

NOT:

`Prove2Me proved` -> `NSC scientific claim accepted`.
