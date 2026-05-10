# OutfitKit visual audit vs erplora.github.io/ux
Audited at: 2026-05-10
Pages audited: 21 (16 with findings, 5 clean)
Total findings: 23 (5 BLOCKING, 8 MAJOR, 10 MINOR)

Severity counts:
- BLOCKING: 5  (hubs/active topbar, hubs/active tabbar, components/datatable scroll, apps/* topbar systemic, apps/* tabbar systemic)
- MAJOR: 8     (datatable view-toggle, datatable IO icons, app_shell tabbar slot demo, app_shell topbar mobile, mobile_shell wrong markup, topbar empty showcase, employees/list missing data, action-buttons no-stack systemic)
- MINOR: 10    (hubs/active partial view-toggle, hubs/active action stacking, datatable date-range, datatable page-size title, datatable simplified columns, auth tabbar leftover, login form missing, filter overflow, datastar JS error, hubs/active card-vs-table note)

Methodology: each outfitkit page loaded via `?embed=1` (raw, no chrome) and
compared against the corresponding reference fragment under
`https://erplora.github.io/ux/#<section>/<page>` (which itself wraps an iframe
with the local preview source at `/Users/ioan/Desktop/code/ux/previews/`).
Mobile viewport 390x844 unless noted; desktop 1280x800 spot-checks where
mobile already showed regressions. Class-name prefix differences
(`ux-*` vs `ok-*`) are expected and ignored.

The two BLOCKING systemic findings ("topbar invisible at mobile" and "tabbar
zero-height in `.ok-app` pages") account for ~12 individual page bugs each —
fixing them at the CSS level should unblock the majority of the apps/* tree.

---

## Findings

### apps/hubs/active

- [hubs/active] BLOCKING: mobile topbar invisible
  Symptom: `.ok-topbar` is in the DOM but `display:none` at 390px width, so back-button / page-title / menu-button never appear on mobile.
  Expected: reference shows a `ux-topbar` banner with Volver, "Hubs activos" title, notifications icon, avatar, and Menú toggle.
  Hint: missing media-query that flips topbar to `display:flex` below the sidebar breakpoint, or the rule that hides it on desktop never gets reverted on mobile.

- [hubs/active] BLOCKING: bottom tab-bar renders zero-height on mobile
  Symptom: `nav.ok-app__tabbar` has `display:flex` but `getBoundingClientRect().height === 0` — items exist but the bar is collapsed and invisible.
  Expected: reference page shows a 5-icon fixed bottom tab-bar (Inicio, Hubs 7, Usuarios, …) with the same height as `--ok-tabbar-h`.
  Hint: tabbar items likely styled `flex:1` with no min-height, or the bar's own height var resolves to 0 in this context.

- [hubs/active] MINOR: grid/list view toggle is incomplete
  Symptom: only one view-toggle button is visible in the filter bar (the second has empty aria-label and no visible icon at mobile).
  Expected: pair of toggle buttons (grid + list) with icons, both visible and switchable, as seen in reference.
  Hint: second toggle's icon/label not wired or hidden by responsive rule.

- [hubs/active] MINOR: page-header action buttons do not stack on mobile
  Symptom: "Exportar CSV" and "+ Crear hub" remain inline on the right at 390px and overflow the heading row.
  Expected: reference stacks (or wraps) the action buttons under the title at mobile width.
  Hint: header lacks `flex-wrap` / vertical-stack media query at small viewports.

- [hubs/active] note on user report: this page does NOT use a DataTable in either build — it's a card grid (article-per-hub). The user's "DataTable lacks grid/list toggle / no horizontal scroll" complaint is most likely about the cards-vs-table view toggle on this page (above) or about the canonical DataTable on `/components/datatable.html`, which is filed below.

### components/datatable

- [components/datatable] BLOCKING: table not horizontally scrollable on mobile
  Symptom: at 390px the inner `<table>` measures 547px wide while its wrapper is 352px and `overflow-x:hidden`, so columns get clipped and there's no scroll affordance.
  Expected: reference uses a `ux-table-scroll` container with horizontal overflow, so the user can swipe to see all columns.
  Hint: outfitkit version skips the dedicated scroll wrapper — `.ok-dt-toolbar`'s parent has `overflow-x:hidden`. Add `overflow-x:auto` (and `-webkit-overflow-scrolling:touch`) on a `.ok-table-scroll` wrapper around `<table>`.

- [components/datatable] MAJOR: grid/list view toggle missing
  Symptom: outfitkit datatable renders only a static toolbar (search + 3 selects + "+ Nuevo"). No table/grid toggle present.
  Expected: reference exposes a `ux-view-toggle` with two buttons (table icon, grid icon) that swap between `data-show="$view === 'table'"` and a grid view.
  Hint: the second view body and the toggle button-pair are simply not in the outfitkit markup; need to port `ok-view-toggle` + a `data-show`-driven grid sibling.

- [components/datatable] MAJOR: import / export / overflow icon-buttons missing
  Symptom: outfitkit toolbar lacks the import, export, and "more options" icon buttons that sit between page-size and "+ Nuevo".
  Expected: reference toolbar has 3 `ux-icon-btn` buttons (import / export / kebab) with `ux-dt-toolbar__divider` separators.
  Hint: omitted in the macro; reuse `ok-icon-btn` and `ok-dt-toolbar__divider`.

- [components/datatable] MINOR: no row-checkbox column / no trend sparkline column / no "Acciones" column
  Symptom: outfitkit table has 6 plain columns (Pedido, Cliente, Canal, Estado, Total, Fecha).
  Expected: reference adds row-select checkbox, "Tendencia 7d" sparkline column, and a per-row "Acciones" column.
  Hint: simplified showcase — fine if intentional, but means the macro example doesn't demonstrate the full DataTable surface.

- [components/datatable] MINOR: page-size select label missing
  Symptom: outfitkit page-size select has just numeric options; reference includes `title="Por página"` so the label is a tooltip.
  Hint: cosmetic, easy fix.

- [components/datatable] MINOR: date-range chip absent from toolbar
  Symptom: reference shows a `ux-date-range` chip ("01/10/25 → 18/10/25") that outfitkit omits.

### components/topbar

- [components/topbar] MAJOR: first showcase example renders empty
  Symptom: at 390px the first `.ok-topbar` example has `display:none` and h=0; only the back-button and breadcrumb variants render (h=52).
  Expected: every variant in the showcase should render at every viewport.
  Hint: a CSS rule like `@media (max-width: ...) { .ok-topbar { display: none } }` is firing for the bare example because it's missing some marker class (e.g. `.ok-topbar--mobile-visible`) that the other variants have.

### components/app_shell

- [components/app_shell] MAJOR: tabbar slot not demonstrated in showcase
  Symptom: the showcase example uses `.ok-app` with sidebar + topbar + body but no tabbar example, even though API table documents `tabbar="bottom"`.
  Expected: reference app-shell shows both desktop (sidebar+topbar) and mobile (sidebar→drawer + tabbar) layouts.
  Hint: add a second example with `tabbar="bottom"` so the macro slot is documented.

- [components/app_shell] MAJOR: topbar inside the app-shell example is invisible at mobile
  Symptom: the showcase `.ok-app` renders its topbar with `display:none` at 390px, leaving the page header area empty above the body.
  Expected: when sidebar collapses to drawer, the topbar should remain visible (with menu-button to open the drawer).
  Hint: shared cause with the hubs/active topbar bug.

### components/mobile_shell

- [components/mobile_shell] MAJOR: showcase doesn't use the actual `.ok-mobile-shell` class
  Symptom: the example markup has no `mobile-shell` class on any element; it's a free-form aside + main + nav.
  Expected: a true Mobile shell macro/wrapper that documents the off-canvas drawer + bottom-tabbar pattern with the canonical class names.
  Hint: macro likely missing in `ux-jinja` or showcase example wires the wrong classes.

### components/sidebar_nav

- [components/sidebar_nav] (no issues at component-level) — renders correctly as a 250px aside at mobile in standalone showcase. The mobile-drawer behavior depends on the consumer page wiring `data-signals='{"sidebar": false}'` + `.ok-app__sidebar-overlay`; that's tested in app pages.

### Cross-cutting / systemic findings (apply to most apps/* pages)

- [apps/*] BLOCKING: `.ok-topbar` is universally hidden at mobile in pages using `.ok-app` shell
  Pages confirmed: hubs/active, dashboard/saas, dashboard/hub, users/list, billing/invoices, employees/list, orgs/list, settings/preferences, modules/overview, profile/saas, marketplace/saas-shop. Pages NOT affected: errors/* (no shell), auth/* (no shell), system/index (no topbar in markup).
  Symptom: every `.ok-app__main > .ok-topbar` has `display:none` and h=0 at 390px viewport.
  Expected: when sidebar collapses to drawer at mobile breakpoints, the topbar must remain visible to surface page title, back-button and the menu (hamburger) button that toggles the drawer.
  Hint: most likely a single CSS rule `.ok-app .ok-topbar { display:none }` (or `display:none` set inside the desktop-grid layout that never gets reverted on small screens). Fix in `.ok-topbar` rules: `display:flex` at mobile, `display:none` only when sidebar is permanently visible (≥ breakpoint).

- [apps/*] BLOCKING: `nav.ok-app__tabbar` renders height 0 in pages using `.ok-app` shell (with exceptions)
  Pages confirmed broken: hubs/active, dashboard/saas, users/list, billing/invoices, orgs/list, settings/preferences, modules/overview, profile/saas — tabbar in DOM, `display:flex`, but height 0.
  Pages where tabbar works: dashboard/hub (h=58), employees/list (h=58). Both wire the tabbar with explicit `<nav class="ok-tabbar ok-tabbar--fixed ...">` markup at the bottom of `.ok-app__main`.
  Expected: tabbar fixed to bottom of viewport, ~58px tall, with 5 icon-only items at mobile.
  Hint: the broken pages use a `nav.ok-app__tabbar` wrapper instead of `.ok-tabbar`; that wrapper class likely lacks the height/min-height rules that `.ok-tabbar--fixed` carries. Either rename to `.ok-tabbar--fixed` or add the missing height var to `.ok-app__tabbar`.

- [apps/*] MINOR: leftover bottom-nav stub on auth pages
  Symptom: `apps/auth/login-saas.html` (and likely all auth/*) renders a bottom `<nav>` with 5 generic icon-only links (no labels, hrefs="#"), inherited from a shared template.
  Expected: auth/* pages should be standalone — no app shell, no tabbar, no sidebar.
  Hint: remove the `_layout.jinja` tabbar block from auth templates, or have those pages extend a different (chrome-less) layout.

- [apps/*] MAJOR: page-header action buttons don't stack/wrap at mobile (multiple pages)
  Pages: hubs/active (Exportar CSV + Crear hub), billing/invoices (Exportar CSV + Descargar todas), modules/overview (Subir módulo + Documentación + range tabs), orgs/list (Exportar + Crear), and others.
  Symptom: title row keeps two/three secondary CTAs inline at the right at 390px, often overflowing or pushing the heading off-screen.
  Expected: at mobile, either stack actions below title, or show only the primary CTA and move the secondary into a kebab menu.
  Hint: the flex container that holds title + actions doesn't `flex-wrap` at small widths.

- [apps/*] MINOR: large filter toolbars overflow horizontally
  Pages: users/list (4 selects + search), billing/invoices (search + 4 filter chips + range + select + export), settings pages with multiple selects.
  Symptom: filter rows pack too many controls into a flex-row that exceeds 390px; some controls clip or wrap awkwardly.
  Expected: collapse to a "Filters" button + drawer/sheet on mobile, or stack controls.
  Hint: missing `flex-wrap` and/or a mobile-only "Filters" trigger.

### apps/employees/list

- [employees/list] MAJOR: actual data table missing from rendered page
  Symptom: only the toolbar (search, role/state/page-size selects, view-toggle) and an orphan `↕` glyph render. No rows, no headers, no empty state visible — yet a `<table>` is present in DOM (1 found).
  Expected: reference shows a table of employees with avatar, name, role, hours, state, kebab menu.
  Hint: `data-show` likely defaults to grid view but the grid card markup also missing; likely the macros render an empty wrapper. Or the table is being clipped by a 0-height container.

### apps/marketplace/saas-shop

- [marketplace/saas-shop] MINOR: Datastar JS error on page
  Symptom: console shows `SyntaxError: Unexpected token ')'` from datastar.js. Functional rendering still happens but interactivity may be partially broken.
  Hint: a malformed expression in a `data-on:*` or `data-signals='...'` attribute on this page; check inline templating.

### apps/auth/login-saas

- [auth/login-saas] MINOR: `<input type="password">` is not inside a `<form>`
  Symptom: browser logs DOM warning "Password field is not contained in a form".
  Hint: wrap the login fields in a `<form action="…" method="POST">` for accessibility/autofill correctness.

### apps/errors/*

- [errors/404] (no issues) — clean standalone error page, no app chrome, search + back/home actions, trace footer.

### apps/system/index

- [system/index] (no issues) — Hub system/hardware page renders correctly at mobile: sidebar drawer (hidden), hardware cards stack, no topbar/tabbar in this design (intentional).

### apps/profile/saas

- [profile/saas] (mostly OK) — same systemic topbar/tabbar invisibility, otherwise content (avatar, name, fields, security cards) renders correctly.

### apps/modules/overview

- [modules/overview] (mostly OK) — KPIs, downloads chart, top-5 list, activity feed, Stripe Connect card, quick-actions all render. Inherits the topbar/tabbar systemic bugs.

### apps/dashboard/hub

- [dashboard/hub] (good) — KPIs + apps grid + sales chart + recent-activity render correctly. Tabbar works (h=58). Topbar still hidden (systemic).

## Pages audited (no issues, OK at a glance)

- components/tabbar — all 4 variants render with h=58
- components/sidebar_nav — standalone aside renders at 250px wide
- components/kanban — 4-column pipeline renders, scrollable
- apps/errors/404 — clean
- apps/system/index — clean

## Pages audited (issues filed above)

- apps/hubs/active
- apps/dashboard/saas
- apps/dashboard/hub
- apps/users/list
- apps/billing/invoices
- apps/employees/list
- apps/orgs/list
- apps/marketplace/saas-shop
- apps/settings/preferences
- apps/modules/overview
- apps/profile/saas
- apps/auth/login-saas
- components/datatable
- components/topbar
- components/app_shell
- components/mobile_shell

