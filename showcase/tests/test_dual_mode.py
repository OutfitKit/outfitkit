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
}

SLOTTED = {"card", "modal", "drawer"}


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
    the preprocessor encounters ``<Component ... />`` in a page."""
    component_name = name.title()  # button -> Button
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
