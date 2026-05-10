"""
OutfitKit — Jinja macros on top of the OutfitKit CSS library.

The package exposes the templates directory so consumers can mount it onto
their Jinja2 environment:

    from jinja2 import Environment, FileSystemLoader
    from outfitkit import TEMPLATES_DIR, register_globals

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    register_globals(env)              # adds `ok_prefix` (default "ok-")

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

Macros emit class names of the form ``{{ ok_prefix }}btn``, where
``ok_prefix`` is a Jinja global. The default is ``"ok-"``, matching the
prefixed CSS bundle (``dist/outfitkit.min.css``). Consumers that load the
unprefixed bundle (``dist/outfitkit.unprefixed.min.css``) should set the
prefix to an empty string:

    register_globals(env, ok_prefix="")

This makes ``{{ button("Save") }}`` emit ``class="btn btn--secondary"``
instead of ``class="ok-btn ok-btn--secondary"``. The HTML is otherwise
identical, so picking a prefix is a one-line decision per consumer.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jinja2 import Environment

__version__ = "1.2.0"

#: Absolute path to the bundled Jinja templates folder.
#: Layout: ``TEMPLATES_DIR/ui/<component>.jinja``.
TEMPLATES_DIR: Path = Path(__file__).parent / "templates"

#: jsDelivr base URL of the OutfitKit CSS bundle on GitHub.
_CDN_BASE = "https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit"

#: Default CSS class prefix emitted by macros. Override with
#: ``register_globals(env, ok_prefix="")`` to use the unprefixed bundle.
DEFAULT_OK_PREFIX = "ok-"


def register_globals(env: "Environment", *, ok_prefix: str = DEFAULT_OK_PREFIX) -> None:
    """Register OutfitKit's Jinja globals on a Jinja2 ``Environment``.

    Currently registers ``ok_prefix`` (used by every macro to build class
    names). Call this once at app startup, after creating the environment.

    Args:
        env: The Jinja2 ``Environment`` to mutate.
        ok_prefix: Class-name prefix. Defaults to ``"ok-"``. Pass ``""``
            when loading the unprefixed CSS bundle so macros emit
            ``class="btn"`` instead of ``class="ok-btn"``.
    """
    env.globals.setdefault("ok_prefix", ok_prefix)
    if ok_prefix != DEFAULT_OK_PREFIX:
        env.globals["ok_prefix"] = ok_prefix


def css_url(
    version: str | None = None,
    minified: bool = True,
    unprefixed: bool = False,
) -> str:
    """Return the jsDelivr URL for the OutfitKit CSS bundle.

    Args:
        version: A semver tag (``"v1.2.0"``), branch name (``"main"``), or
            ``None`` to default to ``"latest"``.
        minified: When True (default), returns the minified bundle from
            ``dist/``. When False, returns the unminified entry point from
            ``css/`` — useful for development inspection.
        unprefixed: When True, returns the bundle whose class names have
            no ``ok-`` prefix (``.btn`` instead of ``.ok-btn``). Pair this
            with ``register_globals(env, ok_prefix="")``.
    """
    ref = version or "latest"
    if not minified:
        return f"{_CDN_BASE}@{ref}/css/outfitkit.css"
    name = "outfitkit.unprefixed.min.css" if unprefixed else "outfitkit.min.css"
    return f"{_CDN_BASE}@{ref}/dist/{name}"


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
