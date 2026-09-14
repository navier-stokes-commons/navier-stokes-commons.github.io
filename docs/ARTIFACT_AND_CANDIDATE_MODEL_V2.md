# Artifact and release-candidate model v2

The previous naming pattern (`FINAL`, `FINAL_VERIFIED`, `ALL_SUPERSEDING`, `SELF_HEALING`) is retired. A package name is not evidence of finality.

## Identity

A user-facing candidate is identified by a monotonically allocated `RC-YYYYMMDD-NNN` id plus the deterministic SHA-256 digest of its generated `public/` product tree. Review evidence binds to that product digest. Git commit SHA remains provenance, but review receipts may be committed after the candidate was rendered, so the product digest is the non-self-referential identity of what reviewers actually saw.

Exactly one candidate may have status `active`. `ACTIVE_CANDIDATE.json` points to it. Previous candidates are preserved; they are never overwritten into a new meaning.

## Supersession

When a new candidate replaces an old one, the old record is marked `superseded` and must state:

- why the old candidate ceased to be acceptable;
- the evidence that triggered supersession;
- which prior evidence remains valid;
- which prior evidence was invalidated;
- known unresolved risks.

The word `final` is not a lifecycle state. The only terminal status is `released`, after release-authoritative evidence passes.

## Release rule

A release candidate is not shippable merely because machine checks pass. It additionally requires review-system-v2 evidence bound to the active candidate's exact product digest. Any unresolved P0/P1 veto, missing required observation modality, or unresolved machine/perceptual contradiction blocks release.
