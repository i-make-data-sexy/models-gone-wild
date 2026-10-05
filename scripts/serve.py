#!/usr/bin/env python3
"""Serves a local preview of the app at its real production subpath.

The plain python3 -m http.server cannot serve the dashboard permalinks,
since /threat-matrix/ and /lab-counts/ are not folders on disk. This
server does what the nginx rewrite does in production: it strips the
view segment, so /tools/models-gone-wild/lab-counts/ serves index.html
and /tools/models-gone-wild/lab-counts/css/styles.css serves the real
stylesheet. Old ?view= links get the same 301 to their permalink that
nginx sends. Serving at the subpath also exercises the relative asset
paths the way production does.

Usage:
  python3 scripts/serve.py [--port 8899]

Then open http://127.0.0.1:8899/tools/models-gone-wild/
"""
import argparse
import os
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX = "/tools/models-gone-wild"

# Keep in step with VIEW_SLUGS in index.html and the rewrite in DEPLOY.md
VIEW_SLUGS = ("threat-matrix", "lab-counts")
VIEW_RE = re.compile(r"^" + re.escape(PREFIX) + r"/(?:" + "|".join(VIEW_SLUGS) + r")(/.*)?$")

# The old ?view= values and the permalink each one now lives at. Mirrors
# the 301s in the nginx page block in DEPLOY.md.
LEGACY_VIEWS = {"matrix": "threat-matrix", "labs": "lab-counts"}


# ========================================================================
#   Request Handler
# ========================================================================

class PreviewHandler(SimpleHTTPRequestHandler):
    """
    Maps the production URL space onto the repo, including the view permalinks
    """

    def translate_path(self, path: str) -> str:
        """
        Turns a request path into a file path inside the repo

        Args:
            path (str): The raw request path, query string included

        Returns:
            str: The file path to serve, or a path that does not exist so the request 404s
        """
        bare = path.split("?", 1)[0].split("#", 1)[0]
        if bare != PREFIX and not bare.startswith(PREFIX + "/"):
            return os.path.join(REPO, "__outside_prefix__")
        view = VIEW_RE.match(bare)
        if view:
            bare = PREFIX + (view.group(1) or "/")
        return super().translate_path(bare[len(PREFIX):] or "/")

    def do_GET(self):
        """
        Answers the redirects nginx answers in production, then serves normally
        """
        bare = self.path.split("?", 1)[0]
        legacy = LEGACY_VIEWS.get(parse_qs(urlsplit(self.path).query).get("view", [""])[0])
        if bare.startswith(PREFIX + "/") and legacy:
            return self.redirect(f"{PREFIX}/{legacy}/")
        if bare in (f"{PREFIX}/{slug}" for slug in VIEW_SLUGS):
            return self.redirect(bare + "/")
        return super().do_GET()

    def redirect(self, location: str):
        """
        Sends a permanent redirect

        Args:
            location (str): The path to send the browser to
        """
        self.send_response(301)
        self.send_header("Location", location)
        self.end_headers()


# ========================================================================
#   Entry Point
# ========================================================================

def main():
    """
    Parses the port and serves the repo until interrupted
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8899)
    args = parser.parse_args()
    handler = partial(PreviewHandler, directory=REPO)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"Serving http://127.0.0.1:{args.port}{PREFIX}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
