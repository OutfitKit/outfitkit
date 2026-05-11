"""
OutfitKit — Jinja macros on top of the OutfitKit CSS library.

The package exposes the templates directory so consumers can mount it onto
their Jinja2 environment:

    from jinja2 import Environment, FileSystemLoader
    from outfitkit import TEMPLATES_DIR, css_url

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    button = env.get_template("ui/button.jinja").module.button
    html = button("Save", variant="primary")

Each component file works two ways:

1. **Vanilla Jinja2** — ``{% from "ui/button.jinja" import button %}`` then
   ``{{ button("Save", variant="primary") }}``.
2. **JinjaX** — ``<Button label="Save" variant="primary" />`` (requires the
   ``outfitkit[jinjax]`` extra installed and the JinjaX extension registered
   on the Jinja2 environment).

Both modes render identical HTML.

CSS class prefix policy (v2.0+)
-------------------------------
OutfitKit 2.0 emits **unprefixed** class names exclusively: ``class="btn
primary"``. The prefixed bundle (``outfitkit.ok.css``) is retained only
as a frozen retro-compat snapshot of v1.5 — see ``dist/outfitkit.ok.css``.
The macros do **not** support a configurable prefix anymore: there is one
canonical bundle (``dist/outfitkit.min.css``) and one canonical class
naming. Consumers with a legacy prefix-pinning need stay on the v1.5
tag (``pip install outfitkit==1.5.0``) and the matching ``ok-`` bundle.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jinja2 import Environment

__version__ = "1.0.0"

#: Absolute path to the bundled Jinja templates folder.
#: Layout: ``TEMPLATES_DIR/ui/<component>.jinja``.
TEMPLATES_DIR: Path = Path(__file__).parent / "templates"

#: jsDelivr base URL of the OutfitKit CSS bundle on GitHub.
_CDN_BASE = "https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit"


def register_globals(env: "Environment") -> None:
    """Reserved hook for future Jinja globals registration.

    OutfitKit 2.0 macros do not need any globals registered — the templates
    emit literal class names without indirection. This function is kept as a
    no-op so existing setups that call ``register_globals(env)`` keep
    working. If we need to register globals in a later release, this is
    where they'll go.
    """
    # No globals to register in v2.0. Kept as a placeholder so external
    # code that imports and calls this does not break.


def css_url(version: str | None = None, minified: bool = True) -> str:
    """Return the jsDelivr URL for the OutfitKit CSS bundle.

    Args:
        version: A semver tag (``"v2.0.0"``), branch name (``"main"``), or
            ``None`` to default to ``"latest"``.
        minified: When True (default), returns the minified bundle from
            ``dist/outfitkit.min.css``. When False, returns the unminified
            entry point from ``css/outfitkit.css`` — useful for DevTools
            inspection.
    """
    ref = version or "latest"
    if minified:
        return f"{_CDN_BASE}@{ref}/dist/outfitkit.min.css"
    return f"{_CDN_BASE}@{ref}/css/outfitkit.css"


def theme_url(name: str, version: str | None = None) -> str:
    """Return the jsDelivr URL for a single theme override file.

    Themes live under ``css/themes/<name>.css``.
    """
    ref = version or "latest"
    return f"{_CDN_BASE}@{ref}/css/themes/{name}.css"


__all__ = [
    "TEMPLATES_DIR",
    "__version__",
    "css_url",
    "register_globals",
    "theme_url",
]
