# OutfitKit · Universal Classes

## Core idea

OutfitKit composes UI with global classes instead of component-specific modifier classes.

Typical usage:

```html
<button class="btn primary lg outline">Save</button>
<article class="card soft">
  <header class="head">
    <h2 class="title lg">Revenue</h2>
    <p class="meta sm">Last 30 days</p>
  </header>
</article>
```

Composition is:

- component: `.btn`, `.card`, `.modal`, `.badge`
- variant: `.primary`, `.danger`, `.success`, `.neutral`, ...
- size: `.2xs`, `.xs`, `.sm`, `.md`, `.lg`, `.xl`, `.2xl`
- style: `.outline`, `.ghost`, `.soft`, `.link`
- layout/shape: `.block`, `.icon`, `.circle`, `.rounded`, `.sticky`, ...

## Variant contract

Variant classes from `css/modifiers.css` set:

- `--variant`
- `--variant-rgb`
- `--variant-contrast`
- `--variant-contrast-rgb`
- `--variant-shade`
- `--variant-tint`

Components consume them with neutral fallbacks.

## Size contract

Size classes set:

- `--size`
- `--pad-x`
- `--pad-y`
- `--text`
- `--icon`
- `--radius`

Components consume those variables directly. Do not create `.btn.lg` or `.modal.sm` component APIs.

## Shared structural classes

Reusable composition helpers used across components:

- `.head`
- `.body`
- `.foot`
- `.title`
- `.sub`
- `.label`
- `.value`
- `.meta`
- `.actions`
- `.icon`
- `.close`

Legitimate BEM remains for truly component-specific sub-elements such as `.kanban__card` or `.calendar__event`.

## Local overrides

One-off tuning should happen through local variables on the element:

```html
<div class="modal" style="--max-width: 42rem; --max-height: 85vh;"></div>
<button class="btn" style="--gap: 0.75rem;"></button>
```

For the full component authoring contract, see [COMPONENT-PATTERN.md](./COMPONENT-PATTERN.md).
