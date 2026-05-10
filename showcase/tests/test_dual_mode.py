"""Verify the dual-mode invariant: every component produces equivalent HTML
when rendered via Jinja2 macro and via JinjaX ``<Component />``.

JinjaX uses its own internal Jinja2 environment with ``StrictUndefined``,
which means whitespace and minor serialization details may differ from a
vanilla macro render. We compare on the **structural** signal (class
names, tag, key attributes) rather than byte-equal HTML.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader
from jinjax import Catalog


UI_DIR = Path(__file__).resolve().parents[1] / "src" / "outfitkit" / "templates" / "ui"

#: Per-component test payload. Each entry produces fixed HTML that we compare
#: structurally between macro path and JinjaX path.
COMPONENTS = {
    "button": {
        "kwargs": {"label": "Save", "variant": "primary", "size": "md"},
        "expected_classes": ["ok-btn", "ok-btn--primary"],
        "expected_text": "Save",
    },
    "badge": {
        "kwargs": {"label": "New", "variant": "brand", "dot": True},
        "expected_classes": ["ok-badge", "ok-badge--brand", "ok-badge__dot"],
        "expected_text": "New",
    },
    "card": {
        "kwargs": {"tag": "div", "variant": "elevated", "interactive": True},
        "expected_classes": ["ok-card", "ok-card--elevated", "ok-card--interactive"],
        "slot": "<p>body</p>",
    },
    "modal": {
        "kwargs": {"title": "Confirm", "size": "md", "icon_variant": "danger", "state": "open"},
        "expected_classes": [
            "ok-backdrop", "ok-modal-root", "ok-modal", "ok-modal--md",
            "ok-modal__icon--danger", "ok-modal__title",
        ],
        "expected_text": "Confirm",
        "slot": "<p>body</p>",
    },
    "drawer": {
        "kwargs": {"title": "Filters", "side": "right", "state": "open"},
        "expected_classes": ["ok-backdrop", "ok-drawer-root", "ok-drawer", "ok-drawer__title"],
        "expected_text": "Filters",
        "slot": "<p>body</p>",
    },
    # --- Category A — atomics ---
    "avatar": {
        "kwargs": {"label": "JC", "size": "lg", "variant": "brand"},
        "expected_classes": ["ok-avatar", "ok-avatar--lg", "ok-avatar--brand"],
        "expected_text": "JC",
    },
    "breadcrumbs": {
        "kwargs": {
            "items": [
                {"label": "Home", "href": "#"},
                {"label": "Section", "href": "#"},
                {"label": "Current"},
            ],
            "variant": "chips",
        },
        "expected_classes": ["ok-crumbs", "ok-crumbs--chips", "ok-crumbs__item"],
        "expected_text": "Current",
    },
    "kpi": {
        "kwargs": {
            "label": "Sales",
            "value": "€2.847",
            "unit": ",30",
            "delta": "+12,4%",
            "delta_dir": "up",
            "variant": "brand",
        },
        "expected_classes": [
            "ok-kpi", "ok-kpi--brand", "ok-kpi__label", "ok-kpi__value",
            "ok-kpi__value-unit", "ok-kpi__delta", "ok-kpi__delta--up",
            "ok-kpi__delta-arrow",
        ],
        "expected_text": "Sales",
    },
    "menu_btn": {
        "kwargs": {"label": "Menu", "expanded": True, "mobile_only": True},
        "expected_classes": [
            "ok-menu-btn", "ok-menu-btn--mobile-only",
            "ok-menu-btn-lines", "ok-menu-btn-line",
        ],
    },
    "progress": {
        "kwargs": {
            "value": 73,
            "label": "Importing",
            "value_text": "73%",
            "variant": "leaf",
            "size": "lg",
        },
        "expected_classes": [
            "ok-progress-block", "ok-progress-block__head",
            "ok-progress-block__label", "ok-progress-block__value",
            "ok-progress", "ok-progress--leaf", "ok-progress--lg",
            "ok-progress__bar",
        ],
        "expected_text": "Importing",
    },
    "stat": {
        "kwargs": {
            "label": "Orders", "value": "1.284",
            "delta": "+6,2%", "delta_dir": "up",
        },
        "expected_classes": [
            "ok-stat", "ok-stat__label", "ok-stat__value",
            "ok-stat__delta", "ok-stat__delta--up",
        ],
        "expected_text": "1.284",
    },
    "sparkline": {
        "kwargs": {"points": "0,18 10,15 20,16 30,12", "direction": "up", "size": "lg"},
        "expected_classes": ["ok-spark", "ok-spark--up", "ok-spark--lg"],
    },
    "empty": {
        "kwargs": {
            "title": "No data",
            "desc": "Nothing to show.",
            "compact": True,
        },
        "expected_classes": [
            "ok-empty", "ok-empty--compact", "ok-empty__title", "ok-empty__desc",
        ],
        "expected_text": "No data",
    },
    # --- Category B — slots ---
    "accordion": {
        "kwargs": {"variant": "ghost"},
        "expected_classes": ["ok-accordion", "ok-accordion--ghost"],
        "slot": '<div class="ok-accordion__item">x</div>',
    },
    "tabs": {
        "kwargs": {"variant": "pill"},
        "expected_classes": ["ok-tabs", "ok-tabs--pill"],
        "slot": '<button class="ok-tab">Hoy</button>',
    },
    "list": {
        "kwargs": {"variant": "separated", "dense": True},
        "expected_classes": ["ok-list", "ok-list--separated", "ok-list--dense"],
        "slot": '<a class="ok-list__item">x</a>',
    },
    "banner": {
        "kwargs": {
            "title": "Heads up", "description": "Maintenance soon",
            "variant": "warn", "dismissible": True,
        },
        "expected_classes": [
            "ok-banner", "ok-banner--warn", "ok-banner__icon",
            "ok-banner__body", "ok-banner__title", "ok-banner__desc", "ok-banner__close",
        ],
        "expected_text": "Heads up",
        "slot": "",
    },
    "receipt": {
        "kwargs": {},
        "expected_classes": ["ok-receipt"],
        "slot": '<div class="ok-receipt__title">Demo</div>',
    },
    "stepper": {
        "kwargs": {"orientation": "vertical"},
        "expected_classes": ["ok-stepper", "ok-stepper--vertical"],
        "slot": '<li class="ok-stepper__step">x</li>',
    },
    "table": {
        "kwargs": {"compact": True, "zebra": True},
        "expected_classes": ["ok-table", "ok-table--compact", "ok-table--zebra"],
        "slot": "<thead><tr><th>x</th></tr></thead>",
    },
    "tabbar": {
        "kwargs": {"variant": "pill"},
        "expected_classes": ["ok-tabbar", "ok-tabbar--pill"],
        "slot": '<a class="ok-tabbar-item">x</a>',
    },
    # --- Forms ---
    "field": {
        "kwargs": {"label": "Email", "required": True, "hint": "We never share."},
        "expected_classes": [
            "ok-field", "ok-field__label", "ok-field__label--req", "ok-field__hint",
        ],
        "expected_text": "Email",
        "slot": '<input class="ok-input" />',
    },
    "input": {
        "kwargs": {"name": "email", "type": "email", "size": "lg", "placeholder": "you@x.com"},
        "expected_classes": ["ok-input", "ok-input--lg"],
    },
    "select": {
        "kwargs": {"name": "country", "size": "sm"},
        "expected_classes": ["ok-select", "ok-select--sm"],
        "slot": "<option>ES</option>",
    },
    "textarea": {
        "kwargs": {"name": "notes", "rows": 6, "invalid": True},
        "expected_classes": ["ok-textarea", "ok-textarea--invalid"],
    },
    "checkbox": {
        "kwargs": {"label": "Accept terms", "name": "tos", "checked": True},
        "expected_classes": ["ok-check", "ok-check__box"],
        "expected_text": "Accept terms",
    },
    "radio": {
        "kwargs": {"label": "Monthly", "name": "plan", "value": "monthly", "checked": True},
        "expected_classes": ["ok-radio", "ok-radio__dot"],
        "expected_text": "Monthly",
    },
    "toggle": {
        "kwargs": {"name": "notif", "checked": True, "size": "lg"},
        "expected_classes": ["ok-toggle", "ok-toggle--lg", "ok-toggle__track"],
    },
    "slider": {
        "kwargs": {"name": "vol", "min": 0, "max": 10, "step": 1, "value": 5},
        "expected_classes": ["ok-slider"],
    },
    # --- Category C — complex compositions ---
    "calendar": {
        "kwargs": {"variant": "month"},
        "expected_classes": ["ok-cal"],
        "slot": '<header class="ok-cal__head"><div class="ok-cal__title">May 2026</div></header>',
    },
    "chart": {
        "kwargs": {"variant": "flat"},
        "expected_classes": ["ok-chart", "ok-chart--flat"],
        "slot": '<header class="ok-chart__head"><h3 class="ok-chart__title">Sales</h3></header>',
    },
    "chat": {
        "kwargs": {},
        "expected_classes": ["ok-chat"],
        "slot": '<aside class="ok-chat__list"></aside>',
    },
    "datatable": {
        "kwargs": {},
        "expected_classes": ["ok-table-wrap"],
        "slot": '<div class="ok-dt-toolbar"><div class="ok-search"></div></div>',
    },
    "kanban": {
        "kwargs": {},
        "expected_classes": ["ok-kanban"],
        "slot": '<section class="ok-kanban__col"></section>',
    },
    "gallery": {
        "kwargs": {},
        "expected_classes": ["ok-gallery"],
        "slot": '<div class="ok-gallery__item"></div>',
    },
    "tree": {
        "kwargs": {"variant": "dense"},
        "expected_classes": ["ok-tree", "ok-tree--dense"],
        "slot": '<div class="ok-tree__node"></div>',
    },
    # --- Category D — verticals ---
    "kds": {
        "kwargs": {"variant": "late"},
        "expected_classes": ["ok-kds", "ok-kds--late"],
        "slot": '<header class="ok-kds__head">x</header>',
    },
    "hr_card": {
        "kwargs": {"tag": "article"},
        "expected_classes": ["ok-emp"],
        "slot": '<div class="ok-emp__cover"></div>',
    },
    "pos": {
        "kwargs": {"tag": "div"},
        "expected_classes": ["ok-pos"],
        "slot": '<section class="ok-pos__main">x</section>',
    },
    "numpad": {
        "kwargs": {"display": "12,50", "label": "Importe"},
        "expected_classes": [
            "ok-numpad", "ok-numpad__btn", "ok-numpad__btn--ghost",
            "ok-numpad-display", "ok-numpad-display__label",
            "ok-numpad-display__value",
        ],
        "expected_text": "Importe",
    },
    "pay": {
        "kwargs": {"tag": "div"},
        "expected_classes": ["ok-pay-methods"],
        "slot": '<button class="ok-pay-method">x</button>',
    },
    "manufacturing": {
        "kwargs": {"tag": "div"},
        "expected_classes": ["ok-bom"],
        "slot": '<div class="ok-bom__head">x</div>',
    },
    # --- Pickers / editors / multimedia / selection ---
    "datepicker": {
        "kwargs": {"title": "Mayo 2026", "range": False},
        "expected_classes": ["ok-datepicker", "ok-datepicker__head", "ok-datepicker__title"],
        "expected_text": "Mayo 2026",
        "slot": '<div class="ok-datepicker__grid"></div>',
    },
    "colorpicker": {
        "kwargs": {"selected": "#D97757"},
        "expected_classes": ["ok-colorpicker", "ok-colorpicker__swatch"],
    },
    "timepicker": {
        "kwargs": {"hour": 9, "minute": 30},
        "expected_classes": ["ok-timepicker", "ok-timepicker__col", "ok-timepicker__opt"],
    },
    "otp": {
        "kwargs": {"length": 6, "value": "392", "size": "md", "separator_at": 3},
        "expected_classes": ["ok-otp", "ok-otp__cell", "ok-otp__sep"],
    },
    "pinpad": {
        "kwargs": {},
        "expected_classes": ["ok-pinpad", "ok-pinpad__key", "ok-pinpad__key--action"],
    },
    "rating": {
        "kwargs": {"value": 4, "max": 5, "size": "lg", "label": "4,0 / 5"},
        "expected_classes": [
            "ok-rating", "ok-rating--lg", "ok-rating__star",
            "ok-rating__star--filled", "ok-rating__label",
        ],
        "expected_text": "4,0 / 5",
    },
    "autocomplete": {
        "kwargs": {"width": "380px"},
        "expected_classes": ["ok-autocomplete"],
        "slot": '<div class="ok-autocomplete__list"></div>',
    },
    "search": {
        "kwargs": {"placeholder": "Buscar producto…", "value": "marmelada", "kbd": "⌘K"},
        "expected_classes": ["ok-search", "ok-search__icon", "ok-search__kbd", "ok-input"],
    },
    "richtext": {
        "kwargs": {"variant": "minimal"},
        "expected_classes": ["ok-richtext", "ok-richtext--minimal"],
        "slot": '<div class="ok-richtext__content"></div>',
    },
    "audio_player": {
        "kwargs": {
            "title": "Briefing", "artist": "Operaciones",
            "duration": "02:14", "current": "00:34",
            "progress": 25, "variant": "compact",
        },
        "expected_classes": [
            "ok-audio", "ok-audio--compact", "ok-audio__play",
            "ok-audio__title", "ok-audio__progress", "ok-audio__bar", "ok-audio__fill",
        ],
        "expected_text": "Briefing",
    },
    "video_player": {
        "kwargs": {
            "poster": "https://example/p.jpg", "duration": "01:48",
            "current": "00:30", "progress": 30, "playing": True,
        },
        "expected_classes": [
            "ok-video", "ok-video__poster", "ok-video__controls",
            "ok-video__progress", "ok-video__progress-fill",
        ],
    },
    "tags": {
        "kwargs": {},
        "expected_classes": ["ok-tags"],
        "slot": '<span class="ok-tag ok-tag--brand">Urgente</span>',
    },
    # --- Worker G: page shells, feedback, misc ---
    "toast": {
        "kwargs": {
            "title": "Pedido pagado",
            "description": "PED-2041 — €124,50",
            "variant": "ok",
            "dismissible": True,
        },
        "expected_classes": [
            "ok-toast", "ok-toast--ok", "ok-toast__icon",
            "ok-toast__body", "ok-toast__title", "ok-toast__desc", "ok-toast__close",
        ],
        "expected_text": "Pedido pagado",
    },
    "tooltip": {
        "kwargs": {"label": "Atajo: F2", "placement": "top"},
        "expected_classes": ["ok-tooltip", "ok-tooltip--top"],
        "expected_text": "Atajo: F2",
    },
    "timeline": {
        "kwargs": {"dense": True},
        "expected_classes": ["ok-timeline", "ok-timeline--dense"],
        "slot": '<li class="ok-timeline__item">x</li>',
    },
    "states": {
        "kwargs": {"kind": "title", "width": "60%"},
        "expected_classes": ["ok-skel", "ok-skel--title"],
    },
    "stats": {
        "kwargs": {},
        "expected_classes": ["ok-stats"],
        "slot": '<div class="ok-stat">x</div>',
    },
    "panel": {
        "kwargs": {"title": "Pedidos", "sub": "Hoy", "variant": "ghost"},
        "expected_classes": [
            "ok-panel", "ok-panel--ghost", "ok-panel__head", "ok-panel__head-text",
            "ok-panel__title", "ok-panel__sub", "ok-panel__body",
        ],
        "expected_text": "Pedidos",
        "slot": "<p>body</p>",
    },
    "context_menu": {
        "kwargs": {"label": "Pedido FCT-184"},
        "expected_classes": ["ok-ctx-menu", "ok-ctx-menu__label"],
        "expected_text": "Pedido FCT-184",
        "slot": '<button class="ok-ctx-menu__item">x</button>',
    },
    "menubar": {
        "kwargs": {"app_name": "ERPlora", "compact": True},
        "expected_classes": [
            "ok-menubar", "ok-menubar--compact",
            "ok-menubar__app-name", "ok-menubar__divider",
        ],
        "expected_text": "ERPlora",
        "slot": '<button class="ok-menubar__menu">File</button>',
    },
    "invoice": {
        "kwargs": {},
        "expected_classes": ["ok-invoice"],
        "slot": '<div class="ok-invoice__title">Factura</div>',
    },
    "system_overlays": {
        "kwargs": {"title": "Notificaciones", "count": 4},
        "expected_classes": ["ok-notif", "ok-notif__head", "ok-notif__title"],
        "expected_text": "Notificaciones",
        "slot": '<div class="ok-notif__list"></div>',
    },
    "app_shell": {
        "kwargs": {"tabbar": "bottom"},
        "expected_classes": ["ok-app"],
        "slot": '<aside class="ok-sidebar"></aside>',
    },
    "sidebar_nav": {
        "kwargs": {},
        "expected_classes": ["ok-sidebar"],
        "slot": '<div class="ok-sidebar__brand">x</div>',
    },
    "topbar": {
        "kwargs": {"page_title": "Pedidos", "back": True},
        "expected_classes": [
            "ok-topbar", "ok-topbar__left",
            "ok-topbar__back-btn", "ok-topbar__page-title",
        ],
        "expected_text": "Pedidos",
        "slot": '<div class="ok-topbar__actions">x</div>',
    },
    "mobile_shell": {
        "kwargs": {},
        "expected_classes": ["ok-app"],
        "slot": '<aside class="ok-sidebar"></aside>',
    },
}

SLOTTED = {
    "card", "modal", "drawer",
    "accordion", "tabs", "list", "banner", "receipt", "stepper", "table", "tabbar",
    "field", "select",
    "calendar", "chart", "chat", "datatable", "kanban", "gallery", "tree",
    "kds", "hr_card", "pos", "pay", "manufacturing",
    "datepicker", "autocomplete", "richtext", "tags",
    "timeline", "stats", "panel", "context_menu", "menubar", "invoice",
    "system_overlays", "app_shell", "sidebar_nav", "topbar", "mobile_shell",
}


def _macro_render(env: Environment, name: str, kwargs: dict, slot: str = "") -> str:
    """Render via vanilla Jinja2 macro import + call."""
    args = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    if name in SLOTTED:
        src = (
            f"{{% from 'ui/{name}.jinja' import {name} %}}"
            f"{{% call {name}({args}) %}}{slot}{{% endcall %}}"
        )
    else:
        src = (
            f"{{% from 'ui/{name}.jinja' import {name} %}}"
            f"{{{{ {name}({args}) }}}}"
        )
    return env.from_string(src).render()


def _jinjax_render(catalog: Catalog, name: str, kwargs: dict, slot: str = "") -> str:
    """Render via JinjaX catalog.render() — the same path JinjaX takes when
    the preprocessor encounters ``<Component ... />`` in a page.

    Components whose file stem contains an underscore (e.g. ``menu_btn``)
    are registered under the same name JinjaX recognises for them. We use
    ``str.title()`` for simple names (``button`` → ``Button``) and fall back
    to the raw stem for any name with an underscore.
    """
    component_name = name if "_" in name else name.title()
    if slot:
        # The catalog's render() accepts a `_content` kwarg as the slot HTML.
        return catalog.render(component_name, _content=slot, **kwargs)
    return catalog.render(component_name, **kwargs)


def _classes(html: str) -> set[str]:
    """Extract every class name occurrence in the rendered HTML."""
    found = set()
    for match in re.finditer(r'class="([^"]*)"', html):
        found.update(match.group(1).split())
    return found


@pytest.fixture
def env() -> Environment:
    e = Environment(
        loader=FileSystemLoader(str(UI_DIR.parent)),
        autoescape=True,
    )
    return e


@pytest.fixture
def catalog() -> Catalog:
    cat = Catalog()
    cat.add_folder(str(UI_DIR))
    return cat


@pytest.mark.parametrize("name,spec", list(COMPONENTS.items()))
def test_macro_render_has_expected_structure(name, spec, env):
    html = _macro_render(env, name, spec["kwargs"], spec.get("slot", ""))
    classes = _classes(html)
    for cls in spec["expected_classes"]:
        assert cls in classes, f"{name} (macro): missing class {cls!r} in {classes}"
    if "expected_text" in spec:
        assert spec["expected_text"] in html, f"{name} (macro): missing text"


@pytest.mark.parametrize("name,spec", list(COMPONENTS.items()))
def test_jinjax_render_has_expected_structure(name, spec, catalog):
    html = _jinjax_render(catalog, name, spec["kwargs"], spec.get("slot", ""))
    classes = _classes(html)
    for cls in spec["expected_classes"]:
        assert cls in classes, f"{name} (jinjax): missing class {cls!r} in {classes}"
    if "expected_text" in spec:
        assert spec["expected_text"] in html, f"{name} (jinjax): missing text"


@pytest.mark.parametrize("name,spec", list(COMPONENTS.items()))
def test_macro_and_jinjax_have_same_class_set(name, spec, env, catalog):
    """Both rendering paths must produce the same set of CSS classes."""
    macro_html = _macro_render(env, name, spec["kwargs"], spec.get("slot", ""))
    jinjax_html = _jinjax_render(catalog, name, spec["kwargs"], spec.get("slot", ""))
    macro_classes = _classes(macro_html)
    jinjax_classes = _classes(jinjax_html)
    assert macro_classes == jinjax_classes, (
        f"{name}: class set differs between paths\n"
        f"  macro only:  {macro_classes - jinjax_classes}\n"
        f"  jinjax only: {jinjax_classes - macro_classes}\n"
    )


def test_all_components_covered():
    """Catch new components without test specs."""
    actual = {p.stem for p in UI_DIR.glob("*.jinja")}
    expected = set(COMPONENTS.keys())
    missing = actual - expected
    assert not missing, f"Add a spec in COMPONENTS for: {missing}"
