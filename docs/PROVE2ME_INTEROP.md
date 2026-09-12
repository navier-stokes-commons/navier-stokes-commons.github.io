# Prove2Me interoperability contract

## Principle

Do not make users choose between NSC and Prove2Me for formal theorem work. Use Prove2Me where it is stronger; make the provenance visible in NSC.

NSC is not a second general Lean theorem service: it owns the domain research
record and delegates formal execution to Prove2Me.

## Export

An NSC problem becomes export-eligible only after its intended semantics are reviewed enough to freeze a formal target. The export packet contains:

- NSC program/problem IDs;
- plain mathematical statement;
- proposed Lean statement or explicit request to formalize it;
- exact source locators;
- definition ledger;
- intended semantics and non-implications;
- candidate Lean/Mathlib environment;
- parent-frontier effect if the theorem succeeds;
- semantic/domain reviewer class required on return.

The packet instructs an agent to use the current Prove2Me `start.md` / skill. NSC never stores a Prove2Me API key in public data.

## Execute externally

Prove2Me owns theorem decomposition, proof/disproof submission, server verification, proof reuse, and Formalpedia attribution.

NSC should link to the resulting mission/theorem rather than mirror its proof library.

## Import

A returned record must identify the exact Prove2Me object, formal statement digest, environment, external status, and proof/disproof artifact.

The first automatic NSC state is `unreviewed-external-evidence`.

A semantic-mapping reviewer checks the formal statement against the approved NSC target. Only then may the evidence become `formally-verified-external` for that target.

A domain reviewer determines what the theorem changes in the parent Navier–Stokes program.

## No automatic overclaim

The bridge must fail if code attempts any of these transitions without a review record:

- Prove2Me `proved` -> NSC parent program `resolved`;
- kernel proof -> `semantic-correspondence-reviewed`;
- Formalpedia publication -> `independently-reviewed analytic claim`;
- Prove2Me campaign status -> CMI recognition.

## Current pin

Observed 2026-09-12:

- workspace: `prove2me/prove2me_workspace`
- commit: `8d697eeda2f65d396209a9b4f888602de1f55fbf`
- skill version: `0.10.3`
- API base advertised by skill: `https://prove2.me/api/v1`

R14 should update the existing NSC Prove2Me source record to this immutable workspace commit and treat later changes as source deltas requiring compatibility review.
