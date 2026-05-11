"""Dev server for the OutfitKit showcase.

Watches `pages/`, `chrome/`, and `src/outfitkit/templates/` for changes,
rebuilds incrementally, and serves `build/` over HTTP at :7777.

Fix de puerto bloqueado: ReusableTCPServer pone allow_reuse_address=True
ANTES del bind, así que tras un kill el puerto vuelve a estar disponible
sin tener que esperar TIME_WAIT (30-60s).
"""
from __future__ import annotations

import http.server
import os
import shutil
import socketserver
import threading
from pathlib import Path

from build import BUILD, ROOT, STATIC, make_site

PORT = 7777


class ReusableTCPServer(socketserver.TCPServer):
    """TCPServer con SO_REUSEADDR aplicado ANTES del bind.

    El default `socketserver.TCPServer` lee el atributo de clase
    `allow_reuse_address` durante `server_bind()`. Si lo asignas a la
    instancia después del __init__, el bind ya ocurrió y el TIME_WAIT
    sigue activo. Subclase con el atributo de clase a True para que el
    socket se pueda reutilizar inmediatamente tras matar el proceso.
    """
    allow_reuse_address = True
    # En macOS/Linux también beneficia SO_REUSEPORT para arranques rápidos
    # paralelos (no aplica aquí pero no daña).
    allow_reuse_port = True


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BUILD), **kwargs)

    def log_message(self, fmt, *args):
        # Silenciar logs de cada request — ruido en consola
        pass


def _copy_static_and_css() -> None:
    """Copia static/ y css/ al build/ — mismo flujo que build.py main().

    Sin esto, serve.py arranca con build/ desactualizado tras editar CSS.
    """
    if STATIC.exists():
        static_dst = BUILD / "static"
        if static_dst.exists():
            shutil.rmtree(static_dst)
        shutil.copytree(STATIC, static_dst)

    if os.environ.get("OUTFITKIT_CSS") == "local":
        css_src = ROOT.parent / "css"
        css_dst = BUILD / "css"
        if css_dst.exists():
            shutil.rmtree(css_dst)
        shutil.copytree(css_src, css_dst)


def serve() -> None:
    with ReusableTCPServer(("", PORT), Handler) as httpd:
        print(f"Serving showcase on http://localhost:{PORT}/")
        httpd.serve_forever()


def main() -> None:
    BUILD.mkdir(exist_ok=True)

    # First build before starting the server, so the user sees something.
    site = make_site()
    site.render()
    _copy_static_and_css()

    # Run the server in a daemon thread; staticjinja's reloader blocks the
    # main thread watching for filesystem changes.
    threading.Thread(target=serve, daemon=True).start()

    print("Watching for changes (CTRL+C to stop)...")
    site.render(use_reloader=True)


if __name__ == "__main__":
    main()
