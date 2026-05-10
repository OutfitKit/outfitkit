# OutfitKit visual regression tests

Playwright-driven screenshot diffing for the deployed OutfitKit showcase.
Each curated page is captured at two viewports (desktop 1280x800 and
mobile 390x844) and compared pixel-for-pixel against a baseline using
Playwright's built-in `toHaveScreenshot()` matcher (pixelmatch under
the hood, ~5% tolerance).

## Install

```bash
cd showcase/tests/visual
npm install
npx playwright install chromium
```

## Run

```bash
# Run the full suite against the deployed showcase (default).
npm test

# Open the Playwright UI runner.
npm run test:ui

# Re-record baselines after intentional UI changes.
# Review the diffs first, then commit the updated PNGs.
npm run test:update
```

By default the suite hits `https://outfitkit.github.io/outfitkit`. To
test against a local build (or a staging mirror) set `OUTFITKIT_BASE_URL`:

```bash
# Local dev (run `python showcase/build.py serve` in another shell first)
OUTFITKIT_BASE_URL=http://localhost:8000 npm test
```

## Where things live

| Path | Purpose |
|------|---------|
| `playwright.config.ts` | Two projects (desktop, mobile), single chromium browser |
| `showcase.spec.ts` | Page list + per-page test |
| `__screenshots__/<project>/<slug>.png` | **Committed** baselines |
| `test-results/` | Diffs + traces from the latest run (gitignored) |
| `playwright-report/` | HTML report (gitignored) |

The slug for `/components/button.html` is `components-button`. For
`/apps/marketplace/saas-shop.html` it's `apps-marketplace-saas-shop`.

## Adding pages to the suite

Edit the `PAGES` array in `showcase.spec.ts`, run `npm run test:update`
to record baselines for the new pages, eyeball the resulting PNGs, and
commit them along with the spec change.

## Behavior notes

- Iconify and Datastar load from CDN. The spec waits 1500ms after
  `domcontentloaded` to give Iconify time to inject SVG markup.
- localStorage is cleared before each navigation so theme is
  deterministic (no light/dark drift between runs).
- CSS animations and transitions are forcibly disabled per-page.
- App pages live in an iframe inside the showcase shell. We screenshot
  the **outer** page (shell + iframe content), which mirrors what users
  actually see.

## CI

`.github/workflows/visual-regression.yml` runs the suite on PRs that
touch `css/**` or `showcase/**`. Note: CI tests against the
**already-deployed** `outfitkit.github.io/outfitkit`, so a PR's own
visual changes won't reach CI until after `pages.yml` deploys them
post-merge. Run the suite locally before merging UI changes.
