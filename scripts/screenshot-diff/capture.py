# ========================================================================
#   About This File
# ========================================================================

"""
Screenshots a fixed list of Models Gone Wild pages and states at several widths.

Usage: capture.py <base url> <out dir>

Drives Playwright's Chromium headlessly against the preview server.
Requests to any host but the local server and Google Fonts are aborted.
The first side records every font response it downloads, and the second
side replays them byte for byte, so both sides draw in the same faces.

Each capture waits for document.fonts.ready, since the Threat Matrix
measures its labels in Oswald and lays out differently in a fallback
face. The poster permalink opens its poster on load, so that capture
also waits for the open overlay.
"""



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import hashlib
import json
import os
import sys

from collections.abc import Callable
from pathlib         import Path
from urllib.parse    import urlparse

# Third party
from playwright.sync_api import Browser, Route, sync_playwright



# ========================================================================
#   Global Variables
# ========================================================================

PREFIX        = "/tools/models-gone-wild"
WIDTHS        = [375, 768, 1024, 1440]
HEIGHT        = 900

# Hosts a capture may reach
LOCAL_HOSTS   = {"127.0.0.1", "localhost"}
ALLOWED_HOSTS = LOCAL_HOSTS | {"fonts.googleapis.com", "fonts.gstatic.com"}

# (name, path, selector to wait for)
PAGES         = [
    ("home",          "/",                         None),
    ("threat-matrix", "/threat-matrix/",           None),
    ("lab-counts",    "/lab-counts/",              None),
    ("poster",        "/poster/sol-hugging-face/", "#overlay.open"),
    ("methodology",   "/methodology/",             None),
]

# Freeze motion and the caret
FREEZE_CSS    = "*,*::before,*::after{transition:none!important;animation:none!important;caret-color:transparent!important}"

# Rasterizer flags for identical text
LAUNCH_ARGS   = [
    "--force-color-profile=srgb", "--disable-gpu", "--font-render-hinting=none",
    "--disable-lcd-text", "--disable-font-subpixel-positioning",
    "--disable-skia-runtime-opts", "--disable-partial-raster",
    "--disable-checker-imaging", "--disable-threaded-animation",
    "--disable-threaded-scrolling", "--disable-renderer-backgrounding",
    "--force-device-scale-factor=1", "--disable-features=PaintHolding",
]



# ========================================================================
#   Arguments and Folders
# ========================================================================

def parse_args() -> tuple:
    """
    Reads the base URL and the output folder

    Args:
        None

    Returns:
        tuple: The base URL and the output Path
    """

    return sys.argv[1], Path(sys.argv[2])


def prepare_folders(out: Path) -> Path:
    """
    Creates the output folder and the font cache folder beside it

    Args:
        out (Path): The output folder

    Returns:
        Path: The font cache folder
    """

    out.mkdir(parents=True, exist_ok=True)

    cache = out.parent / "font-cache"
    cache.mkdir(exist_ok=True)

    return cache



# ========================================================================
#   Request Routing
# ========================================================================

def make_route_filter(cache: Path) -> Callable:
    """
    Builds the request handler that serves local pages, replays cached fonts, and aborts the rest

    Args:
        cache (Path): The font cache folder

    Returns:
        Callable: The handler to pass to a Playwright context's route
    """

    def route_filter(route: Route) -> None:
        """
        Serves local requests, replays cached font responses, and aborts the rest

        Args:
            route (Route): The intercepted request

        Returns:
            None
        """

        url  = route.request.url
        host = urlparse(url).hostname or ""

        if host in LOCAL_HOSTS:
            route.continue_()
            return

        if host not in ALLOWED_HOSTS:
            route.abort()
            return

        key = hashlib.sha256(url.encode()).hexdigest()
        body_path, meta_path = cache / key, cache / f"{key}.json"

        if not meta_path.exists():
            try:
                resp = route.fetch(timeout=15000)
            except Exception:
                route.abort()
                return

            body_path.write_bytes(resp.body())
            meta_path.write_text(json.dumps({"status": resp.status, "headers": resp.headers}))

        meta    = json.loads(meta_path.read_text())
        headers = {k: v for k, v in meta["headers"].items()
                   if k.lower() not in ("content-encoding", "content-length", "transfer-encoding")}

        route.fulfill(status=meta["status"], headers=headers, body=body_path.read_bytes())

    return route_filter



# ========================================================================
#   Capture
# ========================================================================

def capture_one(
    browser:      Browser,
    base:         str,
    out:          Path,
    route_filter: Callable,
    name:         str,
    path:         str,
    ready:        str | None,
    width:        int,
) -> tuple:
    """
    Captures one page at one width, saving the screenshot

    Args:
        browser (Browser): The running Chromium
        base (str): The base URL of the server
        out (Path): The output folder
        route_filter (Callable): The request handler for the context
        name (str): The page name
        path (str): The path under the prefix to load
        ready (str | None): A selector to wait for before the capture, or None
        width (int): The window width in pixels

    Returns:
        tuple: The key for the notes file and the note for this capture
    """

    key = f"{name}@{width}"
    ctx = browser.new_context(viewport={"width": width, "height": HEIGHT},
                              device_scale_factor=1, reduced_motion="reduce",
                              timezone_id="UTC", locale="en-US")
    ctx.set_default_timeout(15000)
    ctx.route("**/*", route_filter)

    page = ctx.new_page()
    note = ""

    try:
        resp = page.goto(base + PREFIX + path, wait_until="load", timeout=30000)
        page.add_style_tag(content=FREEZE_CSS)
        page.evaluate("document.fonts.ready")

        if ready:
            try:
                page.wait_for_selector(ready, timeout=10000)
            except Exception:
                note = f"NO-ACTION({ready})"

        page.wait_for_timeout(1200)
        page.screenshot(path=str(out / f"{key}.png"), full_page=True,
                        animations="disabled", caret="hide", timeout=20000)

        shown = page.url[len(base):].split("?")[0]
        note  = f'{resp.status if resp else "?"} {shown} {note}'.strip()
    except Exception as exc:
        note = f"ERROR {type(exc).__name__}: {str(exc)[:120]}"
    finally:
        ctx.close()

    return key, note


def main() -> None:
    """
    Captures every page at every width into the output directory

    Args:
        None

    Returns:
        None
    """

    base, out    = parse_args()
    route_filter = make_route_filter(prepare_folders(out))
    notes        = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=LAUNCH_ARGS)

        for name, path, ready in PAGES:
            for width in WIDTHS:
                key, note  = capture_one(browser, base, out, route_filter, name, path, ready, width)
                notes[key] = note

            print(name, notes.get(f"{name}@{WIDTHS[-1]}"), flush=True)
            (out / "_notes.json").write_text(json.dumps(notes, indent=1))

    # Skip Chrome's slow shutdown
    os._exit(0)



# ========================================================================
#   Entry Point
# ========================================================================

if __name__ == "__main__":
    main()