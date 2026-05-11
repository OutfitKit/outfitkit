# Adding a component

Receta corta para añadir un componente nuevo al sistema actual.

Antes de tocar CSS, lee [COMPONENT-PATTERN.md](./COMPONENT-PATTERN.md).

## 1. Crea el CSS del componente

Archivo nuevo en `css/components/<name>.css`.

El selector raíz debe exponer variables locales genéricas:

```css
.notification-banner {
  --background: var(--bg-2);
  --color: var(--text-color);
  --border-color: var(--line-2);
  --border-radius: var(--radius, var(--radius-md));
  --height: var(--size, var(--size-md));
  --padding-x: var(--pad-x, var(--pad-md-x));
  --padding-y: var(--pad-y, var(--pad-md-y));
  --font-size: var(--text, var(--text-base));
  --gap: var(--space-2);

  display: flex;
  align-items: center;
  gap: var(--gap);
  padding: var(--padding-y) var(--padding-x);
  background: var(--background);
  color: var(--color);
  border: var(--border-w) solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: var(--font-size);
}
```

Reglas:

- consume `--variant*` y `--size` / `--pad-*` / `--text` / `--icon` / `--radius`
- no añadas tokens globales si el valor es privado del componente
- usa `rem` salvo excepciones permitidas
- evita clases combinadas tipo `.notification-banner.primary` o `.notification-banner.lg`

## 2. Registra el import

Añade el `@import` en `css/outfitkit.css`.

## 3. Crea la macro Jinja si aplica

La macro debe emitir la API CSS canónica:

```jinja
<div class="notification-banner primary">
  <div class="body">Saved correctly</div>
</div>
```

No emitas clases BEM de variante/tamaño antiguas salvo compatibilidad explícita.

## 4. Añade showcase

- `showcase/pages/components/<name>.html`
- opcionalmente template/macro en `showcase/src/outfitkit/templates/ui/`
- entrada en la navegación del showcase

## 5. Verifica

- valida dark/light y varios templates
- prueba composición con `.primary`, `.danger`, `.sm`, `.lg`, `.outline`, etc.
- revisa overrides por instancia con `style="--xxx: ..."`

## 6. Checklist

- el componente no depende de tokens `--component-*` globales
- no añade clases `.component.primary` ni `.component.lg`
- los sub-elementos solo usan BEM cuando son genuinamente específicos
- el CSS nuevo sigue el contrato de [COMPONENT-PATTERN.md](./COMPONENT-PATTERN.md)
