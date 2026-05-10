# OutfitKit — Architecture

The 30-minute read for a new maintainer. After this, jump to:
- [`MAINTAINING.md`](./MAINTAINING.md) — daily ops, hot paths, troubleshooting.
- [`ADDING-A-COMPONENT.md`](./ADDING-A-COMPONENT.md) — how to ship a new component end-to-end.
- [`THEMES.md`](./THEMES.md) — the theme system + how to add a new template.
- [`PUBLISHING.md`](./PUBLISHING.md) — release pipelines (CDN, PyPI, Pages).

---

## What OutfitKit is

Three independent things that ship together:

1. **A CSS component library** — ~260 semantic blocks (BEM-light) built on CSS custom properties (`--ok-*` tokens). One `<link>` and you have buttons, cards, modals, datatables, charts, POS, calendar, kanban, the works. **No JavaScript required.**
2. **A Jinja2 macro package** (`outfitkit` on PyPI) — every component has a dual-mode macro: works as `{% from "ui/button.jinja" import button %}` (vanilla Jinja2) AND as `<Button label="…" />` (JinjaX) from the same file. Optional layer for Python backends.
3. **A live showcase** at <https://outfitkit.github.io/outfitkit/> — every component with Preview / HTML / Jinja / JinjaX / Usage tabs, plus 90+ app demo pages. Runs on staticjinja, deployed to GitHub Pages.

The CSS bundle is the **fundamental** layer. The macros are a convenience for Python consumers. The showcase is a sales pitch + visual regression catalogue.

---

## Repo layout — what's in each top-level directory

```
outfitkit/
├── css/                ← THE LIBRARY (CSS source)
│   ├── tokens.css      ← --ok-* design tokens (colours, spacing, radii, themes)
│   ├── base.css        ← reset + typography
│   ├── utilities.css   ← .ok-flex, .ok-gap-*, .ok-text-*, etc.
│   ├── outfitkit.css   ← entry point — @imports everything in order
│   ├── components/     ← 44 CSS files, one per family (button, card, table, ...)
│   └── themes/         ← 5 opt-in templates (default, corporate, glass, glass-mono, mono)
│
├── dist/               ← BUILD OUTPUT (CI-only; never edit by hand)
│   ├── outfitkit.css         ← unprefixed bundle, default
│   ├── outfitkit.min.css
│   ├── outfitkit.ok.css      ← ok-prefixed bundle, opt-in
│   └── outfitkit.ok.min.css
│
├── showcase/           ← THE PYPI PACKAGE + THE DEMO SITE
│   ├── pyproject.toml          ← `outfitkit` package definition
│   ├── build.py                ← staticjinja site generator
│   ├── src/outfitkit/          ← what `pip install outfitkit` ships
│   │   ├── __init__.py         ← API: TEMPLATES_DIR, register_globals, css_url
│   │   └── templates/ui/       ← 69 dual-mode macro files
│   ├── pages/                  ← demo pages (.html templates extending _layout.jinja)
│   │   ├── _layout.jinja       ← the showcase shell (sidebar, topbar, switchers, iframe)
│   │   ├── components/         ← 68 pages, one per component family
│   │   └── apps/               ← 93 pages, one per app screen, 16 sections
│   ├── chrome/                 ← showcase-only macros (sidebar, demo_frame, search)
│   ├── static/                 ← favicon, theme-runtime.js, og-image
│   └── tests/
│       ├── test_dual_mode.py   ← parity check: macro render == JinjaX render
│       └── visual/             ← Playwright visual regression suite (see MAINTAINING.md)
│
├── docs/               ← THIS DIRECTORY
├── .github/workflows/  ← 3 CI pipelines (css-build, pages, pypi-publish)
├── README.md           ← user-facing intro (consumers, not maintainers)
├── llms.txt + llms-full.txt ← machine-readable docs for LLMs/agents
└── AUDIT.md            ← log of past visual-regression findings (reference)
```

---

## The three pipelines

Each maps to a **different artifact** with a **different trigger**. They don't depend on each other.

```
                ┌─────────────────────────────────────────┐
                │  push to main                            │
                └────────────────┬────────────────────────┘
                                 │
                                 ▼
              ┌─────────────────────────────────────┐
              │  pages.yml                          │  → deploys showcase to
              │  staticjinja build → GH Pages       │    https://outfitkit.github.io/outfitkit/
              └─────────────────────────────────────┘

                ┌─────────────────────────────────────────┐
                │  git tag v1.4.0 + git push --tags       │
                └────────────────┬────────────────────────┘
                                 │
                                 ▼
              ┌─────────────────────────────────────┐
              │  css-build.yml                      │  → commits dist/ to the tag
              │  bundle CSS, minify, generate       │    jsDelivr serves
              │  prefixed AND unprefixed variants   │    @v1.4.0/dist/*
              └─────────────────────────────────────┘

                ┌─────────────────────────────────────────┐
                │  git tag pypi-v1.4.0 + git push --tags  │
                └────────────────┬────────────────────────┘
                                 │
                                 ▼
              ┌─────────────────────────────────────┐
              │  pypi-publish.yml                   │  → publishes outfitkit==1.4.0
              │  build wheel + sdist → PyPI OIDC    │    https://pypi.org/p/outfitkit
              └─────────────────────────────────────┘
```

See [`PUBLISHING.md`](./PUBLISHING.md) for the per-pipeline details.

---

## How the showcase actually renders

When a user visits a `/components/X.html` page:

1. The page extends `_layout.jinja`, which renders the showcase shell: sidebar with all 161 page links, topbar with Dark/Light + Template + Viewport switchers, then the inline `{% block content %}` of the page.
2. `theme-runtime.js` (synchronous, before Datastar) reads localStorage and sets `data-theme` and `data-template` on `<html>`.
3. The CSS rules (default tokens + active template overrides) paint everything.
4. Datastar wires the topbar switchers — clicking Dark calls `window.okTheme.set('erplora', $template)` which updates `<html data-theme>` and re-paints.

When a user visits a `/apps/X.html` page:

1. Same `_layout.jinja`, but the `<script>` block at the top detects `location.pathname.includes('/apps/')`.
2. It replaces the `.doc__body` content with an `<iframe src="<page>?embed=1">`.
3. The iframe loads the same HTML, which detects `?embed=1` and strips the showcase chrome (sidebar, topbar, switchers).
4. The iframe is now a clean, full-bleed render of the app — its own `@media` queries fire correctly because the iframe **is** a real viewport.
5. Theme sync between parent and iframe happens via `storage` event + `postMessage`.

This iframe pattern is what makes the Mobile/Tablet viewport switcher actually work: clamping the iframe `max-width` is equivalent to running the app on a real phone, because the iframe's CSS sees the clamped width as its real viewport.

See [`MAINTAINING.md`](./MAINTAINING.md#hot-paths) for which files are critical here.

---

## Design tokens & themes — at a glance

`css/tokens.css` defines ~140 CSS custom properties under `:root, [data-theme="erplora"]` (the dark default). It also defines the light variant under `[data-theme="erplora-light"]`.

Themes live in `css/themes/<name>.css` and override a subset of those tokens, gated by:

```css
[data-template="glass-mono"][data-theme="erplora"]      { /* dark variant */ }
[data-template="glass-mono"][data-theme="erplora-light"] { /* light variant */ }
```

So composition is `data-template × data-theme`. Five templates × 2 schemes = 10 visual variants on top of the unstyled default. CSS custom properties are inheritance-driven, so the same component CSS works under any combination — no per-theme component overrides.

See [`THEMES.md`](./THEMES.md) for adding a new one.

---

## Macro convention

Every macro file under `showcase/src/outfitkit/templates/ui/<name>.jinja` follows this **dual-mode** pattern:

```jinja
{#def label, variant="primary", size="md", attrs=None #}

{% macro button(label, variant="primary", size="md", attrs=None) -%}
{%- set _attrs = attrs|attr('as_dict')|default(attrs or {}) -%}
<button class="{{ ok_prefix }}btn {{ ok_prefix }}btn--{{ variant }}{% if size != 'md' %} {{ ok_prefix }}btn--{{ size }}{% endif %}"
  {%- for k, v in _attrs.items() %} {{ k }}="{{ v }}"{% endfor %}>
  {{ label }}
</button>
{%- endmacro %}

{% if label is defined %}{{ button(label, variant=variant, size=size, attrs=attrs) }}{% endif %}
```

Three pieces:

1. **`{#def #}`** — JinjaX header. JinjaX reads it to discover props.
2. **`{% macro %}`** — the real Jinja2 macro, importable by anyone.
3. **`{% if X is defined %}` shim** — the magic that makes both modes work from the same file. JinjaX injects the props before evaluating the body, so the `if` is true and the macro runs. Vanilla `{% from %}` doesn't define those names → the `if` is false → only the macro is exposed for callers.

The `{{ ok_prefix }}` placeholder is a Jinja global registered by `outfitkit.register_globals(env)`. Default is `""` (no prefix). Consumers loading the prefixed bundle pass `ok_prefix="ok-"`. See [`ADDING-A-COMPONENT.md`](./ADDING-A-COMPONENT.md).

---

## What changes most often

- **`css/components/<X>.css`** — when you tweak a component's look or fix a regression.
- **`showcase/src/outfitkit/templates/ui/<X>.jinja`** — when you change the API of a macro (new prop, new variant slot).
- **`showcase/pages/components/<X>.html`** — when you add a new demo of an existing component.
- **`showcase/pages/apps/<section>/<X>.html`** — when you build a real app screen mock-up.

What changes **rarely** but is **critical**:

- `showcase/pages/_layout.jinja` — the shell. Changes here affect every page.
- `showcase/static/theme-runtime.js` — theme bootstrap. Touch carefully.
- `css/tokens.css` — design tokens. A token rename ripples through every theme override.
- `showcase/build.py` — site generator. Has `is_partial` overrides for chrome files.

See [`MAINTAINING.md`](./MAINTAINING.md#hot-paths) for the full list and what to check when each one breaks.

---

## Stack summary

| Layer | Stack |
|---|---|
| CSS authoring | Plain CSS, BEM-light, `@import`-based bundling. **No PostCSS, no Sass.** |
| CSS bundling | Pure-Python `rcssmin` in `css-build.yml`. **No node toolchain.** |
| Templates | Jinja2 + JinjaX (optional). |
| Site generator | staticjinja. |
| Reactivity | Datastar via CDN. **No React/Vue/Alpine.** |
| Icons | Iconify web component (`<iconify-icon>`) lazy-loading from `api.iconify.design`. |
| Test | Pytest for dual-mode parity, Playwright for visual regression. |
| CI | GitHub Actions (3 workflows). |
| Hosting | GitHub Pages (showcase) + jsDelivr (CSS) + PyPI (macros). |

The whole stack picks "boring, declarative, no build" wherever it can. That's the property that lets one person maintain it.

---

## Next steps for a new maintainer

1. Read this file (you're here).
2. Read [`MAINTAINING.md`](./MAINTAINING.md) — daily ops.
3. Run the showcase locally:
   ```bash
   cd showcase
   source .venv/bin/activate    # or create one with `python3 -m venv .venv && pip install -e .[showcase]`
   python build.py
   python -m http.server 8000 -d build
   open http://localhost:8000
   ```
4. Click around, try every theme, try every component.
5. Read [`ADDING-A-COMPONENT.md`](./ADDING-A-COMPONENT.md) and add a throwaway component as a smoke test.
6. When ready to ship, read [`PUBLISHING.md`](./PUBLISHING.md) and tag a patch release.
