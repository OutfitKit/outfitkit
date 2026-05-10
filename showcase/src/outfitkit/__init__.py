"""
OutfitKit — Jinja macros on top of the OutfitKit CSS library.

The package exposes the templates directory so consumers can mount it onto
their Jinja2 environment:

    from jinja2 import Environment, FileSystemLoader
    from outfitkit import TEMPLATES_DIR

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    button = env.get_template("ui/button.jinja").module.button
    html = button("Save", variant="primary")

Each component file works two ways:

1. **Vanilla Jinja2** — `{% from "ui/button.jinja" import button %}` then
   `{{ button("Save", variant="primary") }}`.
2. **JinjaX** — `<Button label="Save" variant="primary" />` (requires the
   `outfitkit[jinjax]` extra installed and the JinjaX extension registered
   on the Jinja2 environment).

Both modes render identical HTML.
"""

from __future__ import annotations

from pathlib import Path

__version__ = "1.1.1"

#: Absolute path to the bundled Jinja templates folder.
#: Layout: ``TEMPLATES_DIR/ui/<component>.jinja``.
TEMPLATES_DIR: Path = Path(__file__).parent / "templates"

#: jsDelivr base URL of the OutfitKit CSS bundle on GitHub.
_CDN_BASE = "https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit"


def css_url(version: str | None = None, minified: bool = True) -> str:
    """Return the jsDelivr URL for the OutfitKit CSS bundle.

    Args:
        version: A semver tag (``"v3.0.0"``), branch name (``"main"``), or
            ``None`` to default to ``"latest"``.
        minified: When True (default), returns the minified bundle from
            ``dist/``. When False, returns the unminified entry point from
            ``css/`` — useful for development inspection.
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


__all__ = ["TEMPLATES_DIR", "__version__", "css_url", "theme_url"]
