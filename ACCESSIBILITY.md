# Accessibility

## Target

The public site targets **WCAG 2.2 Level AA**, a stronger and more current target than WCAG 2.1 Level AA. This is a self-assessment target, not a W3C certification.

## Built-in measures

- semantic HTML landmarks;
- one clear page-level heading;
- keyboard-operable native controls;
- skip link on pages with repeated navigation;
- visible `:focus-visible` indicator;
- high-contrast light and dark system themes;
- 44×44 CSS minimum for primary controls;
- no critical information conveyed only by color;
- the rich English home uses one pausable R17 interaction authority for the exploratory flow field and low-opacity page-wide pointer wake; ordinary sessions start automatically, explicit Pause freezes both fields, a fresh browsing session starts alive again, and reduced-motion starts static;
- pointer velocity affects only an explicitly labelled UI wake; Light/Balanced/Viscous are interaction-response modes, not physical viscosity, and the visualization is not the computed 2026 solution;
- the hero permits vertical touch scrolling, hidden/offscreen work is bounded, Canvas2D failure falls back to the static SVG, and the zero-JavaScript path remains complete;
- reduced-motion handling;
- responsive layout without required horizontal scrolling at ordinary phone widths;
- correct language and text-direction declarations;
- Arabic right-to-left layout;
- language changes marked for canonical English scientific blocks;
- no automatic language redirect;
- no analytics, cookies, remote fonts, or third-party scripts by default.

## Automated release checks

`python3 scripts/audit_contrast.py` calculates contrast ratios from the actual CSS design tokens used for foreground/background pairs and checks focus/control requirements.

`python3 scripts/audit_site.py` checks the generated pages for structural issues including language and direction, headings, duplicate IDs, form labels, skip links, positive tabindex, autoplay, missing image alternatives, broken local links, and language alternates.

Automated tools cannot establish full WCAG conformance.

## Manual WCAG AA release checklist

Before a production `1.0` accessibility claim, audit representative pages in every language and both system color schemes with:

1. keyboard-only navigation, including language menus and mission filtering;
2. browser zoom at 200% and text-only zoom where supported;
3. reflow at 320 CSS px width;
4. NVDA + Firefox or Chrome on Windows;
5. VoiceOver + Safari on macOS/iOS;
6. TalkBack + Chrome on Android;
7. Arabic reading order and focus order;
8. error identification on host-native contribution forms;
9. focus visibility and unobscured focus under sticky navigation;
10. target sizing and spacing;
11. translated-page language switching announced correctly;
12. contrast of any future graphics, status indicators, charts, or custom components.

Record browser, assistive technology, version, page URL, criterion, outcome, and remediation commit for each finding.

## Reporting a problem

Use the public review issue form and label the target as an accessibility review.
