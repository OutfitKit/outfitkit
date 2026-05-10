# OutfitKit

Librería CSS de componentes para aplicaciones web. ~260 bloques semánticos con prefijo `ok-*`, BEM-light, themeable vía CSS custom properties.

Cero JS obligatorio. Cero build pipeline para consumidores. Un solo `<link>` y listo.

## Uso (consumidor solo CSS)

OutfitKit se publica en **dos sabores**, ambos con el mismo CSS:

| Bundle | Clases | Cuándo usarlo |
|---|---|---|
| `outfitkit.min.css` | `.ok-btn`, `.ok-card`, `.ok-flex`, … | Cuando OutfitKit convive con otra librería CSS o cuando quieres distinguir tus clases en DevTools. |
| `outfitkit.unprefixed.min.css` | `.btn`, `.card`, `.flex`, … | Cuando OutfitKit es tu única librería y prefieres clases cortas (estilo Tailwind / Daisy). Hub y Cloud usan este. |

Ambos bundles comparten los mismos tokens (`--ok-*`), keyframes y animations — lo único que cambia es el nombre de los selectores de clase.

### Producción — con prefijo `ok-`

```html
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@latest/dist/outfitkit.min.css">

<button class="ok-btn ok-btn--primary">Continuar</button>
```

### Producción — sin prefijo

```html
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@latest/dist/outfitkit.unprefixed.min.css">

<button class="btn btn--primary">Continuar</button>
```

### Desarrollo — fuente sin minificar

Útil para inspeccionar reglas en DevTools sin pasar por la minificación:

```html
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@main/css/outfitkit.css">
```

La fuente en `css/` siempre lleva el prefijo `ok-`; el bundle sin prefijo se genera solo en CI cuando se etiqueta una release. Los navegadores modernos resuelven los `@import` sin problema, así que el archivo de desarrollo no necesita bundling.

## Macros Jinja (opcional)

Si tu backend es Python con Jinja2 (FastAPI, Flask, Django+jinja2 backend), puedes consumir los componentes como macros:

```bash
pip install outfitkit             # macros vanilla
pip install outfitkit[jinjax]     # + sintaxis HTML-like <Button label="x" />
```

Las macros viven en [`showcase/`](./showcase/) y se publican desde ahí a PyPI. Cualquier macro funciona con o sin JinjaX (formato dual-mode).

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
│   ├── outfitkit.css                  (concatenado, con prefijo ok-)
│   ├── outfitkit.min.css              (minificado, con prefijo ok-)
│   ├── outfitkit.unprefixed.css       (concatenado, sin prefijo)
│   └── outfitkit.unprefixed.min.css   (minificado, sin prefijo)
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
