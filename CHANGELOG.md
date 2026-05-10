# Changelog

All notable changes to OutfitKit are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
adheres to [Semantic Versioning](https://semver.org/).

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
