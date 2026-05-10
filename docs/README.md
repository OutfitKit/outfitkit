# OutfitKit — Maintainer documentation

This directory is for **the people who keep OutfitKit running**, not for consumers. If you just want to use OutfitKit on a website, the root [`README.md`](../README.md) is what you want.

---

## Read these in order

| # | Doc | What it covers | When to read |
|---|---|---|---|
| 1 | [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Big picture: what OutfitKit is, how the 3 artifacts (CSS / Python / showcase) fit together, repo layout, the macro pattern. | First. Always first. |
| 2 | [`MAINTAINING.md`](./MAINTAINING.md) | Daily ops: hot paths, "if X breaks, look at Y", local dev, cache caveats. | After ARCHITECTURE, before touching anything. |
| 3 | [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) | Real bugs we hit and how we fixed them. Symptom → fix. | When something breaks. Search this before debugging from scratch. |
| 4 | [`ADDING-A-COMPONENT.md`](./ADDING-A-COMPONENT.md) | End-to-end recipe for shipping a new component (CSS + macro + demo + sidebar). | When you need to add a component. |
| 5 | [`THEMES.md`](./THEMES.md) | The theme system, how the 5 templates compose with `data-theme`, how to add a new template. | When you touch tokens.css or themes/. |
| 6 | [`PUBLISHING.md`](./PUBLISHING.md) | The 3 release pipelines (CDN bundle, PyPI, GH Pages). Which tag triggers what. | When you're ready to ship. |

---

## Other reference

- [`../AUDIT.md`](../AUDIT.md) — log of every visual regression we've ever found, indexed by section/page. Append-only; do **not** delete entries even if "fixed" — they're the historical record.
- [`../llms.txt`](../llms.txt) and [`../llms-full.txt`](../llms-full.txt) — machine-readable docs following the [llmstxt.org](https://llmstxt.org) spec. Update when adding new components.
- `../showcase/tests/visual/README.md` — Playwright visual regression suite.
- `../showcase/tests/test_dual_mode.py` — pytest spec that asserts every macro renders the same HTML in vanilla Jinja2 mode and JinjaX mode.

---

## Maintainer workflow at a glance

```
                     ┌────────────────┐
                     │  user reports  │
                     │  a regression  │
                     └────────┬───────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ TROUBLESHOOTING.md    │  ← search by symptom first
                  │ matches?              │
                  └───────────┬───────────┘
                              │ no
                              ▼
                  ┌───────────────────────┐
                  │ AUDIT.md              │  ← search by page/section
                  │ matches?              │
                  └───────────┬───────────┘
                              │ no
                              ▼
                  ┌───────────────────────┐
                  │ MAINTAINING.md        │  ← "If X breaks, look at Y"
                  │ → likely file         │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Reproduce locally     │
                  │ python build.py       │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Fix → commit → push   │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Add the case to       │
                  │ TROUBLESHOOTING.md    │  ← so future-you saves an hour
                  └───────────────────────┘
```

If the fix needs a release (CSS or PyPI), see [`PUBLISHING.md`](./PUBLISHING.md).

---

## Quality bars before merge

Minimum:
1. `cd showcase && python build.py` — must succeed without errors.
2. Visual eye-check on the affected page in the deployed showcase or a local serve.
3. If you changed a macro signature: `cd showcase && pytest tests/test_dual_mode.py` — must pass.
4. If you changed CSS that affects layout: run the visual regression suite (see `../showcase/tests/visual/README.md`) — must pass or the diffs must be intentional.

Strongly recommended:
5. Add a line to [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) if the bug was non-obvious.
6. Update [`AUDIT.md`](../AUDIT.md) if you fixed an entry (mark it `[fixed]` rather than deleting).
7. Bump the relevant `__version__` if you're shipping (PyPI, CSS bundle).

---

## Conventions

- **Commit messages**: imperative mood, scoped prefix when relevant (`fix(showcase)`, `feat(themes)`, `docs(maintaining)`). Co-authored-by lines are kept for AI-assisted work.
- **Naming**: CSS classes follow BEM-light. Macros are `snake_case` filenames, JinjaX tags are `PascalCase`. `--ok-*` for tokens, `data-ok-*` reserved for future use.
- **Branching**: `main` is always deployable. Hotfixes go directly to `main` (small repo, single maintainer). Larger changes via PR with visual regression CI passing.

---

## When to escalate

Escalate to the team / open a public issue when:

- You're about to change a public API (macro signature, `outfitkit.css` import order, `register_globals` argument).
- You're considering a major version bump (`v2.0.0`).
- You're changing token names (any `--ok-*` rename) — this can ripple through every theme override.
- You're considering removing a component or page (anyone using it externally would break).

For everything else, ship it.
