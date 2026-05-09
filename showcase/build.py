"""Build the OutfitKit showcase to static HTML.

Generates `build/` from `pages/` using staticjinja, with JinjaX components
loaded from `src/outfitkit/templates/ui/` (the public component library) and
`chrome/` (showcase-only chrome).
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from jinja2 import FileSystemLoader
from jinjax import Catalog
from staticjinja import Site

ROOT = Path(__file__).parent
PAGES = ROOT / "pages"
CHROME = ROOT / "chrome"
UI = ROOT / "src" / "outfitkit" / "templates" / "ui"
BUILD = ROOT / "build"
STATIC = ROOT / "static"


class ShowcaseSite(Site):
    """Site that only renders files under ``pages/``.

    The Jinja environment loader must see ``chrome/`` and ``ui/`` so that
    pages can ``{% from "ui/button.jinja" import button %}`` and JinjaX can
    resolve ``<Component />`` tags. But those folders contain reusable
    macros, not pages — they must not be emitted as standalone files into
    ``build/``.

    We mark every template that lives outside ``pages/`` as a partial,
    which keeps it loadable but excluded from the render output.
    """

    def is_partial(self, filename) -> bool:  # type: ignore[override]
        if super().is_partial(filename):
            return True
        # Resolve to absolute path. If the template comes from a folder
        # other than `pages/`, treat it as a partial.
        try:
            self.env.loader.get_source(self.env, str(filename))
        except Exception:
            return False
        # Look up the actual filesystem path of this template name.
        for searchpath in [PAGES, CHROME, UI.parent]:
            candidate = searchpath / Path(filename)
            if candidate.exists():
                return searchpath != PAGES
        return False


def _css_url() -> str:
    """Where the showcase loads OutfitKit's CSS from.

    - Default: jsDelivr CDN, branch ``main`` (always-fresh).
    - Set ``OUTFITKIT_CSS=local`` to load from ``./css/outfitkit.css`` —
      the build copies the CSS folder into ``build/css/`` for that case.
    """
    if os.environ.get("OUTFITKIT_CSS") == "local":
        return "/css/outfitkit.css"
    return "https://cdn.jsdelivr.net/gh/OutfitKit/outfitkit@main/css/outfitkit.css"


def make_site() -> ShowcaseSite:
    site = ShowcaseSite.make_site(
        searchpath=str(PAGES),
        outpath=str(BUILD),
        extensions=["jinjax.JinjaX"],
        env_kwargs={"auto_reload": True},
        env_globals={"css_url": _css_url()},
    )

    # Register every folder so that templates can `{% extends %}` /
    # `{% from "ui/X.jinja" import x %}` from any of them.
    site.env.loader = FileSystemLoader([
        str(PAGES),
        str(CHROME),
        str(UI.parent),  # exposes "ui/<name>.jinja"
    ])

    # Build the JinjaX catalog from both UI components (public) and chrome
    # components (showcase-only). The catalog is also exposed as a Jinja
    # global so that JinjaX can resolve `<Component />` tags during render.
    catalog = Catalog(jinja_env=site.env)
    catalog.add_folder(str(UI))
    catalog.add_folder(str(CHROME))
    site.env.globals["catalog"] = catalog

    return site


def main() -> None:
    BUILD.mkdir(exist_ok=True)
    site = make_site()
    site.render()

    # When using local CSS, copy the source CSS folder into build/css so
    # that <link href="/css/outfitkit.css"> resolves under the dev server.
    if os.environ.get("OUTFITKIT_CSS") == "local":
        css_src = ROOT.parent / "css"
        css_dst = BUILD / "css"
        if css_dst.exists():
            shutil.rmtree(css_dst)
        shutil.copytree(css_src, css_dst)

    print(f"Showcase built into {BUILD}")


if __name__ == "__main__":
    main()
