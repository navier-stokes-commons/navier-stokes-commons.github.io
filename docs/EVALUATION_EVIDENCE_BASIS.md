# Evidence basis for the R7 evaluation/optimization protocol

R7 deliberately distinguishes standards, empirical design evidence, software-delivery evidence, and limits of synthetic evaluation.

## Human-centred design and usability

- ISO 9241-210:2019, *Ergonomics of human-system interaction, Part 210: Human-centred design for interactive systems*. Official ISO record: https://www.iso.org/standard/77520.html
- ISO 9241-11:2018, *Ergonomics of human-system interaction, Part 11: Usability: Definitions and concepts*. Official ISO record: https://www.iso.org/standard/63500.html

These motivate treating usability as contextual outcome and retaining a human/field evidence boundary rather than claiming synthetic optimality.

## Parallel design search

- Dow, Glassco, Kass, Schwarz, Schwartz & Klemmer (2010), *Parallel prototyping leads to better design results, more divergence, and increased self-efficacy*, ACM TOCHI 17(4), DOI 10.1145/1879831.1879836. https://doi.org/10.1145/1879831.1879836

This is evidence against unconstrained serial fixation and in favor of preserving an incumbent while generating materially different candidates in parallel.

## Limits of LLM judges and synthetic users

- Shi et al., *Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge*, arXiv:2406.07791 / ACL Anthology. https://arxiv.org/abs/2406.07791
- Chen, Zhu & Zheng (2026), *When Synthetic Users Fail: A Cross-Domain Benchmark of LLM-Simulated Human Survey Responses*, arXiv:2607.26348. https://arxiv.org/abs/2607.26348

These justify mirrored candidate order, multiple judges/model families, preservation of raw disagreement, and the rule that synthetic confidence intervals describe an instrument rather than a human population.

## Delivery-system observability

- DORA, *DORA’s software delivery performance metrics*. https://dora.dev/guides/dora-metrics/

R7 does not pretend one repository has enough organizational history to estimate every DORA metric before launch. It adopts the methodological lesson: measure delivery outcomes over time and do not optimize speed by sacrificing stability. The immediate implementable precursor is per-gate timing plus a strict fast-preflight/full-release split.

## Field runtime quality

- web.dev, *Web Vitals*. https://web.dev/articles/vitals

Post-launch performance claims should use field evidence where possible. Current recommended good thresholds are p75 LCP <= 2.5 s, INP <= 200 ms, and CLS <= 0.1, segmented by mobile/desktop. R7’s static/runtime budgets are lab safeguards, not a substitute for field Core Web Vitals.

## Machine-readable contracts

- OpenAPI Specification 3.1.2. https://spec.openapis.org/oas/v3.1.2.html. R7 deliberately uses the latest 3.1 patch for broad tooling compatibility; OAS 3.2.0 is the latest feature release, but R7 needs no 3.2-only feature.
- JSON Schema Draft 2020-12. https://json-schema.org/draft/2020-12
- RFC 8615, *Well-Known Uniform Resource Identifiers (URIs)*. https://www.rfc-editor.org/info/rfc8615/
- Jeremy Howard, `/llms.txt` proposal (v2). https://llmstxt.org/

R7 therefore adds a generated OpenAPI description and JSON Schema coverage, explicitly labels its `.well-known/commons.json` usage as a project-local convention rather than an IANA registration, and labels llms.txt as a convenience proposal rather than a ratified standard.

## Interpretation rule

None of these artifacts proves the resulting product is globally optimal. They constrain the search/evaluation procedure and identify evidence classes that are stronger than model self-review. The terminal decision remains evidence-relative: measured non-domination under explicit gates, then real human and field calibration.

- llms.txt v2 (Jeremy Howard, 2026 update): https://llmstxt.org/ is still an informal proposal, but now recommends `rel="describedby"` for discoverability; R7 uses that hint while explicitly avoiding a standards claim.
