# Changelog

All notable changes to OutfitKit are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-05-11

**Versioning reset.** All previous tags (v1.0.0..v1.5.0 + pypi-v1.1.1..pypi-v1.5.0)
have been deleted from GitHub. This v1.0.0 is the new public baseline for the
universal composition system. From here on, all changes are minor versions
(bug fixes and incremental improvements).

### Architecture

- **Universal composition system.** Components compose with universal classes
  (`.title`, `.sub`, `.label`, `.value`, `.meta`, `.heading`, `.head`, `.body`,
  `.foot`, `.content`, `.scroll`, `.row`, `.col`, `.actions`, `.divider`,
  `.item`, `.icon`, `.icon-disc`, `.close`, `.line-input`) and effect
  modifiers (`.blur`, `.saturate`, `.glass`, `.elevated`, `.brightness`,
  `.dim`). The pattern replaces per-component BEM children.
- **App shell** uses `.app + .page + .content + .scroll` (no more
  `.app__main/.app__body/.app__tabbar/.app__sidebar-overlay`).
- **No CSS class prefix.** Single canonical bundle `dist/outfitkit.min.css`
  emits classes like `.btn`, `.card`, `.modal`. The legacy prefixed bundle
  `dist/outfitkit.ok.css` is retained as a frozen snapshot of the v1.5
  era for consumers that need the `ok-` prefix.
- **No BEM `--variant` modifiers.** Components compose with multi-class
  modifiers Bulma-style: `<button class="btn primary lg">`.

### Tokens

- Ionic-like color schema: each variant (primary, secondary, success, warning,
  danger, info, light, medium, dark) exposes 6 sub-properties (base, rgb,
  contrast, contrast-rgb, shade, tint).
- 5 themes: `default` (erplora dark, the default), `corporate`, `glass`,
  `glass-mono`, `mono`.
- Total tokens: 655 (down from 970 at peak after universalising many
  component-scoped vars).
- Defaults of effect modifiers live in tokens: `--blur-default: 24px`,
  `--saturate: 140%` (with `--saturate-soft: 120%` and `--saturate-strong:
  160%`), `--brightness-default: 1.1`, etc.

### Jinja / JinjaX macros

- 79 dual-mode macros (vanilla `{% from "ui/x.jinja" import x %}` AND JinjaX
  `<X />` from the same file). All emit unprefixed universal classes.
- `register_globals(env)` is now a no-op placeholder (the v1 `ok_prefix`
  argument is gone).
- `css_url()` returns the canonical bundle URL with no `prefix` parameter.

### Removed (breaking vs the deleted v1.5)

- `--ok-` class prefix (default bundle).
- `--ok-*` tokens in source CSS (a retro-compat alias block remains in
  `tokens.css` so external code reading `var(--ok-brand)` still works).
- BEM `--variant` modifier syntax.
- The `ok_prefix` argument and `DEFAULT_OK_PREFIX` symbol in the Python
  package.
- 80+ component-namespaced tokens (`--*-fz`, `--*-pad`, `--*-icon-size`,
  `--*-blur`, `--*-saturate`) that duplicated the universal modifier API.

### Showcase

- 161 pages, all using universal class composition.
- Viewport switcher (`▢ Desktop / ▭ Tablet / ▯ Mobile`) and theme toggle
  driven by Datastar signals.
- Local-mode build flag (`OUTFITKIT_CSS=local`) for offline development.

### Historical context

Prior to this versioning reset, the library shipped tags v1.0.0..v1.5.0
between January and May 2026. Those tags were deleted from GitHub on
2026-05-11 along with the corresponding PyPI publish markers
(pypi-v1.1.1..pypi-v1.5.0). The git history is preserved (commit log
intact); only the tag/release labels were reset.

---

## [1.5.0] — 2026-05-10  (superseded — see 1.0.0 reset above)

### Changed

- **Default bundle (`outfitkit.css` / `outfitkit.min.css`) now strips `--ok-`
  from CSS custom properties too**, not just from class selectors. Consumers
  of the unprefixed bundle can write `var(--brand)`, `var(--ink-3)`,
  `var(--space-4)` instead of `var(--ok-brand)`. This makes the unprefixed
  bundle truly prefix-free. The prefixed bundle (`outfitkit.ok.css`) is
  unchanged. **Migration**: search-and-replace `var(--ok-` → `var(--` in
  any consumer that loads the unprefixed bundle.
- Keyframe and `animation-name` identifiers (`ok-spin`, `ok-pulse`, …) keep
  their prefix in both bundles, since they share a global namespace with
  any consumer-defined `@keyframes` and renaming them would risk collisions.

### Added

- **`Section` macro + `.ok-section` CSS**: composable section wrapper for
  marketing/public pages. Props: `title`, `subtitle`, `icon` (iconify name),
  `icon_variant` (`brand` | `leaf` | `warn` | `danger` | `info` | `neutral`),
  `align` (`center` | `left`), `padded` (default `True`), `container`
  (`default` | `narrow` | `wide` | `none`). Slot receives the section body.
  Replaces the 13× hand-rolled `<section><div class="container"><div class="section-header"><div class="icon-circle">…` pattern in ERPlora's landing.

## [1.4.0] — 2026-05-10

### Added

- **`Navbar` macro + `.ok-navbar` CSS**: composable sticky top bar for
  marketing / public sites. Slot-only (`{{ caller() }}`); the consumer fills
  the brand, nav links, language selector, CTA, and mobile menu. Glass
  background, mobile-menu friendly chrome (CSS-only via consumer-provided
  hidden checkbox + `:has()` selector).
- **`Footer` macro + `.ok-footer` CSS**: composable footer container with
  optional helpers (`.ok-footer__columns`, `.ok-footer__col`,
  `.ok-footer__col-title`, `.ok-footer__link`, `.ok-footer__bottom`,
  `.ok-footer__social`, `.ok-footer__social-icon`). 2→5 column responsive
  grid. Slot-only.

Both consumed by ERPlora Cloud's new `PublicLayout.jinja` shell on the
landing page migration.

## [1.3.1] — 2026-05-10

### Fixed

- **Modal / Drawer backdrop interception**: the `<div class="ok-backdrop">`
  was emitted as a sibling of `.ok-modal-root` / `.ok-drawer-root` instead
  of a descendant. CSS rules like `.ok-modal-root .ok-backdrop` never
  applied, and the backdrop intercepted clicks even when the overlay was
  closed (verified end-to-end with Playwright). The macros now place the
  backdrop inside the root and `overlays.css` uses
  `[data-state="open"]` / `:not([data-state="open"])` selectors to switch
  `pointer-events` and `opacity` cleanly.

## [1.0.0] — 2026-05-09

Initial release.

### Added

- **CSS library** with the `ok-*` BEM-light prefix:
  - `tokens.css` — design tokens (palette, spacing, radii, shadows, themes).
  - `base.css` — modern reset + Inter typography.
  - `utilities.css` — atomic utility classes (`.ok-flex`, `.ok-gap-*`, `.ok-text-*`, `.ok-c-*`).
  - `outfitkit.css` — bundle entry point with `@import` of every layer.
  - 44 component files covering button, badge, card, modal, drawer,
    table, kanban, calendar, chat, charts, kds, pos, manufacturing,
    forms, navigation, overlays, and more.
- **Three default themes** via `[data-theme="..."]`: `erplora` (default,
  dark terracotta), `dark`, `light`.
- **Distribution pipeline**:
  - jsDelivr CDN serves both unminified (`@<tag>/css/outfitkit.css`) and
    minified (`@<tag>/dist/outfitkit.min.css`) bundles.
  - GitHub Action `css-build.yml` bundles + minifies on every tag push.
- **Jinja2 addon** (`outfitkit` PyPI package, not yet published):
  - Five dual-mode pilot components — `button`, `badge`, `card`,
    `modal`, `drawer`. Each works as a vanilla Jinja2 macro
    (`{{ button(...) }}`) or as a JinjaX component
    (`<Button label="..." />`) from the same file.
- **Showcase site** at <https://outfitkit.github.io/outfitkit/>:
  - Built with staticjinja + JinjaX, deployed via the `pages.yml` Action.
  - Each component demo includes live render, source code view, and a
    props API table.
  - Datastar (loaded from CDN) powers interactive demos with no backend.
- **Tests** (19 passing) under `showcase/tests/`:
  - `test_signature_sync.py` — verifies that every component's
    `{#def #}` header and `{% macro %}` signature declare the same
    parameters with the same defaults.
  - `test_dual_mode.py` — verifies that vanilla and JinjaX render paths
    produce the same set of CSS classes for the same inputs.

### Notes

The CSS library is the primary deliverable; the Jinja addon is optional
and consumed only by Python applications that already use Jinja2 (Hub,
Cloud, FastAPI, Flask, Django with the Jinja2 backend).

Components in this release follow the BEM-light convention with the
`ok-*` prefix. The legacy `ux-*` prefix from the predecessor library
(ERPlora UX) is **not** carried over — consumers migrating from
`ERPlora/ux` need to rename their class references.

[1.0.0]: https://github.com/OutfitKit/outfitkit/releases/tag/v1.0.0
