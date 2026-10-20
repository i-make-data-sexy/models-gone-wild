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
deploy/nginx/headers.conf. Each page also gets the canonical Link header
and its view's share tags from deploy/nginx/canonical-map.conf and
deploy/nginx/share.conf, and an index.html address gets the same 301 to
its folder. Serving at the subpath also exercises the relative asset
paths the way production does. A missing path under the prefix gets
404.html with a 404, as nginx's error_page sends.

Usage:
    python3 scripts/serve.py [--port 8899]

Then open http://127.0.0.1:8899/tools/models-gone-wild/
"""



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import argparse
import io
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
    index  = re.match(rf"^{root}/((?:{views}|poster/[a-z0-9-]+|methodology)/)?index\.html$", bare)

    if bare.startswith(PREFIX + "/") and legacy:
        target = f"{PREFIX}/{legacy}/"
    elif index:
        target = f"{PREFIX}/{index.group(1) or ''}"
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
#   Canonical and Share Tags
# ========================================================================

def unquote(token: str) -> str:
    """
    Strips the double quotes and escapes from an nginx config token

    Args:
        token (str): A key or value as it appears in the config

    Returns:
        str: The token's text
    """

    if len(token) > 1 and token[0] == token[-1] == '"':
        return re.sub(r"\\(.)", r"\1", token[1:-1])

    return token


@lru_cache(maxsize=None)
def read_maps() -> dict[str, tuple[str, tuple[tuple[str, str], ...]]]:
    """
    Reads the map blocks from the nginx canonical map, once per run

    Args:
        None

    Returns:
        dict[str, tuple[str, tuple[tuple[str, str], ...]]]: Each output variable, with its source variable and its key and value pairs in file order
    """

    conf  = os.path.join(REPO, "deploy", "nginx", "canonical-map.conf")
    token = r'("(?:[^"\\]|\\.)*"|\S+)'
    block = re.compile(r"^map\s+\$(\w+)\s+\$(\w+)\s*\{\n(.*?)^\}", re.M | re.S)
    entry = re.compile(rf"^\s*{token}\s+{token}\s*;", re.M)

    with open(conf, encoding="utf-8") as handle:
        text = handle.read()

    return {output: (source, tuple(entry.findall(body))) for source, output, body in block.findall(text)}


def nginx_variable(name: str, request_uri: str) -> str:
    """
    Works out a variable the canonical map defines, the way nginx's map does

    Args:
        name (str): The variable's name, without the dollar sign
        request_uri (str): The original request path, query string included

    Returns:
        str: The variable's value for the request
    """

    if name == "request_uri":
        return request_uri

    source, entries = read_maps()[name]

    value   = nginx_variable(source, request_uri)
    exact   = {unquote(key): raw for key, raw in entries if key != "default" and not key.startswith("~")}
    chosen  = exact.get(value)
    default = next((raw for key, raw in entries if key == "default"), '""')
    groups  = {}

    for key, raw in entries:
        found = key.startswith("~") and re.search(re.sub(r"\(\?<(?=\w)", "(?P<", key[1:]), value)

        if chosen is None and found:
            chosen, groups = raw, found.groupdict()

    def expand(match: re.Match) -> str:
        """
        Fills in one variable named in a map value

        Args:
            match (re.Match): The dollar sign and name found in the value

        Returns:
            str: A named capture of the matched key, or the variable's own value
        """

        return groups[match.group(1)] if match.group(1) in groups else nginx_variable(match.group(1), request_uri)

    return re.sub(r"\$(\w+)", expand, unquote(default if chosen is None else chosen))


@lru_cache(maxsize=None)
def read_share() -> tuple[tuple[str, str], tuple[tuple[str, str], ...]]:
    """
    Reads the Link header and the share-tag swaps from the nginx share snippet, once per run

    Args:
        None

    Returns:
        tuple[tuple[str, str], tuple[tuple[str, str], ...]]: The header's name and variable, and each search string with its replacement
    """

    snippet = os.path.join(REPO, "deploy", "nginx", "share.conf")

    with open(snippet, encoding="utf-8") as handle:
        text = handle.read()

    header = re.search(r"^add_header\s+([\w-]+)\s+\$(\w+)\s+always;", text, re.M).groups()
    swaps  = tuple(re.findall(r"^sub_filter\s+'([^']*)'\s+'([^']*)';", text, re.M))

    return header, swaps


def swap_share_tags(body: bytes, request_uri: str) -> bytes:
    """
    Swaps a view's share values into a page, as the nginx sub_filter lines do

    Args:
        body (bytes): The page as it sits on disk
        request_uri (str): The original request path, query string included

    Returns:
        bytes: The page with every search string replaced, ignoring case
    """

    text = body.decode("utf-8")

    for search, replacement in read_share()[1]:
        value = re.sub(r"\$(\w+)", lambda match: nginx_variable(match.group(1), request_uri), replacement)
        text  = re.sub(re.escape(search), lambda _: value, text, flags=re.I)

    return text.encode("utf-8")



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

    def send_head(self) -> io.BytesIO | object | None:
        """
        Serves a page with its view's share tags swapped in, and anything else normally

        Args:
            None

        Returns:
            io.BytesIO | object | None: The body to copy to the client, or None after an error
        """

        path = self.translate_path(self.path)

        if os.path.isdir(path) and self.path.split("?", 1)[0].endswith("/"):
            path = os.path.join(path, "index.html")

        if not path.endswith(".html") or not os.path.isfile(path):
            return super().send_head()

        with open(path, "rb") as handle:
            body = swap_share_tags(handle.read(), self.path)

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        return io.BytesIO(body)

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
            body = swap_share_tags(handle.read(), self.path)

        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        if self.command != "HEAD":
            self.wfile.write(body)

    def end_headers(self) -> None:
        """
        Adds the security headers and any canonical Link to every response, errors and redirects included

        Args:
            None

        Returns:
            None
        """

        (header, variable), _ = read_share()
        link                  = nginx_variable(variable, self.path)

        for name, value in read_headers():
            self.send_header(name, value)

        if link:
            self.send_header(header, link)

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