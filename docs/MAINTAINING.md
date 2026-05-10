# Maintaining OutfitKit

Guía rápida para el maintainer. Si vienes a arreglar un bug o cortar una release, lee esto primero.

## Qué importa: tres cosas

OutfitKit es **tres artefactos independientes** que conviven en el mismo repo:

1. **Librería CSS** (`css/`) — fuente con prefijo `ok-`. Lo que el navegador descarga.
2. **Macros Jinja** (`showcase/src/outfitkit/`) — paquete Python publicado en PyPI como `outfitkit`.
3. **Showcase** (`showcase/`) — sitio estático generado con staticjinja, deployado a GitHub Pages.

Los tres tienen su propio trigger de release. Ver [PUBLISHING.md](./PUBLISHING.md).

## Repo layout

| Top-level | Rol | Cuándo lo tocas |
|---|---|---|
| `css/` | Fuente CSS sin minificar (con `ok-` prefix). | Editas componentes, themes, tokens. |
| `css/components/` | Un archivo por familia (~44 archivos). | Añades o ajustas un componente. |
| `css/themes/` | Overrides de tokens por template. | Ajustas o creas un theme. |
| `dist/` | Bundles generados. **Nunca commit a mano** — los genera CI al taggear. | Nunca. |
| `showcase/src/outfitkit/` | Paquete Python (macros + helpers). | Cambias firma de un macro o subes versión. |
| `showcase/src/outfitkit/templates/ui/` | Macros Jinja (`<Component />` o `{{ component(...) }}`). | Añades componente o tocas su HTML. |
| `showcase/pages/` | Páginas del sitio de demos. | Añades página de componente o app demo. |
| `showcase/chrome/` | Sidebar + demo_frame del showcase. | Añades una entrada al nav. |
| `showcase/static/` | JS auxiliar (theme runtime). | Tocas el bootstrap del showcase. |
| `showcase/build.py` | Generador estático. | Cambias cómo se compila el sitio. |
| `showcase/tests/visual/` | Suite Playwright con baselines. | Añades cobertura visual. |
| `.github/workflows/` | 3 workflows (CSS, PyPI, Pages). | Cambias el pipeline de release. |
| `llms.txt`, `llms-full.txt` | Resumen para agentes LLM. | Cambias una API pública. |
| `AUDIT.md` | Auditoría histórica (parcialmente desactualizada). | Sólo lectura. |

## Hot paths — los archivos que rompen todo

- **`showcase/pages/_layout.jinja`** — base de todas las páginas. Carga CSS, theme runtime, sidebar/topbar. Si rompe, el sitio entero se cae.
- **`showcase/static/theme-runtime.js`** — bootstrap síncrono que aplica `data-theme` y `data-template` antes de Datastar. Sin él hay FOUC y los iframes no sincronizan.
- **`css/tokens.css`** — todas las variables `--ok-*`. Un nombre mal escrito aquí cascada a todos los componentes.
- **`css/outfitkit.css`** — entry point con los `@import`. Si añades un componente y olvidas el `@import`, no entra en el bundle.
- **`showcase/build.py`** — generador staticjinja + JinjaX. Configura `OUTFITKIT_BASE`, `OUTFITKIT_CSS`, registra carpetas.
- **`showcase/src/outfitkit/__init__.py`** — `__version__`, `register_globals`, `css_url`, `theme_url`. Cambio de API → release PyPI.

## "Si algo se rompe, mira aquí"

| Síntoma | Archivo más probable |
|---|---|
| FOUC: parpadeo de tema al cargar | `showcase/static/theme-runtime.js` (o falta `<script>` síncrono en `_layout.jinja`) |
| Componente sin estilos | falta `@import` en `css/outfitkit.css`, o nombre del archivo no coincide |
| `--ok-foo is not defined` | `css/tokens.css` o `css/themes/<name>.css` |
| Macro no se importa en JinjaX | `showcase/src/outfitkit/templates/ui/<name>.jinja` (¿tiene `{#def ... #}` y el shim final?) |
| Build falla con "template not found" | `showcase/build.py` — loader paths, o nombre de archivo en `pages/`/`chrome/`/`ui/` |
| 404 en `/static/theme-runtime.js` en GH Pages | `OUTFITKIT_BASE` no se está aplicando; mira `_base_path()` en `build.py` |
| jsDelivr sirve un CSS antiguo después de mergear a `main` | cache de `@main` — purgar (ver abajo) |
| PyPI publish falla | `showcase/pyproject.toml` `version` ≠ tag `pypi-vX.Y.Z` |
| Tag `vX.Y.Z` no genera `dist/` | el workflow `css-build.yml` falló — revisar Actions logs |

## Release flow (resumen)

```
git tag v1.4.0          → CI builds dist/ (concat + minify) → commits to tag → jsDelivr serves
git tag pypi-v1.4.0     → CI builds wheel + sdist → publishes to PyPI (OIDC, no tokens)
git push origin main    → CI builds showcase/build/ → deploys GH Pages
```

Detalles completos en [PUBLISHING.md](./PUBLISHING.md). Antes de taggear `pypi-v*`, sincroniza versiones:

```bash
# Ambos tienen que coincidir con el tag
grep '__version__' showcase/src/outfitkit/__init__.py
grep '^version'    showcase/pyproject.toml
```

## Local dev

Servidor del showcase apuntando a tu CSS local (no al CDN):

```bash
cd showcase
OUTFITKIT_CSS=local OUTFITKIT_BASE="" python build.py
python -m http.server 8000 -d build
# abre http://localhost:8000/
```

- `OUTFITKIT_CSS=local` — carga `css/outfitkit.css` desde el repo (en lugar de `cdn.jsdelivr.net@main`).
- `OUTFITKIT_BASE=""` — quita el prefijo `/outfitkit` (sólo para servir desde la raíz local; en GH Pages se publica en `https://outfitkit.github.io/outfitkit/`).

Para previsualizar el CSS sin pasar por staticjinja:

```bash
python3 -m http.server 8000
# abre http://localhost:8000/css/outfitkit.css
```

Los navegadores resuelven los `@import` directamente, no necesitas bundling local.

## Cache de jsDelivr

`@main` cachea agresivamente — un push a `main` puede tardar varios minutos en propagar. Purga manual:

```bash
curl -X POST 'https://purge.jsdelivr.net/' \
  -H 'Content-Type: application/json' \
  -d '{"path":["gh/OutfitKit/outfitkit@main/css/outfitkit.css"]}'
```

En producción usa siempre `@v<tag>` (immutable, cacheable forever) en vez de `@main`.

## Tests visuales

```bash
cd showcase/tests/visual
npm install            # primera vez
npm test               # corre la suite contra http://localhost:8000
npm run test:update    # regenera baselines tras un cambio intencional
```

Los baselines viven en `showcase/tests/visual/__screenshots__/`. CI corre estos tests antes de cualquier deploy. Más detalle en [ADDING-A-COMPONENT.md](./ADDING-A-COMPONENT.md#tests-visuales).
