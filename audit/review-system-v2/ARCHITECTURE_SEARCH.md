# Beta.8 runtime autopsy and architecture search

The baseline was inspected at source and in the generated English pages. `r17-fluid.js` is the sole English rich-page motion authority: it owns the page canvas, hero canvas, pointer state, pause state, reduced-motion state and its requestAnimationFrame scheduling. `site.js` exits before its legacy ambient writer on English pages; localized pages retain the explicitly separate fallback field. Canvas targets, z-order and computed opacity were recorded in the release evidence packet.

Three materially different candidates were compared before selection:

1. **A — field-dominant:** one full-viewport vector field, gradient compositing through sections, no particle layer. Strength: calm continuity. Risk: weak directional affordance and low focal hierarchy.
2. **B — advection-dominant:** particle advection with a dedicated hero renderer and a separate page trail. Strength: obvious pointer causality. Risk: competing clocks and sparse/toothpick hero failure on constrained devices.
3. **C — hybrid layered field (selected):** one R17 controller and clock with a dense hero field plus page-wide field, shared pointer impulse, explicit section compositing, and intentional static/reduced-motion fallbacks. Strength: coherent atmosphere and directional response while retaining one ownership graph.

Blind comparative review evidence rejected A for insufficient directional salience and B for ownership complexity; C was retained after held-out checks. Candidate records RC-20260914-001 through RC-20260914-003 preserve supersession reasons and invalidated baseline evidence.
