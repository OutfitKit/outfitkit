# Themes

OutfitKit ships con 5 templates: `default`, `corporate`, `glass`, `glass-mono`, `mono`. Cada uno funciona en dark (`erplora`) y light (`erplora-light`). Esta guía explica cómo encajan y cómo añadir uno nuevo.

## 1 · Arquitectura

Tres capas:

1. **`css/tokens.css`** — define cada `--ok-*` con un valor por defecto (paleta erplora dark). Es el contrato — cualquier componente puede asumir que estas variables existen.
2. **`css/themes/<name>.css`** — sobreescribe variables `--ok-*` cuando un template está activo. Cada archivo tiene dos secciones: la definición base del template + dos selectores compuestos para dark/light.
3. **Componentes (`css/components/*.css`)** — siempre leen tokens (`var(--ok-bg)`, `var(--ok-brand)`), nunca valores literales. Por eso un cambio de theme afecta a la librería entera sin tocar componentes.

Ejemplo (extracto de `css/themes/mono.css`):

```css
[data-template="mono"] {
  --ok-brand: #84CC16;
  --ok-radius-md: 4px;
  --ok-shadow-md: 0 2px 8px rgba(0,0,0,0.06);
}
[data-template="mono"][data-theme="erplora-light"] { --ok-bg: #FFFFFF; --ok-ink: #171717; }
[data-template="mono"][data-theme="erplora"]       { --ok-bg: #0A0A0A; --ok-ink: #FAFAFA; }
```

El selector `[data-template="X"]` lleva sólo overrides "estructurales" (radios, sombras, brand color); los compuestos `[data-template="X"][data-theme="Y"]` cargan la paleta dark vs light.

## 2 · Activación

La activación es un atributo en `<html>`:

```html
<html data-theme="erplora" data-template="mono">    <!-- mono · dark   -->
<html data-theme="erplora-light" data-template="">  <!-- default · light -->
```

`data-theme` es **obligatorio** (`erplora` o `erplora-light`). `data-template` es **opcional** — sin él, gana la paleta de `tokens.css`.

Ambos atributos los escribe `showcase/static/theme-runtime.js` antes de que cualquier otro script corra. La selección persiste en `localStorage` (`ok-theme`, `ok-template`).

## 3 · Cross-frame sync

El showcase mete cada app demo en un `<iframe>`. Cuando el usuario cambia tema en la barra superior, dos canales propagan al iframe:

- **`storage` event** — cualquier `localStorage.setItem` dispara este evento en todos los documentos del mismo origen. El runtime escucha `ok-theme` y `ok-template`.
- **`postMessage`** — fallback explícito. Tras `localStorage.setItem`, el padre llama a `iframe.contentWindow.postMessage({type:"ok-theme", ...})`. Es síncrono-ish y evita la race en la que el iframe pinta con el valor anterior antes de que `storage` llegue.

Lectura rápida de `showcase/static/theme-runtime.js`: 134 líneas, una IIFE, no requiere build, expone `window.okTheme.set(theme, template)` y `window.okTheme.getState()`.

## 4 · Receta: añadir el template "ocean"

### 4.1 Crea `css/themes/ocean.css`

```css
/* ============================================================
   Theme: Ocean · Deep blue + cyan accent
   Activate with `data-template="ocean"` on <html>.
   ============================================================ */

[data-template="ocean"] {
  --ok-brand:      #06B6D4;          /* cyan-500 */
  --ok-brand-2:    #0891B2;
  --ok-brand-3:    #22D3EE;
  --ok-brand-fg:   #04222B;
  --ok-brand-soft: color-mix(in oklch, var(--ok-brand) 16%, transparent);

  --ok-radius-md: 10px;
  --ok-radius-lg: 14px;
  --ok-shadow-md: 0 4px 18px rgba(2, 32, 71, 0.18);

  --ok-font-display: "Inter", system-ui, sans-serif;
  --ok-tracking-display: -0.02em;
}

/* Ocean · light */
[data-template="ocean"][data-theme="erplora-light"] {
  --ok-bg:    #F0F9FF;        /* sky-50 */
  --ok-bg-1:  #E0F2FE;
  --ok-bg-2:  #FFFFFF;
  --ok-bg-3:  #BAE6FD;
  --ok-line:  #BAE6FD;
  --ok-line-2:#7DD3FC;
  --ok-ink:   #0C4A6E;        /* sky-900 */
  --ok-ink-2: #075985;
  --ok-ink-3: #0369A1;

  color-scheme: light;
}

/* Ocean · dark */
[data-template="ocean"][data-theme="erplora"] {
  --ok-bg:    #082F49;        /* sky-950 */
  --ok-bg-1:  #0C4A6E;
  --ok-bg-2:  #0E5778;
  --ok-bg-3:  #155E75;
  --ok-line:  rgba(186, 230, 253, 0.10);
  --ok-line-2:rgba(186, 230, 253, 0.18);
  --ok-ink:   #F0F9FF;
  --ok-ink-2: #BAE6FD;
  --ok-ink-3: #7DD3FC;

  color-scheme: dark;
}
```

### 4.2 Registra el `@import` en `css/outfitkit.css`

```css
@import "./themes/glass-mono.css";
@import "./themes/mono.css";
@import "./themes/ocean.css";   /* nuevo */
```

### 4.3 Carga el archivo en el showcase — `showcase/pages/_layout.jinja`

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@main/css/themes/mono.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@main/css/themes/ocean.css">
```

(Cargamos los themes como `<link>` separados para esquivar el cache agresivo de jsDelivr en cadenas de `@import` anidadas; ver [MAINTAINING.md](./MAINTAINING.md#cache-de-jsdelivr).)

### 4.4 Añade la opción al selector — `_layout.jinja`

```html
<select class="topbar-template" ...>
  ...
  <option value="mono">○ Mono</option>
  <option value="ocean">≋ Ocean</option>
</select>
```

### 4.5 Whitelist en `showcase/static/theme-runtime.js`

```js
var KNOWN_TEMPLATES = {
  '': 1, 'default': 1, 'corporate': 1, 'glass': 1,
  'glass-mono': 1, 'mono': 1, 'ocean': 1,
};
```

Sin esto el runtime devuelve `''` para `ocean` (lo trata como desconocido) y borra `data-template`.

### 4.6 Test

```bash
cd /Users/ioan/Desktop/code/ERPlora/outfitkit/showcase
OUTFITKIT_CSS=local OUTFITKIT_BASE="" python build.py
python -m http.server 8000 -d build
```

Abre cualquier página, elige Ocean en el topbar, alterna Dark/Light. Si los componentes mantienen su estructura visual y sólo cambia la paleta, el theme está correcto.

## 5 · Por qué los tokens `--ok-*` nunca pierden el prefijo

El bundler (`.github/workflows/css-build.yml`) genera dos artefactos:

- `dist/outfitkit.ok.css` — la fuente concatenada tal cual, con `.ok-` en todos los selectores.
- `dist/outfitkit.css` — derivado del anterior con un `re.sub(r'\.ok-(?=[a-zA-Z])', '.', src)`.

Esa regex sólo entra cuando hay un punto delante (`.ok-foo`), o sea, **únicamente en selectores de clase**. No toca:

- `--ok-*` (custom properties / tokens)
- `var(--ok-*)` (referencias)
- `@keyframes ok-*`
- `animation: ok-fade-in`

Resultado: en el bundle sin prefijo, los componentes son `.btn`, `.card`, etc., pero por dentro siguen leyendo `var(--ok-brand)`, `var(--ok-bg)`. Los themes funcionan idénticos en ambos bundles porque sólo declaran tokens, no clases. Esa es la razón por la que las variables conservan el prefijo: son el contrato compartido entre las dos versiones del CSS.
