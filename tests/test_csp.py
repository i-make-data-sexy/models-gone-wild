# ========================================================================
#   About This File
# ========================================================================

# Content Security Policy and tag manager tests. The preview server sends
# the policy from the same snippet nginx includes, so every page a reader
# can reach must carry it enforced, never report-only, with no
# 'unsafe-inline' or 'unsafe-eval'. The connect list keeps the hosts GA4
# with Google Signals sends hits to, which the walk cannot see since it
# aborts Google's hosts. The style hash must match the one block
# html2canvas adds while it copies a poster, rebuilt here from the
# vendored library. Each page loads js/gtm.js as its first script and
# carries the noscript fallback frame. The last test runs the CSP walk
# against the working tree under -m browser.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import base64
import hashlib
import json
import re
import subprocess
import sys

from collections.abc import Callable
from pathlib         import Path

# Third party
import pytest



# ========================================================================
#   Global Variables
# ========================================================================

REPO   = Path(__file__).resolve().parent.parent
GTM_ID = "GTM-5FJGP2"

PATHS = [
    "/",
    "/threat-matrix/",
    "/lab-counts/",
    "/poster/sol-hugging-face/",
    "/methodology/",
    "/no-such-page/",
]

PAGES = ["index.html", "methodology/index.html"]



# ========================================================================
#   Helpers
# ========================================================================

def directives(fetch: Callable[[str], tuple]) -> dict[str, list[str]]:
    """
    Splits the home page's policy into its directives

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server

    Returns:
        dict[str, list[str]]: Each directive's name mapped to its sources
    """

    _, headers, _ = fetch("/")
    parts         = [part.split() for part in headers["Content-Security-Policy"].split(";") if part.strip()]

    return {part[0]: part[1:] for part in parts}


def html2canvas_style() -> str:
    """
    Rebuilds the style block html2canvas adds to its copy of the page

    Args:
        None

    Returns:
        str: The block's text, as the library sets it
    """

    js    = (REPO / "js" / "vendor" / "html2canvas.min.js").read_text(encoding="utf-8")
    found = re.search(
        r"\b(\w+)='(\{\\n[^']*\})',\w+=function\(A\)\{\w+\(A,\"\.\"\+(\w+)\+\":before\"\+\1\+\"([^\"]*)\.\"\+(\w+)\+\":after\"\+\1\)\}",
        js,
    )
    assert found, "html2canvas no longer adds its style block the way this test reads it"

    hide, gap = (found.group(n).encode().decode("unicode_escape") for n in (2, 4))
    before    = re.search(rf'\b{found.group(3)}="([^"]+)"', js).group(1)
    after     = re.search(rf'\b{found.group(5)}="([^"]+)"', js).group(1)

    return f".{before}:before{hide}{gap}.{after}:after{hide}"



# ========================================================================
#   The Policy
# ========================================================================

@pytest.mark.parametrize("path", PATHS)
def test_response_enforces_the_policy(fetch: Callable[[str], tuple], path: str) -> None:
    """
    Checks a page or a 404 sends the policy enforced, with no unsafe keyword

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server
        path (str): The path under the prefix

    Returns:
        None
    """

    _, headers, _ = fetch(path)
    policy        = headers.get("Content-Security-Policy", "")

    assert policy
    assert "Content-Security-Policy-Report-Only" not in headers
    assert "'unsafe-inline'" not in policy
    assert "'unsafe-eval'" not in policy


def test_connect_src_keeps_the_signals_hosts(fetch: Callable[[str], tuple]) -> None:
    """
    Checks connect-src names the hosts GA4 with Google Signals sends hits to

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server

    Returns:
        None
    """

    sources = directives(fetch)["connect-src"]

    for host in ("https://analytics.google.com", "https://*.google.com", "https://*.g.doubleclick.net"):
        assert host in sources


def test_style_hash_matches_html2canvas(fetch: Callable[[str], tuple]) -> None:
    """
    Checks style-src allows html2canvas's style block by its hash and nothing else inline

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server

    Returns:
        None
    """

    digest = hashlib.sha256(html2canvas_style().encode("utf-8")).digest()
    source = f"'sha256-{base64.b64encode(digest).decode()}'"

    assert directives(fetch)["style-src"] == ["'self'", source]



# ========================================================================
#   The Tag
# ========================================================================

@pytest.mark.parametrize("page", PAGES)
def test_page_loads_gtm_first(page: str) -> None:
    """
    Checks a page's first script is js/gtm.js carrying the container ID

    Args:
        page (str): The page's path from the repo root

    Returns:
        None
    """

    html  = (REPO / page).read_text(encoding="utf-8")
    first = re.search(r"<script\b[^>]*>", html).group(0)

    assert re.search(r'src="(\.\./)?js/gtm\.js"', first)
    assert f'data-gtm-id="{GTM_ID}"' in first


@pytest.mark.parametrize("page", PAGES)
def test_page_carries_the_noscript_frame(page: str) -> None:
    """
    Checks the tag's noscript fallback frame sits right after the body tag

    Args:
        page (str): The page's path from the repo root

    Returns:
        None
    """

    html  = (REPO / page).read_text(encoding="utf-8")
    frame = (
        f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_ID}" '
        'height="0" width="0" class="gtm-noscript-frame"></iframe></noscript>'
    )

    assert re.search(r"<body>\s*" + re.escape(frame), html)



# ========================================================================
#   The Walk
# ========================================================================

@pytest.mark.browser
def test_csp_walk_is_clean(server_port: int, tmp_path: Path) -> None:
    """
    Runs the CSP walk against the working tree and checks nothing was refused or broke

    Args:
        server_port (int): The port the preview server listens on
        tmp_path (Path): A folder for the report and the downloaded poster

    Returns:
        None
    """

    report = tmp_path / "report.json"
    walk   = REPO / "scripts" / "csp-walk" / "walk.py"

    subprocess.run([sys.executable, str(walk), f"http://127.0.0.1:{server_port}", str(report)],
                   check=True, capture_output=True, timeout=600)

    rows     = json.loads(report.read_text())
    findings = [row for row in rows if row["violations"] or row["console"] or row["errors"]]

    assert rows
    assert findings == []