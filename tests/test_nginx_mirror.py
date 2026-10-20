# ========================================================================
#   About This File
# ========================================================================

# Tests that scripts/serve.py answers every request the way the nginx
# blocks in DEPLOY.md do. The blocks are read from DEPLOY.md and run by a
# small emulator of nginx's location matching, so a change to either the
# blocks or the preview that leaves them disagreeing fails here. Also
# checks the staging blocks route exactly as the production blocks do.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import re

from collections.abc import Callable
from pathlib          import Path
from urllib.parse     import parse_qs, urlsplit

# Third party
import pytest

# Local
from conftest import serve



# ========================================================================
#   Global Variables
# ========================================================================

REPO   = Path(__file__).resolve().parent.parent
PREFIX = serve.PREFIX

PATHS = [
    "",
    "/",
    "/index.html",
    "/threat-matrix",
    "/threat-matrix/",
    "/lab-counts",
    "/lab-counts/",
    "/poster/sol-hugging-face",
    "/poster/sol-hugging-face/",
    "/poster/Bad_Slug",
    "/poster/Bad_Slug/",
    "/threat-matrix/poster/sol-hugging-face/",
    "/methodology/",
    "/methodology/index.html",
    "/no-such-page/",
    "/?view=matrix",
    "/?view=labs",
    "/threat-matrix/?view=labs",
    "/css/base.css",
    "/threat-matrix/css/base.css",
    "/lab-counts/js/cases.js",
    "/poster/sol-hugging-face/js/vendor/html2canvas.min.js",
    "/poster/sol-hugging-face/fonts/oswald/latin.woff2",
    "/img/annielytics-logo.png",
    "/DEPLOY.md",
    "/poster/sol-hugging-face/DEPLOY.md",
]



# ========================================================================
#   Reading the Blocks
# ========================================================================

def deploy_blocks(heading: str) -> list[dict]:
    """
    Parses the location blocks in the first nginx code block after a line of DEPLOY.md

    Args:
        heading (str): The start of the line the code block follows

    Returns:
        list[dict]: Each block's modifier, pattern, returns, rewrites, view redirects, and whether it serves files
    """

    text  = (REPO / "DEPLOY.md").read_text(encoding="utf-8")
    after = text[text.index(heading):]
    code  = re.search(r"```nginx\n(.*?)```", after, re.S).group(1)

    return [
        {
            "modifier": modifier,
            "pattern":  pattern,
            "return":   re.search(r"^\s*return 301 (\S+);", body, re.M),
            "rewrite":  re.search(r"^\s*rewrite (\S+) (\S+) last;", body, re.M),
            "views":    dict(re.findall(r"if \(\$arg_view = (\w+)\)\s*\{\s*return 301 (\S+);", body)),
            "serves":   "alias " in body,
        }
        for modifier, pattern, body in re.findall(r"^location\s+(=|~\*|~|)\s*(\S+)\s*\{\n(.*?)^\}", code, re.M | re.S)
    ]


def routing(blocks: list[dict]) -> list[tuple]:
    """
    Reduces blocks to what decides routing, leaving out aliases and access rules

    Args:
        blocks (list[dict]): The blocks deploy_blocks returns

    Returns:
        list[tuple]: Each block's modifier, pattern, return, rewrite, view redirects, and serving flag
    """

    return [
        (
            block["modifier"],
            block["pattern"],
            block["return"] and block["return"].group(1),
            block["rewrite"] and block["rewrite"].groups(),
            block["views"],
            block["serves"],
        )
        for block in blocks
    ]



# ========================================================================
#   Emulating Nginx
# ========================================================================

def nginx_resolve(blocks: list[dict], path: str) -> tuple[str | None, str | None]:
    """
    Runs a request through the blocks the way nginx matches locations

    Args:
        blocks (list[dict]): The blocks deploy_blocks returns
        path (str): The request path, query string included

    Returns:
        tuple[str | None, str | None]: The 301 target or None, and the path under public/ to serve or None
    """

    uri   = urlsplit(path).path
    query = parse_qs(urlsplit(path).query)

    for _ in range(10):
        exact  = [b for b in blocks if b["modifier"] == "=" and b["pattern"] == uri]
        regex  = [b for b in blocks if b["modifier"].startswith("~")
                  and re.search(b["pattern"], uri, re.I if b["modifier"] == "~*" else 0)]
        prefix = [b for b in blocks if b["modifier"] == "" and uri.startswith(b["pattern"])]
        block  = (exact or regex or prefix or [None])[0]

        if block is None:
            return None, None

        flags = re.I if block["modifier"] == "~*" else 0
        found = re.search(block["pattern"], uri, flags) if block["modifier"].startswith("~") else None

        if block["return"]:
            target = block["return"].group(1)
            return (found.expand(target.replace("$", "\\")) if found else target), None

        if block["rewrite"]:
            source, target = block["rewrite"].groups()
            uri            = re.sub(source, target.replace("$", "\\"), uri)
            continue

        view = query.get("view", [""])[0]

        if view in block["views"]:
            return block["views"][view], None

        return None, uri[len(PREFIX):] or "/"

    raise AssertionError(f"Rewrite cycle for {path}")



# ========================================================================
#   Agreement
# ========================================================================

def expected_response(path: str) -> tuple[int, str | None]:
    """
    Works out the status and Location nginx would send for a path, from DEPLOY.md's production blocks

    Args:
        path (str): The path after the prefix, query string included

    Returns:
        tuple[int, str | None]: The status code, and the Location for a redirect or None
    """

    target, served = nginx_resolve(deploy_blocks("Add all seven blocks"), PREFIX + path)

    if target:
        return 301, target

    site = REPO / "public" / served.lstrip("/")
    page = site / "index.html" if served.endswith("/") else site

    return (200 if page.is_file() else 404), None


@pytest.mark.parametrize("path", PATHS)
def test_preview_matches_production_blocks(path: str, fetch: Callable[[str], tuple]) -> None:
    """
    Checks the preview answers a path with the status and Location DEPLOY.md's production blocks send

    Args:
        path (str): The path after the prefix, query string included
        fetch (Callable[[str], tuple]): The helper that requests a path from the preview server

    Returns:
        None
    """

    status, headers, _ = fetch(path)
    assert (status, headers.get("Location")) == expected_response(path)


def test_staging_blocks_route_like_production() -> None:
    """
    Checks the staging blocks in DEPLOY.md route every request as the production blocks do

    Args:
        None

    Returns:
        None
    """

    production = routing(deploy_blocks("Add all seven blocks"))
    staging    = routing(deploy_blocks("These sit in `staging.annielytics.conf`"))
    assert len(production) == 7
    assert staging == production