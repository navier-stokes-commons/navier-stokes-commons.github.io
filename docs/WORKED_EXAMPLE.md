# Worked contribution example

This example uses the public certificate-audit mission. It is illustrative; it is not a claim that the described audit has already been accepted.

## 1. Mission

Reproduce and inspect the published Lean certificate on the exact pinned source/toolchain, and check how its terminal statement corresponds to the official public problem formulation.

## 2. Attempt

A contributor declares a clean-room reproduction route and records the exact source commit and toolchain they intend to use. Another contributor is still free to perform an independent attempt.

## 3. Artifact

The contributor publishes:

- environment manifest;
- exact commands;
- build logs;
- dependency/axiom report;
- statement-correspondence notes;
- hashes of relevant outputs.

## 4. Evidence

A second party can follow the instructions and determine whether the build and reports reproduce. The evidence explicitly distinguishes “the formal artifact checks” from “the formal statement faithfully expresses the intended mathematics.”

## 5. Review

An independent formal-methods reviewer checks the formal side; an appropriate PDE reviewer checks the semantic correspondence. Any objection is attached to the public record rather than hidden.

## 6. Accepted record

After the required review is satisfied, a contribution manifest is merged. CI regenerates the mission page, global contribution activity, and `data/contributions.json` automatically.
