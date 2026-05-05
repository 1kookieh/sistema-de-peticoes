---
name: "Forum"
version: "alpha"
description: "Judicial-toned, paper-and-ink design system for a Brazilian legal petition workspace."
colors:
  primary: "#161616"
  on-primary: "#fffefa"
  background: "#f5f2ea"
  surface: "#fffdf8"
  surface-elevated: "#f7f2e8"
  on-surface: "#161616"
  muted: "#4f4a43"
  border: "#d6cbb9"
  focus: "#a36b21"
  success: "#1b7a42"
  on-success: "#ffffff"
  warning: "#a16207"
  on-warning: "#ffffff"
  danger: "#b42318"
  on-danger: "#ffffff"
  primary-dark: "#f6f0e5"
  on-primary-dark: "#161616"
  background-dark: "#10100f"
  surface-dark: "#181715"
  surface-elevated-dark: "#22201c"
  on-surface-dark: "#f6f0e5"
  muted-dark: "#b0a796"
  border-dark: "#38342c"
  focus-dark: "#d8a354"
typography:
  h1:
    fontFamily: "Georgia, 'Times New Roman', serif"
    fontSize: "clamp(2rem, 3vw, 3rem)"
    fontWeight: 700
    lineHeight: "1.15"
  h2:
    fontFamily: "Inter, 'Segoe UI', system-ui, sans-serif"
    fontSize: "1.05rem"
    fontWeight: 800
    lineHeight: "1.3"
  h3:
    fontFamily: "Inter, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 800
    lineHeight: "1.35"
  body:
    fontFamily: "Inter, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 400
    lineHeight: "1.5"
  label:
    fontFamily: "Inter, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.82rem"
    fontWeight: 700
    lineHeight: "1.2"
  small:
    fontFamily: "Inter, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.78rem"
    fontWeight: 500
    lineHeight: "1.4"
  code:
    fontFamily: "ui-monospace, 'JetBrains Mono', 'Fira Code', Consolas, monospace"
    fontSize: "0.85rem"
    fontWeight: 500
    lineHeight: "1.5"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  xxl: "48px"
rounded:
  sm: "7px"
  md: "10px"
  lg: "14px"
  xl: "20px"
shadow:
  sm: "0 1px 2px rgba(18, 18, 18, 0.06)"
  md: "0 1px 2px rgba(18, 18, 18, 0.06), 0 16px 42px rgba(18, 18, 18, 0.10)"
breakpoints:
  sm: "640px"
  md: "768px"
  lg: "1024px"
  xl: "1280px"
motion:
  fast: "120ms cubic-bezier(0.2, 0.8, 0.2, 1)"
  normal: "200ms cubic-bezier(0.2, 0.8, 0.2, 1)"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "{spacing.sm} {spacing.md}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    borderColor: "{colors.border}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "{spacing.sm} {spacing.md}"
  button-danger:
    backgroundColor: "{colors.danger}"
    textColor: "{colors.on-danger}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "{spacing.sm} {spacing.md}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    borderColor: "{colors.border}"
    rounded: "{rounded.sm}"
    padding: "{spacing.sm} {spacing.md}"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: "{spacing.lg}"
    shadow: "{shadow.sm}"
  badge:
    backgroundColor: "{colors.surface-elevated}"
    textColor: "{colors.on-surface}"
    typography: "{typography.small}"
    rounded: "{rounded.sm}"
    padding: "{spacing.xs} {spacing.sm}"
  alert:
    backgroundColor: "{colors.surface-elevated}"
    textColor: "{colors.on-surface}"
    borderColor: "{colors.border}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  modal:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    shadow: "{shadow.md}"
---

# Design System

## Overview
- Product: local-first workspace to draft, validate, and render Brazilian legal petitions as `.docx`.
- Visual direction: "judicial paper" — warm parchment background, near-black ink, restrained gold accent. [DESIGN DECISION]
- Personality: serious, document-grade, calm, archival; never playful or marketing-bright.
- Density: comfortable for long-form legal text; generous line-height; firm hierarchy.
- The UI must never feel like a SaaS dashboard, fintech app, or AI chatbot wrapper.
- Existing tokens were extracted from `web/styles.css`; light + dark are already implemented and must be preserved.

## Colors
- `background` (`#f5f2ea`): page canvas. Use behind everything; never as button/card fill.
- `surface` (`#fffdf8`): cards, sidebar, panels, modals, inputs. Default container.
- `surface-elevated` (`#f7f2e8`): hover wells, badge fills, secondary insets.
- `on-surface` / `primary` (`#161616`): primary ink for body, headings, primary buttons. Active sidebar tab uses near-pure `#111`.
- `muted` (`#4f4a43`): secondary text, captions, inactive labels. Never on `surface-elevated` for body copy without size ≥ `body`.
- `border` (`#d6cbb9`): hairlines on cards, inputs, dividers. Prefer borders over shadows.
- `focus` (`#a36b21`, gold): focus ring + decorative legal accent. Never used as a fill for primary actions.
- `success` / `warning` / `danger`: status only. Always paired with an icon or text — never color-only signals.
- Dark tokens (`*-dark`) mirror the same roles via `:root[data-theme="dark"]`. Do not introduce new colors without adding a dark counterpart.

## Typography
- Headings (`h1`): Georgia serif — evokes judicial documents.
- UI text, labels, body, buttons, controls: Inter sans.
- Code/monospace: system mono stack for log/JSON blocks (reports, hashes).
- Type scale is restrained: avoid sizes outside the YAML scale.
- Weight rules: body 400, labels/buttons 700–800, brand/active states up to 900.
- Line-height ≥ 1.5 for body to support dense legal copy.

## Layout
- Shell: 280px sticky sidebar + fluid main column (`app-shell` grid). Collapse to single column under `md`.
- Spacing base: 8px scale (`xs..xxl`). Compose paddings/gaps from these tokens only.
- Container: main content max-width ~1100px, centered; cards stretch to column.
- Section rhythm: `lg` (24px) between blocks, `xl` (32px) between major sections.
- Touch targets ≥ 40×40px on mobile; sidebar tabs and form controls already meet this.
- Background uses a faint 34px grid (`--bg-grid`) — preserve; do not replace with gradients.

## Elevation & Depth
- Prefer borders + tonal surfaces over shadows.
- `shadow.sm`: cards, dropdowns at rest.
- `shadow.md`: only for floating overlays (modals, popovers, active sidebar tab).
- Never stack multiple heavy shadows; never use colored or glow shadows.
- No glassmorphism, no blurs as primary depth cue.

## Shapes
- Buttons, inputs, badges, sidebar items: `rounded.sm` (7px) — crisp, document-like.
- Cards, modals, panels: `rounded.md` (10px).
- Large hero/illustrated containers: `rounded.lg` (14px).
- Avatars / brand mark: 9px square (already used by `.brand-mark`).
- Icons render as 1.8px stroke line icons; never filled, never multicolor.

## Components
- Button: primary = ink fill / cream text; secondary = surface + border; danger reserved for destructive flows.
- Input: surface bg, 1px border, focus ring uses `focus` (gold), no inner shadow.
- Card: surface bg, border, `shadow.sm`, `lg` padding; headings use `h2`.
- Sidebar tab: muted at rest, `surface-elevated` on hover, near-black fill when active (do not change).
- Badge: small, uppercase letter-spacing, surface-elevated fill.
- Alert/Toast: full-width inside container, status border-left + icon + body text.
- Modal: surface bg, `shadow.md`, max-width 560px, centered, scrim `rgba(18,18,18,0.5)`.
- Empty/Loading state: centered text in `muted`, optional icon, no spinners that hijack focus.
- Charts (dashboard): use ink + gold + neutral surfaces; never default chart-library palettes.

## Interaction States
- Hover: `surface-elevated` background or +2px translate for nav items only; never reflow layout.
- Focus: `:focus-visible` → 3px gold outline, 3px offset. Mandatory on every interactive element.
- Active/pressed: darker ink fill or 1% scale-down; no large transforms.
- Selected/current (sidebar, tabs): near-black fill with cream text.
- Disabled: 50% opacity, `cursor: not-allowed`, no hover effect.
- Loading: skeleton blocks tinted from `surface-elevated`; preserve layout dimensions.
- Error/empty/success: pair color with icon and text label.
- Honor `prefers-reduced-motion: reduce` → set transitions to `0.01ms` and disable translate/scale.

## Do's and Don'ts
- Do use the YAML tokens; mirror them as CSS custom properties (already done in `:root`).
- Do keep Portuguese as the user-facing language.
- Do preserve the parchment + ink mood across new screens.
- Do test contrast (WCAG AA) when introducing new text/background pairs.
- Do update this file in the same change that introduces a new token or component pattern.
- Don't add blue, purple, teal, or neon accents.
- Don't introduce gradients beyond the existing background grid blend.
- Don't use emoji as UI iconography — use the existing line-icon sprite.
- Don't add glassmorphism, heavy shadows, or rounded-full pills.
- Don't ship a partial dark mode; if a new token is added, add the `*-dark` counterpart.
- Don't create one-off component styles — extend the shared classes in `web/styles.css`.
- Don't redesign existing screens unless explicitly requested or required for accessibility.

## Design Debt & Open Questions
- [OFFICIAL LOGO REQUIRED] — current `.brand-mark` is a typographic placeholder.
- [OFFICIAL BRAND GUIDELINE REQUIRED] — gold tone (`#a36b21`) chosen by inference; confirm with stakeholder.
- Legacy files in `web/` (`ui.js`, `api.js`, `render.js`, `state/store.js`) predate the workspace refactor — pending cleanup.
- Charts use inline SVG without a shared theme module — consider extracting tokens.
- Service worker (`web/sw.js`) caches static assets; bump version when shipping visual changes.
- Two stale tests reference the old generation form — adjust before broad UI work.
- [INFERENCE — CONFIRM] Sidebar tab forced `#111111` overrides theme variables; intentional for contrast but worth tokenizing.

## Agent Usage Rules
- Read `DESIGN.md` before creating or changing UI, CSS, components, or theme.
- Preserve existing UI unless redesign is explicitly requested or needed for accessibility.
- Use existing tokens before inventing new colors, spacing, shadows, radii, or fonts.
- Do not introduce new visual tokens without updating `DESIGN.md` in the same change.
- Do not create one-off component styles; extend shared classes.
- Validate text/background contrast against WCAG AA for normal text.
- Respect `prefers-reduced-motion`.
- Do not introduce a new dark token without its light counterpart, and vice versa.
- Prefer accessible, semantic, responsive UI over decorative novelty.
- Keep generated UI consistent with the components and states defined here.
- CSS: mirror YAML tokens as stable custom properties on `:root` and `:root[data-theme="dark"]`; avoid duplicated hard-coded values.
- No Tailwind in this project — write tokenized vanilla CSS in `web/styles.css`.
