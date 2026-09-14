# R17 unified fluid interaction system

R17 supersedes the failed R16 hero renderer and page-background interaction model.

## Why R16 failed

R16 stacked a new Canvas2D renderer on top of the legacy R5 vortex and R14 ambient controller. The old derived controls were moved into an expanded disclosure, leaving `Play sweep` visible; the new renderer was too faint at real viewport scale; and the page-wide background never shared the new pointer-response state. Tests mostly verified contract markers and state, so a perceptually broken release could still pass.

R17 removes the duplicated English motion authorities instead of adding another overlay.

## Runtime authority and delivery

For English rich pages, the legacy R14 ambient controller exits before initialization and `assets/r17-fluid.js` becomes the page-wide interaction authority. The English/root home additionally disables the legacy R5 hero runtime. R16 is removed entirely.

The R17 asset is split from `assets/site.js`: the shared base runtime remains small, while the R17 asset is loaded on English rich pages only. The plain `/en/math/` projection does not load it. Non-English pages keep their previous R5/R14 behavior until separately migrated.

One session-scoped R17 motion state owns:

- the hero exploratory flow field when a hero is present;
- the low-opacity page-wide field on English rich pages;
- pointer position and both horizontal and vertical pointer velocity;
- decaying wake memory;
- Light / Balanced / Viscous UI response mode;
- explicit Pause/Resume;
- reduced-motion state;
- document visibility suspension.

Only explicit Pause or `prefers-reduced-motion: reduce` changes running intent. Pointer movement, pointer-down, mode changes, resize, scrolling, and route navigation within the same rich experience do not silently stop motion.

Pause is stored only in `sessionStorage`. A fresh browsing session therefore starts alive again unless the OS asks for reduced motion.

## Pointer and page-wide response

The first pointer sample establishes position with zero velocity, preventing a synthetic wake spike on entry. Subsequent samples drive both x/y velocity terms. Velocity and wake energy decay exponentially when the pointer stops.

Movement while paused does not accumulate hidden wake state: pointer positions are updated defensively, velocity/energy remain zero, and resuming does not release a stored burst.

The page-wide field runs on English rich pages beyond the home hero, including research-problem, guide, agent, review, and frontier surfaces. It is decorative, `aria-hidden`, and `pointer-events:none`; real text and controls never move.

## Visual semantics

The home hero is an **interactive exploratory flow field**, not the computed 2026 solution. It uses coherent advected particles, short persistence trails, broad vortex-density cues, and pointer-velocity perturbations. It deliberately avoids the previous dominant 3-D wireframe/hourglass silhouette.

`Light`, `Balanced`, and `Viscous` are interface response modes, not physical viscosity values. The pointer wake is UI-only, not evidence about the PDE or the 2026 construction.

## Progressive enhancement and failure modes

- ordinary JS mode: automatically running;
- explicit Pause: freezes hero and ambient fields;
- fresh session: automatically running again;
- reduced motion: deterministic, visibly populated static hero; page ambient/cursor hidden;
- no JS: static SVG flow-field fallback and complete content/actions;
- Canvas2D hero initialization failure: enhanced hero controls/canvas are abandoned and the static SVG remains visible; page-wide enhancement may continue independently;
- ambient Canvas2D failure: hero remains usable independently;
- hero offscreen: hero rendering suspends while the much cheaper page-wide field can continue;
- mobile: reduced particle count/cadence and `touch-action: pan-y pinch-zoom` preserve vertical page scrolling;
- `/en/math/`: unchanged, zero JavaScript and zero stylesheet requirement.

## Cadence and budgets

Rendering is cadence-bounded rather than repainting every display refresh: approximately 34 render frames/s on ordinary desktop and 18 on low-power/save-data/mobile paths. DPR and particle counts are capped. The split R17 runtime is budgeted independently, while combined rich-page JavaScript remains under the release budget.

## Acceptance evidence

Release checks measure actual rendered pixels and runtime state, not only labels:

- automatic hero motion;
- bounded render cadence;
- first-pointer zero-velocity guard;
- pointer-driven visible hero wake;
- page-wide motion and pointer wake on a non-home route;
- wake decay after pointer stops;
- explicit pause freezes both fields;
- pointer movement during pause cannot accumulate a hidden burst;
- reset while paused redraws without resuming;
- reduced-motion static density;
- Canvas2D failure leaves the static fallback;
- mobile overflow/touch behavior;
- no-JS fallback;
- Mathematics isolation.
