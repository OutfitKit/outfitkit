# Troubleshooting — OutfitKit

Real bugs we've hit, with the symptom on the left and the fix on the right. Add to this file every time you waste an hour debugging something — future-you will thank you.

---

## Table of contents

1. [The CSS doesn't apply / a class doesn't render](#1-the-css-doesnt-apply)
2. [The theme doesn't change when I click the switcher](#2-the-theme-doesnt-change)
3. [The iframe shows a duplicated chrome](#3-the-iframe-shows-duplicated-chrome)
4. [A page renders fine on desktop but mobile is squashed](#4-mobile-squashed)
5. [Datastar bindings silently do nothing](#5-datastar-silently-does-nothing)
6. [`pip install outfitkit` ships old templates](#6-pypi-ships-old-templates)
7. [jsDelivr keeps serving the old CSS bundle](#7-jsdelivr-cache)
8. [Tests pass locally but fail in CI](#8-tests-fail-in-ci)
9. [`build.py` errors with "ModuleNotFoundError: build"](#9-build-py-shadowing)
10. [Macros emit `class="ok-btn"` even though I asked for unprefixed](#10-prefix-mismatch)

---

## 1. The CSS doesn't apply

**Symptom**: you write `<button class="btn btn--primary">` and the button has no styling, or some styles but not others.

**Diagnose**:
1. Open DevTools → Elements → check the `class` attribute on the rendered HTML matches the CSS bundle's class names. Default bundle = `btn`. Prefixed bundle = `ok-btn`.
2. Network tab → confirm `outfitkit.min.css` (or `.ok.min.css`) actually loaded (status 200).
3. If using macros: confirm `register_globals(env, ok_prefix="…")` matches the bundle. See [#10](#10-prefix-mismatch).

**Common cause**: prefix mismatch. The most common case is loading `outfitkit.ok.min.css` (prefixed) but having `register_globals(env)` (unprefixed default), so macros emit `class="btn"` but CSS only has `.ok-btn`.

**Fix**: pick one and align both. See [`PUBLISHING.md`](./PUBLISHING.md#which-bundle-do-i-use).

---

## 2. The theme doesn't change

**Symptom**: clicking Dark/Light or selecting a Template in the switcher does nothing visually.

**Diagnose**:
1. DevTools → Console → run `document.documentElement.getAttribute('data-theme')` — should be `erplora` or `erplora-light`. If it's `null` or `auto` or anything else, the runtime didn't apply.
2. Run `getComputedStyle(document.documentElement).getPropertyValue('--ok-brand')`. If it stays `#E8552A` regardless of which template is "active", the theme CSS file didn't load.
3. Run `Array.from(document.querySelectorAll('link[href*="themes/"]')).map(l => l.href)` — should list 5 theme CSS files.

**Common causes & fixes**:

- **`data-theme="auto"` from a stale localStorage entry**. Fix: `theme-runtime.js` normalises this on read, but if you see it again, force `localStorage.clear()` and reload.
- **Theme `<link>` elements missing**. The 5 theme CSS files are loaded as separate `<link>` tags directly from `_layout.jinja` (NOT through the `outfitkit.css` bundle's `@import`, because jsDelivr's nested-import cache can lose them). If you removed those `<link>` tags by mistake, restore them.
- **Cross-frame: parent flips theme but iframe doesn't**. `theme-runtime.js` listens for `storage` events and `postMessage`. If the iframe still doesn't sync, check the parent's `okTheme.set()` is calling `notifyChildFrames()`. We hit this exact bug — see commit `8db10a9`.

---

## 3. The iframe shows duplicated chrome

**Symptom**: an `apps/X.html` page inside the iframe shows ANOTHER showcase sidebar/topbar inside, like a fractal.

**Cause**: an internal `<a href="other-page.html">` inside the iframe was clicked and navigated WITHOUT preserving `?embed=1`. The iframe loaded a fresh page that ran the showcase shell again instead of stripping it.

**Fix**: `_layout.jinja` already has a click delegate that adds `?embed=1` to same-origin links inside iframe-mode pages. If a new page introduces JS-driven navigation (e.g. `location.href = "..."`), make sure that navigation also carries `?embed=1`.

See commit `670b28a` for the original fix.

---

## 4. Mobile squashed

**Symptom**: on a 390px phone the showcase content renders into a narrow column with wide gray gutters on each side.

**Cause**: the `.ok-app[data-docs]` shell is `grid-template-columns: 250px 1fr` on desktop. On mobile the sidebar should collapse to an off-canvas drawer and the grid should release that 250px. If only one of those happened (e.g. sidebar hides via `transform: translateX(-100%)` but the grid still reserves 250px), the main content shrinks.

**Fix in CSS**: must have BOTH

```css
.ok-app[data-docs] { grid-template-columns: 250px 1fr; }
@media (max-width: 767px) {
  .ok-app[data-docs] { grid-template-columns: 1fr; }
}
```

We hit this — commit `4be62c8`. **Specificity matters**: the showcase's `[data-docs]` selector wins over `app-shell.css`'s mobile rule, so the override has to live in `_layout.jinja`'s inline style block too.

---

## 5. Datastar silently does nothing

**Symptom**: a button has `data-on:click="$count++"` but clicking it does nothing. No console errors.

**Most common causes**:

1. **Dashed syntax instead of colon**. Datastar v1 uses **colon**: `data-on:click`, `data-attr:aria-pressed`, `data-bind:value`. The dashed form (`data-on-click`, `data-attr-aria-pressed`) is **silently ignored**. We hit this many times — see commits `d9b7e63` and `f76ccac`.
2. **Boolean-attr CSS using `[attr="true"]`**. Datastar v1 sets boolean attrs to `""` (empty string) when truthy, not the literal `"true"`. So `[aria-pressed="true"]` never matches. Fix: also match `[aria-pressed=""]`. We swept this across 16 CSS files — commit `2db5cb4`.
3. **Iconify icons with `width="2"`**. Migration from SVG copied the SVG `stroke-width="2"` to the iconify-icon `width=` attribute → 2-pixel-wide invisible icons. Standard sizes: 16, 18, 20.

**Tip**: when a Datastar binding doesn't fire, search the codebase for the same selector with the dashed legacy form. Often it's already there elsewhere.

---

## 6. PyPI ships old templates

**Symptom**: a consumer runs `pip install outfitkit==1.3.0` but `{{ button(...) }}` emits markup from an older version.

**Cause**: the `pypi-publish.yml` workflow builds from `showcase/` (NOT root) and packages `showcase/src/outfitkit/templates/`. If the macros in that path don't match the version, you have a release bug.

**Diagnose**:
```bash
pip download outfitkit==1.3.0 --no-deps -d /tmp/ok
unzip /tmp/ok/outfitkit-1.3.0-py3-none-any.whl -d /tmp/ok-unpacked
cat /tmp/ok-unpacked/outfitkit/templates/ui/button.jinja
```

**Fix**: tag a new `pypi-vX.Y.Z` and re-release. The version in `showcase/pyproject.toml` AND `showcase/src/outfitkit/__init__.py:__version__` must match the tag.

---

## 7. jsDelivr cache

**Symptom**: you pushed a CSS fix to `main`, the file in the GitHub repo is correct, but the showcase still serves the old version.

**Cause**: jsDelivr aggressively caches `@main` paths. TTL can be 12+ hours.

**Fix immediate**:
```bash
curl -X POST 'https://purge.jsdelivr.net/' \
  -H 'Content-Type: application/json' \
  -d '{"path":["/gh/OutfitKit/outfitkit@main/css/outfitkit.css"]}'
```

The response is `{"id":"...","status":"pending"}` — the actual purge can take 10-60 seconds. Verify with `curl -s 'https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@main/css/outfitkit.css' | head`.

**Fix long-term**: production consumers should use `@vX.Y.Z` (tag-pinned) URLs, which are immutable and CDN-friendly. `@main` is for development only.

We hit this with the themes — commit `5324a1a` flattened the nested `@import` chain because jsDelivr was caching `outfitkit.css` without the inner `themes/index.css` reference. The showcase now loads themes via separate `<link>` tags to bypass this.

---

## 8. Tests fail in CI

**Symptom**: `pytest` or Playwright tests pass locally but fail in GH Actions.

**Common causes**:

- **Timing**: CI runners are slower. If a test relies on Iconify icons rendering in 500ms, it'll flake. Bump waits to 1500ms+ and use proper `wait_for` selectors instead of `sleep`.
- **Visual baselines were taken on a different OS**. Playwright pixelmatch is sensitive to font rendering, antialiasing, sub-pixel positioning. Linux runner != macOS dev. Solution: take baselines on the same OS as CI (Linux), commit them. Or use a Docker container for local runs.
- **`OUTFITKIT_BASE_URL` mismatch**. Visual tests target the deployed showcase by default. If a recent push hasn't deployed yet, the test sees the previous version.

---

## 9. build.py shadowing

**Symptom**: `python -m build` fails with `ModuleNotFoundError: build` or runs `showcase/build.py` (the staticjinja runner) instead of the PyPA `build` module.

**Cause**: `showcase/build.py` is a local file. When you run `python -m build` from `showcase/`, Python's module resolver finds the local file first and tries to import it as `build`.

**Fix**: invoke from a different directory. The `pypi-publish.yml` workflow does this:

```yaml
- name: Build sdist + wheel from /tmp (avoids local build.py shadow)
  run: |
    python -m build \
      --outdir "$GITHUB_WORKSPACE/showcase/dist" \
      "$GITHUB_WORKSPACE/showcase"
```

Locally:
```bash
cd /tmp && python3 -m build --outdir /Users/ioan/Desktop/code/ERPlora/outfitkit/showcase/dist /Users/ioan/Desktop/code/ERPlora/outfitkit/showcase
```

---

## 10. Prefix mismatch

**Symptom**: macros emit `class="ok-btn ok-btn--primary"` but the CSS bundle is `outfitkit.min.css` (unprefixed) → buttons unstyled. Or the inverse.

**The contract**: the macro `ok_prefix` global and the loaded CSS bundle MUST agree.

**Default**: no prefix everywhere.
```python
register_globals(env)                  # ok_prefix=""
ctx = {"css": css_url()}               # → outfitkit.min.css (unprefixed)
```
Result: `<button class="btn btn--primary">`.

**Opt-in**: prefix everywhere.
```python
register_globals(env, ok_prefix="ok-")
ctx = {"css": css_url(prefix="ok-")}   # → outfitkit.ok.min.css (prefixed)
```
Result: `<button class="ok-btn ok-btn--primary">`.

**Tip**: print `env.globals.get('ok_prefix')` at startup to confirm. The default is `""`, so silence = unprefixed.

---

## When all else fails

1. **Reset everything**: `localStorage.clear()`, hard reload (Cmd+Shift+R), check that `data-theme` and `data-template` are blank or default values.
2. **Compare against the deployed showcase**: <https://outfitkit.github.io/outfitkit/> is always the latest `main`. If the live site works but your local doesn't, you have a local repo issue (stale build, untracked file, etc.).
3. **Re-run the local build clean**: `rm -rf showcase/build && cd showcase && python build.py`.
4. **Check the audit log**: [`AUDIT.md`](../AUDIT.md) records every visual regression we've ever found. The same pattern often returns.
5. **Add it here**. Spend 5 minutes documenting your fix so the next person doesn't repeat your debugging session.
