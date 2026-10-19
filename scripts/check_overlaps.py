# ========================================================================
#   About This File
# ========================================================================

"""
Reports anything on the Threat Matrix that is drawn on top of something else.

The other checks read the case data as text. This one renders the real
page in headless Chrome, so it sees what a reader sees: where each dot
landed, where its label went, and whether the axis icons sit clear of
their titles. It runs every combination of the Class, Lab, Outcome, and
Kind filters, since a label can collide in one filtered view and not in
another.

Text is measured by its ink rather than its line box. The line box of
a 13px label is taller than the glyphs in it, and comparing line boxes
would report stacked labels that never touch.

Writes a screenshot of the unfiltered chart to the path given with
--shot, for a look with your own eyes.

Exit status is 1 if anything overlaps or a dot label leaves the plot,
0 otherwise.
"""



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import argparse
import functools
import html
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading



# ========================================================================
#   Global Variables
# ========================================================================

CHROME = os.environ.get("CHROME") or next(
    (p for p in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
     + [shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser")]
     if p and os.path.exists(p)),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")



# ========================================================================
#   Running Chrome
# ========================================================================

def serve(root: str) -> tuple:
    """
    Serves a directory over HTTP on a free local port, in a background thread

    Args:
        root (str): The directory to serve

    Returns:
        tuple: The server, so it can be shut down, and the port it bound
    """

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args: object) -> None:
            """
            Drops the per-request log line so the report stays readable

            Args:
                *args (object): The format string and values the base class would log

            Returns:
                None
            """

            pass

    handler = functools.partial(Quiet, directory=root)
    server  = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    return server, server.server_address[1]


def chrome(args: list) -> str:
    """
    Runs headless Chrome with the given flags and a generous time budget for the fonts to arrive

    Args:
        args (list): Flags and the URL, appended after the fixed flags

    Returns:
        str: Whatever Chrome printed to stdout
    """

    base = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--window-size=1300,1000", "--virtual-time-budget=20000"]
    run  = subprocess.run(base + args, capture_output=True, text=True, timeout=120)

    return run.stdout


def build_site(width: int) -> str:
    """
    Lays out a throwaway web root with the repo at its production subpath and the harness at the top

    Args:
        width (int): The page width to render at, in pixels

    Returns:
        str: The path of the web root
    """

    here    = os.path.dirname(os.path.abspath(__file__))
    repo    = os.path.dirname(here)
    harness = os.path.join(here, "overlap-harness")
    subpath = "tools/models-gone-wild"
    root    = tempfile.mkdtemp(prefix="mgw-overlap-")

    os.makedirs(os.path.join(root, os.path.dirname(subpath)))
    os.symlink(repo, os.path.join(root, subpath))
    shutil.copy(os.path.join(harness, "harness.js"), root)

    with open(os.path.join(harness, "harness.html")) as f:
        page = f.read()

    with open(os.path.join(root, "harness.html"), "w") as f:
        f.write(page.replace("__SUBPATH__", subpath).replace("__WIDTH__", str(width)))

    return root



# ========================================================================
#   Main
# ========================================================================

def main() -> int:
    """
    Renders the chart under every filter combination and prints each overlap found

    Args:
        None

    Returns:
        int: 1 if anything overlapped or left the plot, 0 if the chart is clean
    """

    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--shot", help="Write a PNG of the unfiltered chart to this path")
    ap.add_argument("--width", type=int, default=1300,
                    help="Page width in pixels. The chart fills its column, so check a phone width (390) as well")

    opts = ap.parse_args()

    if not os.path.exists(CHROME):
        print(f"Chrome not found at {CHROME}. Set CHROME to its path.")
        return 1

    root = build_site(opts.width)
    server, port = serve(root)

    try:
        url   = f"http://127.0.0.1:{port}/harness.html"
        dom   = chrome(["--dump-dom", url])
        found = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
        raw   = html.unescape(found.group(1)) if found else "PENDING"

        if raw == "PENDING":
            print("The harness never finished. The page may have thrown, or the fonts never loaded.")
            return 1

        results = json.loads(raw)

        if opts.shot:
            chrome([f"--screenshot={os.path.abspath(opts.shot)}", url + "?shot"])
    finally:
        server.shutdown()
        shutil.rmtree(root, ignore_errors=True)

    bad = 0

    for r in results:
        view = f"class {r['classFilter']}, lab {r['labFilter']}, outcome {r.get('outcomeFilter', 'all')}, kind {r.get('kindFilter', 'all')}"

        if r["hits"]:
            bad += 1
            print(f"  OVERLAP  {view}  ({r['items']} items)")

            for h in r["hits"]:
                print(f"           {h}")
        else:
            print(f"  OK       {view}  ({r['items']} items)")

    print(f"\n{len(results)} filter views checked, {bad} with overlaps")

    if opts.shot:
        print(f"screenshot: {opts.shot}")

    return 1 if bad else 0



# ========================================================================
#   Entry Point
# ========================================================================

if __name__ == "__main__":
    sys.exit(main())