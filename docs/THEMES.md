# Themes

OutfitKit ships con 5 templates: `default`, `corporate`, `glass`, `glass-mono`, `mono`. Cada uno funciona en dark (`erplora`) y light (`erplora-light`).

## 1 · Arquitectura

Tres capas:

1. **`css/tokens.css`** define el contrato global: paleta, tipografía, spacing, sizing semántico, radios, sombras, motion y shell layout.
2. **`css/themes/<name>.css`** sobreescribe una parte de ese contrato cuando un template está activo.
3. **Componentes (`css/components/*.css`)** consumen esos tokens globales y el contrato de modificadores. No deberían necesitar overrides por theme a nivel de componente.

Ejemplo:

```css
[data-template="mono"] {
  --brand: #84CC16;
  --radius-md: 4px;
  --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.06);
}

[data-template="mono"][data-theme="erplora-light"] {
  --bg: #FFFFFF;
  --ink: #171717;
}

[data-template="mono"][data-theme="erplora"] {
  --bg: #0A0A0A;
  --ink: #FAFAFA;
}
```

## 2 · Activación

La activación es un atributo en `<html>`:

```html
<html data-theme="erplora" data-template="mono">
<html data-theme="erplora-light" data-template="">
```

`data-theme` distingue dark vs light. `data-template` es opcional; vacío significa usar el contrato base de `tokens.css`.

## 3 · Qué conviene tocar en un theme

Lo habitual:

- `--brand`, `--brand-*`
- `--bg`, `--bg-*`
- `--ink`, `--ink-*`
- `--line`, `--line-*`
- `--radius-*`
- `--shadow-*`
- `--font-*`

Lo que no debería tocar un theme:

- dimensiones privadas de un componente
- clases concretas de componentes
- tamaños semánticos por componente

## 4 · Añadir un template nuevo

1. Crea `css/themes/<name>.css`.
2. Añade el `@import` en `css/outfitkit.css`.
3. Añade la opción al selector del showcase.
4. Si el runtime del showcase whitelistea templates, añade el nuevo nombre.
5. Verifica dark y light.

## 5 · Compatibilidad

La fuente actual del sistema trabaja con variables sin prefijo (`--bg`, `--brand`, `--space-4`, etc.). Si un consumer externo todavía dependía de `--ok-*`, necesita migrar a los nombres canónicos.
