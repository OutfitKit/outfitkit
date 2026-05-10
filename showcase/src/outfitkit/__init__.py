"""
OutfitKit — Jinja macros on top of the OutfitKit CSS library.

The package exposes the templates directory so consumers can mount it onto
their Jinja2 environment:

    from jinja2 import Environment, FileSystemLoader
    from outfitkit import TEMPLATES_DIR, register_globals

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    register_globals(env)              # default: no prefix

    button = env.get_template("ui/button.jinja").module.button
    html = button("Save", variant="primary")

Each component file works two ways:

1. **Vanilla Jinja2** — ``{% from "ui/button.jinja" import button %}`` then
   ``{{ button("Save", variant="primary") }}``.
2. **JinjaX** — ``<Button label="Save" variant="primary" />`` (requires the
   ``outfitkit[jinjax]`` extra installed and the JinjaX extension registered
   on the Jinja2 environment).

Both modes render identical HTML.

## CSS class prefix

By default, OutfitKit emits **unprefixed** class names: ``class="btn
btn--primary"``. This is what we recommend for any project where
OutfitKit is the only CSS library on the page (Hub, Cloud, the
``m_*`` marketplace modules — everything we control).

Some third-party consumers may need to pin a prefix to avoid clashing
with classes from another library they cannot drop (Bootstrap,
Tailwind utilities, an old design system). Those consumers opt in:

    register_globals(env, ok_prefix="ok-")

This makes ``{{ button("Save") }}`` emit ``class="ok-btn ok-btn--primary"``.
The HTML is otherwise identical, so picking a prefix is a one-line
decision per consumer.

The matching CSS bundle has to be loaded too — every prefix has its own
file in ``dist/``:

    css_url()                            # unprefixed (default)
    css_url(prefix="ok-")                # prefixed bundle ("ok-")

Whatever prefix the macros emit, the linked CSS bundle must use the
same prefix; otherwise nothing styles.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jinja2 import Environment

__version__ = "1.3.1"

#: Absolute path to the bundled Jinja templates folder.
#: Layout: ``TEMPLATES_DIR/ui/<component>.jinja``.
TEMPLATES_DIR: Path = Path(__file__).parent / "templates"

#: jsDelivr base URL of the OutfitKit CSS bundle on GitHub.
_CDN_BASE = "https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit"

#: Default CSS class prefix emitted by macros. Empty by default — most
#: consumers want clean class names. Override with
#: ``register_globals(env, ok_prefix="ok-")`` only when avoiding clashes
#: with other CSS libraries on the same page.
DEFAULT_OK_PREFIX = ""


def register_globals(env: "Environment", *, ok_prefix: str = DEFAULT_OK_PREFIX) -> None:
    """Register OutfitKit's Jinja globals on a Jinja2 ``Environment``.

    Currently registers ``ok_prefix`` (used by every macro to build class
    names). Call this once at app startup, after creating the environment.

    Args:
        env: The Jinja2 ``Environment`` to mutate.
        ok_prefix: Class-name prefix. Defaults to ``""`` (no prefix), which
            pairs with the default ``outfitkit.min.css`` bundle. Set to
            ``"ok-"`` (or any other prefix you'll bake into a custom
            bundle) only when avoiding name collisions with another CSS
            library.
    """
    env.globals["ok_prefix"] = ok_prefix


def css_url(
    version: str | None = None,
    minified: bool = True,
    prefix: str = "",
) -> str:
    """Return the jsDelivr URL for the OutfitKit CSS bundle.

    Args:
        version: A semver tag (``"v1.3.0"``), branch name (``"main"``), or
            ``None`` to default to ``"latest"``.
        minified: When True (default), returns the minified bundle from
            ``dist/``. When False, returns the unminified entry point from
            ``css/`` — useful for development inspection (note: the
            unminified source always carries the ``ok-`` prefix).
        prefix: Empty string (default) returns the unprefixed bundle
            (``.btn``, ``.card``). Pass ``"ok-"`` to get the prefixed
            bundle (``.ok-btn``, ``.ok-card``); pair with
            ``register_globals(env, ok_prefix="ok-")``.
    """
    ref = version or "latest"
    if not minified:
        # The dev source lives in `css/` and is always written with the
        # ok-prefix. No unprefixed dev variant exists — use the dist
        # bundle for prefix-flexible consumption.
        return f"{_CDN_BASE}@{ref}/css/outfitkit.css"
    if prefix == "ok-":
        return f"{_CDN_BASE}@{ref}/dist/outfitkit.ok.min.css"
    if prefix == "":
        return f"{_CDN_BASE}@{ref}/dist/outfitkit.min.css"
    raise ValueError(
        f"Unsupported prefix {prefix!r}. Built-in bundles are '' (default) "
        f"and 'ok-'. For a custom prefix, generate your own bundle by "
        f"running sed on the unprefixed source."
    )


def theme_url(name: str, version: str | None = None) -> str:
    """Return the jsDelivr URL for a single theme override file.

    Themes live under ``css/themes/<name>.css``.
    """
    ref = version or "latest"
    return f"{_CDN_BASE}@{ref}/css/themes/{name}.css"


__all__ = [
    "DEFAULT_OK_PREFIX",
    "TEMPLATES_DIR",
    "__version__",
    "css_url",
    "register_globals",
    "theme_url",
]
