# OutfitKit 2.0 — Roadmap

> Estado tras la universalización completa (2026-05-11).
> v2.0.0 listo para tag tras QA visual final.
> **Fase H** (eliminación de elementos `__`, composición con contexto)
> en ejecución desde 2026-05-14 — ver sección dedicada abajo.

## Estado actual ✅

### Fundación (commits 49dc707 → 5fe3639)
- [x] `tokens.css` con schema Ionic-like (colores × 6 variantes, steps, globals, safe-area)
- [x] `modifiers.css` con `.primary/.danger/.lg/.glass/...` universales (patrón Bulma v1)
- [x] `utilities.css` Tailwind-naming sin prefijo
- [x] `reset.css` moderno
- [x] 72 macros JinjaX migrados a multi-class (sin BEM `--variant`)
- [x] Themes verificados (default · corporate · glass · glass-mono · mono)
- [x] Sed-rename masivo: `ok-` → vacío en pages + jinja + chrome (29.4k clases)

### Universalización v2 (commits 13d94f3 → 2e0e5dd, 2026-05-11)
- [x] **Piloto** (`13d94f3`): clases universales nuevas en modifiers.css:
      `.title .sub .label .value .meta .heading .head .body .foot`
      `.row .col .actions .divider .item .icon .icon-disc .close .line-input`
      `.blur .saturate .glass .elevated .brightness .dim`.
      Refactor modal + invoice como prueba del patrón.
- [x] **App shell** (`80697fe`): `.app + .page + .content + .scroll`. BEM
      `.app__main/.app__body/.app__tabbar/.app__sidebar-overlay` eliminados.
      87 pages migradas. `{{ ok_prefix }}` eliminado end-to-end (macros,
      build.py, package Python). v2 es exclusivamente sin prefijo.
- [x] **Ronda 1** (`a57a157`): 6 familias en paralelo —
      overlays (drawer, toast, tooltip, popover, banner, callout, context_menu, cmdk, system_overlays),
      surfaces (card, kpi, stat, stats, empty, panel, accordion, list, tree),
      forms (12 componentes), data (table, datatable, sparkline, chart, timeline, stepper),
      nav (sidebar, topbar, tabbar, menubar, navbar, footer, breadcrumbs),
      pickers (datepicker, timepicker, colorpicker, otp, pinpad, rating).
      −373 LOC neto, 139 ficheros.
- [x] **Ronda 2** (`2e0e5dd`): 5 familias finales —
      workflow (kanban, calendar, chat, gallery, states),
      industria (manufacturing, hr, multimedia, public),
      POS (pos, numpad, pay, receipt, kds),
      commerce-rest (pmatrix, sign, loyalty, ticket, event-card, product, pdp-gallery, pdp-qty),
      layout-extra (mobile, section, hover-card).
      −232 LOC, **73 tokens borrados**, 99 ficheros.
- [x] **Cleanup tokens huérfanos**: 8 tokens borrados (mfg-sku-fz,
      mfg-wo-pad, hr-card-avatar-size, hr-chart-h, hr-perf-dot,
      popover-pad-x/y/footer-pad-y).
- [x] **Tokens totales**: 149 (v1.5) → 970 (bloque D) → **655 (post-universalización)**.

### Compliance
- [x] Hook PreToolUse global: bloquea cualquier `git commit/tag`, `gh pr/release`
      que mencione Claude/Anthropic/Co-Authored-By/"Generated with".
- [x] Verificado: GitHub `OutfitKit/outfitkit` 0 referencias en commits ni tags.
- [x] Pivote git: develop branch principal, main como release branch.

---

## Pendiente release v2.0.0

- [ ] **QA visual final** — recorrido Playwright 8-10 páginas representativas
      (modal, drawer, invoice, datatable, pos, kanban, calendar, dashboard,
      hubs/active, marketplace/hub-index) en 3 viewports (Desktop/Tablet/Mobile)
      tras toda la universalización. Verificar que no hay regresiones visibles.
- [ ] **F1 · Tag git v2.0.0** — `git tag v2.0.0` + push tag + GitHub release
      con notes:
      * Breaking changes: sin prefijo `ok-`, sin BEM `__variant`, schema
        Ionic, modificadores universales (color + size + efecto + elementos
        compositivos `.title/.sub/.head/.body/.foot/.content/.scroll/etc`).
      * v1.5.x sigue disponible (`pip install outfitkit==1.5.0`,
        `outfitkit@1.5.0` en jsDelivr) para consumidores que no migren.
- [ ] **F2 · jsDelivr verify** — `https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@2.0.0/dist/outfitkit.min.css`
      sirve la versión correcta. Test con curl + visual check.
- [ ] **F3 · PyPI** — `python -m build && twine upload dist/*` desde
      `showcase/pyproject.toml` (ya está en 2.0.0).

---

## Fase H · Eliminación de elementos `__` (composición con contexto)

> ✅ **COMPLETADA 2026-05-15.** Revierte la decisión cerrada #6.
> Resultado verificado: **0 `__`** en todo `css/` y en los ~240 templates,
> **0 modificadores `--` BEM** en componentes y bloques `<style>`,
> build OK, smoke test 200 en 20 páginas representativas.
> 246 ficheros tocados (+12.6k/−12.1k, neto equilibrado).
> Pendiente: QA visual (tabbar desktop+mobile) — ver nota al final.

**Objetivo.** Cero clases NO genéricas en CSS y templates — ni BEM `__`
ni compuestas con guion. `.bom__head` → `.bom .head`,
`.sidebar-brand-text` → `.sidebar > .head .text`: clases 100 % genéricas,
el componente aporta el contexto vía selector descendiente.

**Alcance (decidido 2026-05-14): máximo.** No solo nombres de elemento —
también las raíces compuestas pasan a `base.modificador` cuando aplica
(`.event-card` → `.card.event`).

**Inventario.** 1.251 clases `__` únicas (2.361 ocurrencias) + ~209 clases
compuestas con guion, en 47 CSS de componentes · ~350 templates. Más ~9
stragglers de modificadores `--`.

**Principio de migración.**
- `.comp__el { … }` → `.comp .el { … }`. Usar `> .el` (hijo directo)
  cuando haya componentes anidados que compartan nombre de elemento.
- Sufijo ya universal (`head/title/body/label/value/icon/item/row/
  actions/meta/sub/divider/foot/btn/list`) → reutilizar la clase
  universal; la geometría específica se funde en `.comp .head { … }`.
- Sufijo nuevo → clase genérica scoped. La promoción a universal en
  `modifiers.css` se difiere a una pasada de optimización posterior.
- Colisión con modificador reservado (`brand`, `info`, `link`, `block`,
  `soft`, `light`…) → usar el siguiente sustantivo genérico (`.logo`).
- Especificidad: `.comp .head` (0,2,0) gana siempre a `.head` universal
  (0,1,0), y `modifiers.css` carga antes que `components/*` → cascada OK.
- NO borrar la regla: el cuerpo no cambia, solo el selector.

**Cubos de trabajo.**
- [x] **H0 · Stragglers `--`** — `chat-*`, `masonry--N`, `kpi/stat__delta`,
      `prod-art--*`, `hub-modcard--*`, etc. todos a multi-clase.
- [x] **H1 · Remapeo trivial** — sufijos con universal existente, fundidos
      en selector con contexto.
- [x] **H2 · Compuestos con guion** — `.comp-area-thing` → `.comp .area
      .thing`; raíces compuestas tipo `.event-card` → `.card.event` o
      mantenidas como root cuando son identidad de componente.
- [x] **H3 · Cola larga con contexto** — los ~990 restantes, fichero a
      fichero vía workers Sonnet (60 CSS + 38 ficheros con `<style>`).
- [ ] **H4 · (diferido) Promoción de universales** — deduplicar los
      genéricos recurrentes (`bar name time track dot step cell…`) a
      `modifiers.css`. Optimización post-release, no bloquea.

**Orden de ataque** (por carga `__`, partición por fichero, sin solapes):
- [x] Piloto 1: `card.css` (card+kpi+stat+empty) + 31 templates — patrón
      `.comp__el` → `.comp .el` validado (build OK, 0 `__`).
- [x] Piloto 2: `sidebar.css` + 76 templates — patrón compuestos
      (`.sidebar-brand-text` → `.sidebar > .head .text`) validado.
- [~] manufacturing (246) · navigation (241) · hr (178) · multimedia (149)
      — wave 1 de workers Sonnet en curso
- [ ] commerce (127) · pos (112) · data-extra (110) · calendar (88)
- [ ] editors (82) · states (77) · charts (69) · forms-advanced (65)
- [ ] pickers (62) · timeline (61) · forms-extra (61) · system-overlays (60)
- [ ] forms-inputs (60) · forms (50) · kanban (49) · feedback-extra (46)
- [ ] actions-extra (42) · table (41) · overlays (39) · orphan-variants (38)
- [ ] selection (37) · layout-extra (34) · progress (29) · cmdk (27)
- [ ] inline-feedback (24) · public (18) · mobile (18) · resto (<10)
- [ ] Templates: barrido paralelo de los ~350 jinjax/pages. Verificar
      que el ancestro lleva la clase de componente antes de quitar el
      prefijo del hijo.

**Workers.** Sonnet por fichero CSS (ownership exclusivo → sin contención).
Cada worker emite su replacement map. Los templates se migran centralmente
desde los maps reunidos (no se pueden partir por componente: una página usa
muchos componentes). Claude para revisión por lote. Aviso operativo: no
lanzar demasiados a la vez (se observó carrera de permisos) y dejarlos
terminar — no matar al primer aviso.

**Verificación.**
- [ ] `grep -rE '__' css/components/` → 0 · ídem en templates.
- [ ] Build showcase + smoke curl por familia.
- [ ] Recorrido Playwright QA visual (se solapa con el QA del release).
- [ ] Stylelint rule "cero `__`" (encaja con E1 del tooling pendiente).

**Pregunta abierta — ¿bloquea v2.0.0?** Es un breaking change adicional.
Recomendación: plegarlo dentro de v2.0.0 (el tag aún no está puesto).

**Pendiente tras Fase H (no bloquea el grep, sí recomendable antes del tag):**
- [ ] **QA visual** — recorrido en desktop + mobile; `.tabbar` es prioritario
      (navegación de módulos en ambos viewports). Playwright/manual.
- [ ] **Revisión de inconsistencias menores entre workers** — p.ej.
      `pub-nav__cart-count` mapeado de 2 formas (catalog vs product);
      `.empty` y `.cmdk` definidos en 2 ficheros (duplicados sin reconciliar);
      `status-dot` reconciliado a `.status.dot`; algunos helpers compuestos
      (`mp-head/mp-icon/mp-foot`, `help-icon`…) que los workers mantuvieron
      como roots — revisar si encajan con el alcance "todo descompuesto".
- [ ] **Commit** — 246 ficheros sin commitear; agrupar por fase/familia.

---

## Pendiente post-release (nice-to-have)

- [ ] **test_dual_mode.py rewrite** — los 574 lines de payloads asumen
      el prefijo `ok-` v1. La invariante (macro vs JinjaX emiten mismo HTML)
      sigue siendo válida; reescribir contra el sistema universal.
- [ ] **D5 docs/*.md** — los 7 docs (ADDING-A-COMPONENT, ARCHITECTURE,
      MAINTAINING, PUBLISHING, README, THEMES, TROUBLESHOOTING) todavía
      hablan de v1 (`ok-` prefix, BEM `--variant`). Actualizar a v2.
- [ ] **D4 llms.txt / llms-full.txt** — todavía advertise v1.
- [ ] **D3 design-system.html** — añadir Ionic 6-prop palette table +
      Bulma multi-class composition examples.
- [ ] **TOKEN-MISSING** acumulados: `--cal-week-row-h: 56px`,
      `--cal-cell-min-h: 96px`, `--border-w-3: 3px` (spinner), valoraciones
      acumuladas de cada worker (ver `/tmp/worker-*-report.md`).
- [ ] **Migración consumidores** (G): pinning Cloud + Hub a
      `outfitkit==2.0.0`. Worker-G confirmó que no hay clases `ok-*` que
      migrar en Cloud/Hub, pero pin pip queda al usuario.
- [ ] **Tooling (E)**:
      - **E1 · Stylelint** — config con reglas: cero literales numéricos en
        components/* (excepto contextos permitidos), sin prefijo `ok-`,
        sin BEM `__variant`.
      - **E2 · Visual regression** — Playwright snapshots de páginas clave
        contra baseline en CI.
      - **E3 · GitHub Actions CI** — workflow build + stylelint + visual
        regression en cada push.

---

## Histórico (bloques A-G v1, completados o reemplazados)

Las secciones originales del ROADMAP v1 (A: API externalizada, B: verificación
visual, C: mobile+Datastar, D: pulido, E: tooling, F: publicación, G: migración
consumidores) están todas completadas o **reemplazadas conceptualmente** por
la universalización de v2:

- **A** (API externalizada `--component-*` por componente) → reemplazada por
  el sistema universal. Los componentes ya no exponen su propia API
  namespaced; consumen `--background/--color/--variant/--size/--text/etc.`
  directamente.
- **B** (verificación visual ~110 páginas) → verificada parcialmente con
  Playwright en piloto + smoke por curl en ronda 1/2.
- **C** (mobile + Datastar) → toggle Viewport implementado en showcase,
  Datastar smoke tests verificados manualmente en componentes clave.
- **D** (literales → tokens) → completado en bloque D + ampliado en
  rondas 1/2.
- **E** (tooling) → pendiente nice-to-have, no bloquea release.
- **F** (publicación) → pendiente, ver "Pendiente release v2.0.0".
- **G** (migración consumidores) → discovery completado, pin pip pendiente.

## Resumen ejecutivo

| Bloque | Items | Tiempo | Crítico? |
|---|---|---|---|
| A. API externalizada | 9 | 6-8h | Alto (publicabilidad pro) |
| B. Verificación visual | 11 | 1-2h | Medio (QA) |
| C. Mobile + Datastar | 8 | 1h | Medio (UX) |
| D. Pulido | 5 | 2-3h | Bajo (cosmético) |
| E. Tooling | 3 | 2-4h | Bajo (DX) |
| F. Publicación | 3 | 1h | Alto (release) |
| G. Migración | 2 | 2-4h | Alto (consumidores) |
| H. Eliminación `__` | ~13 | 18-26h | Alto (breaking) |
| **TOTAL** | **54** | **33-49h** | |

## Cómo arrancar el showcase

```bash
cd outfitkit/showcase
OUTFITKIT_BASE="" OUTFITKIT_CSS=local .venv/bin/python serve.py
# → http://localhost:7777/
```

## Backups disponibles

- `/tmp/outfitkit-css-pre-cierre` — estado pre lote 1
- `/tmp/outfitkit-css-pre-purga-final` — pre primer pase literales
- `/tmp/outfitkit-pre-rename-backup` — pre rename masivo `ok-`
- `/tmp/outfitkit-pre-rebuild-completo` — pre segundo rebuild
- `/tmp/outfitkit-components-backup` — pre purga literales components

## Decisiones cerradas (no reabrir sin razón fuerte)

1. CSS puro · no Tailwind · no Node toolchain
2. Variables sin prefijo (`--bg`, `--space-3`, `--color-primary`)
3. Schema Ionic-like (color × 6 variantes, steps, globals, safe-area)
4. Modificadores universales tipo Bulma (`class="btn primary lg"`)
5. `.secondary` = neutral (compat Bootstrap/shadcn) · `.accent` para 2º color
6. BEM eliminado por completo — modificadores `--` (universalización v2)
   y elementos `__` (Fase H, 2026-05-14). Composición con contexto:
   `.comp__el` → `.comp .el`, nombres de elemento siempre genéricos
7. JinjaX templates con `{{ ok_prefix }}` configurable (default vacío)
8. `tokens.css` mantiene alias `--ok-*` retro-compat para Cloud/Hub
9. Dist en `dist/outfitkit.css` + `.min.css`
10. v2.0.0 = breaking change (consumidores migran o fijan `@1.5.0`)
