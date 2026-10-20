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
real stylesheet. Only public/ is served, as nginx's alias serves only
public/ in production, so the repo's tooling is never reachable. Old
?view= links get the same 301 to their permalink that nginx sends, and
every response carries the security headers from
deploy/nginx/headers.conf. Serving at the subpath also exercises the
relative asset paths the way production does. A missing path under the
prefix gets 404.html with a 404, as nginx's error_page sends.

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
PUBLIC = os.path.join(REPO, "public")
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
        tuple[str | None, str | None]: The 301 target or None, and the path under public/ to serve or None
    """

    view_slugs   = ("threat-matrix", "lab-counts")
    legacy_views = {"matrix": "threat-matrix", "labs": "lab-counts"}

    bare      = path.split("?", 1)[0]
    legacy    = legacy_views.get(parse_qs(urlsplit(path).query).get("view", [""])[0])
    root      = re.escape(PREFIX)
    views     = "|".join(view_slugs)
    permalink = re.compile(rf"^{root}/(?:{views}|poster/[a-z0-9-]+)(/.*)?$")

    target = None

    if bare.startswith(PREFIX + "/") and legacy:
        target = f"{PREFIX}/{legacy}/"
    elif bare in (f"{PREFIX}/{slug}" for slug in view_slugs) or re.match(rf"^{root}/poster/[a-z0-9-]+$", bare):
        target = bare + "/"

    served = bare.split("#", 1)[0]

    if served != PREFIX and not served.startswith(PREFIX + "/"):
        return target, None

    while segment := permalink.match(served):
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
    Maps the production URL space onto public/, including the view and poster permalinks
    """

    def translate_path(self, path: str) -> str:
        """
        Turns a request path into a file path inside public/

        Args:
            path (str): The raw request path, query string included

        Returns:
            str: The file path to serve, or a path that does not exist so the request 404s
        """

        _, served = resolve_permalink(path)

        if served is None:
            return os.path.join(PUBLIC, "__outside_prefix__")

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

    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        """
        Serves 404.html for a missing path under the prefix, as nginx's error_page does

        Args:
            code (int): The HTTP status code
            message (str | None): The short reason, used only for other errors
            explain (str | None): The longer reason, used only for other errors

        Returns:
            None
        """

        page      = os.path.join(PUBLIC, "404.html")
        _, served = resolve_permalink(self.path)

        if code != 404 or served is None or not os.path.isfile(page):
            return super().send_error(code, message, explain)

        with open(page, "rb") as handle:
            body = handle.read()

        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        if self.command != "HEAD":
            self.wfile.write(body)

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
    Parses the port and serves public/ until interrupted

    Args:
        None

    Returns:
        None
    """

    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--port", type=int, default=8899)

    args    = parser.parse_args()
    handler = partial(PreviewHandler, directory=PUBLIC)
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