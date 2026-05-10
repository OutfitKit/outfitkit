# Adding a component

Receta paso a paso para añadir un componente nuevo a OutfitKit. Ejemplo concreto: `notification-banner`.

Pre-requisitos: ver [MAINTAINING.md](./MAINTAINING.md#local-dev) para el setup del servidor local.

## 1 · Decide el BEM root

- En la fuente (`css/`) los selectores **siempre** llevan `ok-`. Vivimos con `.ok-notification-banner`.
- El bundle por defecto (`dist/outfitkit.min.css`) los emite **sin** prefijo, gracias al script de `css-build.yml` que reemplaza `.ok-` → `.` sólo en selectores.
- Las macros usan `{{ ok_prefix }}notification-banner` — el showcase pasa `"ok-"`, los consumidores PyPI pasan `""` por defecto.

Convención BEM-light:

```
.ok-notification-banner                  block
.ok-notification-banner__icon            element
.ok-notification-banner--success         modifier
.is-dismissed                            runtime state
```

## 2 · CSS — `css/components/notification-banner.css`

Crea el archivo. Usa tokens (`var(--ok-*)`), no valores duros:

```css
/* ============================================================
   OutfitKit · Notification banner
   Aviso flotante encima del shell. Variantes: info / success / warn / danger.
   ============================================================ */

.ok-notification-banner {
  --_nb-bg: var(--ok-bg-2);
  --_nb-fg: var(--ok-ink);
  --_nb-bd: var(--ok-line-2);

  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: var(--_nb-bg);
  color: var(--_nb-fg);
  border: 1px solid var(--_nb-bd);
  border-radius: var(--ok-radius-md);
  box-shadow: var(--ok-shadow-sm);
  font-size: var(--ok-text-md);
}

.ok-notification-banner__icon {
  display: inline-flex;
  flex: 0 0 auto;
  width: 16px;
  height: 16px;
  color: var(--ok-ink-3);
}

.ok-notification-banner__body { flex: 1 1 auto; }
.ok-notification-banner__close {
  background: transparent;
  border: 0;
  color: var(--ok-ink-3);
  cursor: pointer;
}
.ok-notification-banner__close:hover { color: var(--ok-ink); }

/* Variants */
.ok-notification-banner--info    { --_nb-bd: var(--ok-info); }
.ok-notification-banner--success { --_nb-bd: var(--ok-leaf); }
.ok-notification-banner--warn    { --_nb-bd: var(--ok-warn); }
.ok-notification-banner--danger  { --_nb-bd: var(--ok-danger); }

/* Runtime state */
.ok-notification-banner.is-dismissed { display: none; }
```

## 3 · Registra el `@import` en `css/outfitkit.css`

Sin esto, el bundle no incluye tu CSS:

```css
/* === Inline feedback adicional === */
@import "./components/notification-banner.css";
```

## 4 · Macro Jinja — `showcase/src/outfitkit/templates/ui/notification_banner.jinja`

Patrón **dual-mode** (vanilla Jinja2 + JinjaX). Copia esto verbatim:

```jinja
{#def title, description="", variant="info", dismissible=false, attrs=None #}

{% macro notification_banner(title, description="", variant="info", dismissible=false, attrs=None) -%}
{%- set _attrs = attrs|attr('as_dict')|default(attrs or {}) -%}
<div class="{{ ok_prefix }}notification-banner {{ ok_prefix }}notification-banner--{{ variant }}"
  {%- for key, value in _attrs.items() %} {{ key }}="{{ value }}"{% endfor %}>
  <span class="{{ ok_prefix }}notification-banner__icon">
    <iconify-icon icon="lucide:bell" width="16" height="16"></iconify-icon>
  </span>
  <div class="{{ ok_prefix }}notification-banner__body">
    <strong>{{ title }}</strong>
    {% if description %}<div>{{ description }}</div>{% endif %}
  </div>
  {{ caller() }}
  {% if dismissible %}
    <button class="{{ ok_prefix }}notification-banner__close" aria-label="Cerrar">×</button>
  {% endif %}
</div>
{%- endmacro %}

{% if title is defined %}
  {% call notification_banner(title, description=description, variant=variant, dismissible=dismissible, attrs=attrs) %}{{ content }}{% endcall %}
{% endif %}
```

Las tres piezas que **no** puedes saltarte:

- `{#def ... #}` — declara los props para JinjaX (`<NotificationBanner title="..." />`).
- `{% macro ... %}` — la implementación, llamable desde Jinja2 vanilla.
- `{% if title is defined %}` — el shim al final que ejecuta el macro cuando JinjaX renderiza el archivo como componente.

Reglas: **siempre** `{{ ok_prefix }}` delante de cada clase. Nunca hardcodees `ok-`.

## 5 · Página de demo — `showcase/pages/components/notification_banner.html`

```jinja
{% extends "_layout.jinja" %}
{% from "ui/notification_banner.jinja" import notification_banner %}
{% from "demo_frame.jinja" import demo_frame %}

{% block title %}Notification banner — OutfitKit{% endblock %}

{% block content %}
<h1>Notification banner</h1>
<p class="showcase__lead">Aviso flotante con icono, descripción y acción opcional.</p>

{% set _src_jinja %}{% raw %}{% from "ui/notification_banner.jinja" import notification_banner %}
{% call notification_banner(title="Nuevo mensaje", description="Tienes 3 sin leer", variant="info") %}{% endcall %}{% endraw %}{% endset %}
{% set _src_jinjax %}{% raw %}<NotificationBanner title="Nuevo mensaje" description="Tienes 3 sin leer" variant="info"></NotificationBanner>{% endraw %}{% endset %}

{% call demo_frame("Info", jinja_src=_src_jinja, jinjax_src=_src_jinjax) %}
{% call notification_banner(title="Nuevo mensaje", description="Tienes 3 sin leer", variant="info") %}{% endcall %}
{% endcall %}

{% call demo_frame("Success dismissible") %}
{% call notification_banner(title="Pago recibido", description="Factura #1042 cobrada", variant="success", dismissible=True) %}{% endcall %}
{% endcall %}

{% call demo_frame("Danger") %}
{% call notification_banner(title="Conexión perdida", description="Reintentando…", variant="danger") %}{% endcall %}
{% endcall %}
{% endblock %}
```

## 6 · Sidebar nav — `showcase/chrome/sidebar.jinja`

Localiza el grupo correcto (en este caso "Surfaces") y añade la entrada:

```python
("/components/notification_banner.html", "Notification banner", _ICON_ALERT, ""),
```

## 7 · Test local

```bash
cd /Users/ioan/Desktop/code/ERPlora/outfitkit/showcase
OUTFITKIT_CSS=local OUTFITKIT_BASE="" python build.py
python -m http.server 8000 -d build
# http://localhost:8000/components/notification_banner.html
```

Cambia tema (Dark/Light) y template (Default → Mono → Glass…) desde el topbar para verificar que tus tokens funcionan en todas las variantes.

## 8 · Tests visuales

```bash
cd /Users/ioan/Desktop/code/ERPlora/outfitkit/showcase/tests/visual
npm install            # primera vez
npm test               # falla si la baseline no existe — ejecuta:
npm run test:update    # captura baseline para tu nueva página
```

Si quieres incluir tu página en la suite de regresión, añade su path al array `PAGES` en `showcase.spec.ts`.

## 9 · Commit + push

```bash
git add css/components/notification-banner.css \
        css/outfitkit.css \
        showcase/src/outfitkit/templates/ui/notification_banner.jinja \
        showcase/pages/components/notification_banner.html \
        showcase/chrome/sidebar.jinja \
        showcase/tests/visual/__screenshots__/
git commit -m "feat: notification-banner component"
git push origin develop
```

Push a `main` dispara el deploy del showcase. Para distribuir el CSS, taggea (ver [PUBLISHING.md](./PUBLISHING.md)).
