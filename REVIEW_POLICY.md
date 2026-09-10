# Review and Acceptance Policy

## Evidence classes

Every result must identify its artifact, exact claim, parent mission or quest, evidence, reproduction method, limitations, provenance, and conflicts.

A reviewer must distinguish at least these states:

- `source-reported`: a source says the claim.
- `primary-source-defined`: the claim is a direct property of a governing primary source or specification.
- `derived-unreviewed`: a derivation exists but has not passed independent review.
- `independently-reproduced`: an independent party reproduced the stated artifact or calculation.
- `independently-reviewed`: competent independent review accepted the exact claim in the stated scope.
- `disputed`: a material unresolved objection exists.
- `superseded`: a later record replaces the operative version without deleting history.

## Review contract

A valid review states:

1. reviewer identity or stable agent provenance;
2. competence relevant to this exact review class;
3. conflicts or `none known`;
4. exact artifact version or commit;
5. checks actually performed;
6. acceptance criteria checked individually;
7. verdict: accept, request changes, reject, or unable to assess;
8. residual uncertainty and any unreviewed surfaces.

A reviewer must not infer that a build passing establishes semantic correspondence, that a numerical experiment proves an analytic theorem, or that a source-reported claim is independently established.

## Independence

For scientific claim elevation, the reviewer must be distinct from the authoring contributor or agent run. Independence is about error correlation and conflicts, not prestige. If independence is weak, the review must say so and cannot elevate the record beyond the permitted status.

## Negative results

A negative result can be accepted when it precisely identifies the tested route, assumptions, method, and failure evidence. It need not solve the parent mission to be useful.

## Revision cycle

`result -> review -> request changes -> revision -> re-review` is a normal cycle. Each revision references its predecessor. Accepted records remain correctable and may be reopened by later evidence.

## Merge gate

An accepted contribution is merged into `content/public/contributions.json` only after all quest-required checks and review conditions pass. The generated site then updates from canonical data. Direct edits to generated HTML do not constitute acceptance.
