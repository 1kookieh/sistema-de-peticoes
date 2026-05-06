---
name: "Sistema de Petições Design System"
version: "alpha"
description: "Judicial paper-and-ink design system for a local-first Brazilian legal petition workspace with supervised AI drafting."
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
  accent: "#a36b21"
  on-accent: "#fffefa"
  success: "#1b7a42"
  on-success: "#ffffff"
  warning: "#a16207"
  on-warning: "#ffffff"
  danger: "#b42318"
  on-danger: "#ffffff"
  tab-active-bg: "#111111"
  tab-active-fg: "#fffefa"
  overlay: "rgba(18, 18, 18, 0.50)"
  grid-line: "rgba(163, 107, 33, 0.055)"
  provider-local: "#1b7a42"
  provider-external: "#a16207"
  review-required: "#a16207"
  report-ready: "#1b7a42"
  llm-error: "#b42318"
  primary-dark: "#f6f0e5"
  on-primary-dark: "#161616"
  background-dark: "#10100f"
  surface-dark: "#181715"
  surface-elevated-dark: "#22201c"
  on-surface-dark: "#f6f0e5"
  muted-dark: "#b0a796"
  border-dark: "#38342c"
  focus-dark: "#d8a354"
  accent-dark: "#d8a354"
  on-accent-dark: "#161616"
  success-dark: "#75d995"
  on-success-dark: "#10100f"
  warning-dark: "#f5c46a"
  on-warning-dark: "#10100f"
  danger-dark: "#ff8a7d"
  on-danger-dark: "#10100f"
  tab-active-bg-dark: "#f6f0e5"
  tab-active-fg-dark: "#161616"
  overlay-dark: "rgba(0, 0, 0, 0.62)"
  grid-line-dark: "rgba(216, 163, 84, 0.08)"
  provider-local-dark: "#75d995"
  provider-external-dark: "#f5c46a"
  review-required-dark: "#f5c46a"
  report-ready-dark: "#75d995"
  llm-error-dark: "#ff8a7d"
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
- Product: local-first workspace to draft, validate, review, render, download, and audit Brazilian legal petition drafts as `.docx`.
- Visual direction: judicial paper — warm parchment canvas, near-black ink, restrained gold accent, document-grade hierarchy.
- Personality: serious, calm, archival, precise, professional, and supervised; never playful, marketing-bright, or chatbot-like.
- Density: comfortable for long-form legal reading; compact enough for workspace productivity.
- User-facing UI language is Portuguese.
- The UI supports supervised legal drafting, not automatic filing. It must reinforce lawyer review, auditability, confidentiality, and local control.
- The UI must never feel like a generic SaaS dashboard, fintech app, AI chatbot wrapper, colorful productivity template, or protocol automation tool.
- Existing tokens were extracted from `web/styles.css`; light and dark themes are implemented and must be preserved.
- No Tailwind in this project; write tokenized vanilla CSS in `web/styles.css`.

## Colors
- `background` / `background-dark`: full app canvas. Preserve the parchment/grid mood; never use as a card fill.
- `surface` / `surface-dark`: cards, sidebar, panels, modals, inputs, reports, and primary reading containers.
- `surface-elevated` / `surface-elevated-dark`: hover wells, badge fills, secondary insets, disabled surfaces, and skeleton loading.
- `primary` / `primary-dark`: main ink role for headings, primary actions, active emphasis, and high-priority UI.
- `on-primary` / `on-primary-dark`: text/icons placed on primary fills only.
- `on-surface` / `on-surface-dark`: primary text and line icons on normal surfaces.
- `muted` / `muted-dark`: secondary text, captions, inactive labels, metadata. Never use for critical values or legal warnings.
- `border` / `border-dark`: cards, inputs, dividers, table lines. Prefer borders over shadows for static hierarchy.
- `focus` / `focus-dark`: keyboard focus ring and legal gold accent. Must remain visible on every interactive element.
- `accent` / `accent-dark`: restrained gold accent for brand mark, decorative separators, focus-adjacent emphasis, and audit charts.
- `success`, `warning`, `danger` and dark counterparts: status only. Always pair with icon or text; never rely on color alone.
- `provider-local` / `provider-local-dark`: local or mock provider status such as `mock` and `ollama`.
- `provider-external` / `provider-external-dark`: external provider status such as `openai` and `anthropic`; always pair with consent copy.
- `review-required` / `review-required-dark`: human legal review required, pending review, or draft-not-final warning.
- `report-ready` / `report-ready-dark`: report generated, download available, or successful validation output.
- `llm-error` / `llm-error-dark`: LLM error, missing consent, provider failure, or blocked external call.
- `tab-active-bg` / `tab-active-fg`: active sidebar/tab treatment. Use these tokens instead of hardcoded `#111111` / `#fffefa`.
- `overlay` / `overlay-dark`: modal and drawer scrims.
- `grid-line` / `grid-line-dark`: faint background grid. Do not replace with unrelated gradients.

## Typography
- H1 uses Georgia serif to evoke judicial documents and formal written work.
- H2/H3 use Inter with strong weights for workspace hierarchy, cards, panels, modal titles, and report sections.
- Body, labels, buttons, inputs, navigation, status copy, and tables use Inter.
- Code uses the monospace stack for paths, hashes, logs, JSON, provider names, report metadata, CLI snippets, and API details.
- Type scale is intentionally restrained; avoid sizes outside the YAML scale.
- Body line-height must stay at or above 1.5 for dense legal copy.
- Avoid all-caps paragraphs; reserve uppercase for short labels, badges, and brand tagline.
- Do not introduce decorative script, display, novelty, or marketing fonts.

## Layout
- Shell: 280px sticky sidebar + fluid main column using the existing `app-shell` grid.
- Collapse to a single-column layout below the `md` breakpoint.
- Main content max width is approximately 1100px and centered; dashboards may use the full content column.
- Spacing uses the 8px scale only: `xs`, `sm`, `md`, `lg`, `xl`, `xxl`.
- Section rhythm: `lg` between related blocks and `xl` between major sections.
- Minimum touch target: 40×40px; prefer 44×44px when adding new controls.
- Important actions must stay visually close to the content they affect.
- IA/chat workspace must keep composer, provider selector, consent controls, and generated output visually connected.
- Report/download areas must separate `.docx` drafts from JSON/HTML audit reports.
- Preserve the faint 34px background grid; do not replace it with decorative gradients.

## Elevation & Depth
- Default hierarchy is flat: parchment background, tonal surfaces, borders, then restrained shadows.
- Use `shadow.sm` for cards, dropdowns, and resting surfaces that need separation.
- Use `shadow.md` only for floating overlays: modals, popovers, command palettes, provider menus, and active layered UI.
- Do not stack multiple shadows.
- Do not use colored shadows, glow effects, blur-heavy glassmorphism, or frosted surfaces.
- Prefer borders for permanent structure and shadows for temporary layered UI.

## Shapes
- Buttons, inputs, badges, and sidebar items use `rounded.sm` for crisp document-like controls.
- Cards, modals, and panels use `rounded.md`.
- Large hero or illustrated containers may use `rounded.lg`.
- Avoid `rounded-full` except for intentional small status dots or avatars.
- The brand mark remains a compact serif “P” monogram on ink fill until an official asset replaces it.
- Icons use the existing line-icon style: single color, approximately 1.8px stroke, never multicolor emoji-like icons.
- Provider icons may identify provider type, but must remain line-based, restrained, and non-promotional.

## Components
- Buttons: primary = ink fill/cream text; secondary = surface + border; danger = destructive flows only.
- Inputs: surface background, 1px border, visible label, gold focus ring, no inner shadow.
- Cards: surface background, border, `shadow.sm`, `lg` padding; card headings use H2/H3 scale.
- Sidebar tab: muted at rest, `surface-elevated` on hover, active uses `tab-active-bg` / `tab-active-fg`.
- Badge: small uppercase label with subtle letter spacing, `surface-elevated` fill, semantic text when status-related.
- Alert/Toast: semantic border-left + icon + body text. Critical errors must not rely on transient toasts.
- Modal: `surface`, `shadow.md`, max-width around 560px, centered, `overlay` scrim, explicit cancel/confirm actions.
- Empty state: centered `muted` text, optional line icon, one clear next step when available.
- Loading state: skeleton blocks tinted from `surface-elevated`; preserve layout dimensions.
- Charts: use ink, gold, status colors, and neutral surfaces; never use default chart-library palettes.
- Dashboard charts must feel like audit/reporting visuals: restrained, legible, low-saturation, never decorative analytics.
- Provider selector: show provider identity clearly and distinguish local providers (`mock`, `ollama`) from external providers (`openai`, `anthropic`).
- External consent warning: must be visible, textual, and explicit before external provider use; never hide it behind color-only status.
- Redaction warning: must state that masking is partial; never imply full anonymization.
- Human review banner: generated drafts must preserve the message that a responsible lawyer must review before real use.
- Report/download actions: visually distinguish generated `.docx` drafts from JSON/HTML audit reports.
- Validation warning: use `warning` plus text for missing data, downgraded draft quality, or review-required states.
- LLM error: use `llm-error` plus clear explanation and next step; never silently fallback visually.
- IA chat flow: must feel like supervised legal drafting, not a generic chatbot.

## Interaction States
- Hover: use `surface-elevated`, border emphasis, or small translate on navigation only; never reflow layout.
- Focus: `:focus-visible` uses 3px gold outline with 3px offset. Mandatory on every interactive element.
- Active/pressed: darker ink fill or slight scale-down; no large transforms.
- Selected/current: combine fill, contrast, weight, and position; never color alone.
- Disabled: 50% opacity, `cursor: not-allowed`, no hover effect; explain disabled critical actions when possible.
- Loading: preserve control size and expose busy state to assistive technology when practical.
- Error/empty/success: pair status color with text and/or icon.
- `llm_error`: show blocked/error state with clear text, provider context, and required action.
- Consent required: show explicit external-provider consent state before enabling the call.
- Pending human review: show as a persistent review-required state, not a temporary toast.
- Report generated: show persistent success state with clear download/report actions.
- Download available: distinguish DOCX draft download from JSON/HTML report download.
- Honor `prefers-reduced-motion: reduce`: set transitions to near-zero and disable translate/scale animations.

## Do's and Don'ts
- Do use YAML tokens and mirror them as CSS custom properties in `:root` and `:root[data-theme="dark"]`.
- Do preserve the parchment, ink, gold, archival legal mood across new screens.
- Do keep Portuguese as the user-facing language.
- Do keep legal copy formal, direct, and clear; avoid casual chatbot microcopy.
- Do make audit/report states visually clear: generated, pending review, validation warning, LLM error, download available.
- Do validate WCAG AA contrast when introducing new text/background pairs.
- Do update this file and `web/styles.css` in the same change that introduces a new token or component pattern.
- Do bump `web/sw.js` cache version when shipping visual/static asset changes.
- Don't add blue, purple, teal, neon, playful gradients, or unrelated accent colors.
- Don't use emoji as UI iconography; use the existing line-icon sprite/style.
- Don't add glassmorphism, heavy shadows, glow effects, or rounded-full pill UI.
- Don't ship partial dark mode; every light token addition needs a dark counterpart, and vice versa.
- Don't create one-off component styles; extend shared classes in `web/styles.css`.
- Don't redesign existing screens unless explicitly requested or required for accessibility/consistency.
- Don't make the IA tab feel like a generic chatbot.
- Don't hide external-provider consent, redaction limits, or review warnings in small muted text only.
- Don't make any generated petition look ready to file or protocol.

## Design Debt & Open Questions
- Current identity is the serif “P” monogram plus “Sistema de Petições” Georgia wordmark; treat it as official until replaced.
- Brand tagline remains `PETIÇÕES · MINUTAS · DOCX` in Inter 900 uppercase with 0.14em tracking.
- Brand gold is `accent` (`#a36b21`) and `accent-dark` (`#d8a354`).
- Legacy files in `web/` (`ui.js`, `api.js`, `render.js`, `state/store.js`) predate the workspace refactor; avoid broad UI rewrites until cleanup is scoped.
- Charts still need a shared `chart-tokens` map; do not introduce chart-library default palettes.
- Service worker (`web/sw.js`) caches static assets; bump cache version when visual files change.
- Two stale tests reference the old generation form; adjust before broad UI work if still present.
- Dark status tokens were added to complete theme parity; verify contrast in actual components before production use.
- Add or standardize shared visual states for `llm_error`, pending human review, redaction applied, external consent required, report generated, and DOCX download available.
- Confirm whether provider icons should remain CSS/SVG-only or be mapped through a tiny provider visual registry.

## Agent Usage Rules
- Read `DESIGN.md` before creating or changing UI, CSS, components, theme, icons, charts, or static visual assets.
- Preserve existing UI unless redesign is explicitly requested or needed for accessibility.
- Use existing tokens before inventing new colors, spacing, shadows, radii, fonts, or component styles.
- Do not introduce new visual tokens without updating `DESIGN.md` and `web/styles.css` in the same change.
- Do not create one-off component styles; extend shared classes.
- Validate text/background contrast against WCAG AA for normal text.
- Respect `prefers-reduced-motion`.
- Do not add a light token without its dark counterpart, or a dark token without its light counterpart.
- Keep generated UI consistent with the components and states defined here.
- Keep user-facing text in Portuguese.
- Keep the UI aligned with supervised legal drafting, local control, auditability, and human review.
- Never make generated content appear ready for filing or protocol.
- Bump `web/sw.js` cache version when visual/static assets change.
- CSS: mirror YAML tokens as stable custom properties on `:root` and `:root[data-theme="dark"]`.
- No Tailwind in this project; write tokenized vanilla CSS in `web/styles.css`.