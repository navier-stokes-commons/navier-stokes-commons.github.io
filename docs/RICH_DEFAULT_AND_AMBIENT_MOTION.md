# Rich default and ambient motion specification

## Correct projection architecture

The product has two intentionally different human projections over the same canonical research state:

1. **Interactive view (default):** high visual impact, moving scientific object, compact truth/status layer, direct manipulation, pointer-aware ambient glyph field, research/frontier calls to action.
2. **Mathematics view (`/en/math/`):** plain HTML, zero JavaScript, zero stylesheet dependency, no persuasive layer, exact status/frontier/review/source information.

The Mathematics projection must never become the aesthetic template for the rich default.

## First viewport

Desktop must show simultaneously:

- Navier–Stokes identity;
- concise C/D versus A/B thesis;
- a substantial portion of the live vortex/scientific visual;
- compact A/B/C/D state;
- Research frontier, Mathematics, and agent/review entry paths.

The visual object must not be pushed below a wall of institutional prose.

## Motion

For ordinary users:

- vortex motion starts automatically;
- after the finite intro it transitions to a slow persistent ambient state rather than stopping;
- pointer motion changes probe/lens emphasis and subtle local geometry response;
- background ASCII/vector glyphs evolve continuously at bounded frame rate;
- pointer motion creates a decaying local glyph wake;
- scroll position shifts phase subtly;
- one visible control pauses/resumes nonessential automatic motion globally;
- hidden documents suspend work and resume when visible if the user did not pause it.

For `prefers-reduced-motion: reduce`:

- all automatic nonessential motion is off;
- no content or action becomes unavailable;
- static scientific fallbacks remain complete.

For low-power/save-data:

- reduce DPR, glyph density, and frame rate;
- preserve interaction semantics;
- static fallback is acceptable below a declared capability threshold.

## Ambient field semantics

The background field is not a simulation of the 2026 blowup. Its base may be derived from a declared analytic reference flow; its pointer-induced perturbation is explicitly UI-only.

It is `aria-hidden` and nonessential. All scientific meaning exists independently in text/data.

## Prototype evidence

The R14 handoff includes a prototype rendered from the exact beta.6 public artifact plus the R14 delta. Browser measurements on the prototype show:

- no horizontal overflow at 1440, 390, or 320 CSS px;
- measurable ordinary-mode frame change;
- measurable pointer-response change;
- zero automatic screenshot delta in reduced-motion mode.

These are interaction/layout predicates, not claims of universal aesthetic superiority.
