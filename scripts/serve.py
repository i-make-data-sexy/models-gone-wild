# ========================================================================
#   About This File
# ========================================================================

"""
Serves a local preview of the app at its real production subpath.

The plain python3 -m http.server cannot serve the dashboard or poster
permalinks, since /threat-matrix/, /lab-counts/, and /poster/<id>/ are not
folders on disk. This server does what the nginx rewrite does in production.
It strips that segment, so /tools/models-gone-wild/lab-counts/ serves
index.html and /tools/models-gone-wild/lab-counts/css/base.css serves the
real stylesheet. Old ?view= links get the same 301 to their permalink that
nginx sends, and every response carries the security headers from
deploy/nginx/headers.conf. Serving at the subpath also exercises the
relative asset paths the way production does.

Usage:
    python3 scripts/serve.py [--port 8899]

Then open http://127.0.0.1:8899/tools/models-gone-wild/
"""



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import argparse
import os
import re

from functools    import lru_cache, partial
from http.server  import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit



# ========================================================================
#   Global Variables
# ========================================================================

REPO   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREFIX = "/tools/models-gone-wild"



# ========================================================================
#   Permalink Rules
# ========================================================================

def resolve_permalink(path: str) -> tuple[str | None, str | None]:
    """
    Applies the nginx permalink rules to a request path

    Args:
        path (str): The raw request path, query string included

    Returns:
        tuple[str | None, str | None]: The 301 target or None, and the repo path to serve or None
    """

    view_slugs   = ("threat-matrix", "lab-counts")
    legacy_views = {"matrix": "threat-matrix", "labs": "lab-counts"}

    bare   = path.split("?", 1)[0]
    legacy = legacy_views.get(parse_qs(urlsplit(path).query).get("view", [""])[0])
    root   = re.escape(PREFIX)
    views  = "|".join(view_slugs)

    target = None

    if bare.startswith(PREFIX + "/") and legacy:
        target = f"{PREFIX}/{legacy}/"
    elif bare in (f"{PREFIX}/{slug}" for slug in view_slugs) or re.match(rf"^{root}/poster/[\w-]+$", bare):
        target = bare + "/"

    served = bare.split("#", 1)[0]

    if served != PREFIX and not served.startswith(PREFIX + "/"):
        return target, None

    segment = (re.match(rf"^{root}/(?:{views})(/.*)?$", served)
            or re.match(rf"^{root}/poster/[\w-]+(/.*)?$", served))

    if segment:
        served = PREFIX + (segment.group(1) or "/")

    return target, served[len(PREFIX):] or "/"



# ========================================================================
#   Security Headers
# ========================================================================

@lru_cache(maxsize=None)
def read_headers() -> tuple[tuple[str, str], ...]:
    """
    Reads the add_header lines from the nginx headers snippet, once per run

    Args:
        None

    Returns:
        tuple[tuple[str, str], ...]: Each header's name and value, in file order
    """

    snippet = os.path.join(REPO, "deploy", "nginx", "headers.conf")
    pattern = re.compile(r'^\s*add_header\s+([\w-]+)\s+"([^"]*)"(?:\s+always)?\s*;')

    with open(snippet, encoding="utf-8") as handle:
        return tuple(match.groups() for match in map(pattern.match, handle) if match)



# ========================================================================
#   Request Handler
# ========================================================================

class PreviewHandler(SimpleHTTPRequestHandler):
    """
    Maps the production URL space onto the repo, including the view and poster permalinks
    """

    def translate_path(self, path: str) -> str:
        """
        Turns a request path into a file path inside the repo

        Args:
            path (str): The raw request path, query string included

        Returns:
            str: The file path to serve, or a path that does not exist so the request 404s
        """

        _, served = resolve_permalink(path)

        if served is None:
            return os.path.join(REPO, "__outside_prefix__")

        return super().translate_path(served)

    def do_GET(self) -> None:
        """
        Answers the redirects nginx answers in production, then serves normally

        Args:
            None

        Returns:
            None
        """

        target, _ = resolve_permalink(self.path)

        if target:
            return self.redirect(target)

        return super().do_GET()

    def redirect(self, location: str) -> None:
        """
        Sends a permanent redirect

        Args:
            location (str): The path to send the browser to

        Returns:
            None
        """

        self.send_response(301)
        self.send_header("Location", location)
        self.end_headers()

    def end_headers(self) -> None:
        """
        Adds the security headers to every response, errors and redirects included

        Args:
            None

        Returns:
            None
        """

        for name, value in read_headers():
            self.send_header(name, value)

        super().end_headers()



# ========================================================================
#   Command Line
# ========================================================================

def main() -> None:
    """
    Parses the port and serves the repo until interrupted

    Args:
        None

    Returns:
        None
    """

    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--port", type=int, default=8899)

    args    = parser.parse_args()
    handler = partial(PreviewHandler, directory=REPO)
    server  = ThreadingHTTPServer(("127.0.0.1", args.port), handler)

    print(f"Serving http://127.0.0.1:{args.port}{PREFIX}/")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass



# ========================================================================
#   Entry Point
# ========================================================================

if __name__ == "__main__":
    main()