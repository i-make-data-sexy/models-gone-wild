# ========================================================================
#   About This File
# ========================================================================

"""
Visits every page and home page state with Chrome and records each CSP violation.

Usage: walk.py <base url> <report json>

The pages are the home page, both view permalinks, every poster permalink,
Methodology, and an unknown path. The poster slugs come from the js/cases.js
the server sends, read with scripts/cases.py, so the list always matches the
ref being walked. The home page then gets the states a load alone does not
reach: each tab, each filter, a glossary bubble on hover, an open poster,
Copy link, and Download poster with the PNG actually produced. html2canvas
draws that PNG in a cloned frame under the page's policy, which is why the
download is part of the walk.

Every violation fires a securitypolicyviolation event and a console message,
so this list is exactly what the policy costs a page. JavaScript errors and
alert() messages are recorded too, to catch a script that stops working once
something it needs is refused.

Runs locally only, since Cloudflare blocks automated browsers on staging and
production. Google Tag Manager loads, so its container is checked against the
policy too, and a page that carries the tag fails when the container does not
arrive. Only the analytics beacons are aborted, after the policy has judged
them, so the walk never sends a hit to Google Analytics 4 (GA4). The GA4 tag
still needs a check in GTM's Preview mode on staging.
"""



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import importlib.util
import json
import os
import sys

from collections.abc import Callable
from pathlib         import Path
from types           import ModuleType
from urllib.parse    import urlparse
from urllib.request  import urlopen

# Third party
from playwright.sync_api import Browser, BrowserContext, Page, Route, sync_playwright



# ========================================================================
#   Global Variables
# ========================================================================

PREFIX = "/tools/models-gone-wild"



# ========================================================================
#   Arguments and Cases
# ========================================================================

def parse_args() -> tuple:
    """
    Reads the base URL and the report path from the command line

    Args:
        None

    Returns:
        tuple: The base URL and the report Path
    """

    return sys.argv[1], Path(sys.argv[2])


def load_cases_module() -> ModuleType:
    """
    Imports the shared case loader, scripts/cases.py, by its file path

    Args:
        None

    Returns:
        ModuleType: The cases module
    """

    path = Path(__file__).resolve().parent.parent / "cases.py"
    spec = importlib.util.spec_from_file_location("cases", path)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def poster_slugs(base: str) -> list[str]:
    """
    Lists every poster slug in the js/cases.js the server sends

    Args:
        base (str): The base URL of the server

    Returns:
        list[str]: Each case's poster slug, in registry order
    """

    cases = load_cases_module()

    with urlopen(base + PREFIX + "/js/cases.js", timeout=10) as response:
        js = response.read().decode("utf-8")

    return [cases.text_field(block, "slug") for block in cases.case_blocks(js).values()]



# ========================================================================
#   Request Routing
# ========================================================================

def route_filter(route: Route, entry: dict) -> None:
    """
    Lets every request through except the analytics beacons, which it counts and aborts

    Args:
        route (Route): The intercepted request
        entry (dict): The report entry that counts the aborted beacons

    Returns:
        None
    """

    beacon_suffixes = ("google-analytics.com", "analytics.google.com", "g.doubleclick.net", "google.com")
    host            = urlparse(route.request.url).hostname or ""

    if any(host == suffix or host.endswith("." + suffix) for suffix in beacon_suffixes):
        entry["beacons"] += 1
        route.abort()
    else:
        route.continue_()



# ========================================================================
#   Home Page Actions
# ========================================================================

def act_tab(page: Page, tab: str) -> str:
    """
    Clicks one view tab and checks its panel is the one showing

    Args:
        page (Page): The loaded page
        tab (str): The tab's name, such as "matrix"

    Returns:
        str: A note with the address the tab landed on

    Raises:
        AssertionError: When the tab's panel is still hidden
    """

    page.click(f"#tab-{tab}")
    page.wait_for_timeout(500)

    selected = page.get_attribute(f"#tab-{tab}", "aria-selected")
    panel    = page.get_attribute(f"#tab-{tab}", "aria-controls")

    if selected != "true" or not page.is_visible(f"#{panel}"):
        raise AssertionError(f"tab {tab} did not show #{panel}")

    return f"{panel} showing at {urlparse(page.url).path}"


def open_filters(page: Page) -> None:
    """
    Opens the filter menu

    Args:
        page (Page): The loaded page

    Returns:
        None
    """

    page.click("#optionsMenu summary.options-button")
    page.wait_for_selector("#optionsMenu[open]")


def filter_note(page: Page) -> str:
    """
    Reads the filter count line, which shows once any filter is set

    Args:
        page (Page): The page with a filter set

    Returns:
        str: The count line's text

    Raises:
        AssertionError: When the count line is still hidden
    """

    page.wait_for_selector("#filterCount:not([hidden])")

    return page.inner_text("#filterCount").strip()


def act_select_filter(page: Page, select: str, value: str) -> str:
    """
    Sets one dropdown filter in the filter menu

    Args:
        page (Page): The loaded page
        select (str): The dropdown's id, such as "classFilter"
        value (str): The option value to choose

    Returns:
        str: The filter count line
    """

    open_filters(page)
    page.select_option(f"#{select}", value)

    return filter_note(page)


def act_lab_filter(page: Page) -> str:
    """
    Ticks the first lab in the lab filter's list

    Args:
        page (Page): The loaded page

    Returns:
        str: The filter count line
    """

    open_filters(page)
    page.click("#labSummary")
    page.check("#labList input >> nth=0")

    return filter_note(page)


def act_glossary(page: Page) -> str:
    """
    Hovers the first glossary term on the timeline to show its bubble

    Args:
        page (Page): The loaded page

    Returns:
        str: A note with the bubble's classes
    """

    page.hover("#timeline .term >> nth=0")
    page.wait_for_selector("#tip.show")

    return "bubble shown, " + page.get_attribute("#tip", "class")


def open_poster(page: Page) -> None:
    """
    Opens the first card's wanted poster from its icon button

    Args:
        page (Page): The loaded page

    Returns:
        None
    """

    page.click("#timeline .icon-btn[data-open] >> nth=0")
    page.wait_for_selector("#overlay.open")


def act_poster(page: Page) -> str:
    """
    Opens a wanted poster from the timeline

    Args:
        page (Page): The loaded page

    Returns:
        str: A note with the poster's address
    """

    open_poster(page)

    return f"poster open at {urlparse(page.url).path}"


def act_copy_link(page: Page) -> str:
    """
    Opens a poster, presses Copy link, and checks the clipboard holds its link

    Args:
        page (Page): The loaded page

    Returns:
        str: A note with the copied link's path

    Raises:
        AssertionError: When the clipboard holds anything but the poster's link
    """

    open_poster(page)
    page.click("#copyBtn")
    page.wait_for_function("document.getElementById('copyBtn').textContent === 'Link copied'")

    copied = page.evaluate("navigator.clipboard.readText()")

    if copied != page.url:
        raise AssertionError(f"copied {copied!r} on {page.url!r}")

    return f"copied {urlparse(copied).path}"


def act_download(page: Page, folder: Path) -> str:
    """
    Opens a poster, presses Download poster, and checks the file is a PNG

    Args:
        page (Page): The loaded page
        folder (Path): Where to save the downloaded file

    Returns:
        str: A note with the file's name and size

    Raises:
        AssertionError: When the download is not a PNG
    """

    open_poster(page)

    with page.expect_download(timeout=60000) as download_info:
        page.click("#dlBtn")

    download = download_info.value
    saved    = folder / download.suggested_filename
    download.save_as(saved)

    data = saved.read_bytes()

    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise AssertionError(f"{saved.name} is not a PNG")

    return f"{saved.name}, {len(data):,} bytes"



# ========================================================================
#   The Walk
# ========================================================================

def build_visits(base: str, folder: Path) -> list[tuple]:
    """
    Lists every visit as (name, path, action), pages first and then home page states

    Args:
        base (str): The base URL of the server
        folder (Path): Where the download state saves its PNG

    Returns:
        list[tuple]: One (name, path, action) tuple per visit, the action None for a plain load
    """

    pages = [
        ("home",          "/",               None),
        ("threat-matrix", "/threat-matrix/", None),
        ("lab-counts",    "/lab-counts/",    None),
    ]
    pages += [(f"poster {slug}", f"/poster/{slug}/", None) for slug in poster_slugs(base)]
    pages += [
        ("methodology",   "/methodology/",   None),
        ("404",           "/no-such-page/",  None),
    ]

    states = [
        ("tab-timeline",    "/threat-matrix/", lambda page: act_tab(page, "timeline")),
        ("tab-matrix",      "/",               lambda page: act_tab(page, "matrix")),
        ("tab-labs",        "/",               lambda page: act_tab(page, "labs")),
        ("filter-class",    "/",               lambda page: act_select_filter(page, "classFilter", "3")),
        ("filter-lab",      "/",               act_lab_filter),
        ("filter-outcome",  "/",               lambda page: act_select_filter(page, "outcomeFilter", "attempt")),
        ("filter-kind",     "/",               lambda page: act_select_filter(page, "kindFilter", "action")),
        ("glossary-bubble", "/",               act_glossary),
        ("poster-open",     "/",               act_poster),
        ("copy-link",       "/",               act_copy_link),
        ("download-poster", "/",               lambda page: act_download(page, folder)),
    ]

    return [(name, PREFIX + path, action) for name, path, action in pages + states]


def open_context(browser: Browser, base: str, entry: dict) -> BrowserContext:
    """
    Opens a fresh browser context that records violations into the entry

    Args:
        browser (Browser): The running Chromium
        base (str): The base URL of the server, granted clipboard access
        entry (dict): The report entry the context writes into

    Returns:
        BrowserContext: The configured context
    """

    listener = """
        document.addEventListener("securitypolicyviolation", function (e) {
            try {
                window.__mgwCsp({directive: e.effectiveDirective, blocked: e.blockedURI,
                                 source: e.sourceFile, line: e.lineNumber,
                                 sample: e.sample, disposition: e.disposition});
            } catch (err) {}
        });
    """

    ctx = browser.new_context(viewport={"width": 1280, "height": 900}, accept_downloads=True)
    ctx.set_default_timeout(15000)
    ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=base)
    ctx.expose_binding("__mgwCsp", lambda source, v, e=entry: e["violations"].append(v))
    ctx.add_init_script(listener)
    ctx.route("**/*", lambda route, e=entry: route_filter(route, e))

    return ctx


def watch_page(page: Page, entry: dict) -> None:
    """
    Records policy console messages, uncaught JavaScript errors, and alerts into the entry

    Args:
        page (Page): The page to watch
        entry (dict): The report entry to write into

    Returns:
        None
    """

    page.on(
        "console",
        lambda m, e=entry: e["console"].append(m.text) if "Content Security Policy" in m.text else None,
    )
    page.on("pageerror", lambda err, e=entry: e["errors"].append(str(err)[:200]))
    page.on("dialog",    lambda dialog, e=entry: (e["errors"].append(f"ALERT {dialog.message}"), dialog.dismiss()))


def check_tag(page: Page) -> str:
    """
    Checks the tag manager container arrived on a page that carries the tag

    Args:
        page (Page): The loaded page

    Returns:
        str: "GTM loaded", or an empty string when the page carries no tag

    Raises:
        AssertionError: When the page carries the tag but the container never arrived
    """

    container = page.evaluate("document.querySelector('script[data-gtm-id]')?.dataset.gtmId || ''")

    if not container:
        return ""

    page.wait_for_function(
        "id => window.google_tag_manager && window.google_tag_manager[id]", arg=container, timeout=15000,
    )

    return "GTM loaded"


def visit_page(
    browser: Browser,
    base:    str,
    name:    str,
    path:    str,
    action:  Callable[[Page], str] | None,
) -> dict:
    """
    Loads one page, checks the tag, runs its action, and returns what was recorded

    Args:
        browser (Browser): The running Chromium
        base (str): The base URL of the server
        name (str): The name used in the report
        path (str): The path to load
        action (Callable[[Page], str] | None): The home page state to open, or None

    Returns:
        dict: The report entry with its violations, console messages, errors, and note
    """

    entry = {
        "page":       name,
        "path":       path,
        "violations": [],
        "console":    [],
        "errors":     [],
        "beacons":    0,
        "note":       "",
    }

    ctx  = open_context(browser, base, entry)
    page = ctx.new_page()
    watch_page(page, entry)

    try:
        resp = page.goto(base + path, wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)

        notes = [check_tag(page), action(page) if action else ""]
        page.wait_for_timeout(800)

        notes          += [f"{entry['beacons']} beacons aborted" if entry["beacons"] else ""]
        entry["status"] = resp.status if resp else None
        entry["note"]   = ", ".join(note for note in notes if note)
    except Exception as exc:
        entry["errors"].append(f"WALK {type(exc).__name__}: {str(exc)[:160]}")
    finally:
        ctx.close()

    return entry


def print_result(entry: dict) -> None:
    """
    Prints one line saying whether the visit was clean

    Args:
        entry (dict): The report entry for the visit

    Returns:
        None
    """

    found = entry["violations"] or entry["console"] or entry["errors"]
    flag  = "CHECK" if found else "CLEAN"

    print(f"{flag:5} {entry['page']:38} {entry.get('status')} {entry['note']}", flush=True)


def main() -> None:
    """
    Walks every page and state and writes the violations and errors to the report

    Args:
        None

    Returns:
        None
    """

    base, report = parse_args()
    results      = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for name, path, action in build_visits(base, report.parent):
            entry = visit_page(browser, base, name, path, action)

            print_result(entry)
            results.append(entry)

    report.write_text(json.dumps(results, indent=1))

    os._exit(0)



# ========================================================================
#   Entry Point
# ========================================================================

if __name__ == "__main__":
    main()