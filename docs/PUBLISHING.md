# Publishing

OutfitKit publica **tres artefactos independientes**, cada uno con su propio trigger y workflow. No hay release "única" — cortas la que necesites.

| Artefacto | Trigger | Workflow | Destino |
|---|---|---|---|
| CSS bundle | tag `v*` | `.github/workflows/css-build.yml` | jsDelivr `gh/OutfitKit/outfitkit` |
| Python package | tag `pypi-v*` | `.github/workflows/pypi-publish.yml` | PyPI `outfitkit` |
| Showcase site | push a `main` | `.github/workflows/pages.yml` | https://outfitkit.github.io/outfitkit/ |

Si sólo cambiaste el CSS y un demo, no necesitas tocar PyPI. Si subes `__version__`, sí. Decide qué ha cambiado y taggea sólo eso.

## 1 · CSS bundle (`v<X>.<Y>.<Z>`)

```bash
git tag v1.4.0
git push origin v1.4.0
```

`css-build.yml` (resumen, ver el archivo para el detalle):

1. Resuelve los `@import` recursivamente partiendo de `css/outfitkit.css` → un único string.
2. Escribe `dist/outfitkit.ok.css` (con prefijo `ok-`, tal cual la fuente).
3. Deriva `dist/outfitkit.css` aplicando `re.sub(r'\.ok-(?=[a-zA-Z])', '.', src)` — strip de `ok-` **sólo en selectores de clase** (los tokens `--ok-*` y `@keyframes ok-*` se mantienen).
4. Minifica los dos con `rcssmin` → `dist/*.min.css`.
5. Sanity-checks: tokens y keyframes deben seguir prefijados; selectores no deben tener `.ok-`.
6. Commit + force-push del `dist/` al **mismo tag** (no a `main`).

URLs resultantes:

```
https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@v1.4.0/dist/outfitkit.css           ← unprefixed, dev
https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@v1.4.0/dist/outfitkit.min.css       ← unprefixed, prod (default)
https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@v1.4.0/dist/outfitkit.ok.css        ← ok-prefix, dev
https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@v1.4.0/dist/outfitkit.ok.min.css    ← ok-prefix, prod (opt-in)
```

Y los alias `@latest`:

```
https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@latest/dist/outfitkit.min.css
```

## 2 · PyPI (`pypi-v<X>.<Y>.<Z>`)

Pre-requisito — los tres números han de coincidir:

| Lugar | Cómo se mira |
|---|---|
| Tag | `pypi-v1.4.0` |
| `showcase/pyproject.toml` | `version = "1.4.0"` |
| `showcase/src/outfitkit/__init__.py` | `__version__ = "1.4.0"` |

```bash
# 1. Bump las dos versiones del package
$EDITOR showcase/pyproject.toml
$EDITOR showcase/src/outfitkit/__init__.py
git commit -am "chore: bump to 1.4.0"
git push origin develop

# 2. Tras mergear a main:
git tag pypi-v1.4.0
git push origin pypi-v1.4.0
```

`pypi-publish.yml`:

1. `python -m build --outdir showcase/dist showcase/` — build desde `showcase/` (NO desde la raíz; el `pyproject.toml` vive ahí).
2. Sube `wheel` + `sdist` con `pypa/gh-action-pypi-publish` usando **OIDC Trusted Publishing**. No hay tokens en GitHub Secrets — la confianza está configurada en pypi.org como Trusted Publisher contra el repo `OutfitKit/outfitkit`.

Tras el push, en ~1 minuto el paquete aparece en https://pypi.org/project/outfitkit/.

## 3 · Showcase (push a `main`)

Cero ceremonia:

```bash
git checkout main
git merge develop
git push origin main
```

`pages.yml`:

1. `pip install -e ".[showcase]"` desde `showcase/`.
2. `python build.py` con los defaults — `OUTFITKIT_BASE=/outfitkit`, CSS desde `cdn.jsdelivr.net@main`.
3. Sube `showcase/build/` como artefacto y deploya a GH Pages.

Resultado: cambios visibles en https://outfitkit.github.io/outfitkit/ en ~2 minutos.

## 4 · Cache de jsDelivr

`@main` y `@latest` están cacheados por el edge de jsDelivr. Tras un push o un tag, los browsers pueden seguir viendo el contenido viejo varios minutos. Hay tres formas de lidiar con eso:

**a) Esperar.** Suele tardar 1-5 minutos.

**b) Purga manual** (recomendado tras un tag de release):

```bash
curl -X POST 'https://purge.jsdelivr.net/' \
  -H 'Content-Type: application/json' \
  -d '{
    "path": [
      "gh/OutfitKit/outfitkit@latest/dist/outfitkit.min.css",
      "gh/OutfitKit/outfitkit@latest/dist/outfitkit.ok.min.css",
      "gh/OutfitKit/outfitkit@main/css/outfitkit.css"
    ]
  }'
```

**c) Pin a un tag inmutable.** En producción **siempre** consume `@v1.4.0`, no `@main` ni `@latest` — los tags son immutables, cacheables forever, y nunca te sorprenden con un cambio:

```html
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@v1.4.0/dist/outfitkit.min.css">
```

Reserva `@main` para el showcase de OutfitKit y dev local, `@latest` para sandbox/playground, y `@v<tag>` para todo proyecto productivo (Hub, Cloud, m_*).

## 5 · Versionado

OutfitKit usa SemVer estricto:

- **PATCH** (`1.4.0` → `1.4.1`) — fix CSS o macro sin cambios visibles.
- **MINOR** (`1.4.0` → `1.5.0`) — componente nuevo, theme nuevo, prop nueva opcional.
- **MAJOR** (`1.x` → `2.0`) — rename de clase, eliminación de prop, cambio de comportamiento default.

Los tres tags (`v1.5.0`, `pypi-v1.5.0`, push a `main`) deben ir en este orden:

1. Bump de versiones en `pyproject.toml` + `__init__.py`, push a `develop`.
2. Merge a `main` (dispara deploy del showcase).
3. `git tag v1.5.0 && git push origin v1.5.0` (CSS).
4. `git tag pypi-v1.5.0 && git push origin pypi-v1.5.0` (PyPI).

Si se invierte el orden no rompe nada, pero tener el showcase actualizado antes del CSS evita reportes de "el demo no muestra mi cambio".

## 6 · Si la release falla

| Falla | Diagnóstico |
|---|---|
| `css-build.yml` rojo en `assert ".ok-" not in stripped` | un selector se escribió con el prefijo de forma rara (escapes, comentarios). Mira el output del Action. |
| `pypi-publish.yml` rojo en "Trusted Publishing" | versión de `pyproject.toml` ≠ tag, o el Trusted Publisher ya no apunta al workflow correcto. |
| `pages.yml` rojo en `python build.py` | template no encontrado o syntax error en un `.jinja`. Reproduce local con `python showcase/build.py`. |

Ver también [MAINTAINING.md](./MAINTAINING.md#si-algo-se-rompe-mira-aquí) para troubleshooting cruzado.
