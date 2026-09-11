# Evaluation protocol: synthetic search, measured Pareto decisions, and human escalation

## Purpose

Synthetic review is a high-throughput **search and defect-discovery instrument**. It is not a substitute for human-centred design evidence and is not itself a certification of user preference.

## Review layers

### Layer 0: executable vetoes

Run before any LLM judgment. Scientific/source invariants, schemas, link integrity, layout, accessibility, runtime budgets, machine cold-start, forge actions, leak scans, and packaging either pass or fail.

### Layer 1: task-path evaluators

Give evaluators a goal and only the public artifact. Ask them to return the exact route/actions they would take. Grade task completion independently from prose quality.

### Layer 2: specialist critics

Use separate roles for scientific visualization, realtime graphics, PDE semantics, formal methods, accessibility, multiscript typography, information architecture, open-source onboarding, agent/tool interfaces, runtime performance, and research-credit governance. Each critic returns observations and falsifiable change proposals, not a global score.

### Layer 3: blinded comparative judges

Only surviving candidates enter pairwise comparison. Separate development judges from a held-out confirmation pool. Randomize A/B position and repeat in B/A order using the same judge instance within each mirrored block. Suppress candidate names, model provenance, implementation cost, and previous scores. Require evidence before verdict. For material held-out preference claims, use at least two materially independent model/provider families when feasible; do not repeatedly tune against the held-out pool.

### Layer 4: red-team synthesis

A separate critic receives the winning case and is instructed to find the strongest reason not to ship it. Its role is adversarial, not consensus-seeking.

### Layer 5: human/field escalation

If the remaining uncertainty concerns comprehension, trust, beauty, motivation, cultural fit, or real-world contribution behavior, synthetic review stops and the question is routed to humans/field evidence.

## Judge hygiene

- Never use one unmirrored pairwise order.
- Never use one judge/model family for a material held-out decision when independent families are available.
- Never tune candidates repeatedly against the held-out confirmation pool; that converts it into development data.
- Never tell a judge which candidate is incumbent or newer.
- Never expose prestigious expert names as authority cues inside candidate descriptions.
- Separate critique generation from preference voting.
- Preserve raw judgments and disagreement.
- Report ties and unstable order-sensitive results.
- Use deterministic/executable evidence to override taste scores when they conflict.
- Do not let verbosity count as evidence.

## Efficient allocation of compute

Use successive halving:

1. many cheap candidate/critic passes;
2. deterministic gates eliminate invalid candidates;
3. moderate multi-judge evaluation for survivors;
4. expensive high-capability cross-model review only for close frontier cases;
5. real humans for unresolved human questions.

The incumbent is always retained as a control. Additional compute is justified only when it has a plausible path to changing the decision.

## Statistical interpretation

Synthetic judgments are repeated measurements from a biased instrument, not IID samples from the human population. Confidence intervals quantify uncertainty in the instrument's repeated outputs, not external validity. External validity requires calibration against human data.

For paired synthetic comparisons, use block bootstrap or Wilson intervals over order-balanced blocks. For multiple candidates, select on development evidence and confirm only the finalist(s) on held-out evidence; do not repeatedly mine a hold-out set. Use pairwise preference models only after testing judge/order/family stability. Do not report pseudo-precise 92.7/100 aggregate "UX" scores.

## Monotonicity

R7 implements **incumbent-preserving monotonicity on measured objectives**:

- a new candidate cannot replace the incumbent after a hard regression;
- a candidate with uncertain soft superiority remains a challenger;
- a losing candidate can contribute individual improvements, but those improvements are retested in the incumbent context.

This protects against regression while acknowledging that measured objectives are incomplete proxies for actual human experience.


## Measured Pareto frontier

Production selection retains the incumbent unless all hard vetoes pass and the challenger improves the measured objective vector or an explicit trade-off is documented. Synthetic preference is supporting evidence, not a human-population claim.


## Release separation

`run_fast_checks.py` is a strict local-preflight subset only; `run_all_checks.py` remains release-authoritative.
