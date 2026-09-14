# Synthetic stakeholder strata: operating rule

The project must not confuse a colorful persona biography with an evaluator.

Use stakeholder strata to vary **task, prior knowledge, device/interaction constraints, language/script, accessibility stress condition, motivation and failure sensitivity**. Do not invent demographic stereotypes and then treat them as empirical human behavior.

Minimum recurring strata for public-release review:

- Cold curious visitor: no implementation context; first ten seconds and primary interaction.
- Math/PDE expert: source/claim navigation, mathematical representation, research credibility.
- Prospective contributor: mission selection, acceptance criteria, contribution handoff.
- Formal-methods contributor: machine-legible proof/certificate path and semantic-boundary clarity.
- Constrained mobile visitor: small viewport, touch/scroll, lower runtime budget.
- Scaled-display/low-vision stress stratum: 125–200% zoom, optical legibility and reflow; explicitly not a substitute for disabled-user lived experience.
- Reduced-motion stratum: static alternative completeness; explicitly not a substitute for motion-sensitive users.
- RTL/CJK rendered stratum: layout/typography stress; semantic fidelity still requires native review.
- AI-agent operator: cold machine discovery, task packet and source-safety behavior.
- Skeptical journalist/research-integrity reader: claim/status/source distinction and overclaim detection.
- Hostile specification gamer: search for proxy-success/user-failure counterexamples.

For each release-critical feature, generate additional strata by asking: **what user/context combination could falsify the current claim while all existing reviewers still pass?** Add the smallest reviewer that covers that uncovered failure mode.
