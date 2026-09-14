# Review-system v2: incident diagnosis and replacement protocol

## Incident

The R17 process demonstrated two symmetric assurance failures:

1. **False blocker:** a repairable deployment-SSOT schema mismatch was treated as terminal because executor policy forbade correcting authored integration defects.
2. **False green:** the release later reached `R17_TERMINAL_PUBLIC_PASS` while ordinary product inspection still found the motion experience effectively broken/static, weak page-wide background salience, unfinished language-grid borders and visibly poor microtypography.

The second failure is more serious. It proves that release certification optimized surrogate predicates that were not construct-valid for the user-facing objective.

## Why the old synthetic panel did not sound the alarm

The historical panel contained apparently strong professional profiles, including an independent creative director, motion-design auditor and multiscript typography specialist. The problem was not the mere absence of expert titles. The operational layer was missing.

### D1 - Persona without evaluator contract

The old auditor schema specified role, mission, resume floor, methods, owned lenses and calibration thresholds. It did **not** require:

- the exact task script used for a review;
- the evidence modalities the reviewer must inspect;
- blind versus informed conditions;
- task-specific failure sensitivities;
- adversarial counterexample prompts;
- non-compensable veto conditions;
- observation/inference separation;
- uncertainty/abstention behavior;
- raw-output preservation;
- contradiction escalation.

That makes the profile a hiring sketch, not an executable evaluator.

### D2 - Unreproducible synthetic reviews

The historical `synthetic_frontend_audit.py` validates catalog/schema coverage only. It does not call or orchestrate a model. The historical `synthetic_panel_reviews.json` contains compact conclusions but no prompt, model/provider/version, run identifier, evidence hashes, raw output or review transcript. Therefore the synthetic panel result cannot be independently reproduced or audited as an evaluation run.

### D3 - Evidence/claim mismatch

The visual reviewer concluded that the motion system was coherent from reviewed **screenshots**. A still screenshot cannot establish motion salience, pointer causality, pause/resume behavior or animation coherence over time. The motion specialist likewise summarized implementation properties without a recorded time-based observation protocol.

V2 makes evidence modality a type constraint: motion claims require time-based evidence or live interaction; runtime ownership requires runtime/source evidence; typography claims require multi-scale rendered evidence and font-load traces.

### D4 - No mandatory hostile counterexample lane

The old framework had mutation testing for machine checks, but not a release-critical reviewer whose sole job was to find implementations that satisfy the current gates while violating user intent. V2 adds G01, the Goodhart red team. Its failure condition is itself a process defect: if it can produce a material counterexample not exposed by the evidence system, release is blocked until the measurement regime is strengthened.

### D5 - Weak minority-veto semantics

A severe dissenting review must not become a sentence inside a consensus summary. V2 preserves P0/P1 vetoes as non-compensable release blockers. `ABSTAIN` never counts as PASS, and missing evidence blocks rather than silently degrading confidence.

### D6 - Synthetic-user strata were not grounded enough

A title such as “novice user” is insufficient. V2 user strata are defined by task, context and constraints: cold first impression, constrained mobile, scaled display, research contributor, etc. They are explicitly prohibited from claiming population prevalence or lived experience. Their purpose is high-throughput defect discovery under diverse conditions.

### D7 - The system confused synthetic external validity with synthetic defect-discovery power

Synthetic reviewers are not valid substitutes for representative human preference studies. But that does **not** imply they should have weak release authority. A synthetic reviewer can directly expose an observable defect. One well-grounded, independently reproduced P1 observation can and should veto release even though ten synthetic PASS votes cannot establish that ten real people would like the product.

### D8 - Control-plane success displaced product truth

The prior workflow gave great authority to hashes, same-SHA deployment, deterministic builds, state receipts, pixel differences and machine gates. Those are useful but lower-level facts. V2 forces product-facing observation before certification and treats machine/user contradiction as an escalation signal rather than noise.

## V2 architecture

The system has four first-class objects:

1. **Evaluator contract** - who/what the reviewer represents, what it is competent to establish, what it cannot establish, exactly what it must inspect, what adversarial tests it must run and what can veto release.
2. **Evidence packet** - hash-bound screenshots, timed frames/video, live interaction traces, runtime instrumentation, computed styles, font/network traces, source fragments or other modality appropriate to the claim.
3. **Review run** - model identity, exact prompt hashes, evidence hashes, observations, epistemic type, severity, vetoes, contradictions, unknowns and raw-output hash.
4. **Panel policy** - criterion-to-modality mapping, independent reviewer quorum, blind/user-stratum requirements and non-compensable stopping rules.

## Epistemic weighting

V2 intentionally gives synthetic stakeholders **more authority for defect discovery** than the failed system did:

- A P0/P1 synthetic finding grounded in required evidence blocks release.
- A missing required observation blocks release.
- A contradiction between a machine PASS and perceptual FAIL blocks release pending arbitration.
- A single relevant minority veto is preserved.

At the same time, V2 refuses a different overclaim:

- Synthetic PASS does not estimate human-population preference.
- Synthetic vote counts are not human sample sizes.
- Lived-experience claims require real affected users.
- Taste, motivation, trust and cultural fit ultimately require human/field calibration when material.

This is not “less synthetic review.” It is synthetic review used for the epistemic job it is strongest at: broad, cheap, adversarial defect search with explicit evidence and veto power.

## Required release sequence

1. Build the deterministic candidate and compute the `public/` product digest.
2. Run cheap machine vetoes.
3. Capture the evidence modalities required by `PANEL_POLICY.json`.
4. Run blind user-stratum reviews before exposing implementation rationale or prior PASS labels.
5. Run specialist expert reviews.
6. Run G01 hostile Goodhart review against the gates themselves.
7. If any reviewer conflicts with machine evidence or another material reviewer, run ARB01 to diagnose the conflict and acquire the cheapest discriminating evidence. The same candidate remains blocked; arbitration is not permission to average or overrule a valid FAIL. Corrected evidence or product changes produce a new auditable review/candidate state.
8. Only after zero unresolved P0/P1 vetoes, complete required independent review coverage and exact product-digest binding may the synthetic-review gate PASS.
9. Human/field studies remain required for claims about real-user prevalence or preference where those claims matter.
10. Deploy the same product digest and verify the live host has not changed the evidence-relevant behavior.

## Stopping rule

A candidate may advance only when:

- all deterministic hard gates pass;
- every critical criterion has the specified evidence modalities;
- reviewer coverage/independence requirements are met;
- there are no active P0/P1 vetoes;
- there are no unresolved contradictions;
- the hostile Goodhart lane has not found an unmeasured material counterexample;
- the committed review records bind to the exact product digest;
- any required human/field boundary is explicitly satisfied or the release claim is narrowed accordingly.

No average score, majority vote, Pareto frontier or impressive resume can override those conditions.

## Current R17 incident classification

Under V2, the historical R17 evidence would never have been eligible for a synthetic PASS on motion because still screenshots cannot satisfy the required timed-motion/live-interaction modalities. A21/A22 would have been forced to abstain or fail for insufficient evidence before any motion-quality conclusion. The later ordinary visual complaint would then create a machine-versus-perception contradiction requiring arbitration rather than being discovered after terminal release.


## Current beta.8 enforcement gap found during this incident

The live beta.8 repository had already improved its written evaluation doctrine: it distinguishes executable vetoes, task-path evaluators, specialist critics, blinded comparisons, red-team synthesis and human/field escalation. The failure was that this doctrine was not made release-authoritative. `scripts/audit_evaluation_protocol.py` primarily checks for the presence of files/tokens. `scripts/pareto_review.py` conservatively aggregates *pre-recorded* evidence but explicitly never calls an evaluator. `scripts/run_all_checks.py` runs many machine audits but did not require reproducible synthetic-review receipts. `scripts/audit_visual_integrity.py` explicitly states that it is not an aesthetic oracle.

V2 closes that policy/execution gap: the release runner itself requires the review-system static contract, an active product-digest-bound candidate, and evidence-bound review receipts after the deterministic build.

## External methodological basis

The design follows the general TEVV principle that evaluation should combine multiple modes rather than treat one metric family as sufficient. NIST ARIA separates model testing, red teaming and field testing; the NIST AI RMF Measure function recommends independent assessment, mixed qualitative/quantitative methods, documented tools and deployment-like conditions. LLM-judge research documents order/authority/other evaluation biases, motivating blind lanes, model-family diversity and raw-evidence preservation. These sources support the architecture; they do not certify this implementation.
