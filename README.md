# OutfitKit

Librería CSS de componentes para aplicaciones web. ~260 bloques semánticos con prefijo `ok-*`, BEM-light, themeable vía CSS custom properties.

Cero JS obligatorio. Cero build pipeline para consumidores. Un solo `<link>` y listo.

## Uso (consumidor solo CSS)

### Producción (default, sin prefijo)

```html
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@latest/dist/outfitkit.min.css">

<button class="btn btn--primary">Continuar</button>
```

Clases cortas, sin ruido. Es lo recomendado para cualquier proyecto donde OutfitKit sea la única librería CSS de la página — Hub, Cloud, los módulos `m_*` del marketplace.

### Producción (opcional, con prefijo `ok-`)

Solo necesario si OutfitKit convive con otra librería CSS que ya define `.btn`, `.card`, etc. (Bootstrap, Tailwind utilities, Daisy, un design system propio anterior). El bundle prefijado evita las colisiones:

```html
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@latest/dist/outfitkit.ok.min.css">

<button class="ok-btn ok-btn--primary">Continuar</button>
```

Ambos bundles comparten exactamente los mismos tokens (`--ok-*`), keyframes y animations. Lo único que cambia son los nombres de los selectores de clase.

### Desarrollo — fuente sin minificar

Útil para inspeccionar reglas individuales en DevTools:

```html
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@main/css/outfitkit.css">

<button class="ok-btn ok-btn--primary">Continuar</button>
```

La fuente en `css/` siempre lleva el prefijo `ok-` (es como editamos el repo). El bundle sin prefijo se genera solo en CI al taggear. Los navegadores modernos resuelven los `@import` directamente, sin bundling local.

## Macros Jinja (opcional)

Si tu backend es Python con Jinja2 (FastAPI, Flask, Django+jinja2 backend), puedes consumir los componentes como macros:

```bash
pip install outfitkit             # macros vanilla
pip install outfitkit[jinjax]     # + sintaxis HTML-like <Button label="x" />
```

Las macros viven en [`showcase/`](./showcase/) y se publican desde ahí a PyPI. Cualquier macro funciona con o sin JinjaX (formato dual-mode).

### Setup mínimo (default, sin prefijo)

```python
from jinja2 import Environment, FileSystemLoader
from outfitkit import TEMPLATES_DIR, register_globals, css_url

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
register_globals(env)            # establece ok_prefix = ""

# En tu base.html
#   <link rel="stylesheet" href="{{ css }}">
ctx = {"css": css_url()}         # → outfitkit.min.css (sin prefijo)
```

Resultado: `{{ button("Save") }}` → `<button class="btn btn--primary">…</button>`.

### Cambiar a prefijo `ok-` (solo si lo necesitas)

```python
register_globals(env, ok_prefix="ok-")
ctx = {"css": css_url(prefix="ok-")}     # → outfitkit.ok.min.css
```

Resultado: `{{ button("Save") }}` → `<button class="ok-btn ok-btn--primary">…</button>`.

### Regla de oro

El **prefijo de las macros** y el **bundle CSS cargado** tienen que coincidir. Como ambos se controlan desde dos líneas del setup, no es una preocupación recurrente — lo eliges una vez y olvidas.

## Sitio de demos

Componentes en vivo con código fuente al lado, navegable:
**https://outfitkit.github.io/outfitkit/**

## Estructura del repositorio

```
outfitkit/
├── css/                ← fuentes CSS sin minificar (lo que editas)
│   ├── tokens.css      ← variables --ok-* (paleta, spacing, themes)
│   ├── base.css        ← reset + tipografía
│   ├── utilities.css   ← .ok-flex, .ok-gap-*, .ok-text-*
│   ├── outfitkit.css   ← entry point con @import de todo
│   └── components/     ← 44 archivos, uno por familia (button, card, modal, ...)
├── dist/               ← bundles generados SOLO en CI al taggear (no editar a mano)
│   ├── outfitkit.css        (concatenado, sin prefijo — default)
│   ├── outfitkit.min.css    (minificado, sin prefijo — default)
│   ├── outfitkit.ok.css     (concatenado, prefijo ok- — opt-in)
│   └── outfitkit.ok.min.css (minificado, prefijo ok- — opt-in)
└── showcase/           ← macros Jinja + sitio de demos + paquete PyPI
```

## Contribuir

### Editar CSS

Edita los archivos en `css/`. Para previsualizar tus cambios:

```html
<link rel="stylesheet" href="./css/outfitkit.css">
```

cargado desde un servidor local cualquiera (`python3 -m http.server 8000`). No hay build local. Cuando estés contento, push y abre PR.

### Releases

El bundle minificado lo genera la Action `css-build.yml` al taggear:

```bash
git tag v3.0.0
git push origin v3.0.0
```

La Action concatena `css/*.css`, minifica con `lightningcss-cli` y commitea `dist/outfitkit.{css,min.css}` al tag. jsDelivr sirve `@v3.0.0/dist/outfitkit.min.css` y `@latest` automáticamente.

## Convenciones

### Naming (BEM-light)

```
.ok-{block}              base               .ok-card
.ok-{block}__{element}   child element      .ok-card__header
.ok-{block}--{modifier}  variant            .ok-btn--primary
.is-{state}              runtime state      .is-active, .is-open
```

### Theming

Themes se aplican vía atributo `data-theme` en `<html>` o cualquier subárbol:

```html
<html data-theme="erplora">  <!-- default, dark terracota -->
<html data-theme="dark">
<html data-theme="light">
```

Cualquier variable `--ok-*` puede sobreescribirse para crear tu propio theme.

## Licencia

MIT.
