# OutfitKit Component Pattern

## Contract

Every component consumes the global modifier contract from `css/modifiers.css`:

- Variants:
  `--variant`, `--variant-rgb`, `--variant-contrast`, `--variant-contrast-rgb`, `--variant-shade`, `--variant-tint`
- Sizes:
  `--size`, `--pad-x`, `--pad-y`, `--text`, `--icon`, `--radius`

Components must not define their own `.component.primary`, `.component.lg`, or similar combined APIs. Usage is always composable:

```html
<button class="btn primary lg outline">Save</button>
<div class="modal soft" style="--max-width: 40rem;">...</div>
```

## Local Variables

Component root selectors use generic Ionic-style names only:

- `--background`
- `--color`
- `--border-color`
- `--border-width`
- `--border-radius`
- `--width`
- `--height`
- `--min-height`
- `--max-width`
- `--max-height`
- `--padding-x`
- `--padding-y`
- `--font-size`
- `--font-weight`
- `--gap`
- `--shadow`

Forbidden examples:

- `--modal-width`
- `--btn-height`
- `--chat-avatar-size`
- `--menu-item-gap`

If a value is private to one component, it still lives in that component file, but under a generic local variable on the root selector.

## Token Boundaries

`css/tokens.css` contains only global scales and shared system primitives:

- typography
- spacing
- semantic sizes
- icon/avatar/dot scales
- radii and borders
- palette and Ionic color schema
- safe area, shadows, motion, z-index
- shell layout tokens

`css/tokens.css` must not hold component-private dimensions.

## Sizing Rules

Use `rem` for the design system.

Allowed `px` exceptions:

- `--border-w*`
- shadow offsets and blur values
- `@media`
- explicit sub-pixel exceptions such as `--dot-2xs: 3px`

## Instance Overrides

Prefer instance overrides for one-off adjustments:

```html
<div class="modal" style="--max-width: 44rem; --max-height: 85vh;"></div>
<button class="btn" style="--width: 100%; --gap: 0.75rem;"></button>
```

Add a new modifier class only when the behavior is intentionally reusable across many components or many call sites.

## Canonical Example: Button

```css
.btn {
  --background: var(--bg-mode, var(--variant, var(--color-medium)));
  --color: var(--color-mode, var(--variant-contrast, var(--color-medium-contrast)));
  --border-color: var(--border-mode, transparent);
  --border-radius: var(--radius, var(--radius-md));
  --height: var(--size, var(--size-md));
  --padding-x: var(--pad-x, var(--pad-md-x));
  --padding-y: var(--pad-y, var(--pad-md-y));
  --font-size: var(--text, var(--text-base));
  --gap: var(--space-2);
}

.btn:hover {
  --background: var(--bg-mode, var(--variant-shade, var(--color-medium-shade)));
}
```

## Canonical Example: Modal

```css
.modal {
  --background: color-mix(in oklch, var(--bg-2) 88%, transparent);
  --color: var(--text-color);
  --border-color: color-mix(in oklch, var(--line-2) 85%, transparent);
  --border-radius: var(--radius, var(--radius-2xl));
  --max-width: 30rem;
  --max-height: calc(100vh - var(--space-8));
  --font-size: var(--text, var(--text-base));
  --min-height: calc(var(--size, var(--size-md)) * 4);
}
```

The component consumes the global size contract without needing `.modal.lg`. Width and height overrides remain instance-level via `style`.
