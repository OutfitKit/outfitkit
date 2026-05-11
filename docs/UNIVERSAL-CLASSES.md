# OutfitKit · Universal classes (design proposal)

> Estado: **propuesta**, pendiente de aprobación.
> Fecha: 2026-05-11.
> Contexto: tras el bloque A, el repo tiene dos sistemas de composición conviviendo
> (BEM `__element` + tokens namespaced `--component-*`). Esta propuesta unifica
> todo en un único sistema universal tipo Bulma + Ionic.

---

## Regla cardinal

**Todo valor numérico va detrás de una variable. Ningún literal en componentes
ni en modificadores.** Los defaults también viven en variables del sistema
(`tokens.css` o themes).

```css
/* MAL */
.modal { backdrop-filter: blur(24px); }

/* MAL: literal "24px" como default */
.blur { backdrop-filter: blur(var(--blur, 24px)); }

/* BIEN */
.blur {
  --blur: var(--blur-default);          /* default vive en tokens.css */
  backdrop-filter: blur(var(--blur));
}
```

En `tokens.css`:
```css
--blur-default: 24px;
```

Override en el consumidor:
```html
<div class="modal blur" style="--blur: 32px;">…</div>
```

---

## Las tres familias de clases universales

### 1. Componentes (root)

Ya existen: `.btn`, `.card`, `.modal`, `.drawer`, `.invoice`, `.kpi`, etc.
Definen estructura y consumen modificadores. **No se tocan en esta propuesta.**

### 2. Elementos compositivos (universales · NUEVOS)

Hoy: 767 elementos BEM distintos (`.modal__title`, `.invoice__title`,
`.card__title`, ...). Top reutilizados: `__item` (123), `__icon` (81),
`__btn` (74), `__title` (68), `__row` (53), `__head` (48), `__label` (45),
`__content` (35), `__body` (32), `__actions` (32), `__bar` (30), `__sub` (28),
`__value` (27), `__divider` (19), `__footer` (18), `__meta` (18), `__close` (15).

**Propuesta: extraer los elementos reutilizables a clases universales y
deprecar la versión BEM.**

| Clase | Reemplaza | Setea | Consume |
|---|---|---|---|
| `.title` | `.X__title` (51 instancias) | font-size, font-weight, line-height, letter-spacing, color, font-family | `--text`, `--weight`, `--leading`, `--tracking`, `--color`, `--font` |
| `.sub` | `.X__sub`, `.X__subtitle` (24) | font-size, color, line-height | `--text`, `--color`, `--leading` |
| `.body` | `.X__body`, `.X__content` (35) | padding, color | `--pad-x`, `--pad-y`, `--color` |
| `.head` | `.X__head`, `.X__header` (48) | padding, border-bottom | `--pad-x`, `--pad-y`, `--border-color` |
| `.foot` | `.X__footer` (18) | padding, border-top | `--pad-x`, `--pad-y`, `--border-color` |
| `.label` | `.X__label` (45) | font-size, color, text-transform, letter-spacing | `--text`, `--color`, `--tracking` |
| `.value` | `.X__value`, `.X__num` (39) | font-size, font-weight, font-variant-numeric | `--text`, `--weight` |
| `.meta` | `.X__meta`, `.X__time`, `.X__desc` (49) | font-size, color | `--text`, `--color` |
| `.actions` | `.X__actions` (32) | display flex, gap | `--gap` |
| `.divider` | `.X__divider`, `.X__sep` (19) | height/width, background | `--divider-thickness`, `--color` |
| `.close` | `.X__close` (15) | width/height de boton X | `--size`, `--icon` |
| `.icon` | `.X__icon` (81) | width/height/color de svg | `--icon`, `--color` |
| `.item` | `.X__item` (123) — más controvertido | padding, hover bg | `--pad-x`, `--pad-y`, `--bg-hover` |
| `.row` | `.X__row` (53) | display flex/grid, gap | `--gap` |

**Notas:**
- `.item` (123) y `.row` (53) son tan estructurales que probablemente se quedan
  como BEM porque el espaciado y comportamiento varía mucho entre componentes
  (lista vs grid vs kanban vs ...). **A discutir.**
- `__btn` (74) NO se universaliza — los botones internos ya usan `.btn`
  con su propia API. El BEM `.X__btn` añade typing de posición; eso se
  resuelve con utilities (`.absolute`, `.top`, etc.) o queda BEM.
- Hay ~700 BEM más con conteo bajo (1–10) que son **legítimamente específicos
  del componente** (`.kanban__column`, `.cal__event`, `.pos__cart-line`). No
  se tocan.

**Net:** universalizamos ~14 clases que cubren ~50% del peso de uso de BEM.
Los 767 elementos se quedan en ~600.

### 3. Modificadores (universales · ya existen + AMPLIACIÓN)

Hoy en `modifiers.css`:
- Color: `.primary`, `.secondary`, `.tertiary`, `.success`, `.warning`, `.danger`,
  `.info`, `.neutral`, `.light`, `.dark`, `.brand`, `.accent`, `.ok`, `.leaf`
  → setean `--variant` + 5 sufijos.
- Tamaño: `.xs`, `.sm`, `.md`, `.lg`, `.xl`
  → setean `--size`, `--pad-x`, `--pad-y`, `--text`, `--icon`, `--radius`.
- Estructura: `.outline`, `.ghost`, `.soft`, `.link`, `.block`, `.rounded`,
  `.icon`, `.circle`, `.fixed`, `.sticky`, `.inset`.

**Propuesta de ampliación: modificadores de efecto.**

Hoy hardcoded: 22 `blur(Npx)`, 8 `saturate(N%)`, varios `filter: brightness()`
en componentes individuales (`--topbar-blur`, `--sidebar-blur`, `--modal-blur`,
etc., 14 tokens distintos para lo mismo).

| Clase | Setea | Default token | Aplica |
|---|---|---|---|
| `.blur` | `--blur` | `--blur-default: 24px` | `backdrop-filter: blur(var(--blur))` |
| `.blur-sm` | `--blur` | `--blur-sm: 8px` | idem |
| `.blur-lg` | `--blur` | `--blur-lg: 32px` | idem |
| `.saturate` | `--saturate` | `--saturate-default: 160%` | `backdrop-filter: saturate(var(--saturate))` |
| `.glass` | (compose) | usa `--blur`+`--saturate`+ bg semi-transparente | combo |
| `.elevated` | `--shadow` | `--shadow-lg` | `box-shadow: var(--shadow)` |
| `.elevated-sm` | `--shadow` | `--shadow-sm` | idem |
| `.elevated-xl` | `--shadow` | `--shadow-xl` | idem |
| `.brightness` | `--brightness` | `--brightness-default: 1.1` | `filter: brightness(var(--brightness))` |
| `.dim` | `--brightness` | `--brightness-dim: 0.6` | idem |

**Tokens nuevos en `tokens.css`:**
```css
--blur-default: 24px;
--blur-sm:      8px;
--blur-lg:      32px;
--saturate-default: 160%;
--brightness-default: 1.1;
--brightness-dim:     0.6;
```

**Tokens a borrar** (por redundancia con el modificador `.blur`/`.saturate`):
`--topbar-blur`, `--sidebar-blur`, `--modal-blur`, `--drawer-blur`,
`--tabbar-blur`, `--public-nav-blur`, `--pdp-gallery-nav-blur`,
`--product-wishlist-blur`, `--product-sold-out-blur`, `--topbar-saturate`,
`--sidebar-saturate`, `--modal-saturate`, `--drawer-saturate`.

13 tokens fuera.

---

## Composición resultante

### Ejemplo invoice
**Antes:**
```html
<article class="invoice">
  <header class="invoice__header">
    <h1 class="invoice__title">Factura 001</h1>
    <p class="invoice__sub">Cliente: Juan</p>
  </header>
  <div class="invoice__body">…</div>
  <footer class="invoice__footer">
    <button class="btn primary">Pagar</button>
  </footer>
</article>
```

**Después:**
```html
<article class="invoice">
  <header class="head">
    <h1 class="title 2xl">Factura 001</h1>
    <p class="sub sm">Cliente: Juan</p>
  </header>
  <div class="body">…</div>
  <footer class="foot">
    <button class="btn primary">Pagar</button>
  </footer>
</article>
```

### Ejemplo modal con blur custom
```html
<div class="modal blur saturate">
  <header class="head">
    <h2 class="title xl">Confirmar</h2>
  </header>
  <div class="body">…</div>
</div>

<!-- Override de blur -->
<div class="modal blur saturate" style="--blur: 32px;">…</div>
```

### Ejemplo card con elevación custom
```html
<div class="card elevated">
  <h3 class="title lg">Producto</h3>
  <p class="meta">€19.99</p>
</div>

<!-- Card shadow más fuerte -->
<div class="card elevated-xl">…</div>
```

---

## Tokens redundantes a borrar (post-implementación)

### Categoría 1 · `*-fz` font-size por elemento (36 tokens)
Sustituido por `var(--text)` consumido desde `.title`, `.sub`, `.label`, etc.

`--invoice-title-fz`, `--invoice-sub-fz`, `--invoice-sec-fz`, `--invoice-h4-fz`,
`--invoice-logo-fz`, `--invoice-lines-fz`, `--invoice-sum-fz`, `--invoice-total-fz`,
`--modal-title-fz`, `--chat-msg-fz`, `--chat-meta-fz`, `--event-avatar-fz`,
`--hover-card-avatar-fz`, `--menu-section-fz`, `--mfg-bom-row-fz`,
`--mfg-gantt-bar-fz`, `--mfg-gantt-head-fz`, `--mfg-oee-pct-fz`,
`--mfg-oee-metric-label-fz`, `--mfg-scanner-title-fz`, `--mfg-sku-fz`,
`--mfg-wo-id-fz`, `--mfg-wo-pct-fz`, `--mfg-wo-progress-fz`,
`--mfg-wo-step-name-fz`, `--mfg-wo-step-num-fz`, `--mfg-wo-sub-fz`,
`--mfg-wo-title-fz`, `--mfg-gantt-head-time-fz`, `--pdp-qty-fz`,
`--pdp-qty-sm-fz`, `--pdp-qty-sm-value-fz`, `--pos-cart-total-fz`,
`--pos-numpad-fz`, `--product-cta-fz`, `--sign-label-fz`.

### Categoría 2 · `*-pad` padding por elemento (13 tokens)
Sustituido por `var(--pad-x)`/`var(--pad-y)` consumido desde `.head`, `.body`, `.foot`, `.label`.

`--ctx-menu-pad`, `--hover-card-pad`, `--invoice-pad`, `--menu-sub-pad`,
`--menu-userblock-pad`, `--menubar-trigger-pad`, `--mfg-gantt-head-pad`,
`--mfg-gantt-pad`, `--mfg-scanner-pad`, `--mfg-wo-pad`, `--modal-header-pad`,
`--pos-cat-rail-pad`, `--sign-pad`.

### Categoría 3 · `*-icon-size` (9 tokens)
Sustituido por `var(--icon)`.

`--bootstrap-icon-size`, `--crumb-icon-size`, `--error-diag-icon-size`,
`--error-icon-size`, `--event-icon-size`, `--list-icon-size`,
`--tabbar-icon-size`, `--toast-icon-size`, `--tree-icon-size`.

### Categoría 4 · `*-blur` / `*-saturate` por componente (13 tokens)
Listados arriba en sección "Modificadores de efecto".

**Total a borrar: ~71 tokens. Quedarían ~180 namespaced legítimos** (dimensiones
fijas como `--invoice-w`, escalas específicas `--avatar-{xs..2xl}`, conceptos
del dominio `--cat-coffee-a`, z-index).

---

## Plan de implementación (orden propuesto)

1. **Acordar este documento.** Sin tu visto bueno no toco código.
2. **Añadir clases universales nuevas a `modifiers.css`** (elementos compositivos + modificadores de efecto). No toca componentes aún.
3. **Añadir tokens nuevos a `tokens.css`** (`--blur-default`, etc.) y mantener los viejos como alias temporales.
4. **Piloto: refactorizar `modal` + `invoice`** componentes + sus páginas showcase. Verificar visualmente.
5. **Si OK, propagar a los 28 componentes restantes**. Cada uno:
   - Sustituye `*__title` → `.title`, etc. en el CSS y en showcase pages y en JinjaX templates.
   - Borra los tokens `--X-title-fz`, `--X-pad`, `--X-icon-size`, `--X-blur`, `--X-saturate`.
6. **Borrar los tokens redundantes** de `tokens.css`.
7. **Rebuild dist**, QA visual completo, commit, push, tag v2.0.0.

Tiempo estimado: **5–10h** de trabajo concentrado.

---

## Riesgos y trade-offs

- **Specificity wars:** si una página tiene `<h1 class="invoice__title title 2xl">`, el orden de carga en CSS determina cuál gana. Mitigación: mismo nivel de especificidad (todo `.clase` single-class), orden de carga estable (`reset` → `tokens` → `modifiers` → `components` → `utilities`).
- **Migración consumidores:** Cloud/Hub que ya usan `.X__title` se rompen. Mitigación: mantener los selectores BEM como aliases en `components/*.css` durante v2 (`.invoice__title { @apply .title... }` o copia literal), deprecar en v3.
- **Breaking change documentado:** v2.0.0 ya es breaking. Esto se añade a la nota de release.
- **`.item`/`.row`** quedan fuera del set universal por variabilidad estructural — si después cambias de opinión, fácil añadirlos.

---

## Decisiones tomadas (2026-05-11)

1. **`.item` y `.row` van como universales.** Cubre 123+53 = 176 BEM. Acepto el riesgo de variabilidad estructural — si algún componente necesita overrides feos, se reevalúa caso por caso.
2. **No mantenemos aliases BEM en v2.** Romper limpio en v2.0.0. Consumidores migran a clases universales a la vez. CSS más ligero. Breaking change ya documentado en v2.
3. **Sin prefijo `ok-`** en `outfitkit.css` default (coherente con ROADMAP decisión nº 2). El bundle paralelo `outfitkit.ok.css` mantiene el prefijo para consumidores con colisiones (decisión nº 9). Ya hay precedente con tokens.
