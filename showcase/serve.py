"""Dev server for the OutfitKit showcase.

Watches `pages/`, `chrome/`, and `src/outfitkit/templates/` for changes,
rebuilds incrementally, and serves `build/` over HTTP at :7777.
"""
from __future__ import annotations

import http.server
import socketserver
import threading

from build import BUILD, make_site

PORT = 7777


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BUILD), **kwargs)


def serve() -> None:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.allow_reuse_address = True
        print(f"Serving showcase on http://localhost:{PORT}/")
        httpd.serve_forever()


def main() -> None:
    BUILD.mkdir(exist_ok=True)

    # First build before starting the server, so the user sees something.
    site = make_site()
    site.render()

    # Run the server in a daemon thread; staticjinja's reloader blocks the
    # main thread watching for filesystem changes.
    threading.Thread(target=serve, daemon=True).start()

    print("Watching for changes (CTRL+C to stop)...")
    site.render(use_reloader=True)


if __name__ == "__main__":
    main()
