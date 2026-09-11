# Operations, field performance, and post-launch UX measurement

R7 separates three questions that are easy to conflate:

1. **Is the release pipeline efficient and stable?**
2. **Is the public runtime fast on real devices/networks?**
3. **Can real humans and agents complete the intended research tasks?**

A green build answers none of these by itself.

## 1. SDLC outcomes

Use the current DORA five-metric model over rolling windows for this one public application/release process:

- change lead time: commit -> successful live deployment;
- deployment frequency;
- failed deployment recovery time;
- change fail rate;
- deployment rework rate.

R7 additionally records per-gate wall time for the fast and full suites. These are diagnostic process metrics, not substitutes for delivery outcomes. Track p50/p90 total full-suite time and the slowest gates. Optimize a gate only after it is a material repeated bottleneck or source of flakiness.

Do not reward deployment frequency in isolation; DORA explicitly treats throughput and instability together.

## 2. Runtime field outcomes

Lab budgets and Playwright checks are release vetoes. Real-user performance claims require field evidence.

When sample size is sufficient, report Core Web Vitals at the 75th percentile, segmented mobile/desktop:

- LCP <= 2.5 s;
- INP <= 200 ms;
- CLS <= 0.1.

Where traffic is too low for stable field quantiles, say so rather than substituting lab Lighthouse/Playwright values as population evidence.

Also record WebGL/fallback mode during voluntary test sessions so a fast Canvas/static fallback is not mistaken for proof that the flagship WebGL path performs well everywhere.

## 3. Human task outcomes

For cohort-specific moderated sessions, use the exact public release and pre-registered tasks. Record:

- binary task completion;
- critical interpretation errors (especially forced C/D vs unforced A/B, schematic-vs-computed visualization, Lean-vs-independent-review semantics);
- time on task;
- recovery after an error;
- confidence calibration;
- route chosen to contribute and whether the participant can state the acceptance contract.

Qualitative rounds use sequential defect-discovery saturation. Quantitative population claims require an explicit sample-size/power model and a defined target population.

## 4. Agent outcomes

The release already has a public-only cold-start gate. Post-launch, separately test at least two agent/model families against only the live public surface and record:

- discovery success;
- starter-quest selection validity;
- source/claim scope correctness;
- action discovery;
- tokens/requests to first valid bounded action;
- hallucinated paths or stronger-than-supported claim states.

Machine-legibility should improve agent task success or reduce retrieval cost, not merely increase the number of metadata files.

## 5. Community outcomes

Use public forge state and voluntary studies rather than invasive analytics where possible:

- first-time attempt authors;
- attempt -> result conversion;
- result -> independent review conversion;
- median review latency;
- correction/falsification rate;
- accepted artifacts per active contributor;
- repeated/rejected low-signal submissions;
- cohort diversity when voluntarily/self-disclosed and ethically appropriate.

Do not optimize raw issue count, stars, pageviews, or generated comments as proxies for research value.

## Decision rule

A post-launch change is a demonstrated improvement only when it either:

- improves an objective release/runtime/task metric without material regression elsewhere; or
- is supported by appropriately scoped human/field evidence for a subjective objective.

Keep an incumbent archive. If evidence is equivocal, retain the current release and collect the more discriminating evidence rather than manufacturing a winner.
