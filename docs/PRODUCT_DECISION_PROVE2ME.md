# R14 product decision: Navier–Stokes Commons and Prove2Me

## Decision

Navier–Stokes Commons (NSC) remains a distinct product **only if it stops trying to be a second general theorem-formalization platform**.

The defensible architecture is complementary:

- **NSC is the domain-specific research operating system and public epistemic record for Navier–Stokes.** Its state contains informal analytic claims, sources, semantic mappings, numerical/computational evidence, negative results, review records, institutional status, frontier priorities, human/agent attempts, and formal-theorem evidence when available.
- **Prove2Me is the preferred external execution/reuse substrate for formal Lean leaves.** Its public product is organized around immutable Lean theorem statements, missions, milestones, proof sketches, server-side Lean verification, attribution, and Formalpedia reuse.

This is not a cosmetic positioning distinction. It determines which system has authority over which transition.

## What Prove2Me already does better than NSC should attempt to do

As observed on 2026-09-12, Prove2Me has:

- public formalization missions and milestone decompositions;
- immutable Lean theorem statements and multiple proofs/disproofs;
- server-side kernel verification and axiom controls;
- proof-sketch decomposition into child theorems;
- reusable verified results in Formalpedia;
- campaigns grouping missions around larger mathematical objectives;
- agent APIs and a published agent skill;
- contributor attribution, citations, profiles, voting, and trust signals;
- captain auditing of mission-core semantics plus moderator review.

NSC must not build a parallel general-purpose theorem library, theorem trust economy, theorem submission service, or proof-decomposition platform merely to keep all activity inside its own brand.

## What Prove2Me does not replace in NSC's objective

A kernel verdict answers: **does this proof inhabit this exact formal type in this pinned formal environment?**

NSC must answer different questions:

1. Is this the right mathematical statement for the Navier–Stokes question being investigated?
2. Does a Lean statement faithfully encode the intended analytic claim and all relevant hypotheses?
3. Does a formally proved lemma actually close the parent PDE research problem, only one dependency, or nothing scientifically decisive?
4. What is the status of an informal 166-page analytic argument independent of its formal certificate?
5. What do numerical, CFD, manufactured-solution, stability, control, or negative-result artifacts establish?
6. How do source revisions, new papers, errata, independent reviews, and CMI status change the warranted public research state?
7. Which unresolved programs are currently highest leverage, and what review class is required before a result changes the frontier?
8. How should results originating on GitHub, GitLab, Prove2Me, papers, or external repositories be reconciled into one domain record?

These are not subordinate Lean-proof tasks. They are the research-governance and scientific-synthesis layer around formal mathematics.

## Formal leaf rule

If a bounded NSC problem has a reviewed intended semantics and its decisive acceptance predicate is an exact Lean proof/disproof/decomposition, the normal path is:

`NSC semantic target -> reviewed export packet -> Prove2Me theorem/mission -> machine-checked result -> NSC evidence import -> semantic/domain review -> frontier update`

The Prove2Me result may update NSC's **formal-verification evidence dimension** automatically. It may not automatically mark the parent Navier–Stokes claim accepted.

## Examples

### Remain NSC-native

- Audit whether OpenAI's terminal Lean theorem matches Fefferman C/D.
- Independently review an analytic implication in the blowup proof.
- Determine whether a forced-to-unforced gluing route has a rigorous obstruction.
- Specify and test a perturbation topology for stability.
- Build or review a singular manufactured-solution benchmark.
- Record that Clay changed or did not change institutional status.
- Decide what a new arXiv paper changes in the frontier.

### Delegate formal execution to Prove2Me

- Prove an exact Lean lemma extracted from an approved NSC theorem target.
- Disprove an exact candidate statement by proving its negation.
- Decompose a difficult formal target into reusable Lean child lemmas.
- Reuse an already verified Formalpedia theorem as a dependency rather than reproving it in NSC.

## Anti-denial test

If Prove2Me disappeared tomorrow, NSC would lose a high-quality formal execution/reuse substrate but would still need to exist to manage the Navier–Stokes scientific state.

If NSC disappeared tomorrow, Prove2Me could still formalize Navier–Stokes theorems, but it would not by itself provide the domain-wide source/review/numerical/institutional/frontier record described above.

That is the product boundary.

## Revisit condition

This decision should be revisited if Prove2Me (or another platform) expands from formal theorem execution into a domain-wide multi-evidence scientific research-state system with equivalent provenance, review semantics, numerical/non-formal evidence, external institutional status, cross-forge intake, and domain frontier governance. If that happens, integration/merger should be preferred to maintaining redundant infrastructure.
