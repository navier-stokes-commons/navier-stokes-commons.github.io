# Assurance model

Navier-Stokes Commons uses four distinct authority classes. Conflating them is a release defect.

1. **Canonical state** is human-editable source data. A release-critical fact has exactly one writable authority.
2. **Derived projections** are generated from canonical state. They are never edited as a second authority. Reconciliation fails when a projection drifts.
3. **Evidence-derived state** is computed from canonical state plus exact-content public evidence records. Locale scientific-review status and scientific claim elevation are examples.
4. **Independent oracles** intentionally repeat an expectation through an independent implementation so they can falsify the canonical model or renderer. The Taylor-vortex residual audit is an example.

This is closer to a compiler/control-plane architecture than to a collection of synchronized documents: source objects are the input language, generated pages and machine endpoints are projections, validators enforce contracts, and CI reconciles and rejects invalid states.

The main engineering families are single source of truth, derived/materialized views, design by contract, policy as code, GitOps-style reconciliation, and mistake-proofing. The desired property is not merely DRY. It is that accidental contradictory release states either cannot be represented or cannot pass the release controller.

## Failure policy

Automatic reconciliation is allowed for deterministic projections. It is not allowed to manufacture external evidence. A locale cannot become scientifically reviewed because a script wants a green build. A scientific claim cannot become independently reviewed because an author changes a label. Missing external evidence leaves the stronger state unavailable.

## Test independence

Independent oracles are deliberately not generated from the implementation they test. This is why the exact-flow mathematical oracle is separate from the canonical expression AST and its browser renderer. Duplicating an expected mathematical result inside an independent test is useful; duplicating a writable project fact in two source files is not.

## Regression evidence

`scripts/audit_fault_seeds.py` injects representative historical failure classes into disposable RAM-backed or explicitly configured audit-scratch copies and requires the responsible gate to reject every case. This does not prove absence of all future defects. It demonstrates sensitivity to the known systemic classes rather than merely showing that the current good tree passes.
