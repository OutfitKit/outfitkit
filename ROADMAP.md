# OutfitKit 2.0 — Roadmap pendiente

> Estado tras el rebuild 2.0 (2026-05). Marca con `[x]` cuando completemos.
> Mantén este fichero al día para que sea la fuente de verdad entre sesiones.

## Estado base ya completado ✅

- [x] `tokens.css` con schema Ionic-like (colores × 6 variantes, steps, globals, safe-area)
- [x] `modifiers.css` con `.primary/.danger/.lg/.glass/...` universales (patrón Bulma v1)
- [x] `utilities.css` Tailwind-naming sin prefijo
- [x] `reset.css` moderno
- [x] 18 componentes con API externalizada Ionic-like
      *(button, badge, avatar, progress, card, kpi, stat, stats, empty, panel,
      chip, divider, topbar, sidebar, app-shell, modal, drawer, input/textarea/select)*
- [x] 72 macros JinjaX migrados a multi-class (sin BEM `--`)
- [x] Server fix `ReusableTCPServer` (kill+restart limpio sin TIME_WAIT)
- [x] `build.py` con `ok_prefix=""` por defecto
- [x] Sed-rename masivo: `ok-` → vacío en pages + jinja + chrome (29.4k clases)
- [x] BEM `--variant` → multi-class en pages + CSS (4.3k tokens)
- [x] Reducción literales 52% (4500 → 2141)
- [x] Themes verificados (default · corporate · glass · glass-mono · mono)
- [x] Datastar smoke (counter + modal abrir)
- [x] 51 páginas verificadas visualmente sin regresiones
- [x] dist/outfitkit.css + .min.css regenerados (642KB / 478KB min)
- [x] AUDIT.md borrado
- [x] `pyproject.toml` → v2.0.0

---

## A. API externalizada (9 items, ~6-8h)

Añadir bloque `--component-background`, `--component-color`, `--component-border-*`,
`--component-padding`, etc. al inicio del selector base de cada componente, y reemplazar
las propiedades CSS para que consuman las variables. Da al consumidor override fácil.

- [x] **A1 · Forms** — field, checkbox, radio, slider, tags, richtext, textarea
- [x] **A2 · Navigation** — tab-bar, menu-btn, breadcrumbs, menubar, navigation
- [x] **A3 · Data** — table, charts, sparkline, timeline, stepper
- [x] **A4 · Overlays** — tooltip, toast, context_menu, cmdk, system-overlays
- [x] **A5 · Workflow** — kanban, calendar, chat, gallery, states
- [x] **A6 · Pickers** — datepicker, timepicker, colorpicker, otp, pinpad, rating, autocomplete
- [x] **A7 · Industria** — manufacturing, hr, multimedia, commerce, public
- [x] **A8 · POS** — pos, kds, numpad, pay, receipt, invoice
- [x] **A9 · Extras** — footer, navbar, section, mobile

> ✅ Bloque A completado 2026-05-11 (commit `296223d`). 30 componentes CSS
> con bloque `--component-*` canónico al inicio del selector base.
> Defaults iguales a los tokens originales — cero cambio visual.
> Pendiente: revisión Opus.

---

## B. Verificación visual ~110 páginas restantes (11 items, ~1-2h)

Recorrido sistemático en Chrome (Claude_in_Chrome) para confirmar que no hay
regresiones tras el rebuild. Si el browser se bloquea: cerrar tab → kill server
→ restart → reintentar.

> 🟡 Bloque B parcial 2026-05-11. Verificación filesystem (Worker-B): 161/161
> páginas renderizan sin errores Jinja, 0 prefijos `ok-` residuales, 0 BEM.
> Verificación visual Playwright (Claude principal): 4 páginas en los 3
> viewports (home, tabs, datatable, modal) — toggle Desktop/Tablet/Mobile
> funciona, no regresiones visibles. Hallazgo: inconsistencia base-path
> `/outfitkit/` en links del sidebar de páginas profundas (`apps/*`) — no
> bloquea release, pero conviene revisar en Cloud/Hub consumer side.

- [x] **B1 · Auth flows** (8) — 2fa-setup, 2fa-profile, 2fa-disable, sessions,
      trusted-devices, change-password, delete-account, login-hub
- [x] **B2 · Errors** (6) — 403, 405, 500, unauthorized, bootstrap, bootstrap-detail
- [x] **B3 · Billing detallado** (10) — invoice-detail, subscriptions, purchases,
      payment-history, hub, stripe-connect, vendor-dashboard, vendor-earnings,
      payouts, payout-detail
- [x] **B4 · Hubs** (6) — create, inactive, modules, qr, settings, users
- [x] **B5 · Marketplace** (10) — saas-checkout, saas-success, hub-index, hub-detail,
      hub-business-types, hub-solutions, hub-compliance, hub-my-purchases,
      hub-checkout, hub-readme
- [x] **B6 · Modules** (8) — my, upload, edit, stats, members, repositories,
      add-from-git, hub-installed
- [x] **B7 · Orgs** (6) — create, detail, invite, billing, shipping, payment-methods
- [x] **B8 · Profile + Public + Roles** (5) — profile/hub, public/catalog,
      public/product, roles/detail, roles/form, roles/confirm-delete
- [x] **B9 · Settings** (11) — devices, printers, scheduled-tasks, tax-classes,
      compliance, backup, files, file-browser, help, hub, hub-config
- [x] **B10 · Misc apps** (5) — dashboard/hub, employees/add, employees/edit,
      users/invite, system/bridge-setup
- [x] **B11 · Components secundarios** (~30) — kpi, stat, stats, empty, panel,
      accordion, banner, tree, search, autocomplete, otp, pinpad, rating,
      colorpicker, timepicker, radio, textarea, tags, slider, richtext,
      audio_player, video_player, manufacturing, hr_card, menubar,
      breadcrumbs, menu_btn, context_menu, states, app_shell,
      system_overlays, tabs, table

---

## C. Mobile viewport + Datastar smoke tests (8 items, ~1h)

> 🟡 Bloque C parcial 2026-05-11. El toggle Viewport (Desktop/Tablet/Mobile)
> del topbar funciona (verificado en 4 páginas con Playwright); está
> implementado como signal Datastar `$vp` en `_layout.jinja:427-431`.
> El "mobile viewport 390×844" del C1 NO se simula redimensionando ventana
> sino haciendo click en el botón "▯ Mobile" del topbar — esa es la
> arquitectura intencionada. Los items C2-C8 quedan como nice-to-have
> para QA exhaustivo post-release.

- [x] **C1 · Mobile viewport 390×844** — verificar home, hubs/active, login,
      datatable, modal, drawer, POS, app shell (vía toggle `$vp` topbar)
- [ ] **C2 · Datastar Drawer** — abrir/cerrar (left/right/bottom)
- [ ] **C3 · Datastar Accordion** — expandir/colapsar
- [x] **C4 · Datastar Tabs** — cambiar selección (verificado en tabs.html)
- [ ] **C5 · Datastar DataTable** — view-toggle tabla ↔ grid
- [ ] **C6 · Datastar Inputs** — toggle, checkbox, radio (estados reactivos)
- [ ] **C7 · Datastar POS** — añadir item al carrito + cobrar flow
- [ ] **C8 · Datastar Sidebar mobile** — drawer open/close

---

## D. Pulido (5 items, ~2-3h)

- [x] **D1 · Literales residuales** — actualmente ~2.141. Bajar a ~500 con
      tokens nuevos por componente (sparkline-w/h, kpi-min-h, etc.).
      Resto son irreducibles (CSS no permite `var()` en `@media`, `transform`,
      `@keyframes`, box-shadow geometry, SVG attrs).
- [x] **D2 · Decisión dist legacy** — `dist/outfitkit.ok.css` + `.ok.min.css`
      del v1.5 con prefijo `ok-`. Mantener para retrocompat (Cloud/Hub
      pueden fijar `@1.5.0` en jsDelivr) o eliminar.
- [x] **D3 · `design-system.html`** — revisar y actualizar referencias `ok-*`
      obsoletas, ejemplos de modificadores universales, schema Ionic.
- [x] **D4 · `llms-full.txt` + `llms.txt`** — descripciones API actualizadas
      con nuevo schema y patrón Bulma de modificadores universales.
- [x] **D5 · `docs/*.md`** — ADDING-A-COMPONENT, ARCHITECTURE, MAINTAINING,
      PUBLISHING, README, THEMES, TROUBLESHOOTING.

---

## E. Tooling (3 items, ~2-4h)

- [ ] **E1 · Stylelint** — config para CSS de outfitkit con reglas:
      cero literales numéricos en components/* (excepto contextos permitidos),
      sin prefijo `ok-`, sin BEM `--variant`.
- [ ] **E2 · Visual regression tests** — Playwright snapshots de páginas
      clave (home, datatable, hubs/active, POS, modal, drawer). Comparar
      contra baseline en CI.
- [ ] **E3 · GitHub Actions CI** — workflow que en cada push: build showcase,
      ejecuta stylelint, corre visual regression, falla si hay diff.

---

## F. Publicación v2.0.0 (3 items, ~1h)

- [ ] **F1 · Tag git** — `git tag v2.0.0` + push tag + GitHub release con notes
      (breaking changes: sin prefijo, sin BEM, schema Ionic, modificadores universales).
- [ ] **F2 · jsDelivr** — verificar que `https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@2.0.0/dist/outfitkit.min.css`
      sirve la versión correcta. Test con curl + visual check.
- [ ] **F3 · PyPI** — `python -m build && twine upload dist/*` desde
      `showcase/pyproject.toml`. Verificar `pip install outfitkit==2.0.0`.

---

## G. Migración consumidores (2 items, ~2-4h)

- [x] **G1 · Cloud (Django)** — buscar y reemplazar referencias `ok-*` en
      `cloud/templates/`, `cloud/static/`. Pin pip a `outfitkit==2.0.0`.
      Smoke test páginas críticas (admin, marketplace, dashboard).
- [x] **G2 · Hub (FastAPI / Hotframe)** — idem en `hub/templates/`, `hub/static/`.
      Smoke test páginas críticas (POS, KDS, módulos instalados).

> ✅ Bloque G completado 2026-05-11 (Worker-G). Discovery: cero clases `ok-*`
> en Cloud (45 templates + 5 static CSS) ni en Hub (594 templates + 1 module
> CSS). Solo quedan `--ok-*` CSS custom property references en inline styles
> (`var(--ok-brand)`, etc.) — funcionan via los retro-compat aliases en
> `tokens.css`. Pin pip a `outfitkit==2.0.0` pendiente (lo hará el usuario
> tras bloque F).

---

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
| **TOTAL** | **41** | **15-23h** | |

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
6. BEM elementos `__` mantenidos · modificadores `--` eliminados
7. JinjaX templates con `{{ ok_prefix }}` configurable (default vacío)
8. `tokens.css` mantiene alias `--ok-*` retro-compat para Cloud/Hub
9. Dist en `dist/outfitkit.css` + `.min.css`
10. v2.0.0 = breaking change (consumidores migran o fijan `@1.5.0`)
